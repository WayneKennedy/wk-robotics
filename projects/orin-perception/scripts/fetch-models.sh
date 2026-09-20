#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Run on a workstation (not the Jetson): produce the four ONNX models the bench uses and
# copy them to the Jetson's ~/models. Provenance and checksums are in ../AGENTS.md.
#   ./fetch-models.sh <jetson-ssh-host>
set -euo pipefail
HOST=${1:?usage: fetch-models.sh <jetson-ssh-host>}
WORK=${WORK:-$(mktemp -d)}
cd "$WORK"
uv venv export-venv -p 3.12 -q
uv pip install -q -p export-venv/bin/python torch --index-url https://download.pytorch.org/whl/cpu
uv pip install -q -p export-venv/bin/python ultralytics onnx onnxslim
for m in yolov8s yolov8m; do
  export-venv/bin/yolo export model=$m.pt format=onnx imgsz=640 opset=17 simplify=True dynamic=False
done
curl -sL -o buffalo_sc.zip https://github.com/deepinsight/insightface/releases/download/v0.7/buffalo_sc.zip
python3 -c "import zipfile; zipfile.ZipFile('buffalo_sc.zip').extractall('buffalo_sc')"
sha256sum yolov8s.onnx yolov8m.onnx buffalo_sc/det_500m.onnx buffalo_sc/w600k_mbf.onnx
ssh "$HOST" 'mkdir -p ~/models'
scp yolov8s.onnx yolov8m.onnx buffalo_sc/det_500m.onnx buffalo_sc/w600k_mbf.onnx "$HOST":~/models/
echo "models in $WORK, copied to $HOST:~/models"
