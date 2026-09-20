# orin-perception — the Jetson half of the perception bench

**Read [`../../AGENTS.md`](../../AGENTS.md) first.** This folder is the Orin Nano half of the
two-host perception experiment specified in
[`docs/status.md` → Perception bench](../../docs/status.md#perception-bench-the-same-experiment-on-the-hat-and-on-the-orin-opened-2026-09-19).
It lives here until the Jetson is allocated to a robot; then it moves to that robot's repo.
The AI HAT+ 2 half is in [`../devastator/software/`](../devastator/software/README.md).
Results go in [`docs/common.md`](../../docs/common.md) beside the HAT measurements, not here.

## What it does

RealSense D435i colour (1280×720×30) → `perception_node` → annotated image → `web_video_server`
(MJPEG at `http://<jetson>:8080/stream?topic=/perception/annotated&type=mjpeg`).

| Stage | Model | Runtime |
|---|---|---|
| Objects | YOLOv8s or YOLOv8m, Ultralytics export, 640×640, COCO-80 | TensorRT FP16 engine, Python API + cuda-python |
| Face detect | SCRFD-500M with 5 keypoints (`det_500m`, InsightFace `buffalo_sc` pack), 640×640 | same |
| Face embed | MobileFaceNet ArcFace (`w600k_mbf`, same pack), 112×112 aligned crop → 512-d | same |
| Recognise | cosine against `~/orin/gallery/<name>.txt`, the HAT half's format (512 floats, one per line) | numpy |

**Same interface as the HAT node** (`hailo_perception`): topics `image`, `enroll`, `objects`,
`faces`, `image_annotated` under the namespace `/orin` (the HAT uses `/hailo`), the same
threshold and gallery parameter names, and the same gallery format, so the two halves are driven
and read the same way. `stats` (JSON, 1 Hz) is additional.

**Model choice vs the HAT half.** The HAT runs `scrfd_2.5g` + `arcface_mobilefacenet` from the
Hailo Model Zoo. InsightFace publishes `scrfd_2.5g` only via Drive/OneDrive, so the Orin uses the
smaller `det_500m` from the curl-able `buffalo_sc` release. Embeddings from different weights are
**not** comparable: the gallery *format* is shared, its *contents* are per-model. `model.txt` in
the gallery directory records which model wrote it and the node warns on a mismatch.

No torch on the Jetson by design: ONNX is produced on a workstation (`scripts/fetch-models.sh`),
engines are built on the Jetson with `trtexec` (`scripts/build-engines.sh`).

## Layout

- `ros2_ws/src/orin_perception/` — ament_python package: `perception_node`, `enrol`, `launch/bench.launch.py`,
  `config/realsense.yaml` (colour only, derived from wk-hexapod's), `config/perception.yaml`.
- `scripts/setup-orin.sh` — host install mirroring wk-hexapod `scripts/ubuntu-setup.sh` (JetPack SDK, ROS 2 Jazzy, realsense2_camera,
  web_video_server, cuda-python). `scripts/deploy.sh` syncs and builds. `scripts/bench-record.sh`
  captures `tegrastats` + `/perception/stats` and summarises.

## Models (not checked in — regenerate with `scripts/fetch-models.sh`)

Exported 2026-09-19 with ultralytics 8.4.155 / torch 2.14.0+cpu / onnx 1.23.0 / onnxslim 0.1.96,
`imgsz=640 opset=17 simplify=True dynamic=False`; InsightFace pack
[`buffalo_sc.zip` (v0.7 release)](https://github.com/deepinsight/insightface/releases/download/v0.7/buffalo_sc.zip).

| File | Input | Output | sha256 |
|---|---|---|---|
| `yolov8s.onnx` | `images` 1×3×640×640 | `output0` 1×84×8400 | `0d3e05a2…74010` |
| `yolov8m.onnx` | same | same | `2c10cfa6…e10aeb` |
| `det_500m.onnx` | `input.1` 1×3×?×? (build at 640) | 9 tensors: scores/bbox/kps × strides 8,16,32 | `5e4447f5…4ea3a` |
| `w600k_mbf.onnx` | `input.1` ?×3×112×112 (build at 1) | `516` 1×512 | `9cc6e4a7…9eb4e` |

## Verified so far

- **Decoders, 2026-09-19, workstation CPU via onnxruntime** (no ROS, no GPU) on Ultralytics'
  `bus.jpg`: YOLOv8s → bus 0.91 and four persons 0.61–0.91 (the reference result for that image);
  SCRFD-500M → two faces at 0.85 and 0.76; ArcFace embeddings of the two faces have cosine 0.00
  to each other and 1.00 to themselves through a gallery write-and-read in the HAT's file format.
  Class-aware NMS is done by offsetting boxes per class, because Ubuntu 24.04's OpenCV 4.6 has no
  `NMSBoxesBatched`.

## Run

```bash
# workstation
scripts/fetch-models.sh <jetson>    # once: ONNX -> jetson ~/models
scripts/deploy.sh <jetson>          # sync this folder to ~/Code/wk-robotics/projects/orin-perception and build
# jetson, in that folder
sudo scripts/setup-orin.sh          # once: JetPack SDK, ROS 2 Jazzy, deps, workspace build
scripts/build-engines.sh            # once per TensorRT version: ONNX -> FP16 engines in ~/models
scripts/launch.sh [yolo_engine:=yolov8m.engine]                 # camera + node + web_video_server
source /opt/ros/jazzy/setup.bash && source ros2_ws/install/setup.bash
ros2 topic pub --once /orin/enroll std_msgs/msg/String "{data: <name>}"   # enrol the largest face in view
ros2 run orin_perception enrol -- --list                                  # or --name x --images a.jpg
scripts/bench-record.sh 60 yolov8s                                         # the numbers for common.md
```

## State

See [`docs/status.md`](../../docs/status.md#perception-bench-the-same-experiment-on-the-hat-and-on-the-orin-opened-2026-09-19).
