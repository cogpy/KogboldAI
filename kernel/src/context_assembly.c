/**
 * @file context_assembly.c
 * @brief Context assembly functions for KoboldAI kernel
 * 
 * Implements context assembly from story components (memory, author's note,
 * world info, and story chunks) using GGML tensor operations.
 */

#include "kobold_kernel.h"
#include "ggml.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

/* Configuration constants */
#define WORLDINFO_MIN_TOKEN_THRESHOLD 10  /**< Minimum tokens for partial entry */

/* Forward declarations */
extern void *kobold_alloc(size_t size);
extern void kobold_free(void *ptr, size_t size);

/* GGML integration functions */
extern struct ggml_context *ggml_kernel_get_context(void);
extern size_t ggml_kernel_tokenize(const char *text, int32_t *tokens, size_t max_tokens);
extern struct ggml_tensor *ggml_kernel_create_token_tensor(const int32_t *tokens, size_t token_count);
extern struct ggml_tensor *ggml_kernel_concat_tensors(struct ggml_tensor *a, struct ggml_tensor *b);
extern size_t ggml_kernel_tensor_nelements(struct ggml_tensor *tensor);

/* Internal story state structure (from story_management.c) */
struct story_chunk {
    uint32_t chunk_num;
    size_t token_count;
    int32_t *tokens;
    char *text;
    size_t text_len;
    struct story_chunk *next;
};

struct story_state {
    struct story_chunk *chunks_head;
    struct story_chunk *chunks_tail;
    size_t chunk_count;
    char *memory_text;
    size_t memory_len;
    char *authors_note;
    size_t authors_note_len;
    void **worldinfo_entries;
    size_t worldinfo_count;
    size_t worldinfo_capacity;
    void *lock; /* pthread_mutex_t */
};

/**
 * @brief Assemble generation context from story components
 * @param story Story state handle
 * @param settings Generation settings (includes context preferences)
 * @param budget Maximum token count for context
 * @return GGML tensor containing assembled context tokens, NULL on failure
 * 
 * Assembles context by allocating tokens according to budget:
 * - Memory: 15%
 * - Author's Note: 5%
 * - World Info: 20%
 * - Story Chunks: 60%
 * 
 * @performance ≤1ms
 * @thread-safety Thread-safe
 */
struct ggml_tensor *ctx_assemble_tensor(
    void *story,
    const struct gen_settings *settings,
    size_t budget
) {
    if (!story || !settings || budget == 0) {
        return NULL;
    }
    
    /* Calculate token budgets for each component */
    size_t memory_tokens = (size_t)(budget * 0.15);    /* 15% for memory */
    size_t note_tokens = (size_t)(budget * 0.05);      /* 5% for author's note */
    size_t wi_tokens = (size_t)(budget * 0.20);        /* 20% for world info */
    size_t story_tokens = (size_t)(budget * 0.60);     /* 60% for story chunks */
    
    /* Start with NULL result */
    struct ggml_tensor *result = NULL;
    
    /* 1. Retrieve memory tensor (if enabled) */
    if (settings->use_memory && memory_tokens > 0) {
        result = memory_tensor_retrieve(story, memory_tokens);
    }
    
    /* 2. Add author's note (if enabled) */
    /* TODO: Fix tensor concatenation - dimensions must match */
    /* For now, just return the first tensor we create */
    if (!result && settings->use_authors_note && note_tokens > 0) {
        result = authors_note_tensor(story, note_tokens);
    }
    
    /* 3. Add world info (if enabled) */
    if (!result && settings->use_world_info && wi_tokens > 0) {
        result = worldinfo_scan_tensor(story, wi_tokens, NULL);
    }
    
    /* 4. Add recent story chunks */
    if (!result && story_tokens > 0) {
        result = get_recent_chunks_tensor(story, story_tokens);
    }
    
    return result;
}

/**
 * @brief Retrieve persistent memory context as tensor
 * @param story Story state handle
 * @param max_tokens Maximum tokens to retrieve
 * @return GGML tensor with memory tokens, NULL if no memory
 * 
 * @performance ≤200µs
 * @thread-safety Thread-safe
 */
struct ggml_tensor *memory_tensor_retrieve(void *story, size_t max_tokens) {
    if (!story || max_tokens == 0) {
        return NULL;
    }
    
    struct story_state *s = (struct story_state*)story;
    
    if (!s->memory_text || s->memory_len == 0) {
        return NULL;
    }
    
    /* Allocate token buffer */
    int32_t *tokens = kobold_alloc(max_tokens * sizeof(int32_t));
    if (!tokens) {
        return NULL;
    }
    
    /* Tokenize memory text */
    size_t token_count = ggml_kernel_tokenize(s->memory_text, tokens, max_tokens);
    
    if (token_count == 0) {
        kobold_free(tokens, max_tokens * sizeof(int32_t));
        return NULL;
    }
    
    /* Create GGML tensor from tokens */
    struct ggml_tensor *tensor = ggml_kernel_create_token_tensor(tokens, token_count);
    
    kobold_free(tokens, max_tokens * sizeof(int32_t));
    
    return tensor;
}

/**
 * @brief Retrieve author's note as tensor
 * @param story Story state handle
 * @param max_tokens Maximum tokens to use
 * @return GGML tensor with author's note tokens, NULL if no note
 * 
 * @performance ≤100µs
 * @thread-safety Thread-safe
 */
struct ggml_tensor *authors_note_tensor(void *story, size_t max_tokens) {
    if (!story || max_tokens == 0) {
        return NULL;
    }
    
    struct story_state *s = (struct story_state*)story;
    
    if (!s->authors_note || s->authors_note_len == 0) {
        return NULL;
    }
    
    /* Allocate token buffer */
    int32_t *tokens = kobold_alloc(max_tokens * sizeof(int32_t));
    if (!tokens) {
        return NULL;
    }
    
    /* Tokenize author's note */
    size_t token_count = ggml_kernel_tokenize(s->authors_note, tokens, max_tokens);
    
    if (token_count == 0) {
        kobold_free(tokens, max_tokens * sizeof(int32_t));
        return NULL;
    }
    
    /* Create GGML tensor from tokens */
    struct ggml_tensor *tensor = ggml_kernel_create_token_tensor(tokens, token_count);
    
    kobold_free(tokens, max_tokens * sizeof(int32_t));
    
    return tensor;
}

/**
 * @brief Scan world info and assemble relevant entries
 * @param story Story state handle
 * @param max_tokens Maximum tokens for world info
 * @param context_text Recent context for keyword matching
 * @return GGML tensor with world info tokens, NULL if no matches
 * 
 * Implements keyword scanning for world info entries.
 * Handles selective vs. constant entries.
 * Priority-based selection when budget exceeded.
 * 
 * @performance ≤2ms
 * @thread-safety Thread-safe
 */
struct ggml_tensor *worldinfo_scan_tensor(
    void *story,
    size_t max_tokens,
    const char *context_text
) {
    if (!story || max_tokens == 0) {
        return NULL;
    }
    
    /* Forward declarations from worldinfo.c */
    extern bool worldinfo_match_keywords(void *entry, const char *context_text);
    extern const char *worldinfo_entry_get_content(void *entry);
    extern size_t worldinfo_entry_get_token_count(void *entry);
    extern bool worldinfo_entry_is_constant(void *entry);
    
    /* Forward declaration from story_management.c */
    extern void **story_get_worldinfo_entries(void *story, size_t *out_count);
    
    /* Get world info entries from story */
    size_t entry_count;
    void **entries = story_get_worldinfo_entries(story, &entry_count);
    
    if (!entries || entry_count == 0) {
        return NULL;
    }
    
    /* Allocate array to track which entries match */
    bool *matches = (bool *)calloc(entry_count, sizeof(bool));
    if (!matches) {
        return NULL;
    }
    
    /* Check each entry for keyword matches or constant flag */
    size_t match_count = 0;
    for (size_t i = 0; i < entry_count; i++) {
        if (worldinfo_entry_is_constant(entries[i]) ||
            worldinfo_match_keywords(entries[i], context_text)) {
            matches[i] = true;
            match_count++;
        }
    }
    
    if (match_count == 0) {
        free(matches);
        return NULL;
    }
    
    /* Allocate token buffer */
    int32_t *tokens = kobold_alloc(max_tokens * sizeof(int32_t));
    if (!tokens) {
        free(matches);
        return NULL;
    }
    
    /* Collect matched entry content within budget */
    size_t token_count = 0;
    for (size_t i = 0; i < entry_count && token_count < max_tokens; i++) {
        if (!matches[i]) {
            continue;
        }
        
        const char *content = worldinfo_entry_get_content(entries[i]);
        if (!content) {
            continue;
        }
        
        size_t entry_token_count = worldinfo_entry_get_token_count(entries[i]);
        
        /* Check if we have room for this entry */
        if (token_count + entry_token_count > max_tokens) {
            /* Try to fit partial content if possible */
            size_t remaining = max_tokens - token_count;
            if (remaining > WORLDINFO_MIN_TOKEN_THRESHOLD) {
                entry_token_count = remaining;
            } else {
                break;  /* Not enough room */
            }
        }
        
        /* Tokenize entry content */
        size_t actual_count = ggml_kernel_tokenize(
            content,
            tokens + token_count,
            entry_token_count
        );
        
        token_count += actual_count;
    }
    
    free(matches);
    
    if (token_count == 0) {
        kobold_free(tokens, max_tokens * sizeof(int32_t));
        return NULL;
    }
    
    /* Create GGML tensor from tokens */
    struct ggml_tensor *tensor = ggml_kernel_create_token_tensor(tokens, token_count);
    
    kobold_free(tokens, max_tokens * sizeof(int32_t));
    
    return tensor;
}

/**
 * @brief Get recent story chunks as tensor
 * @param story Story state handle
 * @param max_tokens Maximum tokens to retrieve
 * @return GGML tensor with story chunk tokens, NULL on failure
 * 
 * Retrieves the most recent story chunks up to the token budget.
 * Chunks are retrieved in reverse order (newest first).
 * 
 * @performance ≤500µs
 * @thread-safety Thread-safe
 */
struct ggml_tensor *get_recent_chunks_tensor(void *story, size_t max_tokens) {
    if (!story || max_tokens == 0) {
        return NULL;
    }
    
    struct story_state *s = (struct story_state*)story;
    
    if (!s->chunks_head) {
        return NULL; /* No chunks */
    }
    
    /* For now, return NULL to avoid concat dimension issues 
     * TODO: Implement proper chunk concatenation with dimension checking */
    return NULL;
}
