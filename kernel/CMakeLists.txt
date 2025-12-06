cmake_minimum_required(VERSION 3.15)
project(kobold-kernel C CXX)

set(CMAKE_C_STANDARD 99)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# Install directories
include(GNUInstallDirs)
if(NOT CMAKE_INSTALL_LIBDIR)
    set(CMAKE_INSTALL_LIBDIR lib)
endif()
if(NOT CMAKE_INSTALL_INCLUDEDIR)
    set(CMAKE_INSTALL_INCLUDEDIR include)
endif()
if(NOT CMAKE_INSTALL_BINDIR)
    set(CMAKE_INSTALL_BINDIR bin)
endif()

# Options
option(KOBOLD_KERNEL_BUILD_TESTS "Build test suite" ON)
option(KOBOLD_KERNEL_BUILD_BENCHMARKS "Build benchmarks" ON)
option(KOBOLD_KERNEL_BUILD_PYTHON_FFI "Build Python FFI bindings" ON)

# Build type
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release)
endif()

# Compiler flags
if(CMAKE_C_COMPILER_ID MATCHES "GNU|Clang")
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Wall -Wextra -Wpedantic -D_GNU_SOURCE")
    set(CMAKE_C_FLAGS_DEBUG "${CMAKE_C_FLAGS_DEBUG} -g -O0 -fsanitize=address -fsanitize=undefined")
    set(CMAKE_C_FLAGS_RELEASE "${CMAKE_C_FLAGS_RELEASE} -O3 -march=native -DNDEBUG")
endif()

if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra -Wpedantic -D_GNU_SOURCE")
    set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} -g -O0 -fsanitize=address -fsanitize=undefined")
    set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} -O3 -march=native -DNDEBUG")
endif()

# Include directories
include_directories(
    ${CMAKE_CURRENT_SOURCE_DIR}/include
    ${CMAKE_CURRENT_SOURCE_DIR}/../modeling/inference_models/koboldcpp
)

# Find GGML from KoboldCpp
set(GGML_SOURCE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../modeling/inference_models/koboldcpp)
if(NOT EXISTS ${GGML_SOURCE_DIR}/ggml.h)
    message(FATAL_ERROR "GGML not found. Expected at ${GGML_SOURCE_DIR}")
endif()

# Source files for kernel library
set(KOBOLD_KERNEL_SOURCES
    src/version.c
    src/memory.c
    src/story_management.c
    src/context_assembly.c
    src/ggml_integration.c
    # Sampling functions (Phase 2)
    # src/sampler.c
    # World info functions (Phase 3)
    # src/worldinfo.c
    # Agent orchestration (Phase 3)
    # src/agent_orchestrator.c
    # World building (Phase 3)
    # src/world_builder.c
)

# GGML source files from KoboldCpp
set(GGML_SOURCES
    ${GGML_SOURCE_DIR}/ggml.c
    ${GGML_SOURCE_DIR}/ggml-alloc.c
    ${GGML_SOURCE_DIR}/ggml-backend.c
    ${GGML_SOURCE_DIR}/ggml-quants.c
)

# Main kernel library (shared)
add_library(koboldkern SHARED ${KOBOLD_KERNEL_SOURCES} ${GGML_SOURCES})
target_include_directories(koboldkern PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
)

# Link with GGML dependencies
target_link_libraries(koboldkern PRIVATE m pthread)

# Static library variant
add_library(koboldkern_static STATIC ${KOBOLD_KERNEL_SOURCES} ${GGML_SOURCES})
target_include_directories(koboldkern_static PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
)
target_link_libraries(koboldkern_static PRIVATE m pthread)

# Python FFI wrapper
if(KOBOLD_KERNEL_BUILD_PYTHON_FFI)
    add_library(koboldkern_python SHARED
        src/python_ffi.c
    )
    target_link_libraries(koboldkern_python PRIVATE koboldkern)
endif()

# Tests
if(KOBOLD_KERNEL_BUILD_TESTS)
    enable_testing()
    add_subdirectory(tests)
endif()

# Install targets
install(TARGETS koboldkern koboldkern_static
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)

install(FILES include/kobold_kernel.h
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)

if(KOBOLD_KERNEL_BUILD_PYTHON_FFI)
    install(TARGETS koboldkern_python
        LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
        RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    )
endif()

# Generate pkg-config file (optional)
if(EXISTS ${CMAKE_CURRENT_SOURCE_DIR}/kobold-kernel.pc.in)
    configure_file(
        ${CMAKE_CURRENT_SOURCE_DIR}/kobold-kernel.pc.in
        ${CMAKE_CURRENT_BINARY_DIR}/kobold-kernel.pc
        @ONLY
    )
    install(FILES ${CMAKE_CURRENT_BINARY_DIR}/kobold-kernel.pc
        DESTINATION ${CMAKE_INSTALL_LIBDIR}/pkgconfig
    )
endif()

# Print configuration summary
message(STATUS "")
message(STATUS "KoboldAI Kernel Configuration:")
message(STATUS "  Build type: ${CMAKE_BUILD_TYPE}")
message(STATUS "  C compiler: ${CMAKE_C_COMPILER_ID} ${CMAKE_C_COMPILER_VERSION}")
message(STATUS "  CXX compiler: ${CMAKE_CXX_COMPILER_ID} ${CMAKE_CXX_COMPILER_VERSION}")
message(STATUS "  Build tests: ${KOBOLD_KERNEL_BUILD_TESTS}")
message(STATUS "  Build benchmarks: ${KOBOLD_KERNEL_BUILD_BENCHMARKS}")
message(STATUS "  Build Python FFI: ${KOBOLD_KERNEL_BUILD_PYTHON_FFI}")
message(STATUS "  GGML source: ${GGML_SOURCE_DIR}")
message(STATUS "")
