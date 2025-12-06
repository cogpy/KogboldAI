/**
 * @file benchmark_worldinfo.c
 * @brief Benchmarks for world info functions
 */

#include "kobold_kernel.h"
#include <stdio.h>
#include <time.h>
#include <string.h>

#define ITERATIONS 10000

/**
 * @brief Get current time in microseconds
 */
static double get_time_us(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec * 1000000.0 + ts.tv_nsec / 1000.0;
}

/**
 * @brief Benchmark world info entry creation
 */
void benchmark_worldinfo_entry_create(void) {
    double start = get_time_us();
    
    for (int i = 0; i < ITERATIONS; i++) {
        void *entry = worldinfo_entry_create(
            "dragon, castle, knight",
            "A mighty dragon guards the ancient castle where brave knights once lived.",
            true,
            false
        );
        worldinfo_entry_free(entry);
    }
    
    double end = get_time_us();
    double avg_time = (end - start) / ITERATIONS;
    
    printf("World Info Entry Creation:\n");
    printf("  Average time: %.2f µs\n", avg_time);
    printf("  Target: ≤100 µs\n");
    printf("  Status: %s\n\n", avg_time <= 100.0 ? "✓ PASS" : "✗ NEEDS OPTIMIZATION");
}

/**
 * @brief Benchmark keyword matching
 */
void benchmark_worldinfo_keyword_matching(void) {
    /* Create test entry */
    void *entry = worldinfo_entry_create(
        "dragon, castle, knight, sword, wizard, magic",
        "Fantasy world content.",
        true,
        false
    );
    
    if (!entry) {
        printf("Failed to create entry for benchmark\n");
        return;
    }
    
    const char *test_contexts[] = {
        "The brave knight drew his sword.",
        "A wizard appeared with magic powers.",
        "The dragon attacked the castle.",
        "Nothing relevant here at all.",
        "Another unrelated piece of text.",
    };
    int num_contexts = sizeof(test_contexts) / sizeof(test_contexts[0]);
    
    double start = get_time_us();
    
    for (int i = 0; i < ITERATIONS; i++) {
        for (int j = 0; j < num_contexts; j++) {
            worldinfo_match_keywords(entry, test_contexts[j]);
        }
    }
    
    double end = get_time_us();
    double avg_time = (end - start) / (ITERATIONS * num_contexts);
    
    printf("World Info Keyword Matching:\n");
    printf("  Average time: %.2f µs\n", avg_time);
    printf("  Target: ≤50 µs per entry\n");
    printf("  Status: %s\n\n", avg_time <= 50.0 ? "✓ PASS" : "✗ NEEDS OPTIMIZATION");
    
    worldinfo_entry_free(entry);
}

/**
 * @brief Benchmark world info scanning with story
 */
void benchmark_worldinfo_scan_tensor(void) {
    /* Initialize memory */
    if (kobold_memory_init(64) != 0) {
        printf("Failed to initialize memory\n");
        return;
    }
    
    /* Create story with world info entries */
    void *story = story_create();
    if (!story) {
        printf("Failed to create story\n");
        kobold_memory_shutdown();
        return;
    }
    
    /* Add multiple world info entries */
    for (int i = 0; i < 10; i++) {
        char keys[256];
        char content[512];
        snprintf(keys, sizeof(keys), "key%d, keyword%d, test%d", i, i, i);
        snprintf(content, sizeof(content), "World info content for entry %d with some details.", i);
        
        void *entry = worldinfo_entry_create(keys, content, true, false);
        if (entry) {
            story_add_worldinfo(story, entry);
        }
    }
    
    /* Add one constant entry */
    void *constant = worldinfo_entry_create(
        NULL,
        "This is always included in the context.",
        false, true
    );
    if (constant) {
        story_add_worldinfo(story, constant);
    }
    
    const char *context = "This is a test context with key5 and keyword7 mentioned.";
    
    double start = get_time_us();
    
    for (int i = 0; i < 1000; i++) {
        struct ggml_tensor *result = worldinfo_scan_tensor(story, 512, context);
        /* Note: result is NULL because tokenizer is stubbed */
        (void)result;
    }
    
    double end = get_time_us();
    double avg_time = (end - start) / 1000.0;
    
    printf("World Info Scanning (worldinfo_scan_tensor):\n");
    printf("  Average time: %.2f µs\n", avg_time);
    printf("  Target: ≤2000 µs (2 ms)\n");
    printf("  Status: %s\n", avg_time <= 2000.0 ? "✓ PASS" : "✗ NEEDS OPTIMIZATION");
    printf("  Note: Tokenization is stubbed\n\n");
    
    story_free(story);
    kobold_memory_shutdown();
}

/**
 * @brief Run all world info benchmarks
 */
void run_worldinfo_benchmarks(void) {
    printf("\n--- World Info Benchmarks ---\n\n");
    
    benchmark_worldinfo_entry_create();
    benchmark_worldinfo_keyword_matching();
    benchmark_worldinfo_scan_tensor();
}
