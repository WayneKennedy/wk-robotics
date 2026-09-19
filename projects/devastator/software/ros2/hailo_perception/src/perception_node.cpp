// hailo_perception/perception_node — objects (YOLOv8, NMS on-chip) and faces
// (SCRFD detection + ArcFace embeddings matched against a gallery) from one image
// topic, on one Hailo device. One process on purpose: HailoRT lets one process own
// the device unless its multi-process service is running, so both pipelines share a
// VDevice here and the scheduler multiplexes them.
//
// Topics (all under the node's namespace):
//   sub  image            sensor_msgs/Image, rgb8 or bgr8 (usb_cam's /image_raw remapped)
//   sub  enroll           std_msgs/String — name; the next frame's largest face is saved
//                         to <gallery_dir>/<name>.txt and added to the gallery
//   pub  objects          vision_msgs/Detection2DArray, class_id = COCO label
//   pub  faces            vision_msgs/Detection2DArray, class_id = gallery name or "unknown",
//                         score = cosine similarity to the best gallery match
//   pub  image_annotated  sensor_msgs/Image bgr8, boxes and labels drawn
//
// Every 5 s the node logs frames/s and per-stage milliseconds; those are the numbers
// the family's perception bench records (wk-robotics docs/status.md).

#include <cv_bridge/cv_bridge.hpp>
#include <opencv2/calib3d.hpp>
#include <opencv2/imgproc.hpp>
#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/image.hpp>
#include <std_msgs/msg/string.hpp>
#include <vision_msgs/msg/detection2_d_array.hpp>

#include <algorithm>
#include <chrono>
#include <cmath>
#include <filesystem>
#include <fstream>
#include <memory>
#include <string>
#include <vector>

#include "hailo_perception/hailo_model.hpp"

namespace fs = std::filesystem;
using Clock = std::chrono::steady_clock;

namespace {

const char *const kCoco[80] = {
    "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train", "truck", "boat", "traffic light",
    "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat", "dog", "horse", "sheep", "cow",
    "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella", "handbag", "tie", "suitcase", "frisbee",
    "skis", "snowboard", "sports ball", "kite", "baseball bat", "baseball glove", "skateboard", "surfboard",
    "tennis racket", "bottle", "wine glass", "cup", "fork", "knife", "spoon", "bowl", "banana", "apple",
    "sandwich", "orange", "broccoli", "carrot", "hot dog", "pizza", "donut", "cake", "chair", "couch",
    "potted plant", "bed", "dining table", "toilet", "tv", "laptop", "mouse", "remote", "keyboard",
    "cell phone", "microwave", "oven", "toaster", "sink", "refrigerator", "book", "clock", "vase",
    "scissors", "teddy bear", "hair drier", "toothbrush"};

struct Box {
  float x1, y1, x2, y2, score;
  int cls;
  std::vector<cv::Point2f> kps;  // faces: 5 landmarks in frame pixels
  std::string label;
};

// Letterbox `bgr` into a square RGB canvas of side `side`; returns scale and offsets
// so detections can be mapped back to frame pixels.
struct Letterbox {
  float scale;
  int pad_x, pad_y;
};
Letterbox letterbox(const cv::Mat &bgr, int side, cv::Mat &out_rgb) {
  float s = std::min(float(side) / bgr.cols, float(side) / bgr.rows);
  int w = std::max(1, int(std::round(bgr.cols * s))), h = std::max(1, int(std::round(bgr.rows * s)));
  cv::Mat resized;
  cv::resize(bgr, resized, cv::Size(w, h), 0, 0, cv::INTER_LINEAR);
  out_rgb.create(side, side, CV_8UC3);
  out_rgb.setTo(cv::Scalar(114, 114, 114));
  int px = (side - w) / 2, py = (side - h) / 2;
  cv::Mat roi = out_rgb(cv::Rect(px, py, w, h));
  cv::cvtColor(resized, roi, cv::COLOR_BGR2RGB);
  return {s, px, py};
}

float iou(const Box &a, const Box &b) {
  float ix1 = std::max(a.x1, b.x1), iy1 = std::max(a.y1, b.y1), ix2 = std::min(a.x2, b.x2), iy2 = std::min(a.y2, b.y2);
  float inter = std::max(0.f, ix2 - ix1) * std::max(0.f, iy2 - iy1);
  float ua = (a.x2 - a.x1) * (a.y2 - a.y1) + (b.x2 - b.x1) * (b.y2 - b.y1) - inter;
  return ua > 0 ? inter / ua : 0.f;
}

std::vector<Box> nms(std::vector<Box> boxes, float thr) {
  std::sort(boxes.begin(), boxes.end(), [](const Box &a, const Box &b) { return a.score > b.score; });
  std::vector<Box> keep;
  for (auto &b : boxes) {
    bool ok = true;
    for (auto &k : keep)
      if (iou(b, k) > thr) { ok = false; break; }
    if (ok) keep.push_back(b);
  }
  return keep;
}

// ArcFace's canonical 5-point template for a 112x112 crop (left eye, right eye, nose,
// left mouth corner, right mouth corner).
const std::vector<cv::Point2f> kArcfaceTemplate = {
    {38.2946f, 51.6963f}, {73.5318f, 51.5014f}, {56.0252f, 71.7366f}, {41.5493f, 92.3655f}, {70.7299f, 92.2041f}};

struct StageTimer {
  double ms_sum = 0;
  int n = 0;
  void add(double ms) { ms_sum += ms; ++n; }
  double mean() const { return n ? ms_sum / n : 0; }
  void reset() { ms_sum = 0; n = 0; }
};
double ms_since(Clock::time_point t) { return std::chrono::duration<double, std::milli>(Clock::now() - t).count(); }

}  // namespace

class PerceptionNode : public rclcpp::Node {
public:
  PerceptionNode() : Node("hailo_perception") {
    enable_objects_ = declare_parameter<bool>("enable_objects", true);
    enable_faces_ = declare_parameter<bool>("enable_faces", true);
    hef_objects_ = declare_parameter<std::string>("hef_objects", "");
    hef_face_det_ = declare_parameter<std::string>("hef_face_det", "");
    hef_face_id_ = declare_parameter<std::string>("hef_face_id", "");
    object_score_ = declare_parameter<double>("object_score_threshold", 0.4);
    face_score_ = declare_parameter<double>("face_score_threshold", 0.5);
    face_nms_iou_ = declare_parameter<double>("face_nms_iou", 0.4);
    face_match_ = declare_parameter<double>("face_match_threshold", 0.45);
    gallery_dir_ = declare_parameter<std::string>("gallery_dir", std::string(std::getenv("HOME") ? std::getenv("HOME") : "") + "/hailo/gallery");
    publish_annotated_ = declare_parameter<bool>("publish_annotated", true);

    auto vdev = hailort::VDevice::create();
    if (!vdev) throw std::runtime_error("VDevice::create failed, HailoRT status " + std::to_string(vdev.status()));
    vdevice_ = std::shared_ptr<hailort::VDevice>(vdev.release().release());

    if (enable_objects_) {
      objects_ = std::make_unique<hailo_perception::HailoModel>(vdevice_, hef_objects_);
      const auto &info = objects_->output_info(objects_->output_names()[0]);
      if (info.format.order != HAILO_FORMAT_ORDER_HAILO_NMS_BY_CLASS)
        RCLCPP_WARN(get_logger(), "objects HEF output order is %d, expected NMS_BY_CLASS (%d); parsing may be wrong",
                    int(info.format.order), int(HAILO_FORMAT_ORDER_HAILO_NMS_BY_CLASS));
      obj_classes_ = info.nms_shape.number_of_classes;
      obj_max_per_class_ = info.nms_shape.max_bboxes_per_class;
      RCLCPP_INFO(get_logger(), "objects: %s, input %dx%d, %u classes, NMS on-chip", hef_objects_.c_str(),
                  objects_->input_width(), objects_->input_height(), obj_classes_);
    }
    if (enable_faces_) {
      face_det_ = std::make_unique<hailo_perception::HailoModel>(vdevice_, hef_face_det_);
      face_id_ = std::make_unique<hailo_perception::HailoModel>(vdevice_, hef_face_id_);
      map_scrfd_outputs();
      load_gallery();
      RCLCPP_INFO(get_logger(), "faces: %s (%dx%d) + %s (%dx%d), gallery %zu names in %s", hef_face_det_.c_str(),
                  face_det_->input_width(), face_det_->input_height(), hef_face_id_.c_str(), face_id_->input_width(),
                  face_id_->input_height(), gallery_.size(), gallery_dir_.c_str());
    }

    pub_objects_ = create_publisher<vision_msgs::msg::Detection2DArray>("objects", 10);
    pub_faces_ = create_publisher<vision_msgs::msg::Detection2DArray>("faces", 10);
    pub_annotated_ = create_publisher<sensor_msgs::msg::Image>("image_annotated", 1);
    sub_image_ = create_subscription<sensor_msgs::msg::Image>(
        "image", rclcpp::SensorDataQoS().keep_last(1), [this](sensor_msgs::msg::Image::ConstSharedPtr m) { on_image(m); });
    sub_enroll_ = create_subscription<std_msgs::msg::String>("enroll", 10, [this](std_msgs::msg::String::ConstSharedPtr m) {
      pending_enroll_ = m->data;
      RCLCPP_INFO(get_logger(), "enroll: waiting for a face to save as '%s'", m->data.c_str());
    });
    stats_timer_ = create_wall_timer(std::chrono::seconds(5), [this] { report(); });
    RCLCPP_INFO(get_logger(), "ready");
  }

private:
  // SCRFD-2.5g's nine outputs are named conv42..conv57; identify each by shape:
  // features 2 = scores, 8 = boxes, 20 = landmarks; height 80/40/20 = stride 8/16/32.
  struct ScrfdLevel {
    int stride, h, w;
    std::string score, box, kps;
  };
  void map_scrfd_outputs() {
    std::map<int, ScrfdLevel> by_h;
    for (auto &name : face_det_->output_names()) {
      const auto &info = face_det_->output_info(name);
      auto &lvl = by_h[info.shape.height];
      lvl.h = info.shape.height;
      lvl.w = info.shape.width;
      lvl.stride = face_det_->input_height() / info.shape.height;
      if (info.shape.features == 2) lvl.score = name;
      else if (info.shape.features == 8) lvl.box = name;
      else if (info.shape.features == 20) lvl.kps = name;
    }
    for (auto &[h, lvl] : by_h) {
      if (lvl.score.empty() || lvl.box.empty() || lvl.kps.empty())
        throw std::runtime_error("SCRFD outputs at height " + std::to_string(h) + " incomplete");
      scrfd_levels_.push_back(lvl);
    }
  }

  void load_gallery() {
    gallery_.clear();
    if (!fs::exists(gallery_dir_)) return;
    for (auto &e : fs::directory_iterator(gallery_dir_)) {
      if (e.path().extension() != ".txt") continue;
      std::ifstream f(e.path());
      std::vector<float> v;
      float x;
      while (f >> x) v.push_back(x);
      if (v.size() == 512) gallery_.push_back({e.path().stem().string(), v});
      else RCLCPP_WARN(get_logger(), "gallery: %s has %zu values, expected 512", e.path().c_str(), v.size());
    }
  }

  static void l2_normalise(std::vector<float> &v) {
    double n = 0;
    for (float x : v) n += double(x) * x;
    n = std::sqrt(n);
    if (n > 0) for (float &x : v) x = float(x / n);
  }

  // ---- objects -------------------------------------------------------------
  std::vector<Box> detect_objects(const cv::Mat &bgr, StageTimer &t_pre, StageTimer &t_inf, StageTimer &t_post) {
    auto t0 = Clock::now();
    cv::Mat in;
    auto lb = letterbox(bgr, objects_->input_width(), in);
    t_pre.add(ms_since(t0));
    t0 = Clock::now();
    objects_->infer(in.data);
    t_inf.add(ms_since(t0));
    t0 = Clock::now();
    // NMS_BY_CLASS layout: for each class, float32 count then count x
    // {y_min, x_min, y_max, x_max, score} as float32, coordinates normalised to the input.
    const float *p = objects_->output(objects_->output_names()[0]).f32();
    std::vector<Box> out;
    const int side = objects_->input_width();
    for (uint32_t c = 0; c < obj_classes_; ++c) {
      uint32_t n = static_cast<uint32_t>(*p++);
      if (n > obj_max_per_class_) n = obj_max_per_class_;
      for (uint32_t i = 0; i < n; ++i, p += 5) {
        float score = p[4];
        if (score < object_score_) continue;
        Box b;
        b.x1 = (p[1] * side - lb.pad_x) / lb.scale;
        b.y1 = (p[0] * side - lb.pad_y) / lb.scale;
        b.x2 = (p[3] * side - lb.pad_x) / lb.scale;
        b.y2 = (p[2] * side - lb.pad_y) / lb.scale;
        b.score = score;
        b.cls = int(c);
        b.label = c < 80 ? kCoco[c] : std::to_string(c);
        out.push_back(b);
      }
    }
    t_post.add(ms_since(t0));
    return out;
  }

  // ---- faces ---------------------------------------------------------------
  std::vector<Box> detect_faces(const cv::Mat &bgr, StageTimer &t_pre, StageTimer &t_inf, StageTimer &t_post) {
    auto t0 = Clock::now();
    cv::Mat in;
    auto lb = letterbox(bgr, face_det_->input_width(), in);
    t_pre.add(ms_since(t0));
    t0 = Clock::now();
    face_det_->infer(in.data);
    t_inf.add(ms_since(t0));
    t0 = Clock::now();
    std::vector<Box> cands;
    for (auto &lvl : scrfd_levels_) {
      const float *sc = face_det_->output(lvl.score).f32();
      const float *bx = face_det_->output(lvl.box).f32();
      const float *kp = face_det_->output(lvl.kps).f32();
      // The HEF's score output may be logits or already sigmoid; decide per frame.
      bool logits = false;
      for (int i = 0; i < lvl.h * lvl.w * 2; ++i)
        if (sc[i] < 0.f || sc[i] > 1.f) { logits = true; break; }
      for (int r = 0; r < lvl.h; ++r) {
        for (int c = 0; c < lvl.w; ++c) {
          int cell = r * lvl.w + c;
          float cx = float(c * lvl.stride), cy = float(r * lvl.stride);
          for (int a = 0; a < 2; ++a) {
            float s = sc[cell * 2 + a];
            if (logits) s = 1.f / (1.f + std::exp(-s));
            if (s < face_score_) continue;
            const float *d = bx + cell * 8 + a * 4;  // distances l, t, r, b in stride units
            Box b;
            b.x1 = cx - d[0] * lvl.stride;
            b.y1 = cy - d[1] * lvl.stride;
            b.x2 = cx + d[2] * lvl.stride;
            b.y2 = cy + d[3] * lvl.stride;
            b.score = s;
            b.cls = 0;
            const float *k = kp + cell * 20 + a * 10;
            for (int j = 0; j < 5; ++j) b.kps.emplace_back(cx + k[2 * j] * lvl.stride, cy + k[2 * j + 1] * lvl.stride);
            cands.push_back(b);
          }
        }
      }
    }
    auto faces = nms(cands, float(face_nms_iou_));
    // back to frame pixels
    for (auto &f : faces) {
      f.x1 = (f.x1 - lb.pad_x) / lb.scale;
      f.x2 = (f.x2 - lb.pad_x) / lb.scale;
      f.y1 = (f.y1 - lb.pad_y) / lb.scale;
      f.y2 = (f.y2 - lb.pad_y) / lb.scale;
      for (auto &p : f.kps) p = cv::Point2f((p.x - lb.pad_x) / lb.scale, (p.y - lb.pad_y) / lb.scale);
    }
    t_post.add(ms_since(t0));
    return faces;
  }

  std::vector<float> embed_face(const cv::Mat &bgr, const Box &f) {
    cv::Mat M = cv::estimateAffinePartial2D(f.kps, kArcfaceTemplate, cv::noArray(), cv::LMEDS);
    cv::Mat crop;
    if (M.empty()) {
      cv::Rect r(cv::Point(int(f.x1), int(f.y1)), cv::Point(int(f.x2), int(f.y2)));
      r &= cv::Rect(0, 0, bgr.cols, bgr.rows);
      if (r.empty()) return {};
      cv::resize(bgr(r), crop, cv::Size(face_id_->input_width(), face_id_->input_height()));
    } else {
      cv::warpAffine(bgr, crop, M, cv::Size(face_id_->input_width(), face_id_->input_height()), cv::INTER_LINEAR, cv::BORDER_CONSTANT);
    }
    cv::Mat rgb;
    cv::cvtColor(crop, rgb, cv::COLOR_BGR2RGB);
    face_id_->infer(rgb.data);
    const auto &out = face_id_->output(face_id_->output_names()[0]);
    std::vector<float> v(out.f32(), out.f32() + out.size / sizeof(float));
    l2_normalise(v);
    return v;
  }

  void match_face(Box &f, const std::vector<float> &emb) {
    float best = -1.f;
    std::string name = "unknown";
    for (auto &g : gallery_) {
      float dot = 0;
      for (size_t i = 0; i < emb.size() && i < g.second.size(); ++i) dot += emb[i] * g.second[i];
      if (dot > best) { best = dot; name = g.first; }
    }
    f.label = (best >= face_match_) ? name : "unknown";
    f.score = best;  // similarity to the best match, -1 with an empty gallery
  }

  void maybe_enroll(const std::vector<Box> &faces, const std::vector<std::vector<float>> &embs) {
    if (pending_enroll_.empty() || faces.empty()) return;
    size_t best = 0;
    for (size_t i = 1; i < faces.size(); ++i)
      if ((faces[i].x2 - faces[i].x1) * (faces[i].y2 - faces[i].y1) > (faces[best].x2 - faces[best].x1) * (faces[best].y2 - faces[best].y1)) best = i;
    if (embs[best].size() != 512) return;
    fs::create_directories(gallery_dir_);
    std::ofstream f(fs::path(gallery_dir_) / (pending_enroll_ + ".txt"));
    for (float x : embs[best]) f << x << "\n";
    gallery_.erase(std::remove_if(gallery_.begin(), gallery_.end(), [&](auto &g) { return g.first == pending_enroll_; }), gallery_.end());
    gallery_.push_back({pending_enroll_, embs[best]});
    RCLCPP_INFO(get_logger(), "enrolled '%s' (%zu in gallery)", pending_enroll_.c_str(), gallery_.size());
    pending_enroll_.clear();
  }

  // ---- frame ---------------------------------------------------------------
  void on_image(sensor_msgs::msg::Image::ConstSharedPtr msg) {
    auto t_frame = Clock::now();
    cv::Mat bgr;
    try {
      bgr = cv_bridge::toCvCopy(msg, "bgr8")->image;
    } catch (const std::exception &e) {
      RCLCPP_WARN_THROTTLE(get_logger(), *get_clock(), 5000, "cv_bridge: %s", e.what());
      return;
    }

    std::vector<Box> objects, faces;
    if (enable_objects_) objects = detect_objects(bgr, t_obj_pre_, t_obj_inf_, t_obj_post_);
    if (enable_faces_) {
      faces = detect_faces(bgr, t_face_pre_, t_face_inf_, t_face_post_);
      std::vector<std::vector<float>> embs;
      auto t0 = Clock::now();
      for (auto &f : faces) {
        embs.push_back(embed_face(bgr, f));
        if (!embs.back().empty()) match_face(f, embs.back());
        else f.label = "unknown";
      }
      if (!faces.empty()) t_face_id_.add(ms_since(t0));
      maybe_enroll(faces, embs);
    }

    publish_detections(pub_objects_, msg->header, objects);
    publish_detections(pub_faces_, msg->header, faces);
    if (publish_annotated_) publish_annotated(msg->header, bgr, objects, faces);
    t_total_.add(ms_since(t_frame));
    ++frames_;
  }

  void publish_detections(const rclcpp::Publisher<vision_msgs::msg::Detection2DArray>::SharedPtr &pub,
                          const std_msgs::msg::Header &hdr, const std::vector<Box> &boxes) {
    vision_msgs::msg::Detection2DArray arr;
    arr.header = hdr;
    for (auto &b : boxes) {
      vision_msgs::msg::Detection2D d;
      d.header = hdr;
      d.bbox.center.position.x = (b.x1 + b.x2) / 2;
      d.bbox.center.position.y = (b.y1 + b.y2) / 2;
      d.bbox.size_x = b.x2 - b.x1;
      d.bbox.size_y = b.y2 - b.y1;
      vision_msgs::msg::ObjectHypothesisWithPose h;
      h.hypothesis.class_id = b.label;
      h.hypothesis.score = b.score;
      d.results.push_back(h);
      arr.detections.push_back(d);
    }
    pub->publish(arr);
  }

  void publish_annotated(const std_msgs::msg::Header &hdr, cv::Mat bgr, const std::vector<Box> &objects, const std::vector<Box> &faces) {
    auto draw = [&](const Box &b, const cv::Scalar &col, const std::string &text) {
      cv::rectangle(bgr, cv::Point(int(b.x1), int(b.y1)), cv::Point(int(b.x2), int(b.y2)), col, 2);
      int base = 0;
      auto sz = cv::getTextSize(text, cv::FONT_HERSHEY_SIMPLEX, 0.5, 1, &base);
      cv::Point o(int(b.x1), std::max(int(b.y1) - 4, sz.height + 2));
      cv::rectangle(bgr, o + cv::Point(0, base), o + cv::Point(sz.width, -sz.height - 2), col, cv::FILLED);
      cv::putText(bgr, text, o, cv::FONT_HERSHEY_SIMPLEX, 0.5, cv::Scalar(0, 0, 0), 1, cv::LINE_AA);
    };
    char buf[64];
    for (auto &b : objects) {
      std::snprintf(buf, sizeof buf, "%s %.0f%%", b.label.c_str(), b.score * 100);
      draw(b, cv::Scalar(80, 220, 80), buf);
    }
    for (auto &f : faces) {
      std::snprintf(buf, sizeof buf, "%s %.2f", f.label.c_str(), f.score);
      draw(f, cv::Scalar(230, 160, 40), buf);
      for (auto &p : f.kps) cv::circle(bgr, p, 2, cv::Scalar(0, 0, 255), cv::FILLED);
    }
    std::snprintf(buf, sizeof buf, "%.1f fps  %.0f ms", fps_, t_total_.mean());
    cv::putText(bgr, buf, cv::Point(8, 20), cv::FONT_HERSHEY_SIMPLEX, 0.6, cv::Scalar(255, 255, 255), 2, cv::LINE_AA);
    cv_bridge::CvImage out(hdr, "bgr8", bgr);
    pub_annotated_->publish(*out.toImageMsg());
  }

  void report() {
    fps_ = frames_ / 5.0;
    RCLCPP_INFO(get_logger(),
                "%.1f fps, %.1f ms/frame | objects pre %.1f inf %.1f post %.1f | faces pre %.1f inf %.1f post %.1f id %.1f (ms)",
                fps_, t_total_.mean(), t_obj_pre_.mean(), t_obj_inf_.mean(), t_obj_post_.mean(), t_face_pre_.mean(),
                t_face_inf_.mean(), t_face_post_.mean(), t_face_id_.mean());
    frames_ = 0;
    for (auto *t : {&t_total_, &t_obj_pre_, &t_obj_inf_, &t_obj_post_, &t_face_pre_, &t_face_inf_, &t_face_post_, &t_face_id_}) t->reset();
  }

  bool enable_objects_, enable_faces_, publish_annotated_;
  std::string hef_objects_, hef_face_det_, hef_face_id_, gallery_dir_, pending_enroll_;
  double object_score_, face_score_, face_nms_iou_, face_match_;
  uint32_t obj_classes_ = 0, obj_max_per_class_ = 0;

  std::shared_ptr<hailort::VDevice> vdevice_;
  std::unique_ptr<hailo_perception::HailoModel> objects_, face_det_, face_id_;
  std::vector<ScrfdLevel> scrfd_levels_;
  std::vector<std::pair<std::string, std::vector<float>>> gallery_;

  rclcpp::Subscription<sensor_msgs::msg::Image>::SharedPtr sub_image_;
  rclcpp::Subscription<std_msgs::msg::String>::SharedPtr sub_enroll_;
  rclcpp::Publisher<vision_msgs::msg::Detection2DArray>::SharedPtr pub_objects_, pub_faces_;
  rclcpp::Publisher<sensor_msgs::msg::Image>::SharedPtr pub_annotated_;
  rclcpp::TimerBase::SharedPtr stats_timer_;

  int frames_ = 0;
  double fps_ = 0;
  StageTimer t_total_, t_obj_pre_, t_obj_inf_, t_obj_post_, t_face_pre_, t_face_inf_, t_face_post_, t_face_id_;
};

int main(int argc, char **argv) {
  rclcpp::init(argc, argv);
  try {
    rclcpp::spin(std::make_shared<PerceptionNode>());
  } catch (const std::exception &e) {
    RCLCPP_FATAL(rclcpp::get_logger("hailo_perception"), "%s", e.what());
    rclcpp::shutdown();
    return 1;
  }
  rclcpp::shutdown();
  return 0;
}
