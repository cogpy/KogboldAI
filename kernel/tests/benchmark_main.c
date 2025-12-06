/**
 * @file benchmark_main.c
 * @brief Main benchmark runner for KoboldAI kernel
 */

#include <stdio.h>
#include <stdlib.h>

/* Benchmark function declarations */
extern void benchmark_story_chunk_alloc(void);
extern void benchmark_context_assembly(void);

int main(void) {
    printf("===========================================\n");
    printf("KoboldAI Kernel Benchmark Suite\n");
    printf("===========================================\n\n");
    
    printf("Running benchmarks...\n\n");
    
    benchmark_story_chunk_alloc();
    benchmark_context_assembly();
    
    printf("\n===========================================\n");
    printf("Benchmarks complete\n");
    printf("===========================================\n");
    
    return EXIT_SUCCESS;
}
