#!/usr/bin/env python3
"""
Test script for KoboldAI Kernel Python FFI
Verifies that all core functionality works correctly from Python.
"""

import kobold_kernel_ffi as kernel
import sys

def test_initialization():
    """Test kernel initialization"""
    print("Testing kernel initialization...")
    if not kernel.is_available():
        print("  ✗ FAIL: Kernel library not available")
        return False
    
    if not kernel.init(memory_size_mb=256):
        print("  ✗ FAIL: Failed to initialize kernel")
        return False
    
    print("  ✓ PASS: Kernel initialized successfully")
    return True

def test_story_management():
    """Test story management functionality"""
    print("\nTesting story management...")
    
    try:
        # Create story
        story = kernel.Story()
        print("  ✓ Story created")
        
        # Set memory
        story.set_memory("This is a fantasy world with magic and dragons.")
        print("  ✓ Memory set")
        
        # Set author's note
        story.set_authors_note("[Author's note: Keep the tone adventurous]")
        print("  ✓ Author's note set")
        
        # Create and append chunks
        chunk1 = kernel.StoryChunk("Once upon a time, ", chunk_num=0, token_count=5)
        story.append_chunk(chunk1)
        print("  ✓ Chunk 1 appended")
        
        chunk2 = kernel.StoryChunk("there was a brave knight.", chunk_num=1, token_count=5)
        story.append_chunk(chunk2)
        print("  ✓ Chunk 2 appended")
        
        print("  ✓ PASS: Story management works")
        return True
        
    except Exception as e:
        print(f"  ✗ FAIL: {e}")
        return False

def test_world_info():
    """Test world info functionality"""
    print("\nTesting world info...")
    
    try:
        story = kernel.Story()
        
        # Create world info entries
        entry1 = kernel.WorldInfoEntry(
            keywords="dragon, drake",
            content="Dragons are ancient magical creatures with immense power.",
            selective=True,
            constant=False
        )
        print("  ✓ Selective entry created")
        
        entry2 = kernel.WorldInfoEntry(
            keywords=None,
            content="This world is filled with magic and wonder.",
            selective=False,
            constant=True
        )
        print("  ✓ Constant entry created")
        
        # Add to story
        story.add_worldinfo(entry1)
        story.add_worldinfo(entry2)
        print("  ✓ Entries added to story")
        
        print("  ✓ PASS: World info works")
        return True
        
    except Exception as e:
        print(f"  ✗ FAIL: {e}")
        return False

def test_gen_settings():
    """Test generation settings"""
    print("\nTesting generation settings...")
    
    try:
        settings = kernel.GenSettings()
        print(f"  Temperature: {settings.temperature}")
        print(f"  Top-p: {settings.top_p}")
        print(f"  Top-k: {settings.top_k}")
        print(f"  Max context: {settings.max_context}")
        
        # Modify settings
        settings.temperature = 0.8
        settings.top_p = 0.95
        settings.top_k = 40
        
        print("  ✓ PASS: Generation settings work")
        return True
        
    except Exception as e:
        print(f"  ✗ FAIL: {e}")
        return False

def test_memory_stats():
    """Test memory statistics"""
    print("\nTesting memory statistics...")
    
    try:
        stats = kernel.get_memory_stats()
        print(f"  Total bytes: {stats['total_bytes']}")
        print(f"  Used bytes: {stats['used_bytes']}")
        print(f"  Peak bytes: {stats['peak_bytes']}")
        print(f"  Allocations: {stats['num_allocations']}")
        
        print("  ✓ PASS: Memory stats work")
        return True
        
    except Exception as e:
        print(f"  ✗ FAIL: {e}")
        return False

def test_cleanup():
    """Test cleanup"""
    print("\nTesting cleanup...")
    
    try:
        kernel.shutdown()
        print("  ✓ PASS: Kernel shutdown successfully")
        return True
        
    except Exception as e:
        print(f"  ✗ FAIL: {e}")
        return False

def main():
    """Run all tests"""
    print("="*50)
    print("KoboldAI Kernel Python FFI Test Suite")
    print("="*50)
    
    tests = [
        test_initialization,
        test_story_management,
        test_world_info,
        test_gen_settings,
        test_memory_stats,
        test_cleanup,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        if test():
            passed += 1
        else:
            failed += 1
    
    print("\n" + "="*50)
    print(f"Results: {passed} passed, {failed} failed")
    print("="*50)
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
