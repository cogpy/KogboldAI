# KoboldAI Kernel Troubleshooting Guide

This guide helps you diagnose and fix common issues with the KoboldAI kernel.

## Table of Contents
1. [Build Issues](#build-issues)
2. [Python Integration Issues](#python-integration-issues)
3. [Runtime Errors](#runtime-errors)
4. [Performance Issues](#performance-issues)
5. [Memory Issues](#memory-issues)
6. [Platform-Specific Issues](#platform-specific-issues)

---

## Build Issues

### Problem: CMake not found
**Symptom:**
```
bash: cmake: command not found
```

**Solution:**
```bash
# Ubuntu/Debian
sudo apt-get install cmake

# macOS
brew install cmake

# Windows (use chocolatey)
choco install cmake
```

### Problem: Compiler errors about C99/C++17
**Symptom:**
```
error: 'for' loop initial declarations are only allowed in C99 mode
```

**Solution:**
Ensure you're using a modern compiler:
```bash
# Check versions
gcc --version    # Should be 7.0+
g++ --version    # Should be 7.0+

# Update if needed (Ubuntu/Debian)
sudo apt-get install build-essential
```

### Problem: GGML source files not found
**Symptom:**
```
fatal error: ggml.h: No such file or directory
```

**Solution:**
The kernel expects GGML sources in `modeling/inference_models/koboldcpp/`. Make sure you have the full repository:
```bash
# Clone the full repository
git clone https://github.com/cogpy/KogboldAI.git
cd KogboldAI

# Check GGML files exist
ls modeling/inference_models/koboldcpp/ggml.c
```

### Problem: Build fails with undefined references
**Symptom:**
```
undefined reference to `pthread_create'
```

**Solution:**
Add pthread library to your build:
```bash
cd kernel/build
cmake .. -DCMAKE_C_FLAGS="-lpthread"
cmake --build .
```

---

## Python Integration Issues

### Problem: Kernel library not found
**Symptom:**
```python
Kernel available: False
Library loaded successfully
```

**Solution:**
1. Build the kernel first:
```bash
cd kernel
mkdir build && cd build
cmake .. && cmake --build .
```

2. Check library exists:
```bash
ls kernel/build/libkoboldkern.so      # Linux
ls kernel/build/libkoboldkern.dylib   # macOS
ls kernel/build/Release/koboldkern.dll # Windows
```

3. Update `kobold_kernel_ffi.py` if your library is in a different location.

### Problem: Import error for kobold_kernel_ffi
**Symptom:**
```python
ModuleNotFoundError: No module named 'kobold_kernel_ffi'
```

**Solution:**
Make sure you're running Python from the KoboldAI root directory:
```bash
cd /path/to/KogboldAI
python3 -c "import kobold_kernel_ffi"
```

Or add to PYTHONPATH:
```bash
export PYTHONPATH=/path/to/KogboldAI:$PYTHONPATH
python3 your_script.py
```

### Problem: Segmentation fault on library load
**Symptom:**
```
Segmentation fault (core dumped)
```

**Solution:**
1. Rebuild in debug mode to get more info:
```bash
cd kernel/build
cmake .. -DCMAKE_BUILD_TYPE=Debug
cmake --build .
```

2. Run with debugger:
```bash
gdb python3
(gdb) run test_python_ffi.py
(gdb) backtrace  # After crash
```

3. Check for ABI compatibility issues - ensure Python and library are both 64-bit or both 32-bit.

---

## Runtime Errors

### Problem: Initialization fails
**Symptom:**
```python
kernel.init(256)  # Returns False
```

**Solution:**
1. Check memory availability:
```bash
free -h  # Linux
vm_stat  # macOS
```

2. Try a smaller memory pool:
```python
kernel.init(64)  # Use 64 MB instead of 256 MB
```

3. Check error logs:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
import kobold_kernel_ffi as kernel
kernel.init(256)
```

### Problem: "Invalid handle" errors
**Symptom:**
```
ValueError: Invalid handle
```

**Solution:**
Don't use objects after they've been freed or transferred ownership:
```python
# Bad: Using chunk after adding to story
chunk = kernel.StoryChunk("text", 0, 5)
story.append_chunk(chunk)  # Story takes ownership
chunk.free()  # ERROR: Double free!

# Good: Let story manage the lifecycle
chunk = kernel.StoryChunk("text", 0, 5)
story.append_chunk(chunk)
# Don't free chunk manually
```

### Problem: World info not matching keywords
**Symptom:**
World info entries not being triggered.

**Solution:**
1. Check keyword format (case-insensitive, comma-separated):
```python
# Correct
entry = kernel.WorldInfoEntry(
    keywords="dragon, drake, wyrm",  # Comma-separated
    content="...",
    selective=True
)

# Wrong
entry = kernel.WorldInfoEntry(
    keywords="dragon;drake;wyrm",  # Don't use semicolons
    content="...",
    selective=True
)
```

2. Ensure context text contains the keywords:
```python
context = "A dragon appeared"  # Will match "dragon"
```

3. Check if entry is actually selective:
```python
# This will always be included (constant=True)
entry = kernel.WorldInfoEntry(
    keywords="dragon",
    content="...",
    selective=False,  # Not keyword-triggered
    constant=True     # Always active
)
```

---

## Performance Issues

### Problem: Sampling slower than expected
**Symptom:**
Benchmarks show 5-10ms sampling time instead of <1ms.

**Solution:**
1. This is normal for random uniform distributions (test data). Real LLM outputs are more peaked.

2. Check if you're in Debug mode:
```bash
cd kernel/build
cmake .. -DCMAKE_BUILD_TYPE=Release  # Use Release mode
cmake --build .
```

3. Verify optimization flags are applied:
```bash
cmake .. -DCMAKE_BUILD_TYPE=Release -DCMAKE_C_FLAGS="-O3 -march=native"
cmake --build .
```

### Problem: No speedup over Python
**Symptom:**
Kernel performance similar to Python.

**Solution:**
1. Ensure you're using Release build (see above).

2. Profile to find bottlenecks:
```bash
cd kernel/build
perf record ./tests/benchmark_kernel
perf report
```

3. Check if softmax is the bottleneck (expected for 50k vocabularies).

---

## Memory Issues

### Problem: Memory leak detected
**Symptom:**
Memory usage grows over time.

**Solution:**
1. Ensure proper cleanup:
```python
try:
    kernel.init(256)
    story = kernel.Story()
    # ... use story ...
finally:
    kernel.shutdown()  # Always shutdown
```

2. Check for Python reference cycles:
```python
import gc
gc.collect()  # Force garbage collection
```

3. Run with Valgrind to find leaks:
```bash
valgrind --leak-check=full ./tests/test_kernel
```

### Problem: Out of memory
**Symptom:**
```
Failed to allocate memory
```

**Solution:**
1. Reduce memory pool size:
```python
kernel.init(128)  # Use 128 MB instead of 256 MB
```

2. Free stories when done:
```python
story = kernel.Story()
# ... use story ...
del story  # Free immediately
gc.collect()
```

3. Check system memory:
```bash
free -h
top
```

---

## Platform-Specific Issues

### Linux

**Problem: Library not found at runtime**
**Solution:**
```bash
# Add to library path
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/path/to/kernel/build
```

**Problem: Permission denied**
**Solution:**
```bash
chmod +x kernel/build/libkoboldkern.so
chmod +x test_python_ffi.py
```

### macOS

**Problem: Library blocked by Gatekeeper**
**Solution:**
```bash
# Remove quarantine attribute
xattr -d com.apple.quarantine kernel/build/libkoboldkern.dylib
```

**Problem: Architecture mismatch (M1/M2)**
**Solution:**
Rebuild for ARM64:
```bash
cd kernel/build
cmake .. -DCMAKE_OSX_ARCHITECTURES=arm64
cmake --build .
```

### Windows

**Problem: DLL not found**
**Solution:**
1. Install Visual C++ Redistributables
2. Add to PATH:
```cmd
set PATH=%PATH%;C:\path\to\kernel\build\Release
```

**Problem: MSVC not found**
**Solution:**
Install Visual Studio Build Tools:
https://visualstudio.microsoft.com/downloads/

Then use x64 Native Tools Command Prompt.

---

## Getting More Help

### Enable Debug Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)

import kobold_kernel_ffi as kernel
# Now all operations will log details
```

### Run Tests
```bash
# C tests
cd kernel/build
./tests/test_kernel

# Python tests
python3 test_python_ffi.py

# Benchmarks
./tests/benchmark_kernel
```

### Check Version
```python
import kobold_kernel_ffi as kernel
print(f"Kernel version: {kernel.get_version()}")
print(f"Available: {kernel.is_available()}")
```

### Memory Statistics
```python
import kobold_kernel_ffi as kernel
kernel.init(256)
stats = kernel.get_memory_stats()
print(f"Memory used: {stats['used_bytes']} bytes")
print(f"Peak usage: {stats['peak_bytes']} bytes")
print(f"Allocations: {stats['num_allocations']}")
```

### Report Issues
If you can't resolve your issue:

1. Check existing issues: https://github.com/cogpy/KogboldAI/issues
2. Create new issue with:
   - Operating system and version
   - Python version (`python3 --version`)
   - Compiler version (`gcc --version`)
   - Full error message
   - Steps to reproduce
   - Output of `kernel.get_version()`

---

## Common Solutions Summary

| Problem | Quick Fix |
|---------|-----------|
| Build fails | Install cmake, gcc 7+, check GGML files exist |
| Library not found | Build kernel, check build/libkoboldkern.so exists |
| Segfault | Rebuild in Debug mode, check with gdb |
| Slow performance | Use Release build, -O3 -march=native flags |
| Memory leak | Always call kernel.shutdown() |
| Import error | Run from KoboldAI root directory |
| World info not matching | Use comma-separated keywords, check selective flag |
| Out of memory | Reduce pool size, free unused stories |

---

## Advanced Debugging

### GDB (Linux/macOS)
```bash
gdb python3
(gdb) run test_python_ffi.py
# On crash:
(gdb) backtrace
(gdb) info locals
(gdb) print variable_name
```

### Valgrind (Memory debugging)
```bash
valgrind --leak-check=full --show-leak-kinds=all python3 test_python_ffi.py
```

### AddressSanitizer (Detect memory errors)
```bash
cd kernel/build
cmake .. -DCMAKE_BUILD_TYPE=Debug
cmake --build .
ASAN_OPTIONS=detect_leaks=1 ./tests/test_kernel
```

### Profiling
```bash
# CPU profiling
perf record -g ./tests/benchmark_kernel
perf report

# Memory profiling
valgrind --tool=massif ./tests/benchmark_kernel
ms_print massif.out.*
```

---

## FAQ

**Q: Do I need to build the kernel?**
A: No, it's optional. KoboldAI will work fine without it, just slower.

**Q: Will the kernel work on my CPU?**
A: Yes, it works on any x86-64 or ARM CPU. No special requirements.

**Q: Does it need a GPU?**
A: No, the kernel runs entirely on CPU. GPU is only for the AI models.

**Q: Is it thread-safe?**
A: Yes, all operations are thread-safe for concurrent Flask requests.

**Q: Can I use it in production?**
A: Yes, it's production-ready and has automatic fallback to Python.

**Q: How much faster is it?**
A: 4-5500× faster depending on operation. See README for benchmarks.

---

**Last Updated:** 2025-12-06  
**Kernel Version:** 1.0.0  
**Status:** Production Ready
