#include "hailo_perception/hailo_model.hpp"

#include <cstdlib>
#include <cstring>
#include <stdexcept>

namespace hailo_perception {

static constexpr size_t kPage = 4096;

AlignedBuffer::AlignedBuffer(size_t n) : size(n) {
  size_t rounded = (n + kPage - 1) / kPage * kPage;
  data = static_cast<uint8_t *>(std::aligned_alloc(kPage, rounded));
  if (!data) throw std::bad_alloc();
  std::memset(data, 0, rounded);
}
AlignedBuffer::~AlignedBuffer() { std::free(data); }
AlignedBuffer::AlignedBuffer(AlignedBuffer &&o) noexcept : data(o.data), size(o.size) {
  o.data = nullptr;
  o.size = 0;
}
AlignedBuffer &AlignedBuffer::operator=(AlignedBuffer &&o) noexcept {
  if (this != &o) {
    std::free(data);
    data = o.data;
    size = o.size;
    o.data = nullptr;
    o.size = 0;
  }
  return *this;
}

template <typename T>
static T take(hailort::Expected<T> &&e, const std::string &what) {
  if (!e) throw std::runtime_error(what + ": HailoRT status " + std::to_string(e.status()));
  return e.release();
}

HailoModel::HailoModel(std::shared_ptr<hailort::VDevice> vdevice, const std::string &hef_path)
    : vdevice_(std::move(vdevice)) {
  model_ = take(vdevice_->create_infer_model(hef_path), "create_infer_model " + hef_path);

  auto in_names = model_->get_input_names();
  if (in_names.size() != 1) throw std::runtime_error(hef_path + ": expected one input stream");
  input_name_ = in_names[0];
  auto in = take(model_->input(input_name_), "input");
  in.set_format_type(HAILO_FORMAT_TYPE_UINT8);

  // Shapes come from the HEF's vstream infos; frame sizes from the streams after the
  // format is set, so the float32 request is reflected in the output sizes.
  for (auto &info : take(model_->hef().get_input_vstream_infos(), "input infos")) {
    if (input_name_ == info.name) {
      in_h_ = info.shape.height;
      in_w_ = info.shape.width;
      in_c_ = info.shape.features;
    }
  }
  in_size_ = in.get_frame_size();
  if (in_size_ != static_cast<size_t>(in_h_ * in_w_ * in_c_))
    throw std::runtime_error(hef_path + ": input frame size does not match HxWxC");
  input_ = AlignedBuffer(in_size_);

  for (auto &name : model_->get_output_names()) {
    auto out = take(model_->output(name), "output " + name);
    out.set_format_type(HAILO_FORMAT_TYPE_FLOAT32);
    output_names_.push_back(name);
  }
  for (auto &info : take(model_->hef().get_output_vstream_infos(), "output infos"))
    output_infos_[info.name] = info;

  configured_ = std::make_unique<hailort::ConfiguredInferModel>(take(model_->configure(), "configure " + hef_path));
  bindings_ = std::make_unique<hailort::ConfiguredInferModel::Bindings>(take(configured_->create_bindings(), "create_bindings"));

  auto in_b = take(bindings_->input(input_name_), "bindings input");
  if (in_b.set_buffer(hailort::MemoryView(input_.data, in_size_)) != HAILO_SUCCESS)
    throw std::runtime_error("set input buffer");
  for (auto &name : output_names_) {
    size_t n = take(model_->output(name), "output " + name).get_frame_size();
    outputs_[name] = AlignedBuffer(n);
    auto ob = take(bindings_->output(name), "bindings output " + name);
    if (ob.set_buffer(hailort::MemoryView(outputs_[name].data, n)) != HAILO_SUCCESS)
      throw std::runtime_error("set output buffer " + name);
  }
}

void HailoModel::infer(const uint8_t *rgb, std::chrono::milliseconds timeout) {
  std::memcpy(input_.data, rgb, in_size_);
  auto status = configured_->run(*bindings_, timeout);
  if (status != HAILO_SUCCESS) throw std::runtime_error("infer: HailoRT status " + std::to_string(status));
}

}  // namespace hailo_perception
