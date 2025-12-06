/**
 * @file benchmark_main.c
 * @brief Main benchmark runner for KoboldAI kernel
 */

#include <stdio.h>
#include <stdlib.h>

/* Benchmark function declarations */
extern void benchmark_story_chunk_alloc(void);
extern void benchmark_context_assembly(void);
extern void run_sampler_benchmarks(void);
extern void run_worldinfo_benchmarks(void);

int main(void) {
    printf("===========================================\n");
    printf("KoboldAI Kernel Benchmark Suite\n");
    printf("===========================================\n\n");
    
    printf("Running benchmarks...\n\n");
    
    benchmark_story_chunk_alloc();
    benchmark_context_assembly();
    run_sampler_benchmarks();
    run_worldinfo_benchmarks();
    
    printf("\n===========================================\n");
    printf("Benchmarks complete\n");
    printf("===========================================\n");
    
    return EXIT_SUCCESS;
}
