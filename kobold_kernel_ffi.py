"""
KoboldAI Kernel FFI Bindings

This module provides Python bindings for the KoboldAI kernel library,
which implements high-performance story generation, sampling, and world
building primitives in C/C++ using GGML tensors.

Usage:
    import kobold_kernel_ffi as kernel
    
    # Initialize
    if kernel.init(memory_size_mb=256):
        # Create a story
        story = kernel.Story()
        
        # Add content
        chunk = kernel.StoryChunk("Once upon a time...", chunk_num=0, token_count=5)
        story.append_chunk(chunk)
        
        # Sample tokens (requires logits tensor from model)
        # token = kernel.sample_nucleus(logits, top_p=0.9, temperature=0.7)
        
        # Cleanup
        kernel.shutdown()
"""

import ctypes
import os
import sys
from ctypes import (
    c_void_p, c_char_p, c_int, c_int32, c_uint32, c_size_t, c_float, c_bool,
    POINTER, Structure, CFUNCTYPE, byref, create_string_buffer
)
from typing import Optional, List, Tuple
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Try to find and load the kernel library
def find_kernel_library():
    """Find the kernel library in various possible locations"""
    possible_paths = [
        # Relative to this file
        os.path.join(os.path.dirname(__file__), "kernel", "build", "libkoboldkern.so"),
        os.path.join(os.path.dirname(__file__), "kernel", "build", "libkoboldkern.dylib"),
        os.path.join(os.path.dirname(__file__), "kernel", "build", "Release", "koboldkern.dll"),
        # System paths
        "libkoboldkern.so",
        "libkoboldkern.dylib",
        "koboldkern.dll",
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    return None

# Global library handle
_lib = None
_kernel_available = False

def load_library():
    """Load the kernel library"""
    global _lib, _kernel_available
    
    lib_path = find_kernel_library()
    if lib_path is None:
        logger.warning("KoboldAI kernel library not found. Kernel functions will not be available.")
        logger.warning("Build the kernel with: cd kernel && mkdir build && cd build && cmake .. && make")
        return False
    
    try:
        _lib = ctypes.CDLL(lib_path)
        _kernel_available = True
        logger.info(f"KoboldAI kernel library loaded from {lib_path}")
        _setup_function_signatures()
        return True
    except Exception as e:
        logger.error(f"Failed to load kernel library: {e}")
        return False

# C Structure definitions
class MemoryStats(Structure):
    """Memory statistics structure"""
    _fields_ = [
        ("total_bytes", c_size_t),
        ("used_bytes", c_size_t),
        ("peak_bytes", c_size_t),
        ("num_allocations", c_size_t),
    ]

class GenSettings(Structure):
    """Generation settings structure"""
    _fields_ = [
        ("temperature", c_float),
        ("top_p", c_float),
        ("top_k", c_int32),
        ("top_a", c_float),
        ("tfs", c_float),
        ("typical", c_float),
        ("rep_pen", c_float),
        ("rep_pen_range", c_int32),
        ("rep_pen_slope", c_float),
        ("max_length", c_int32),
        ("max_context", c_int32),
        ("use_memory", c_bool),
        ("use_authors_note", c_bool),
        ("use_world_info", c_bool),
    ]

def _setup_function_signatures():
    """Set up ctypes function signatures for all kernel functions"""
    if not _lib:
        return
    
    # Version
    _lib.kobold_kernel_version.restype = c_char_p
    _lib.kobold_kernel_version.argtypes = []
    
    # Generation settings
    _lib.gen_settings_init_default.restype = None
    _lib.gen_settings_init_default.argtypes = [POINTER(GenSettings)]
    
    # Memory management
    _lib.kobold_memory_init.restype = c_int
    _lib.kobold_memory_init.argtypes = [c_size_t]
    
    _lib.kobold_memory_shutdown.restype = None
    _lib.kobold_memory_shutdown.argtypes = []
    
    _lib.kobold_memory_stats.restype = None
    _lib.kobold_memory_stats.argtypes = [POINTER(MemoryStats)]
    
    # Story management
    _lib.story_create.restype = c_void_p
    _lib.story_create.argtypes = []
    
    _lib.story_free.restype = None
    _lib.story_free.argtypes = [c_void_p]
    
    _lib.story_chunk_alloc.restype = c_void_p
    _lib.story_chunk_alloc.argtypes = [c_char_p, c_uint32, c_size_t]
    
    _lib.story_chunk_free.restype = None
    _lib.story_chunk_free.argtypes = [c_void_p]
    
    _lib.story_chunk_get_tokens.restype = POINTER(c_int32)
    _lib.story_chunk_get_tokens.argtypes = [c_void_p, POINTER(c_size_t)]
    
    _lib.story_chunk_get_num.restype = c_int32
    _lib.story_chunk_get_num.argtypes = [c_void_p]
    
    _lib.story_chunk_append.restype = c_int
    _lib.story_chunk_append.argtypes = [c_void_p, c_void_p]
    
    _lib.story_set_memory.restype = c_int
    _lib.story_set_memory.argtypes = [c_void_p, c_char_p]
    
    _lib.story_set_authors_note.restype = c_int
    _lib.story_set_authors_note.argtypes = [c_void_p, c_char_p]
    
    # Sampling functions
    _lib.sample_nucleus_tensor.restype = c_int32
    _lib.sample_nucleus_tensor.argtypes = [c_void_p, c_float, c_float]
    
    _lib.sample_topk_tensor.restype = c_int32
    _lib.sample_topk_tensor.argtypes = [c_void_p, c_int32, c_float]
    
    _lib.sample_typical_tensor.restype = c_int32
    _lib.sample_typical_tensor.argtypes = [c_void_p, c_float, c_float]
    
    _lib.apply_repetition_penalty.restype = None
    _lib.apply_repetition_penalty.argtypes = [c_void_p, POINTER(c_int32), c_size_t, c_float, c_float]
    
    # World info functions
    _lib.worldinfo_entry_create.restype = c_void_p
    _lib.worldinfo_entry_create.argtypes = [c_char_p, c_char_p, c_bool, c_bool]
    
    _lib.worldinfo_entry_free.restype = None
    _lib.worldinfo_entry_free.argtypes = [c_void_p]
    
    _lib.worldinfo_match_keywords.restype = c_bool
    _lib.worldinfo_match_keywords.argtypes = [c_void_p, c_char_p]
    
    _lib.worldinfo_entry_get_content.restype = c_char_p
    _lib.worldinfo_entry_get_content.argtypes = [c_void_p]
    
    _lib.worldinfo_entry_is_constant.restype = c_bool
    _lib.worldinfo_entry_is_constant.argtypes = [c_void_p]
    
    _lib.worldinfo_entry_is_selective.restype = c_bool
    _lib.worldinfo_entry_is_selective.argtypes = [c_void_p]
    
    _lib.story_add_worldinfo.restype = c_int
    _lib.story_add_worldinfo.argtypes = [c_void_p, c_void_p]

# High-level Python API
def is_available() -> bool:
    """Check if kernel is available"""
    return _kernel_available

def get_version() -> str:
    """Get kernel version string"""
    if not _lib:
        return "unavailable"
    return _lib.kobold_kernel_version().decode('utf-8')

def init(memory_size_mb: int = 256) -> bool:
    """
    Initialize the kernel memory system
    
    Args:
        memory_size_mb: Memory pool size in megabytes
        
    Returns:
        True on success, False on failure
    """
    if not _lib:
        return False
    return _lib.kobold_memory_init(memory_size_mb) == 0

def shutdown():
    """Shutdown the kernel and free all resources"""
    if _lib:
        _lib.kobold_memory_shutdown()

def get_memory_stats() -> dict:
    """
    Get memory usage statistics
    
    Returns:
        Dictionary with memory stats
    """
    if not _lib:
        return {}
    
    stats = MemoryStats()
    _lib.kobold_memory_stats(byref(stats))
    
    return {
        "total_bytes": stats.total_bytes,
        "used_bytes": stats.used_bytes,
        "peak_bytes": stats.peak_bytes,
        "num_allocations": stats.num_allocations,
    }

class StoryChunk:
    """Represents a story chunk"""
    
    def __init__(self, text: str, chunk_num: int, token_count: int):
        """
        Create a story chunk
        
        Args:
            text: Story text content
            chunk_num: Sequence number in story
            token_count: Number of tokens in chunk
        """
        if not _lib:
            raise RuntimeError("Kernel library not available")
        
        self._handle = _lib.story_chunk_alloc(
            text.encode('utf-8'),
            chunk_num,
            token_count
        )
        
        if not self._handle:
            raise RuntimeError("Failed to allocate story chunk")
        
        self._owned_by_story = False  # Track ownership
    
    def __del__(self):
        """Free the chunk (only if not owned by a story)"""
        if hasattr(self, '_handle') and self._handle and _lib and not getattr(self, '_owned_by_story', False):
            _lib.story_chunk_free(self._handle)
    
    def _mark_owned(self):
        """Mark this chunk as owned by a story (internal use)"""
        self._owned_by_story = True
    
    @property
    def chunk_num(self) -> int:
        """Get chunk number"""
        if not self._handle or not _lib:
            return -1
        return _lib.story_chunk_get_num(self._handle)
    
    def get_tokens(self) -> List[int]:
        """Get token IDs"""
        if not self._handle or not _lib:
            return []
        
        count = c_size_t()
        tokens_ptr = _lib.story_chunk_get_tokens(self._handle, byref(count))
        
        if not tokens_ptr:
            return []
        
        return [tokens_ptr[i] for i in range(count.value)]

class WorldInfoEntry:
    """Represents a world info entry"""
    
    def __init__(self, keywords: str, content: str, selective: bool = True, constant: bool = False):
        """
        Create a world info entry
        
        Args:
            keywords: Comma-separated keyword list
            content: Entry content text
            selective: True for keyword-based activation
            constant: True for always-active entries
        """
        if not _lib:
            raise RuntimeError("Kernel library not available")
        
        self._handle = _lib.worldinfo_entry_create(
            keywords.encode('utf-8') if keywords else None,
            content.encode('utf-8'),
            selective,
            constant
        )
        
        if not self._handle:
            raise RuntimeError("Failed to create world info entry")
        
        self._owned_by_story = False  # Track ownership
    
    def __del__(self):
        """Free the entry (only if not owned by a story)"""
        if hasattr(self, '_handle') and self._handle and _lib and not getattr(self, '_owned_by_story', False):
            _lib.worldinfo_entry_free(self._handle)
    
    def _mark_owned(self):
        """Mark this entry as owned by a story (internal use)"""
        self._owned_by_story = True
    
    def matches(self, context: str) -> bool:
        """Check if keywords match the given context"""
        if not self._handle or not _lib:
            return False
        return _lib.worldinfo_match_keywords(self._handle, context.encode('utf-8'))
    
    @property
    def content(self) -> str:
        """Get entry content"""
        if not self._handle or not _lib:
            return ""
        content_ptr = _lib.worldinfo_entry_get_content(self._handle)
        return content_ptr.decode('utf-8') if content_ptr else ""
    
    @property
    def is_constant(self) -> bool:
        """Check if always active"""
        if not self._handle or not _lib:
            return False
        return _lib.worldinfo_entry_is_constant(self._handle)
    
    @property
    def is_selective(self) -> bool:
        """Check if keyword-triggered"""
        if not self._handle or not _lib:
            return False
        return _lib.worldinfo_entry_is_selective(self._handle)

class Story:
    """Represents a story with chunks, memory, and world info"""
    
    def __init__(self):
        """Create a new story"""
        if not _lib:
            raise RuntimeError("Kernel library not available")
        
        self._handle = _lib.story_create()
        if not self._handle:
            raise RuntimeError("Failed to create story")
        
        self._chunks = []  # Keep references to prevent GC
        self._worldinfo = []  # Keep references to prevent GC
    
    def __del__(self):
        """Free the story"""
        if hasattr(self, '_handle') and self._handle and _lib:
            _lib.story_free(self._handle)
    
    def append_chunk(self, chunk: StoryChunk) -> bool:
        """
        Append a chunk to the story
        
        Args:
            chunk: StoryChunk to append
            
        Returns:
            True on success, False on failure
            
        Note:
            The story takes ownership of the chunk. The chunk will be freed
            when the story is freed. Do not manually free the chunk after appending it.
        """
        if not self._handle or not _lib:
            return False
        
        result = _lib.story_chunk_append(self._handle, chunk._handle)
        if result == 0:
            chunk._mark_owned()  # Story now owns this chunk
            self._chunks.append(chunk)  # Keep reference to prevent GC
            return True
            return True
        return False
    
    def set_memory(self, memory_text: str) -> bool:
        """Set persistent memory text"""
        if not self._handle or not _lib:
            return False
        return _lib.story_set_memory(self._handle, memory_text.encode('utf-8')) == 0
    
    def set_authors_note(self, note_text: str) -> bool:
        """Set author's note text"""
        if not self._handle or not _lib:
            return False
        return _lib.story_set_authors_note(self._handle, note_text.encode('utf-8')) == 0
    
    def add_worldinfo(self, entry: WorldInfoEntry) -> bool:
        """
        Add a world info entry to the story
        
        Args:
            entry: WorldInfoEntry to add
            
        Returns:
            True on success, False on failure
            
        Note:
            The story takes ownership of the entry. The entry will be freed
            when the story is freed. Do not manually free the entry after adding it.
        """
        if not self._handle or not _lib:
            return False
        
        result = _lib.story_add_worldinfo(self._handle, entry._handle)
        if result == 0:
            entry._mark_owned()  # Story now owns this entry
            self._worldinfo.append(entry)  # Keep reference to prevent GC
            return True
        return False

# Sampling functions
def sample_nucleus(logits_tensor_ptr: int, top_p: float = 0.9, temperature: float = 0.7) -> int:
    """
    Sample a token using nucleus (top-p) sampling
    
    Args:
        logits_tensor_ptr: Pointer to GGML logits tensor (as integer)
        top_p: Cumulative probability threshold (0.0-1.0)
        temperature: Sampling temperature
        
    Returns:
        Sampled token ID, or -1 on error
    """
    if not _lib:
        return -1
    return _lib.sample_nucleus_tensor(logits_tensor_ptr, top_p, temperature)

def sample_topk(logits_tensor_ptr: int, top_k: int = 50, temperature: float = 0.7) -> int:
    """
    Sample a token using top-k sampling
    
    Args:
        logits_tensor_ptr: Pointer to GGML logits tensor (as integer)
        top_k: Number of top tokens to consider
        temperature: Sampling temperature
        
    Returns:
        Sampled token ID, or -1 on error
    """
    if not _lib:
        return -1
    return _lib.sample_topk_tensor(logits_tensor_ptr, top_k, temperature)

def sample_typical(logits_tensor_ptr: int, typical_p: float = 0.95, temperature: float = 0.7) -> int:
    """
    Sample a token using typical (locally typical) sampling
    
    Args:
        logits_tensor_ptr: Pointer to GGML logits tensor (as integer)
        typical_p: Typical probability mass
        temperature: Sampling temperature
        
    Returns:
        Sampled token ID, or -1 on error
    """
    if not _lib:
        return -1
    return _lib.sample_typical_tensor(logits_tensor_ptr, typical_p, temperature)

def apply_repetition_penalty(
    logits_tensor_ptr: int,
    recent_tokens: List[int],
    penalty: float = 1.1,
    slope: float = 0.5
):
    """
    Apply repetition penalty to logits based on recent tokens
    
    Args:
        logits_tensor_ptr: Pointer to GGML logits tensor (as integer)
        recent_tokens: List of recent token IDs
        penalty: Repetition penalty value (>1.0 = penalty)
        slope: Penalty decay slope
    """
    if not _lib or not recent_tokens:
        return
    
    # Convert to C array
    token_array = (c_int32 * len(recent_tokens))(*recent_tokens)
    
    _lib.apply_repetition_penalty(
        logits_tensor_ptr,
        token_array,
        len(recent_tokens),
        penalty,
        slope
    )

# Auto-load library on import
load_library()

# Example usage
if __name__ == "__main__":
    print(f"KoboldAI Kernel FFI")
    print(f"Available: {is_available()}")
    print(f"Version: {get_version()}")
    
    if is_available():
        print("\nInitializing kernel...")
        if init(256):
            print("✓ Kernel initialized")
            
            print("\nMemory stats:")
            stats = get_memory_stats()
            for key, value in stats.items():
                print(f"  {key}: {value}")
            
            print("\nTesting Story API...")
            story = Story()
            print("✓ Story created")
            
            chunk = StoryChunk("Once upon a time...", 0, 5)
            print(f"✓ Chunk created (num={chunk.chunk_num})")
            
            story.append_chunk(chunk)
            print("✓ Chunk appended")
            
            story.set_memory("This is a fantasy world.")
            print("✓ Memory set")
            
            story.set_authors_note("[Genre: Fantasy]")
            print("✓ Author's note set")
            
            print("\nTesting World Info API...")
            entry = WorldInfoEntry(
                keywords="dragon, drake",
                content="Dragons are mighty creatures.",
                selective=True,
                constant=False
            )
            print(f"✓ World info entry created")
            print(f"  Content: {entry.content}")
            print(f"  Is constant: {entry.is_constant}")
            print(f"  Is selective: {entry.is_selective}")
            print(f"  Matches 'dragon': {entry.matches('The dragon appeared')}")
            print(f"  Matches 'cat': {entry.matches('The cat meowed')}")
            
            story.add_worldinfo(entry)
            print("✓ World info added to story")
            
            print("\n✓ All tests passed!")
            
            # Explicitly delete objects before shutdown to avoid double-free
            del story
            del chunk  
            del entry
            
            shutdown()
            print("\n✓ Kernel shutdown")
        else:
            print("✗ Failed to initialize kernel")
    else:
        print("\n✗ Kernel library not available")
        print("Build the kernel with: cd kernel && mkdir build && cd build && cmake .. && make")
