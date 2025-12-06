/**
 * @file benchmark_story.c
 * @brief Benchmarks for story management functions
 */

#include "kobold_kernel.h"
#include <stdio.h>
#include <time.h>

#define NUM_ITERATIONS 1000

static double get_time_us(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec * 1000000.0 + ts.tv_nsec / 1000.0;
}

/**
 * @brief Benchmark story chunk allocation
 */
void benchmark_story_chunk_alloc(void) {
    kobold_memory_init(256);
    
    const char *text = "Once upon a time in a fantasy world full of magic and adventure...";
    
    double start = get_time_us();
    
    for (int i = 0; i < NUM_ITERATIONS; i++) {
        void *chunk = story_chunk_alloc(text, i, 15);
        story_chunk_free(chunk);
    }
    
    double end = get_time_us();
    double avg_us = (end - start) / NUM_ITERATIONS;
    
    printf("Story Chunk Allocation:\n");
    printf("  Average time: %.2f µs\n", avg_us);
    printf("  Target: ≤100 µs\n");
    printf("  Status: %s\n\n", avg_us <= 100.0 ? "✓ PASS" : "✗ NEEDS OPTIMIZATION");
    
    kobold_memory_shutdown();
}

/**
 * @brief Benchmark context assembly
 */
void benchmark_context_assembly(void) {
    kobold_memory_init(256);
    
    void *story = story_create();
    
    /* Add some chunks */
    for (int i = 0; i < 10; i++) {
        char text[256];
        snprintf(text, sizeof(text), "Story chunk number %d with some content.", i);
        void *chunk = story_chunk_alloc(text, i, 10);
        story_chunk_append(story, chunk);
    }
    
    story_set_memory(story, "This is the memory context.");
    story_set_authors_note(story, "[Write in fantasy style]");
    
    struct gen_settings settings;
    gen_settings_init_default(&settings);
    
    double start = get_time_us();
    
    for (int i = 0; i < NUM_ITERATIONS; i++) {
        /* Context assembly is currently stubbed, so this measures overhead only */
        struct ggml_tensor *ctx = ctx_assemble_tensor(story, &settings, 2048);
        (void)ctx; /* Suppress unused warning */
    }
    
    double end = get_time_us();
    double avg_us = (end - start) / NUM_ITERATIONS;
    
    printf("Context Assembly:\n");
    printf("  Average time: %.2f µs\n", avg_us);
    printf("  Target: ≤1000 µs (1 ms)\n");
    printf("  Status: %s\n", avg_us <= 1000.0 ? "✓ PASS" : "✗ NEEDS OPTIMIZATION");
    printf("  Note: Currently stubbed - measures overhead only\n\n");
    
    story_free(story);
    kobold_memory_shutdown();
}
