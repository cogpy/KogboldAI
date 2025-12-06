/**
 * @file worldinfo.c
 * @brief World Info Management - Keyword matching and context injection
 * 
 * Implements the world info system for KoboldAI, which provides keyword-based
 * context injection for story generation. World info entries contain keywords
 * and associated content that gets injected into the generation context when
 * keywords are detected in recent story text.
 * 
 * @performance
 * - Entry creation: ≤100µs
 * - Keyword matching: ≤50µs per entry
 * - Context scanning: ≤2ms for typical collections
 */

#include "kobold_kernel.h"
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <pthread.h>

/* Configuration constants */
#define WORLDINFO_TOKEN_ESTIMATE_RATIO 4  /**< Estimated characters per token */

/**
 * @brief World info entry internal structure
 */
struct worldinfo_entry {
    char **keywords;           /**< Array of keyword strings */
    size_t keyword_count;      /**< Number of keywords */
    char *content;             /**< Entry content text */
    bool selective;            /**< Keyword-based activation */
    bool constant;             /**< Always-active flag */
    int32_t *content_tokens;   /**< Tokenized content */
    size_t token_count;        /**< Number of tokens in content */
    pthread_mutex_t lock;      /**< Thread safety lock */
};

/**
 * @brief Parse comma-separated keywords into array
 * @param keys Comma-separated keyword string
 * @param out_count Output parameter for keyword count
 * @return Array of keyword strings (allocated)
 */
static char **parse_keywords(const char *keys, size_t *out_count) {
    if (!keys || !out_count) {
        return NULL;
    }
    
    // Handle empty string
    if (!*keys) {
        *out_count = 0;
        return NULL;
    }
    
    // Count keywords (count commas + 1)
    size_t count = 1;
    for (const char *p = keys; *p; p++) {
        if (*p == ',') count++;
    }
    
    // Allocate keyword array
    char **keywords = (char **)calloc(count, sizeof(char *));
    if (!keywords) {
        return NULL;
    }
    
    // Parse and copy keywords
    const char *start = keys;
    size_t idx = 0;
    
    for (const char *p = keys; ; p++) {
        if (*p == ',' || *p == '\0') {
            // Skip leading whitespace
            while (start < p && isspace((unsigned char)*start)) {
                start++;
            }
            
            // Find end (skip trailing whitespace)
            const char *end = p;
            while (end > start && isspace((unsigned char)*(end - 1))) {
                end--;
            }
            
            // Copy keyword
            size_t len = end - start;
            if (len > 0) {
                keywords[idx] = (char *)malloc(len + 1);
                if (!keywords[idx]) {
                    // Cleanup on failure
                    for (size_t i = 0; i < idx; i++) {
                        free(keywords[i]);
                    }
                    free(keywords);
                    return NULL;
                }
                memcpy(keywords[idx], start, len);
                keywords[idx][len] = '\0';
                
                // Convert to lowercase for case-insensitive matching
                for (size_t i = 0; i < len; i++) {
                    keywords[idx][i] = tolower((unsigned char)keywords[idx][i]);
                }
                
                idx++;
            }
            
            if (*p == '\0') break;
            start = p + 1;
        }
    }
    
    *out_count = idx;
    return keywords;
}

/**
 * @brief Create a world info entry
 * 
 * Allocates and initializes a world info entry with the given parameters.
 * The entry can be either selective (keyword-triggered) or constant (always active).
 * 
 * @param keys Comma-separated keyword list (case-insensitive)
 * @param content Entry content text to inject
 * @param selective True for keyword-based activation
 * @param constant True for always-active entries
 * @return Entry handle, NULL on failure
 * 
 * @performance ≤100µs
 * @thread-safety Thread-safe
 */
void *worldinfo_entry_create(
    const char *keys,
    const char *content,
    bool selective,
    bool constant
) {
    if (!content) {
        return NULL;
    }
    
    // Selective entries must have keywords
    if (selective && (!keys || !*keys)) {
        return NULL;
    }
    
    struct worldinfo_entry *entry = (struct worldinfo_entry *)calloc(1, sizeof(struct worldinfo_entry));
    if (!entry) {
        return NULL;
    }
    
    // Initialize mutex
    if (pthread_mutex_init(&entry->lock, NULL) != 0) {
        free(entry);
        return NULL;
    }
    
    // Parse keywords if selective
    if (selective && keys) {
        entry->keywords = parse_keywords(keys, &entry->keyword_count);
        if (!entry->keywords) {
            pthread_mutex_destroy(&entry->lock);
            free(entry);
            return NULL;
        }
    }
    
    // Copy content
    entry->content = strdup(content);
    if (!entry->content) {
        if (entry->keywords) {
            for (size_t i = 0; i < entry->keyword_count; i++) {
                free(entry->keywords[i]);
            }
            free(entry->keywords);
        }
        pthread_mutex_destroy(&entry->lock);
        free(entry);
        return NULL;
    }
    
    entry->selective = selective;
    entry->constant = constant;
    entry->content_tokens = NULL;  // Will be tokenized on demand
    entry->token_count = 0;
    
    return (void *)entry;
}

/**
 * @brief Free a world info entry
 * 
 * Releases all memory associated with a world info entry.
 * 
 * @param entry Entry handle from worldinfo_entry_create()
 * 
 * @performance ≤50µs
 * @thread-safety Not thread-safe (caller must ensure no concurrent access)
 */
void worldinfo_entry_free(void *entry) {
    if (!entry) {
        return;
    }
    
    struct worldinfo_entry *wi = (struct worldinfo_entry *)entry;
    
    // Free keywords
    if (wi->keywords) {
        for (size_t i = 0; i < wi->keyword_count; i++) {
            free(wi->keywords[i]);
        }
        free(wi->keywords);
    }
    
    // Free content
    if (wi->content) {
        free(wi->content);
    }
    
    // Free tokens
    if (wi->content_tokens) {
        free(wi->content_tokens);
    }
    
    // Destroy mutex
    pthread_mutex_destroy(&wi->lock);
    
    free(wi);
}

/**
 * @brief Test if entry keywords match context
 * 
 * Performs case-insensitive substring matching of entry keywords against
 * the provided context text. Returns true if any keyword is found.
 * 
 * @param entry World info entry handle
 * @param context_text Text to search for keywords (case-insensitive)
 * @return True if any keyword matches, false otherwise
 * 
 * @performance ≤50µs per entry
 * @thread-safety Thread-safe
 * 
 * @note Uses case-insensitive substring matching
 * @note Constant entries always return true
 * @note Empty context returns false for selective entries
 */
bool worldinfo_match_keywords(void *entry, const char *context_text) {
    if (!entry) {
        return false;
    }
    
    struct worldinfo_entry *wi = (struct worldinfo_entry *)entry;
    
    // Thread-safe access
    pthread_mutex_lock(&wi->lock);
    
    // Constant entries always match
    if (wi->constant) {
        pthread_mutex_unlock(&wi->lock);
        return true;
    }
    
    // Non-selective entries don't match
    if (!wi->selective) {
        pthread_mutex_unlock(&wi->lock);
        return false;
    }
    
    // Empty context never matches
    if (!context_text || !*context_text) {
        pthread_mutex_unlock(&wi->lock);
        return false;
    }
    
    // Convert context to lowercase for matching
    size_t context_len = strlen(context_text);
    char *lower_context = (char *)malloc(context_len + 1);
    if (!lower_context) {
        pthread_mutex_unlock(&wi->lock);
        return false;
    }
    
    for (size_t i = 0; i < context_len; i++) {
        lower_context[i] = tolower((unsigned char)context_text[i]);
    }
    lower_context[context_len] = '\0';
    
    // Check each keyword
    bool matched = false;
    for (size_t i = 0; i < wi->keyword_count; i++) {
        if (strstr(lower_context, wi->keywords[i]) != NULL) {
            matched = true;
            break;
        }
    }
    
    free(lower_context);
    pthread_mutex_unlock(&wi->lock);
    
    return matched;
}

/**
 * @brief Get entry content
 * @param entry Entry handle
 * @return Content string (do not free)
 */
const char *worldinfo_entry_get_content(void *entry) {
    if (!entry) {
        return NULL;
    }
    
    struct worldinfo_entry *wi = (struct worldinfo_entry *)entry;
    return wi->content;
}

/**
 * @brief Get entry token count
 * @param entry Entry handle
 * @return Number of tokens in entry content
 */
size_t worldinfo_entry_get_token_count(void *entry) {
    if (!entry) {
        return 0;
    }
    
    struct worldinfo_entry *wi = (struct worldinfo_entry *)entry;
    
    // If not tokenized yet, estimate based on content length
    if (wi->token_count == 0 && wi->content) {
        return strlen(wi->content) / WORLDINFO_TOKEN_ESTIMATE_RATIO;
    }
    
    return wi->token_count;
}

/**
 * @brief Check if entry is constant
 * @param entry Entry handle
 * @return True if entry is always active
 */
bool worldinfo_entry_is_constant(void *entry) {
    if (!entry) {
        return false;
    }
    
    struct worldinfo_entry *wi = (struct worldinfo_entry *)entry;
    return wi->constant;
}

/**
 * @brief Check if entry is selective
 * @param entry Entry handle
 * @return True if entry is keyword-triggered
 */
bool worldinfo_entry_is_selective(void *entry) {
    if (!entry) {
        return false;
    }
    
    struct worldinfo_entry *wi = (struct worldinfo_entry *)entry;
    return wi->selective;
}
