/**
 * @file story_management.c
 * @brief Story state and chunk management for KoboldAI kernel
 * 
 * Implements core story management functions including story state creation,
 * chunk allocation, and token management.
 */

#include "kobold_kernel.h"
#include <stdlib.h>
#include <string.h>
#include <pthread.h>

/* Forward declarations for internal functions */
extern void *kobold_alloc(size_t size);
extern void kobold_free(void *ptr, size_t size);

/**
 * @brief Story chunk internal structure
 */
struct story_chunk {
    uint32_t chunk_num;      /**< Sequence number in story */
    size_t token_count;      /**< Number of tokens */
    int32_t *tokens;         /**< Token array */
    char *text;              /**< Original UTF-8 text */
    size_t text_len;         /**< Text length in bytes */
    struct story_chunk *next; /**< Next chunk in sequence */
};

/**
 * @brief Story state internal structure
 */
struct story_state {
    struct story_chunk *chunks_head; /**< First chunk in sequence */
    struct story_chunk *chunks_tail; /**< Last chunk in sequence */
    size_t chunk_count;              /**< Total number of chunks */
    
    char *memory_text;               /**< Persistent memory */
    size_t memory_len;
    
    char *authors_note;              /**< Author's note */
    size_t authors_note_len;
    
    void **worldinfo_entries;        /**< Array of world info entries */
    size_t worldinfo_count;
    size_t worldinfo_capacity;
    
    pthread_mutex_t lock;            /**< Thread safety lock */
};

/**
 * @brief Create a new story state
 * @return Opaque story handle, NULL on failure
 * 
 * Allocates and initializes a new story state structure with default values.
 * The story must be freed with story_free() when no longer needed.
 * 
 * @performance ≤50µs
 * @thread-safety Thread-safe
 */
void *story_create(void) {
    struct story_state *story = kobold_alloc(sizeof(struct story_state));
    if (!story) {
        return NULL;
    }
    
    memset(story, 0, sizeof(struct story_state));
    
    /* Initialize mutex */
    if (pthread_mutex_init(&story->lock, NULL) != 0) {
        kobold_free(story, sizeof(struct story_state));
        return NULL;
    }
    
    /* Allocate initial worldinfo capacity */
    story->worldinfo_capacity = 16;
    story->worldinfo_entries = kobold_alloc(
        sizeof(void*) * story->worldinfo_capacity
    );
    if (!story->worldinfo_entries) {
        pthread_mutex_destroy(&story->lock);
        kobold_free(story, sizeof(struct story_state));
        return NULL;
    }
    
    return (void*)story;
}

/**
 * @brief Free story state and all associated resources
 * @param story Story handle from story_create()
 * 
 * Frees all memory associated with the story including chunks, memory,
 * author's note, and world info entries.
 * 
 * @performance ≤100µs
 * @thread-safety Not thread-safe (caller must ensure no concurrent access)
 */
void story_free(void *story) {
    if (!story) return;
    
    struct story_state *s = (struct story_state*)story;
    
    /* Free all chunks */
    struct story_chunk *chunk = s->chunks_head;
    while (chunk) {
        struct story_chunk *next = chunk->next;
        if (chunk->tokens) {
            kobold_free(chunk->tokens, sizeof(int32_t) * chunk->token_count);
        }
        if (chunk->text) {
            kobold_free(chunk->text, chunk->text_len + 1);
        }
        kobold_free(chunk, sizeof(struct story_chunk));
        chunk = next;
    }
    
    /* Free memory text */
    if (s->memory_text) {
        kobold_free(s->memory_text, s->memory_len + 1);
    }
    
    /* Free author's note */
    if (s->authors_note) {
        kobold_free(s->authors_note, s->authors_note_len + 1);
    }
    
    /* Free worldinfo entries array */
    if (s->worldinfo_entries) {
        kobold_free(s->worldinfo_entries, sizeof(void*) * s->worldinfo_capacity);
    }
    
    pthread_mutex_destroy(&s->lock);
    kobold_free(story, sizeof(struct story_state));
}

/**
 * @brief Allocate a story chunk as a GGML tensor
 * @param text UTF-8 encoded story text
 * @param chunk_num Sequence number in story (0-based)
 * @param token_count Number of tokens in chunk
 * @return Opaque chunk handle, NULL on failure
 * 
 * Creates a story chunk with tokenized text. For now, this is a placeholder
 * that stores tokens directly. Full GGML tensor integration will be added
 * once we link with the actual GGML library.
 * 
 * @performance ≤100µs
 * @thread-safety Thread-safe
 */
void *story_chunk_alloc(const char *text, uint32_t chunk_num, size_t token_count) {
    if (!text || token_count == 0) {
        return NULL;
    }
    
    struct story_chunk *chunk = kobold_alloc(sizeof(struct story_chunk));
    if (!chunk) {
        return NULL;
    }
    
    memset(chunk, 0, sizeof(struct story_chunk));
    chunk->chunk_num = chunk_num;
    chunk->token_count = token_count;
    
    /* Store text */
    chunk->text_len = strlen(text);
    chunk->text = kobold_alloc(chunk->text_len + 1);
    if (!chunk->text) {
        kobold_free(chunk, sizeof(struct story_chunk));
        return NULL;
    }
    strcpy(chunk->text, text);
    
    /* Allocate token array */
    chunk->tokens = kobold_alloc(sizeof(int32_t) * token_count);
    if (!chunk->tokens) {
        kobold_free(chunk->text, chunk->text_len + 1);
        kobold_free(chunk, sizeof(struct story_chunk));
        return NULL;
    }
    
    /* TODO: Actual tokenization will be implemented once we integrate
     * with the tokenizer from koboldcpp/llama.cpp. For now, we just
     * allocate space for the tokens. */
    memset(chunk->tokens, 0, sizeof(int32_t) * token_count);
    
    return (void*)chunk;
}

/**
 * @brief Free a story chunk
 * @param chunk Chunk handle from story_chunk_alloc()
 * 
 * @performance ≤50µs
 * @thread-safety Not thread-safe
 */
void story_chunk_free(void *chunk) {
    if (!chunk) return;
    
    struct story_chunk *c = (struct story_chunk*)chunk;
    
    if (c->tokens) {
        kobold_free(c->tokens, sizeof(int32_t) * c->token_count);
    }
    if (c->text) {
        kobold_free(c->text, c->text_len + 1);
    }
    
    kobold_free(chunk, sizeof(struct story_chunk));
}

/**
 * @brief Get token array from chunk
 * @param chunk Chunk handle
 * @param out_count Output parameter for token count
 * @return Pointer to token array (owned by chunk), NULL on failure
 * 
 * @performance ≤10µs
 * @thread-safety Thread-safe (read-only access)
 */
int32_t *story_chunk_get_tokens(void *chunk, size_t *out_count) {
    if (!chunk || !out_count) {
        return NULL;
    }
    
    struct story_chunk *c = (struct story_chunk*)chunk;
    *out_count = c->token_count;
    return c->tokens;
}

/**
 * @brief Get chunk sequence number
 * @param chunk Chunk handle
 * @return Chunk number, or -1 on error
 * 
 * @performance ≤5µs
 * @thread-safety Thread-safe
 */
int32_t story_chunk_get_num(void *chunk) {
    if (!chunk) {
        return -1;
    }
    
    struct story_chunk *c = (struct story_chunk*)chunk;
    return (int32_t)c->chunk_num;
}

/**
 * @brief Append a chunk to the story sequence
 * @param story Story state handle
 * @param chunk Chunk to append
 * @return 0 on success, -1 on failure
 * 
 * Adds the chunk to the story's sequence. The story takes ownership
 * of the chunk; do not free it separately.
 * 
 * @performance ≤50µs
 * @thread-safety Not thread-safe (requires external synchronization)
 */
int story_chunk_append(void *story, void *chunk) {
    if (!story || !chunk) {
        return -1;
    }
    
    struct story_state *s = (struct story_state*)story;
    struct story_chunk *c = (struct story_chunk*)chunk;
    
    pthread_mutex_lock(&s->lock);
    
    c->next = NULL;
    
    if (!s->chunks_head) {
        s->chunks_head = c;
        s->chunks_tail = c;
    } else {
        s->chunks_tail->next = c;
        s->chunks_tail = c;
    }
    
    s->chunk_count++;
    
    pthread_mutex_unlock(&s->lock);
    
    return 0;
}

/**
 * @brief Set persistent memory text for story
 * @param story Story state handle
 * @param memory_text UTF-8 encoded memory text
 * @return 0 on success, -1 on failure
 * 
 * @performance ≤100µs
 * @thread-safety Not thread-safe
 */
int story_set_memory(void *story, const char *memory_text) {
    if (!story || !memory_text) {
        return -1;
    }
    
    struct story_state *s = (struct story_state*)story;
    
    pthread_mutex_lock(&s->lock);
    
    /* Free existing memory */
    if (s->memory_text) {
        kobold_free(s->memory_text, s->memory_len + 1);
    }
    
    /* Allocate new memory */
    s->memory_len = strlen(memory_text);
    s->memory_text = kobold_alloc(s->memory_len + 1);
    if (!s->memory_text) {
        s->memory_len = 0;
        pthread_mutex_unlock(&s->lock);
        return -1;
    }
    
    strcpy(s->memory_text, memory_text);
    
    pthread_mutex_unlock(&s->lock);
    
    return 0;
}

/**
 * @brief Set author's note for story
 * @param story Story state handle
 * @param note_text UTF-8 encoded author's note
 * @return 0 on success, -1 on failure
 * 
 * @performance ≤100µs
 * @thread-safety Not thread-safe
 */
int story_set_authors_note(void *story, const char *note_text) {
    if (!story || !note_text) {
        return -1;
    }
    
    struct story_state *s = (struct story_state*)story;
    
    pthread_mutex_lock(&s->lock);
    
    /* Free existing note */
    if (s->authors_note) {
        kobold_free(s->authors_note, s->authors_note_len + 1);
    }
    
    /* Allocate new note */
    s->authors_note_len = strlen(note_text);
    s->authors_note = kobold_alloc(s->authors_note_len + 1);
    if (!s->authors_note) {
        s->authors_note_len = 0;
        pthread_mutex_unlock(&s->lock);
        return -1;
    }
    
    strcpy(s->authors_note, note_text);
    
    pthread_mutex_unlock(&s->lock);
    
    return 0;
}
