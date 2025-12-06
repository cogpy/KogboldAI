/**
 * @file test_memory.c
 * @brief Tests for memory management functions
 */

#include "kobold_kernel.h"
#include <stdio.h>
#include <assert.h>

/**
 * @brief Test memory initialization and shutdown
 */
int test_memory_init_shutdown(void) {
    /* Test initialization */
    int ret = kobold_memory_init(256);
    if (ret != 0) {
        fprintf(stderr, "Failed to initialize memory system\n");
        return -1;
    }
    
    /* Test shutdown */
    kobold_memory_shutdown();
    
    /* Test re-initialization */
    ret = kobold_memory_init(128);
    if (ret != 0) {
        fprintf(stderr, "Failed to re-initialize memory system\n");
        return -1;
    }
    
    kobold_memory_shutdown();
    
    return 0;
}

/**
 * @brief Test memory statistics
 */
int test_memory_stats(void) {
    int ret = kobold_memory_init(256);
    if (ret != 0) {
        return -1;
    }
    
    struct memory_stats stats;
    kobold_memory_stats(&stats);
    
    /* Verify initial state */
    if (stats.total_bytes != 256 * 1024 * 1024) {
        fprintf(stderr, "Incorrect total_bytes: %zu\n", stats.total_bytes);
        kobold_memory_shutdown();
        return -1;
    }
    
    if (stats.used_bytes != 0) {
        fprintf(stderr, "Incorrect initial used_bytes: %zu\n", stats.used_bytes);
        kobold_memory_shutdown();
        return -1;
    }
    
    if (stats.num_allocations != 0) {
        fprintf(stderr, "Incorrect initial num_allocations: %zu\n", stats.num_allocations);
        kobold_memory_shutdown();
        return -1;
    }
    
    kobold_memory_shutdown();
    return 0;
}
