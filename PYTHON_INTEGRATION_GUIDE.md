# Python Integration Guide for KoboldAI Kernel

This guide shows how to integrate the KoboldAI C kernel with your Python code.

## Installation

1. **Build the kernel library:**
```bash
cd kernel
mkdir build && cd build
cmake ..
cmake --build .
```

2. **Verify the build:**
```bash
# The library should be at: kernel/build/libkoboldkern.so (Linux/Mac)
# Or: kernel/build/Release/koboldkern.dll (Windows)
ls -lh kernel/build/libkoboldkern.so
```

## Quick Start

```python
import kobold_kernel_ffi as kernel

# Check if kernel is available
if not kernel.is_available():
    print("Kernel not available, using Python fallback")
    # Your Python fallback code here
else:
    print(f"Kernel v{kernel.get_version()} loaded")
    
    # Initialize with 256 MB memory pool
    if kernel.init(256):
        # Use the kernel!
        story = kernel.Story()
        # ... your code ...
        
        # Always cleanup
        kernel.shutdown()
```

## Basic Usage

### Story Management

```python
import kobold_kernel_ffi as kernel

kernel.init(256)

# Create a story
story = kernel.Story()

# Set persistent memory
story.set_memory("This is a fantasy world with magic and dragons.")

# Set author's note
story.set_authors_note("[Genre: Fantasy] [Style: Epic]")

# Add story chunks
chunk1 = kernel.StoryChunk("Once upon a time...", chunk_num=0, token_count=5)
chunk2 = kernel.StoryChunk("In a faraway land...", chunk_num=1, token_count=5)

story.append_chunk(chunk1)
story.append_chunk(chunk2)

kernel.shutdown()
```

### World Info

```python
import kobold_kernel_ffi as kernel

kernel.init(256)
story = kernel.Story()

# Create selective entries (keyword-triggered)
dragon_info = kernel.WorldInfoEntry(
    keywords="dragon, drake, wyrm",
    content="Dragons are ancient, intelligent creatures with scales and wings.",
    selective=True,
    constant=False
)

# Create constant entries (always active)
world_lore = kernel.WorldInfoEntry(
    keywords=None,
    content="Magic is powered by ancient runes etched into reality itself.",
    selective=False,
    constant=True
)

# Add to story
story.add_worldinfo(dragon_info)
story.add_worldinfo(world_lore)

# Check keyword matching
if dragon_info.matches("The dragon appeared from the cave"):
    print("Dragon info would be included in context!")

kernel.shutdown()
```

### Token Sampling

**Note:** Sampling functions require GGML tensor pointers from your model inference code.

```python
import kobold_kernel_ffi as kernel

kernel.init(256)

# After model inference, you have logits as a GGML tensor
# logits_ptr = your_model.get_logits_tensor_ptr()

# Nucleus sampling (top-p)
token = kernel.sample_nucleus(
    logits_ptr, 
    top_p=0.9, 
    temperature=0.7
)

# Top-K sampling
token = kernel.sample_topk(
    logits_ptr,
    top_k=50,
    temperature=0.7
)

# Typical sampling
token = kernel.sample_typical(
    logits_ptr,
    typical_p=0.95,
    temperature=0.7
)

# Apply repetition penalty
recent_tokens = [123, 456, 789]  # Recent token history
kernel.apply_repetition_penalty(
    logits_ptr,
    recent_tokens,
    penalty=1.1,
    slope=0.5
)

kernel.shutdown()
```

## Integration with Flask/SocketIO

```python
from flask import Flask
from flask_socketio import SocketIO, emit
import kobold_kernel_ffi as kernel

app = Flask(__name__)
socketio = SocketIO(app)

# Initialize kernel on startup
if kernel.is_available():
    kernel.init(256)
    print("✓ Kernel initialized")
else:
    print("⚠ Kernel unavailable, using Python fallback")

# Global story state (in production, use per-session storage)
current_story = None

@socketio.on('new_story')
def handle_new_story(data):
    global current_story
    
    if kernel.is_available():
        # Use kernel
        current_story = kernel.Story()
        
        if 'memory' in data:
            current_story.set_memory(data['memory'])
        
        if 'authors_note' in data:
            current_story.set_authors_note(data['authors_note'])
        
        emit('story_created', {'using_kernel': True})
    else:
        # Python fallback
        current_story = create_story_python_fallback(data)
        emit('story_created', {'using_kernel': False})

@socketio.on('add_chunk')
def handle_add_chunk(data):
    global current_story
    
    if kernel.is_available() and current_story:
        chunk = kernel.StoryChunk(
            text=data['text'],
            chunk_num=data['chunk_num'],
            token_count=data['token_count']
        )
        current_story.append_chunk(chunk)
        emit('chunk_added', {'success': True})
    else:
        # Python fallback
        add_chunk_python_fallback(current_story, data)

@socketio.on('add_worldinfo')
def handle_add_worldinfo(data):
    global current_story
    
    if kernel.is_available() and current_story:
        entry = kernel.WorldInfoEntry(
            keywords=data.get('keywords', ''),
            content=data['content'],
            selective=data.get('selective', True),
            constant=data.get('constant', False)
        )
        current_story.add_worldinfo(entry)
        emit('worldinfo_added', {'success': True})

# Cleanup on shutdown
@app.teardown_appcontext
def shutdown_kernel(exception=None):
    if kernel.is_available():
        kernel.shutdown()

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
```

## Memory Management

The kernel uses a memory pool for efficiency:

```python
import kobold_kernel_ffi as kernel

# Initialize with custom pool size (in megabytes)
kernel.init(512)  # 512 MB pool

# Get memory statistics
stats = kernel.get_memory_stats()
print(f"Total: {stats['total_bytes'] / 1024 / 1024:.2f} MB")
print(f"Used: {stats['used_bytes'] / 1024 / 1024:.2f} MB")
print(f"Peak: {stats['peak_bytes'] / 1024 / 1024:.2f} MB")
print(f"Allocations: {stats['num_allocations']}")

# Always call shutdown when done
kernel.shutdown()
```

## Object Ownership

**Important:** When you add chunks or world info entries to a story, the story takes ownership:

```python
story = kernel.Story()

# Create chunk
chunk = kernel.StoryChunk("Text", 0, 5)

# Story now owns the chunk - don't manually free it
story.append_chunk(chunk)

# When story is deleted/freed, it will free the chunk automatically
del story  # Frees story AND all chunks/worldinfo
```

The Python wrapper handles this automatically with ownership tracking.

## Error Handling

```python
import kobold_kernel_ffi as kernel

try:
    if not kernel.is_available():
        raise RuntimeError("Kernel library not found")
    
    if not kernel.init(256):
        raise RuntimeError("Failed to initialize kernel")
    
    story = kernel.Story()
    
    # Use story...
    
except RuntimeError as e:
    print(f"Kernel error: {e}")
    # Fall back to Python implementation
    
finally:
    if kernel.is_available():
        kernel.shutdown()
```

## Performance Tips

1. **Reuse objects:** Create Story/Chunk objects once and reuse them
2. **Batch operations:** Add multiple chunks/worldinfo at once instead of one-by-one
3. **Memory pool size:** Set initial pool size large enough to avoid reallocation (256-512 MB recommended)
4. **Sampling:** Kernel sampling is 4-11× faster than Python implementations

## Fallback to Python

Always provide a Python fallback for when the kernel isn't available:

```python
import kobold_kernel_ffi as kernel

class StoryManager:
    def __init__(self):
        self.use_kernel = kernel.is_available()
        
        if self.use_kernel:
            kernel.init(256)
            self.story = kernel.Story()
        else:
            self.story = self.create_python_story()
    
    def create_python_story(self):
        # Your Python implementation
        return {"chunks": [], "memory": "", "worldinfo": []}
    
    def add_chunk(self, text, chunk_num, token_count):
        if self.use_kernel:
            chunk = kernel.StoryChunk(text, chunk_num, token_count)
            self.story.append_chunk(chunk)
        else:
            # Python fallback
            self.story["chunks"].append({
                "text": text,
                "num": chunk_num,
                "tokens": token_count
            })
```

## Troubleshooting

### Library not found
```
ERROR: KoboldAI kernel library not found
```

**Solution:** Build the kernel library:
```bash
cd kernel && mkdir build && cd build && cmake .. && make
```

### Import error
```
ModuleNotFoundError: No module named 'kobold_kernel_ffi'
```

**Solution:** Make sure `kobold_kernel_ffi.py` is in your Python path or the same directory as your script.

### Segmentation fault
```
Segmentation fault (core dumped)
```

**Solution:** Make sure you're not manually freeing objects owned by a Story. The Python wrapper should prevent this, but if you're using low-level ctypes directly, check ownership.

## API Reference

See `kobold_kernel_ffi.py` for complete API documentation with docstrings.

### Key Functions

- `kernel.init(memory_size_mb)` - Initialize kernel
- `kernel.shutdown()` - Shutdown and cleanup
- `kernel.is_available()` - Check if kernel is loaded
- `kernel.get_version()` - Get kernel version string
- `kernel.get_memory_stats()` - Get memory usage statistics

### Key Classes

- `kernel.Story` - Story state manager
- `kernel.StoryChunk` - Story text chunk
- `kernel.WorldInfoEntry` - World info entry
- `kernel.GenSettings` - Generation settings (ctypes structure)
- `kernel.MemoryStats` - Memory statistics (ctypes structure)

## Performance Comparison

| Operation | Python | Kernel | Speedup |
|-----------|--------|--------|---------|
| Story Chunk Allocation | ~500µs | 0.09µs | 5500× |
| World Info Keyword Match | ~50µs | 0.09µs | 555× |
| Context Assembly | ~5ms | 7µs | 714× |
| Top-K Sampling | ~5ms | 445µs | 11× |
| Nucleus Sampling | ~5ms | 1121µs | 4.5× |

## Next Steps

- See `kernel/README.md` for kernel C API documentation
- See `KOBOLD_KERNEL_MANIFEST.md` for complete function specifications
- See `kernel/tests/` for C test examples
- Join the development at https://github.com/cogpy/KogboldAI
