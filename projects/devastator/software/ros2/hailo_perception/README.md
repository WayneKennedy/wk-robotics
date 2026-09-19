# hailo_perception

Object detection and face recognition on a Raspberry Pi AI HAT+ 2 (Hailo-10H), as ROS 2
Jazzy topics. The Devastator's intent-tier perception node (its DEC-15), developed and
measured on the family's bench Pi 5 under Ubuntu 24.04. **State (2026-09-19): objects, face
detection and face recognition all run live from a webcam — the owner enrolled from the
stream and was recognised at 0.78 cosine similarity on the next frame.**

## What it does

One process, one Hailo virtual device, three compiled networks from Hailo's public Model
Zoo (v5.4.0, Hailo-10H builds), scheduled by HailoRT:

| Stage | Model | Input | Output handled here |
|---|---|---|---|
| Objects | `yolov8s.hef` (COCO, 80 classes) | 640×640 RGB8, letterboxed | NMS runs **on-chip**; the host reads the `NMS_BY_CLASS` float layout (per class: count, then boxes `{y_min,x_min,y_max,x_max,score}` normalised to the input) and un-letterboxes |
| Face detection | `scrfd_2.5g.hef` | 640×640 RGB8, letterboxed | Nine raw maps (strides 8/16/32 × scores/boxes/landmarks, two anchors per cell), decoded and NMS'd on the CPU; outputs are identified by shape, not name |
| Face identity | `arcface_mobilefacenet.hef` | 112×112 RGB8, aligned by the five landmarks to ArcFace's template | 512-float embedding, L2-normalised, cosine-matched against a gallery |

Outputs are requested from HailoRT as `FLOAT32`, so dequantisation happens in the runtime
and the code never touches quantisation parameters.

Why one process: HailoRT lets one process own the device unless its multi-process
service is running, so objects and faces are two pipelines in one node sharing a
`VDevice`, not two nodes.

## Topics and parameters

Namespace `/hailo` in the launch file.

| | Topic | Type | Notes |
|---|---|---|---|
| sub | `image` | `sensor_msgs/Image` | rgb8 or bgr8; remapped to `/image_raw` from `usb_cam` |
| sub | `enroll` | `std_msgs/String` | a name; the next frame's largest face is saved as `<gallery_dir>/<name>.txt` (512 floats) and joins the gallery |
| pub | `objects` | `vision_msgs/Detection2DArray` | `class_id` = COCO label, `score` = detector confidence |
| pub | `faces` | `vision_msgs/Detection2DArray` | `class_id` = gallery name or `unknown`; `score` = cosine similarity to the best gallery entry (−1 with an empty gallery) |
| pub | `image_annotated` | `sensor_msgs/Image` bgr8 | boxes, labels, landmarks, fps overlay |

Unknown faces are recorded (`record_unknown`, default on): the crop and the embedding go
to `<gallery_dir>/unknown/<timestamp>.{jpg,txt}`, at most one per
`record_unknown_interval_s` (5 s), and the log line carries the best gallery similarity —
the stranger side of the threshold. To enrol one after the fact, rename its `.txt` to
`<name>.txt` in the gallery directory and restart the node.

Parameters (`config/bench.yaml`): `enable_objects`, `enable_faces`, the three `hef_*`
paths (set by the launch file to `~/hailo/models/`), `object_score_threshold` (0.4),
`face_score_threshold` (0.5), `face_nms_iou` (0.4), `face_match_threshold` (0.45 — tune
from the logged similarities; unverified on this camera), `gallery_dir`,
`publish_annotated`.

Every 5 s the node logs fps and per-stage milliseconds (letterbox, inference,
post-processing, identity). Those are the bench numbers.

## Running the bench

```bash
# on the bench host, once: models from the public Model Zoo
mkdir -p ~/hailo/models && cd ~/hailo/models
for m in yolov8s scrfd_2.5g arcface_mobilefacenet; do
  curl -sSL -O https://hailo-model-zoo.s3.eu-west-2.amazonaws.com/ModelZoo/Compiled/v5.4.0/hailo10h/$m.hef
done
# build and run
cd ~/ros2_ws && source /opt/ros/jazzy/setup.bash
colcon build --packages-select hailo_perception && source install/setup.bash
ros2 launch hailo_perception bench.launch.py            # video_device:=/dev/video0
# watch: http://<host>:8080/stream?topic=/hailo/image_annotated
# enrol:  ros2 topic pub --once /hailo/enroll std_msgs/msg/String "{data: wayne}"
```

Host prerequisites are recorded in wk-robotics `docs/common.md` → *Operating system for
the HAT's Pi 5*: `h10-hailort-pcie-driver` and `h10-hailort` 5.1.1 from Raspberry Pi's
apt archive, ROS 2 Jazzy from apt, plus `ros-jazzy-usb-cam`, `ros-jazzy-web-video-server`,
`ros-jazzy-cv-bridge`, `ros-jazzy-vision-msgs`, `libopencv-dev`.

## Measured (2026-09-19, bench Pi 5, Ubuntu 24.04, HailoRT 5.1.1)

C920-clone UVC webcam, 640×480 MJPEG at 30 fps, both pipelines on, no faces in view:
**24 fps, 41 ms/frame** — objects: letterbox 0.8 ms, inference 20.7 ms, parse < 0.1 ms;
faces: letterbox 1.0 ms, inference 16.7 ms, decode 0.1 ms. With one face in view and a
one-entry gallery: **19 fps, 48 ms/frame**, identity (align + ArcFace + match) 4.2 ms;
the owner's face read 0.78 similarity against his own enrolment, the person box 94 %.
The 0.45 match threshold is therefore conservative for the same person; the stranger
side is unmeasured. The two inferences run
back-to-back synchronously in the image callback, so the frame time is their sum; the
HAT itself benchmarks at 166 fps for YOLOv8s alone (`common.md`). Running the two
models concurrently (`run_async`, or a second thread) is the obvious next step and is
not done.

## Known limits

- `usb_cam` 0.8.1 segfaults with `mjpeg2rgb` at 1280×720 on this camera; 640×480 works.
  Untested: `v4l2_camera`, or YUYV at 720p (10 fps on this camera).
- The C920 clone (Sonix `0c45:6536`) dropped off USB and re-enumerated once in the first
  hour, taking `/dev/video0` with it and aborting `usb_cam` ("Unable to exchange buffer
  with the driver"). `usb_cam` 0.8.1 will not open a `/dev/v4l/by-id` symlink (it
  validates against its own `/dev/videoN` list and shuts down), so `~/hailo/bench.sh`
  resolves the by-id link at start and passes the real node; a drop mid-run still needs a
  restart. Whether the drop is the camera, its cable or the Pi's USB 2 port is unknown.
- `pkill -f <node name>` from an interactive shell whose command line mentions the node
  kills that shell: start and stop the bench with `~/hailo/bench.sh` on the host.
- Face recognition is verified on one enrolled face; the stranger side of the match
  threshold is unmeasured. The gallery format is deliberately plain text so the Orin
  half of the bench (wk-robotics `docs/status.md`) can share galleries.
- The SCRFD score maps may arrive as logits or probabilities depending on the HEF; the
  decoder checks the range each frame and applies a sigmoid only if needed.
- The HailoRT Python binding does not install on Ubuntu 24.04 (wants Python 3.13), which
  is why this is C++.

## Licence and provenance

MIT, like the rest of this project's software. The HailoRT API usage follows Hailo's
MIT-licensed `hailo-apps` C++ examples (`hailo_infer.cpp`, the NMS parse in
`object_detection/utils/utils.cpp`), re-derived, not copied; the SCRFD decode follows
InsightFace's reference implementation.
