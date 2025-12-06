/**
 * @file memory.c
 * @brief Memory management for KoboldAI kernel
 * 
 * Implements efficient memory pooling and allocation tracking for
 * GGML tensors and kernel data structures.
 */

#include "kobold_kernel.h"
#include <stdlib.h>
#include <string.h>
#include <pthread.h>

/* Memory pool state */
static struct {
    bool initialized;
    size_t pool_size;
    size_t used_bytes;
    size_t peak_bytes;
    size_t num_allocations;
    pthread_mutex_t lock;
} g_memory = {
    .initialized = false,
    .pool_size = 0,
    .used_bytes = 0,
    .peak_bytes = 0,
    .num_allocations = 0
};

/**
 * @brief Initialize kernel memory system
 * @param pool_size_mb Memory pool size in megabytes
 * @return 0 on success, -1 on failure
 * 
 * Initializes the memory management system with the specified pool size.
 * Must be called before any other kernel functions.
 * 
 * @performance ≤10ms
 * @thread-safety Not thread-safe (call once at startup)
 */
int kobold_memory_init(size_t pool_size_mb) {
    if (g_memory.initialized) {
        return -1; /* Already initialized */
    }
    
    /* Initialize mutex */
    if (pthread_mutex_init(&g_memory.lock, NULL) != 0) {
        return -1;
    }
    
    g_memory.pool_size = pool_size_mb * 1024 * 1024;
    g_memory.used_bytes = 0;
    g_memory.peak_bytes = 0;
    g_memory.num_allocations = 0;
    g_memory.initialized = true;
    
    return 0;
}

/**
 * @brief Shutdown memory system and free all resources
 * 
 * Cleans up the memory management system. After this call, no kernel
 * functions should be used until kobold_memory_init() is called again.
 * 
 * @performance ≤50ms
 * @thread-safety Not thread-safe (call once at shutdown)
 */
void kobold_memory_shutdown(void) {
    if (!g_memory.initialized) {
        return;
    }
    
    pthread_mutex_destroy(&g_memory.lock);
    
    g_memory.initialized = false;
    g_memory.pool_size = 0;
    g_memory.used_bytes = 0;
    g_memory.peak_bytes = 0;
    g_memory.num_allocations = 0;
}

/**
 * @brief Get current memory usage statistics
 * @param out_stats Output parameter for statistics
 * 
 * Returns current memory usage information including total allocated,
 * currently used, peak usage, and number of active allocations.
 * 
 * @performance ≤10µs
 * @thread-safety Thread-safe
 */
void kobold_memory_stats(struct memory_stats *out_stats) {
    if (!out_stats || !g_memory.initialized) {
        return;
    }
    
    pthread_mutex_lock(&g_memory.lock);
    
    out_stats->total_bytes = g_memory.pool_size;
    out_stats->used_bytes = g_memory.used_bytes;
    out_stats->peak_bytes = g_memory.peak_bytes;
    out_stats->num_allocations = g_memory.num_allocations;
    
    pthread_mutex_unlock(&g_memory.lock);
}

/* Internal allocation tracking */
void *kobold_alloc(size_t size) {
    if (!g_memory.initialized || size == 0) {
        return NULL;
    }
    
    pthread_mutex_lock(&g_memory.lock);
    
    /* Check if allocation would exceed pool */
    if (g_memory.used_bytes + size > g_memory.pool_size) {
        pthread_mutex_unlock(&g_memory.lock);
        return NULL;
    }
    
    void *ptr = malloc(size);
    if (ptr) {
        g_memory.used_bytes += size;
        if (g_memory.used_bytes > g_memory.peak_bytes) {
            g_memory.peak_bytes = g_memory.used_bytes;
        }
        g_memory.num_allocations++;
    }
    
    pthread_mutex_unlock(&g_memory.lock);
    return ptr;
}

void kobold_free(void *ptr, size_t size) {
    if (!ptr || !g_memory.initialized) {
        return;
    }
    
    pthread_mutex_lock(&g_memory.lock);
    
    free(ptr);
    g_memory.used_bytes -= size;
    g_memory.num_allocations--;
    
    pthread_mutex_unlock(&g_memory.lock);
}
