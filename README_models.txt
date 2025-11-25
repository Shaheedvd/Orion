Offline models (GGUF / llama.cpp)

Place your GGUF model files under `backend/models/`. Example: `backend/models/my-gguf-3b.gguf`

This scaffold uses a local stub if no model is provided. To enable local inference with llama.cpp or pyllamacpp:

1. Install dependencies and build llama.cpp (https://github.com/ggerganov/llama.cpp)
2. Install pyllamacpp (pip install pyllamacpp) or use ctypes binding
3. Use `ModelManager.load_local_model(path)` to register the model path. Replace `_call_local_stub` with real generation calls.

TODO: add example commands and exact minimal build steps for Windows.
