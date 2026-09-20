// One compiled network (HEF) on a shared Hailo virtual device, run synchronously.
// Outputs are requested as FLOAT32 so HailoRT dequantises them; callers never see
// the HEF's native UINT8 outputs or its quantisation parameters.
#pragma once

#include <hailo/hailort.hpp>

#include <chrono>
#include <cstdint>
#include <map>
#include <memory>
#include <string>
#include <vector>

namespace hailo_perception {

// Page-aligned buffer, as HailoRT prefers for DMA.
struct AlignedBuffer {
  uint8_t *data = nullptr;
  size_t size = 0;
  AlignedBuffer() = default;
  explicit AlignedBuffer(size_t n);
  ~AlignedBuffer();
  AlignedBuffer(const AlignedBuffer &) = delete;
  AlignedBuffer &operator=(const AlignedBuffer &) = delete;
  AlignedBuffer(AlignedBuffer &&o) noexcept;
  AlignedBuffer &operator=(AlignedBuffer &&o) noexcept;
  const float *f32() const { return reinterpret_cast<const float *>(data); }
};

class HailoModel {
public:
  // Several HailoModels may share one VDevice; HailoRT's scheduler multiplexes them.
  HailoModel(std::shared_ptr<hailort::VDevice> vdevice, const std::string &hef_path);

  // The single input stream, NHWC UINT8.
  int input_height() const { return in_h_; }
  int input_width() const { return in_w_; }
  int input_channels() const { return in_c_; }
  size_t input_size() const { return in_size_; }

  // Run one frame. `rgb` must be exactly input_size() bytes, HWC, row-major.
  void infer(const uint8_t *rgb, std::chrono::milliseconds timeout = std::chrono::milliseconds(2000));

  // Output buffers by vstream name, valid until the next infer().
  const AlignedBuffer &output(const std::string &name) const { return outputs_.at(name); }
  const std::vector<std::string> &output_names() const { return output_names_; }
  const hailo_vstream_info_t &output_info(const std::string &name) const { return output_infos_.at(name); }

private:
  std::shared_ptr<hailort::VDevice> vdevice_;
  std::shared_ptr<hailort::InferModel> model_;
  std::unique_ptr<hailort::ConfiguredInferModel> configured_;
  std::unique_ptr<hailort::ConfiguredInferModel::Bindings> bindings_;
  std::string input_name_;
  int in_h_ = 0, in_w_ = 0, in_c_ = 0;
  size_t in_size_ = 0;
  AlignedBuffer input_;
  std::vector<std::string> output_names_;
  std::map<std::string, AlignedBuffer> outputs_;
  std::map<std::string, hailo_vstream_info_t> output_infos_;
};

}  // namespace hailo_perception
