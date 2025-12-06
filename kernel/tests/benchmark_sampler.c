/**
 * @file benchmark_sampler.c
 * @brief Benchmarks for token sampling functions
 */

#include "kobold_kernel.h"
#include "ggml.h"
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define NUM_ITERATIONS 1000
#define VOCAB_SIZE 50000

extern struct ggml_context *ggml_kernel_get_context(void);

static double get_time_us(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec * 1000000.0 + ts.tv_nsec / 1000.0;
}

/**
 * @brief Create test logits tensor
 */
static struct ggml_tensor *create_test_logits(void) {
    struct ggml_context *ctx = ggml_kernel_get_context();
    struct ggml_tensor *logits = ggml_new_tensor_1d(ctx, GGML_TYPE_F32, VOCAB_SIZE);
    
    float *data = (float *)logits->data;
    for (size_t i = 0; i < VOCAB_SIZE; i++) {
        data[i] = (float)(rand() % 100) / 10.0f - 5.0f;
    }
    
    return logits;
}

/**
 * @brief Benchmark nucleus sampling
 */
void benchmark_nucleus_sampling(void) {
    kobold_memory_init(256);
    srand(42);
    
    struct ggml_tensor *logits = create_test_logits();
    
    double start = get_time_us();
    
    for (int i = 0; i < NUM_ITERATIONS; i++) {
        int32_t token = sample_nucleus_tensor(logits, 0.9f, 0.7f);
        (void)token; /* Suppress warning */
    }
    
    double end = get_time_us();
    double avg_us = (end - start) / NUM_ITERATIONS;
    
    printf("Nucleus Sampling (top-p=0.9):\n");
    printf("  Average time: %.2f µs\n", avg_us);
    printf("  Target: ≤500 µs\n");
    printf("  Status: %s\n\n", avg_us <= 500.0 ? "✓ PASS" : "✗ NEEDS OPTIMIZATION");
    
    kobold_memory_shutdown();
}

/**
 * @brief Benchmark top-k sampling
 */
void benchmark_topk_sampling(void) {
    kobold_memory_init(256);
    srand(43);
    
    struct ggml_tensor *logits = create_test_logits();
    
    double start = get_time_us();
    
    for (int i = 0; i < NUM_ITERATIONS; i++) {
        int32_t token = sample_topk_tensor(logits, 50, 0.7f);
        (void)token;
    }
    
    double end = get_time_us();
    double avg_us = (end - start) / NUM_ITERATIONS;
    
    printf("Top-K Sampling (k=50):\n");
    printf("  Average time: %.2f µs\n", avg_us);
    printf("  Target: ≤500 µs\n");
    printf("  Status: %s\n\n", avg_us <= 500.0 ? "✓ PASS" : "✗ NEEDS OPTIMIZATION");
    
    kobold_memory_shutdown();
}

/**
 * @brief Benchmark typical sampling
 */
void benchmark_typical_sampling(void) {
    kobold_memory_init(256);
    srand(44);
    
    struct ggml_tensor *logits = create_test_logits();
    
    double start = get_time_us();
    
    for (int i = 0; i < NUM_ITERATIONS; i++) {
        int32_t token = sample_typical_tensor(logits, 0.95f, 0.7f);
        (void)token;
    }
    
    double end = get_time_us();
    double avg_us = (end - start) / NUM_ITERATIONS;
    
    printf("Typical Sampling (p=0.95):\n");
    printf("  Average time: %.2f µs\n", avg_us);
    printf("  Target: ≤500 µs\n");
    printf("  Status: %s\n\n", avg_us <= 500.0 ? "✓ PASS" : "✗ NEEDS OPTIMIZATION");
    
    kobold_memory_shutdown();
}

/**
 * @brief Benchmark repetition penalty
 */
void benchmark_repetition_penalty(void) {
    kobold_memory_init(256);
    
    struct ggml_tensor *logits = create_test_logits();
    int32_t recent[64];
    for (int i = 0; i < 64; i++) {
        recent[i] = rand() % VOCAB_SIZE;
    }
    
    double start = get_time_us();
    
    for (int i = 0; i < NUM_ITERATIONS; i++) {
        apply_repetition_penalty(logits, recent, 64, 1.2f, 0.5f);
    }
    
    double end = get_time_us();
    double avg_us = (end - start) / NUM_ITERATIONS;
    
    printf("Repetition Penalty:\n");
    printf("  Average time: %.2f µs\n", avg_us);
    printf("  Target: ≤200 µs\n");
    printf("  Status: %s\n\n", avg_us <= 200.0 ? "✓ PASS" : "✗ NEEDS OPTIMIZATION");
    
    kobold_memory_shutdown();
}

/**
 * @brief Run all sampler benchmarks
 */
void run_sampler_benchmarks(void) {
    printf("\n--- Token Sampling Benchmarks ---\n\n");
    benchmark_nucleus_sampling();
    benchmark_topk_sampling();
    benchmark_typical_sampling();
    benchmark_repetition_penalty();
}
