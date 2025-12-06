/**
 * @file python_ffi.c
 * @brief Python FFI bindings for KoboldAI kernel
 * 
 * This file provides ctypes-compatible FFI bindings for Python integration.
 * All kernel functions are already designed to be ctypes-compatible, so this
 * file mainly serves as a designated entry point for the Python binding library.
 */

#include "kobold_kernel.h"

/* 
 * Note: All functions in kobold_kernel.h are already ctypes-compatible.
 * This file is a placeholder for any Python-specific wrapper functions
 * that may be needed in the future.
 * 
 * The Python bindings will use ctypes to load libkoboldkern.so directly
 * and call the kernel functions through their C ABI.
 */

/**
 * @brief Python FFI initialization (optional)
 * 
 * This function can be called from Python to verify the library is loaded
 * correctly and to perform any initialization needed for Python integration.
 * 
 * @return 0 on success, -1 on failure
 */
int kobold_python_ffi_init(void) {
    /* Currently no special initialization needed */
    return 0;
}

/**
 * @brief Get FFI version
 * @return Version string
 */
const char *kobold_python_ffi_version(void) {
    return kobold_kernel_version();
}
