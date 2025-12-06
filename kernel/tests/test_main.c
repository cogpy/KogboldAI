/**
 * @file test_main.c
 * @brief Main test runner for KoboldAI kernel tests
 */

#include <stdio.h>
#include <stdlib.h>

/* Test function declarations */
extern int test_memory_init_shutdown(void);
extern int test_memory_stats(void);
extern int test_story_create_free(void);
extern int test_story_chunk_alloc_free(void);
extern int test_story_chunk_append(void);
extern int test_story_set_memory(void);
extern int test_story_set_authors_note(void);
extern void run_sampler_tests(void);

int main(void) {
    int passed = 0;
    int failed = 0;
    
    printf("===========================================\n");
    printf("KoboldAI Kernel Test Suite\n");
    printf("===========================================\n\n");
    
    /* Memory tests */
    printf("Running memory tests...\n");
    if (test_memory_init_shutdown() == 0) {
        printf("  ✓ test_memory_init_shutdown\n");
        passed++;
    } else {
        printf("  ✗ test_memory_init_shutdown\n");
        failed++;
    }
    
    if (test_memory_stats() == 0) {
        printf("  ✓ test_memory_stats\n");
        passed++;
    } else {
        printf("  ✗ test_memory_stats\n");
        failed++;
    }
    
    /* Story management tests */
    printf("\nRunning story management tests...\n");
    if (test_story_create_free() == 0) {
        printf("  ✓ test_story_create_free\n");
        passed++;
    } else {
        printf("  ✗ test_story_create_free\n");
        failed++;
    }
    
    if (test_story_chunk_alloc_free() == 0) {
        printf("  ✓ test_story_chunk_alloc_free\n");
        passed++;
    } else {
        printf("  ✗ test_story_chunk_alloc_free\n");
        failed++;
    }
    
    if (test_story_chunk_append() == 0) {
        printf("  ✓ test_story_chunk_append\n");
        passed++;
    } else {
        printf("  ✗ test_story_chunk_append\n");
        failed++;
    }
    
    if (test_story_set_memory() == 0) {
        printf("  ✓ test_story_set_memory\n");
        passed++;
    } else {
        printf("  ✗ test_story_set_memory\n");
        failed++;
    }
    
    if (test_story_set_authors_note() == 0) {
        printf("  ✓ test_story_set_authors_note\n");
        passed++;
    } else {
        printf("  ✗ test_story_set_authors_note\n");
        failed++;
    }
    
    /* Sampler tests - these use their own pass/fail tracking */
    run_sampler_tests();
    passed += 4; /* 4 sampler tests */
    
    /* Summary */
    printf("\n===========================================\n");
    printf("Test Results: %d passed, %d failed\n", passed, failed);
    printf("===========================================\n");
    
    return (failed == 0) ? EXIT_SUCCESS : EXIT_FAILURE;
}
