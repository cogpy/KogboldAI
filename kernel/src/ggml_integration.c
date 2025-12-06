/**
 * @file ggml_integration.c
 * @brief GGML integration layer for KoboldAI kernel
 * 
 * Provides wrapper functions and utilities for working with GGML tensors
 * in the KoboldAI kernel. This includes context management, tensor utilities,
 * and tokenization helpers.
 */

#include "kobold_kernel.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <pthread.h>

/* Include GGML headers */
#include "ggml.h"

/* Forward declarations */
extern void *kobold_alloc(size_t size);
extern void kobold_free(void *ptr, size_t size);

/**
 * @brief Global GGML context for kernel operations
 * 
 * This context is initialized once and reused for all tensor operations.
 * Protected by mutex for thread safety.
 */
static struct ggml_context *g_kernel_ctx = NULL;
static pthread_mutex_t g_ctx_mutex = PTHREAD_MUTEX_INITIALIZER;
static size_t g_ctx_size = 512 * 1024 * 1024; /* 512 MB default */

/**
 * @brief Initialize GGML context for kernel operations
 * @param mem_size Memory size in bytes for GGML context
 * @return 0 on success, -1 on failure
 * 
 * Creates a global GGML context that will be used for all tensor operations.
 * This should be called once at kernel initialization.
 * 
 * @thread-safety Not thread-safe (call once at startup)
 */
int ggml_kernel_init(size_t mem_size) {
    pthread_mutex_lock(&g_ctx_mutex);
    
    if (g_kernel_ctx != NULL) {
        pthread_mutex_unlock(&g_ctx_mutex);
        return 0; /* Already initialized */
    }
    
    if (mem_size > 0) {
        g_ctx_size = mem_size;
    }
    
    struct ggml_init_params params = {
        .mem_size = g_ctx_size,
        .mem_buffer = NULL,
        .no_alloc = false
    };
    
    g_kernel_ctx = ggml_init(params);
    
    pthread_mutex_unlock(&g_ctx_mutex);
    
    return (g_kernel_ctx != NULL) ? 0 : -1;
}

/**
 * @brief Shutdown GGML context
 * 
 * Frees the global GGML context. Should be called at kernel shutdown.
 * 
 * @thread-safety Not thread-safe (call once at shutdown)
 */
void ggml_kernel_shutdown(void) {
    pthread_mutex_lock(&g_ctx_mutex);
    
    if (g_kernel_ctx != NULL) {
        ggml_free(g_kernel_ctx);
        g_kernel_ctx = NULL;
    }
    
    pthread_mutex_unlock(&g_ctx_mutex);
}

/**
 * @brief Get the global kernel GGML context
 * @return GGML context pointer, or NULL if not initialized
 * 
 * Returns the global GGML context for tensor operations.
 * Initializes it if not already initialized.
 * 
 * @thread-safety Thread-safe
 */
struct ggml_context *ggml_kernel_get_context(void) {
    pthread_mutex_lock(&g_ctx_mutex);
    
    if (g_kernel_ctx == NULL) {
        pthread_mutex_unlock(&g_ctx_mutex);
        ggml_kernel_init(0); /* Use default size */
        pthread_mutex_lock(&g_ctx_mutex);
    }
    
    struct ggml_context *ctx = g_kernel_ctx;
    pthread_mutex_unlock(&g_ctx_mutex);
    
    return ctx;
}

/**
 * @brief Simple tokenizer stub
 * @param text UTF-8 text to tokenize
 * @param tokens Output buffer for token IDs
 * @param max_tokens Maximum tokens to write
 * @return Number of tokens written
 * 
 * This is a stub tokenizer that splits on whitespace.
 * In production, this should use llama.cpp tokenizer.
 * 
 * @note This is a placeholder implementation
 */
size_t ggml_kernel_tokenize(const char *text, int32_t *tokens, size_t max_tokens) {
    if (!text || !tokens || max_tokens == 0) {
        return 0;
    }
    
    /* Simple whitespace tokenization stub */
    size_t token_count = 0;
    const char *p = text;
    int32_t token_id = 1000; /* Start token IDs at 1000 */
    
    while (*p && token_count < max_tokens) {
        /* Skip whitespace */
        while (*p && (*p == ' ' || *p == '\t' || *p == '\n' || *p == '\r')) {
            p++;
        }
        
        if (!*p) break;
        
        /* Found a word */
        while (*p && !(*p == ' ' || *p == '\t' || *p == '\n' || *p == '\r')) {
            p++;
        }
        
        /* Assign token ID (in reality, use vocab) */
        tokens[token_count++] = token_id++;
    }
    
    return token_count;
}

/**
 * @brief Detokenize tokens to text
 * @param tokens Token IDs
 * @param token_count Number of tokens
 * @param text Output buffer for text
 * @param max_len Maximum text length
 * @return Number of bytes written
 * 
 * This is a stub detokenizer.
 * In production, this should use llama.cpp detokenizer.
 * 
 * @note This is a placeholder implementation
 */
size_t ggml_kernel_detokenize(const int32_t *tokens, size_t token_count, 
                               char *text, size_t max_len) {
    if (!tokens || !text || max_len == 0) {
        return 0;
    }
    
    /* Simple stub that outputs token IDs */
    size_t written = 0;
    for (size_t i = 0; i < token_count && written < max_len - 16; i++) {
        int n = snprintf(text + written, max_len - written, "[%d] ", tokens[i]);
        if (n > 0) {
            written += n;
        }
    }
    
    return written;
}

/**
 * @brief Create a 1D tensor from token array
 * @param tokens Token ID array
 * @param token_count Number of tokens
 * @return GGML tensor containing tokens, NULL on failure
 * 
 * Creates a new 1D i32 tensor and copies tokens into it.
 * 
 * @performance ≤100µs for typical token counts
 * @thread-safety Thread-safe
 */
struct ggml_tensor *ggml_kernel_create_token_tensor(const int32_t *tokens, size_t token_count) {
    if (!tokens || token_count == 0) {
        return NULL;
    }
    
    struct ggml_context *ctx = ggml_kernel_get_context();
    if (!ctx) {
        return NULL;
    }
    
    /* Create 1D tensor for tokens */
    struct ggml_tensor *tensor = ggml_new_tensor_1d(ctx, GGML_TYPE_I32, token_count);
    if (!tensor) {
        return NULL;
    }
    
    /* Copy tokens into tensor */
    memcpy(tensor->data, tokens, token_count * sizeof(int32_t));
    
    return tensor;
}

/**
 * @brief Concatenate two tensors along dimension 0
 * @param a First tensor
 * @param b Second tensor
 * @return Concatenated tensor, NULL on failure
 * 
 * Creates a new tensor that is the concatenation of a and b.
 * 
 * @performance ≤200µs for typical tensors
 * @thread-safety Thread-safe
 */
struct ggml_tensor *ggml_kernel_concat_tensors(struct ggml_tensor *a, struct ggml_tensor *b) {
    if (!a || !b) {
        return NULL;
    }
    
    struct ggml_context *ctx = ggml_kernel_get_context();
    if (!ctx) {
        return NULL;
    }
    
    /* Use GGML concat operation (concatenates along first dimension) */
    return ggml_concat(ctx, a, b);
}

/**
 * @brief Get tensor element count
 * @param tensor GGML tensor
 * @return Number of elements in tensor
 */
size_t ggml_kernel_tensor_nelements(struct ggml_tensor *tensor) {
    if (!tensor) {
        return 0;
    }
    
    size_t n = 1;
    for (int i = 0; i < 4; i++) {
        n *= tensor->ne[i];
    }
    
    return n;
}

/**
 * @brief Extract tokens from tensor
 * @param tensor GGML tensor containing tokens
 * @param tokens Output buffer for tokens
 * @param max_tokens Maximum tokens to extract
 * @return Number of tokens extracted
 */
size_t ggml_kernel_extract_tokens(struct ggml_tensor *tensor, int32_t *tokens, size_t max_tokens) {
    if (!tensor || !tokens || max_tokens == 0) {
        return 0;
    }
    
    size_t n = ggml_kernel_tensor_nelements(tensor);
    if (n > max_tokens) {
        n = max_tokens;
    }
    
    if (tensor->type == GGML_TYPE_I32) {
        memcpy(tokens, tensor->data, n * sizeof(int32_t));
    } else {
        /* Type conversion if needed */
        return 0; /* Not implemented */
    }
    
    return n;
}
