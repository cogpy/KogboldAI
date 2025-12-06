cmake_minimum_required(VERSION 3.15)

# Test executable
add_executable(test_kernel
    test_story_management.c
    test_memory.c
    test_sampler.c
    test_worldinfo.c
    test_main.c
)

target_link_libraries(test_kernel PRIVATE koboldkern_static m pthread)

target_include_directories(test_kernel PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../include
)

# Add tests
add_test(NAME kernel_tests COMMAND test_kernel)

# Benchmark executable (optional)
if(KOBOLD_KERNEL_BUILD_BENCHMARKS)
    add_executable(benchmark_kernel
        benchmark_story.c
        benchmark_sampler.c
        benchmark_worldinfo.c
        benchmark_main.c
    )
    
    target_link_libraries(benchmark_kernel PRIVATE koboldkern_static m pthread)
    
    target_include_directories(benchmark_kernel PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/../include
    )
endif()
