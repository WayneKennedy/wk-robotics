#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Run on the Jetson: build FP16 TensorRT engines from the ONNX models in ~/models.
# Engines are host- and TensorRT-version-specific; rebuild after a JetPack upgrade.
# Each build logs trtexec's own throughput figure (engine only, no pre/post) to <name>.trtexec.log.
set -euo pipefail
MODELS=${MODELS:-$HOME/models}
TRTEXEC=${TRTEXEC:-/usr/src/tensorrt/bin/trtexec}
cd "$MODELS"
build() {  # name, extra args
  local n=$1; shift
  if [ -s "$n.engine" ]; then echo "$n.engine exists, skipping"; return; fi
  echo "== building $n.engine"
  "$TRTEXEC" --onnx="$n.onnx" --saveEngine="$n.engine" --fp16 --memPoolSize=workspace:2048 "$@" \
    2>&1 | tee "$n.trtexec.log" | grep -E "Throughput|Latency|mean|error|Error" | tail -6
}
build yolov8s
build yolov8m
build det_500m  --shapes=input.1:1x3x640x640
build w600k_mbf --shapes=input.1:1x3x112x112
ls -la "$MODELS"/*.engine
