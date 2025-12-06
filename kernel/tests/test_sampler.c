/**
 * @file test_sampler.c
 * @brief Tests for token sampling functions
 */

#include "kobold_kernel.h"
#include "ggml.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <time.h>

/* Forward declarations */
extern struct ggml_context *ggml_kernel_get_context(void);

/**
 * @brief Create a test logits tensor with known values
 */
static struct ggml_tensor *create_test_logits(size_t vocab_size) {
    struct ggml_context *ctx = ggml_kernel_get_context();
    if (!ctx) {
        return NULL;
    }
    
    struct ggml_tensor *logits = ggml_new_tensor_1d(ctx, GGML_TYPE_F32, vocab_size);
    if (!logits) {
        return NULL;
    }
    
    /* Fill with random-ish logits */
    float *data = (float *)logits->data;
    for (size_t i = 0; i < vocab_size; i++) {
        data[i] = (float)(rand() % 100) / 10.0f - 5.0f; /* Range: -5.0 to 5.0 */
    }
    
    return logits;
}

/**
 * @brief Test nucleus sampling
 */
void test_sample_nucleus(void) {
    printf("  Testing nucleus sampling...\n");
    
    kobold_memory_init(256);
    srand(42); /* Deterministic random for testing */
    
    struct ggml_tensor *logits = create_test_logits(1000);
    assert(logits != NULL);
    
    /* Sample with top_p = 0.9 */
    int32_t token1 = sample_nucleus_tensor(logits, 0.9f, 0.7f);
    assert(token1 >= 0 && token1 < 1000);
    
    /* Sample again - should potentially get different result */
    int32_t token2 = sample_nucleus_tensor(logits, 0.9f, 0.7f);
    assert(token2 >= 0 && token2 < 1000);
    
    /* With top_p = 1.0, should still work */
    int32_t token3 = sample_nucleus_tensor(logits, 1.0f, 0.7f);
    assert(token3 >= 0 && token3 < 1000);
    
    /* Invalid parameters should return -1 */
    int32_t invalid = sample_nucleus_tensor(NULL, 0.9f, 0.7f);
    assert(invalid == -1);
    
    invalid = sample_nucleus_tensor(logits, 0.0f, 0.7f);
    assert(invalid == -1);
    
    kobold_memory_shutdown();
    
    printf("    ✓ test_sample_nucleus\n");
}

/**
 * @brief Test top-k sampling
 */
void test_sample_topk(void) {
    printf("  Testing top-k sampling...\n");
    
    kobold_memory_init(256);
    srand(43);
    
    struct ggml_tensor *logits = create_test_logits(1000);
    assert(logits != NULL);
    
    /* Sample with top_k = 50 */
    int32_t token1 = sample_topk_tensor(logits, 50, 0.7f);
    assert(token1 >= 0 && token1 < 1000);
    
    /* Sample with top_k = 1 (greedy-ish) */
    int32_t token2 = sample_topk_tensor(logits, 1, 0.01f);
    assert(token2 >= 0 && token2 < 1000);
    
    /* With large top_k */
    int32_t token3 = sample_topk_tensor(logits, 500, 1.0f);
    assert(token3 >= 0 && token3 < 1000);
    
    /* Invalid parameters */
    int32_t invalid = sample_topk_tensor(NULL, 50, 0.7f);
    assert(invalid == -1);
    
    invalid = sample_topk_tensor(logits, 0, 0.7f);
    assert(invalid == -1);
    
    kobold_memory_shutdown();
    
    printf("    ✓ test_sample_topk\n");
}

/**
 * @brief Test typical sampling
 */
void test_sample_typical(void) {
    printf("  Testing typical sampling...\n");
    
    kobold_memory_init(256);
    srand(44);
    
    struct ggml_tensor *logits = create_test_logits(1000);
    assert(logits != NULL);
    
    /* Sample with typical_p = 0.95 */
    int32_t token1 = sample_typical_tensor(logits, 0.95f, 0.7f);
    assert(token1 >= 0 && token1 < 1000);
    
    /* Sample with different temperature */
    int32_t token2 = sample_typical_tensor(logits, 0.95f, 1.5f);
    assert(token2 >= 0 && token2 < 1000);
    
    /* Invalid parameters */
    int32_t invalid = sample_typical_tensor(NULL, 0.95f, 0.7f);
    assert(invalid == -1);
    
    invalid = sample_typical_tensor(logits, 0.0f, 0.7f);
    assert(invalid == -1);
    
    kobold_memory_shutdown();
    
    printf("    ✓ test_sample_typical\n");
}

/**
 * @brief Test repetition penalty
 */
void test_repetition_penalty(void) {
    printf("  Testing repetition penalty...\n");
    
    kobold_memory_init(256);
    
    struct ggml_tensor *logits = create_test_logits(1000);
    assert(logits != NULL);
    
    /* Save original values for some tokens */
    float *data = (float *)logits->data;
    float orig_logit_10 = data[10];
    float orig_logit_50 = data[50];
    
    /* Apply penalty to some recent tokens */
    int32_t recent[] = {10, 20, 30, 40, 50};
    apply_repetition_penalty(logits, recent, 5, 1.2f, 0.5f);
    
    /* Check that penalized tokens changed */
    assert(data[10] != orig_logit_10); /* Token 10 should be penalized */
    assert(data[50] != orig_logit_50); /* Token 50 should be penalized */
    
    /* Test with invalid parameters (should not crash) */
    apply_repetition_penalty(NULL, recent, 5, 1.2f, 0.5f);
    apply_repetition_penalty(logits, NULL, 5, 1.2f, 0.5f);
    apply_repetition_penalty(logits, recent, 0, 1.2f, 0.5f);
    
    kobold_memory_shutdown();
    
    printf("    ✓ test_repetition_penalty\n");
}

/**
 * @brief Run all sampler tests
 */
void run_sampler_tests(void) {
    printf("\nRunning sampler tests...\n");
    
    test_sample_nucleus();
    test_sample_topk();
    test_sample_typical();
    test_repetition_penalty();
}
