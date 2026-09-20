# SPDX-License-Identifier: MIT
"""Minimal TensorRT 10 runner: one engine, synchronous execute on its own CUDA stream.

Uses cuda-python's runtime bindings (cudart) for device memory; no torch on the host.
Inputs and outputs are numpy arrays in the engine's tensor dtype; the caller owns
pre/post-processing.
"""
import numpy as np
import tensorrt as trt

try:  # cuda-python >= 12.6 layout
    from cuda.bindings import runtime as cudart
except ImportError:  # older cuda-python
    from cuda import cudart


def _check(res):
    err = res[0]
    if err != cudart.cudaError_t.cudaSuccess:
        raise RuntimeError(f'CUDA error {err}')
    return res[1] if len(res) > 1 else None


class TrtRunner:
    def __init__(self, engine_path: str, logger_severity=trt.Logger.WARNING):
        self.logger = trt.Logger(logger_severity)
        with open(engine_path, 'rb') as f, trt.Runtime(self.logger) as rt:
            self.engine = rt.deserialize_cuda_engine(f.read())
        if self.engine is None:
            raise RuntimeError(f'failed to load engine {engine_path}')
        self.context = self.engine.create_execution_context()
        self.stream = _check(cudart.cudaStreamCreate())
        self.inputs, self.outputs = {}, {}   # name -> (host ndarray, device ptr, nbytes)
        for i in range(self.engine.num_io_tensors):
            name = self.engine.get_tensor_name(i)
            shape = tuple(self.engine.get_tensor_shape(name))
            if -1 in shape:
                raise RuntimeError(f'{engine_path}: tensor {name} has dynamic shape {shape}; build with fixed --shapes')
            dtype = np.dtype(trt.nptype(self.engine.get_tensor_dtype(name)))
            host = np.empty(shape, dtype=dtype)
            dev = _check(cudart.cudaMalloc(host.nbytes))
            self.context.set_tensor_address(name, int(dev))
            entry = (host, dev, host.nbytes)
            if self.engine.get_tensor_mode(name) == trt.TensorIOMode.INPUT:
                self.inputs[name] = entry
            else:
                self.outputs[name] = entry

    def input_shape(self, name=None):
        name = name or next(iter(self.inputs))
        return self.inputs[name][0].shape

    def __call__(self, *arrays) -> dict:
        """Run with positional inputs (in engine input order). Returns {name: ndarray}."""
        for (name, (host, dev, nbytes)), arr in zip(self.inputs.items(), arrays):
            arr = np.ascontiguousarray(arr, dtype=host.dtype)
            assert arr.shape == host.shape, f'{name}: got {arr.shape}, engine wants {host.shape}'
            _check(cudart.cudaMemcpyAsync(dev, arr.ctypes.data, nbytes,
                                          cudart.cudaMemcpyKind.cudaMemcpyHostToDevice, self.stream))
        if not self.context.execute_async_v3(self.stream):
            raise RuntimeError('execute_async_v3 failed')
        out = {}
        for name, (host, dev, nbytes) in self.outputs.items():
            _check(cudart.cudaMemcpyAsync(host.ctypes.data, dev, nbytes,
                                          cudart.cudaMemcpyKind.cudaMemcpyDeviceToHost, self.stream))
            out[name] = host
        _check(cudart.cudaStreamSynchronize(self.stream))
        return out
