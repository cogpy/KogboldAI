# KoboldAI Kernel Library

High-performance C/C++ implementation of KoboldAI's AI-assisted writing and storytelling primitives using GGML and llama.cpp backends.

## Overview

The KoboldAI kernel provides optimized implementations of core story generation functions:

- **Story Management**: Chunk allocation, context assembly, memory management
- **Token Sampling**: Nucleus, top-k, typical sampling with repetition penalty
- **World Info**: Keyword matching and context injection
- **Agent Orchestration**: Multi-agent collaboration (planned)
- **World Building**: Procedural generation (planned)

## Performance Targets

| Operation | Target | Status |
|-----------|--------|--------|
| Story Chunk Alloc | ≤100µs | ✓ Implemented |
| Context Assembly | ≤1ms | ⏳ In Progress |
| World Info Scan | ≤2ms | ⏳ Planned |
| Token Sampling | ≤500µs | ⏳ Planned |

## Building

### Prerequisites

- CMake 3.15+
- C99/C++17 compatible compiler (GCC 7+, Clang 8+, MSVC 2019+)
- GGML (from KoboldCpp)

### Build Instructions

```bash
cd kernel
mkdir build
cd build
cmake ..
cmake --build .
```

### Build Options

- `KOBOLD_KERNEL_BUILD_TESTS` - Build test suite (default: ON)
- `KOBOLD_KERNEL_BUILD_BENCHMARKS` - Build benchmarks (default: ON)
- `KOBOLD_KERNEL_BUILD_PYTHON_FFI` - Build Python bindings (default: ON)

### Build Types

```bash
# Debug build with sanitizers
cmake .. -DCMAKE_BUILD_TYPE=Debug

# Optimized release build
cmake .. -DCMAKE_BUILD_TYPE=Release
```

## Running Tests

```bash
cd build
ctest --output-on-failure
```

Or run tests directly:

```bash
./tests/test_kernel
```

## Running Benchmarks

```bash
./tests/benchmark_kernel
```

## API Documentation

See `include/kobold_kernel.h` for the complete API reference with Doxygen-style comments.

### Example Usage

```c
#include "kobold_kernel.h"

int main() {
    // Initialize memory system
    kobold_memory_init(256); // 256 MB pool
    
    // Create a story
    void *story = story_create();
    
    // Add story chunks
    void *chunk = story_chunk_alloc("Once upon a time...", 0, 5);
    story_chunk_append(story, chunk);
    
    // Set memory and author's note
    story_set_memory(story, "The hero is brave and loyal.");
    story_set_authors_note(story, "[Write in fantasy style]");
    
    // Assemble context
    struct gen_settings settings;
    gen_settings_init_default(&settings);
    struct ggml_tensor *ctx = ctx_assemble_tensor(story, &settings, 2048);
    
    // ... use context for generation ...
    
    // Cleanup
    story_free(story);
    kobold_memory_shutdown();
    
    return 0;
}
```

## Python FFI

Python bindings are automatically generated when `KOBOLD_KERNEL_BUILD_PYTHON_FFI=ON`:

```python
from ctypes import CDLL, c_void_p, c_char_p, c_size_t

kobold = CDLL("./libkoboldkern.so")

# Initialize
kobold.kobold_memory_init(256)

# Create story
story = kobold.story_create()

# ... use kernel functions ...

# Cleanup
kobold.story_free(story)
kobold.kobold_memory_shutdown()
```

## Project Structure

```
kernel/
├── include/
│   └── kobold_kernel.h       # Public API
├── src/
│   ├── version.c              # Version info
│   ├── memory.c               # Memory management
│   ├── story_management.c     # Story state and chunks
│   ├── context_assembly.c     # Context assembly (stub)
│   ├── sampler.c              # Token sampling (planned)
│   ├── worldinfo.c            # World info (planned)
│   ├── agent_orchestrator.c   # Agents (planned)
│   └── world_builder.c        # World building (planned)
├── tests/
│   ├── test_main.c            # Test runner
│   ├── test_memory.c          # Memory tests
│   ├── test_story_management.c # Story tests
│   ├── benchmark_main.c       # Benchmark runner
│   └── benchmark_story.c      # Story benchmarks
├── CMakeLists.txt             # Build configuration
└── README.md                  # This file
```

## Development Status

### Phase 1: Foundation (IN PROGRESS - 40%)

- [x] Project structure
- [x] Build system (CMake)
- [x] Memory management
- [x] Story state management
- [x] Chunk allocation
- [x] Basic tests
- [x] Benchmarks
- [ ] Context assembly (stub only)
- [ ] GGML tensor integration
- [ ] Python FFI bindings

### Phase 2: Sampling (PLANNED)

- [ ] Top-p (nucleus) sampling
- [ ] Top-k sampling
- [ ] Typical sampling
- [ ] Repetition penalty
- [ ] Performance optimization

### Phase 3: Advanced Features (PLANNED)

- [ ] World info keyword matching
- [ ] Agent orchestration
- [ ] World building primitives
- [ ] Coherence checking

### Phase 4: Optimization (PLANNED)

- [ ] SIMD vectorization
- [ ] Memory pooling optimization
- [ ] Cache optimization
- [ ] Parallel processing

## Documentation

- [Kernel Function Manifest](../KOBOLD_KERNEL_MANIFEST.md) - Complete function specifications
- [Implementation Status](../KOBOLD_KERNEL_STATUS.md) - Progress tracking
- [Agent Instructions](../.github/agents/kobold-kernel-ggml.md) - Development guidelines

## Performance Notes

The kernel is designed for real-time interactive story generation with strict latency requirements:

- All allocations use a pre-allocated memory pool
- Lock-free data structures where possible
- Thread-safe for concurrent Flask requests
- Minimal overhead (≤10µs for most operations)

## Integration with KoboldAI

The kernel integrates with KoboldAI through:

1. **Direct Linking**: C library linked into Python via ctypes/cffi
2. **Python Fallback**: Automatic fallback to Python implementation if kernel unavailable
3. **API Compatibility**: Matches Python GenerationSettings and story structure
4. **GGML Backend**: Uses existing GGML from KoboldCpp for tensor operations

## Contributing

1. Follow C99/C++17 standards
2. Use Doxygen-style comments for all functions
3. Add tests for new functionality
4. Update KOBOLD_KERNEL_STATUS.md with progress
5. Run tests and benchmarks before committing

## License

Same as KoboldAI (AGPL-3.0). See LICENSE.md in repository root.

## Contact

For issues and questions, see the main KoboldAI repository.
