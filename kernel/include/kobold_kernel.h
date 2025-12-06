/**
 * @file kobold_kernel.h
 * @brief KoboldAI Kernel C API - High-performance GGML-based story generation primitives
 * 
 * This header defines the C API for the KoboldAI kernel library, which implements
 * AI-assisted writing and storytelling functions as pure C/C++ tensor operations
 * using GGML and llama.cpp backends.
 * 
 * @version 1.0.0
 * @date 2025-12-06
 * 
 * @section overview Overview
 * 
 * The KoboldAI kernel provides:
 * - Story management (chunk allocation, context assembly)
 * - Token sampling (nucleus, top-k, typical, repetition penalty)
 * - World info management (keyword matching, context injection)
 * - Memory management (efficient tensor allocation)
 * - Agent orchestration (multi-agent collaboration)
 * - World building (procedural generation)
 * 
 * @section thread_safety Thread Safety
 * 
 * Functions are marked as thread-safe or not in their documentation.
 * Thread-safe functions can be called from multiple threads concurrently.
 * Non-thread-safe functions require external synchronization.
 * 
 * @section performance Performance
 * 
 * Target performance metrics:
 * - Story chunk allocation: ≤100µs
 * - Context assembly: ≤1ms
 * - World info scan: ≤2ms
 * - Token sampling: ≤500µs
 * 
 * @section example Example Usage
 * 
 * @code
 * // Initialize memory system
 * kobold_memory_init(256); // 256 MB pool
 * 
 * // Create a story
 * void *story = story_create();
 * 
 * // Add story chunks
 * void *chunk1 = story_chunk_alloc("Once upon a time...", 0, 5);
 * story_chunk_append(story, chunk1);
 * 
 * // Assemble context
 * struct gen_settings settings = {
 *     .temperature = 0.7f,
 *     .top_p = 0.9f,
 *     .max_context = 2048
 * };
 * struct ggml_tensor *ctx = ctx_assemble_tensor(story, &settings, 2048);
 * 
 * // Sample token (after model inference)
 * int32_t token = sample_nucleus_tensor(logits, 0.9f, 0.7f);
 * 
 * // Cleanup
 * story_free(story);
 * kobold_memory_shutdown();
 * @endcode
 */

#ifndef KOBOLD_KERNEL_H
#define KOBOLD_KERNEL_H

#ifdef __cplusplus
extern "C" {
#endif

#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>

/* Forward declare GGML types to avoid requiring ggml.h */
struct ggml_tensor;
struct ggml_context;

/**
 * @defgroup version Version Information
 * @{
 */

#define KOBOLD_KERNEL_VERSION_MAJOR 1
#define KOBOLD_KERNEL_VERSION_MINOR 0
#define KOBOLD_KERNEL_VERSION_PATCH 0

/** Get kernel version string */
const char *kobold_kernel_version(void);

/** @} */

/**
 * @defgroup gen_settings Generation Settings
 * @{
 */

/**
 * @brief Generation settings structure
 * 
 * Maps to Python GenerationSettings for API compatibility.
 * All values have sensible defaults.
 */
struct gen_settings {
    float temperature;        /**< Sampling temperature (0.0-2.0, default 0.7) */
    float top_p;             /**< Nucleus sampling threshold (0.0-1.0, default 0.9) */
    int32_t top_k;           /**< Top-k sampling (0=disabled, default 0) */
    float top_a;             /**< Top-a sampling (0.0-1.0, default 0.0) */
    float tfs;               /**< Tail-free sampling (0.0-1.0, default 1.0) */
    float typical;           /**< Typical sampling (0.0-1.0, default 1.0) */
    float rep_pen;           /**< Repetition penalty (1.0=none, >1.0=penalty, default 1.0) */
    int32_t rep_pen_range;   /**< Lookback tokens for rep penalty (default 64) */
    float rep_pen_slope;     /**< Penalty decay slope (default 0.0) */
    int32_t max_length;      /**< Max generation tokens (default 80) */
    int32_t max_context;     /**< Context window size (default 2048) */
    bool use_memory;         /**< Enable memory context (default true) */
    bool use_authors_note;   /**< Enable author's note (default true) */
    bool use_world_info;     /**< Enable world info (default true) */
};

/**
 * @brief Initialize generation settings with defaults
 * @param settings Settings structure to initialize
 */
void gen_settings_init_default(struct gen_settings *settings);

/** @} */

/**
 * @defgroup memory Memory Management
 * @{
 */

/**
 * @brief Memory usage statistics
 */
struct memory_stats {
    size_t total_bytes;      /**< Total allocated memory */
    size_t used_bytes;       /**< Currently used memory */
    size_t peak_bytes;       /**< Peak memory usage */
    size_t num_allocations;  /**< Number of active allocations */
};

/**
 * @brief Initialize kernel memory system
 * @param pool_size_mb Memory pool size in megabytes
 * @return 0 on success, -1 on failure
 * 
 * @note Not thread-safe. Call once at program startup.
 * @performance ≤10ms
 */
int kobold_memory_init(size_t pool_size_mb);

/**
 * @brief Shutdown memory system and free all resources
 * 
 * @note Not thread-safe. Call once at program shutdown.
 * @performance ≤50ms
 */
void kobold_memory_shutdown(void);

/**
 * @brief Get current memory usage statistics
 * @param out_stats Output parameter for statistics
 * 
 * @note Thread-safe
 * @performance ≤10µs
 */
void kobold_memory_stats(struct memory_stats *out_stats);

/** @} */

/**
 * @defgroup story Story Management
 * @{
 */

/**
 * @brief Create a new story state
 * @return Opaque story handle, NULL on failure
 * 
 * Creates a new story state structure that manages story chunks,
 * memory, author's note, and world info.
 * 
 * @note Thread-safe
 * @performance ≤50µs
 */
void *story_create(void);

/**
 * @brief Free story state and all associated resources
 * @param story Story handle from story_create()
 * 
 * @note Not thread-safe. Caller must ensure no concurrent access.
 * @performance ≤100µs
 */
void story_free(void *story);

/**
 * @brief Allocate a story chunk as a GGML tensor
 * @param text UTF-8 encoded story text
 * @param chunk_num Sequence number in story (0-based)
 * @param token_count Number of tokens in chunk
 * @return Opaque chunk handle, NULL on failure
 * 
 * Tokenizes text and stores it as a GGML tensor for efficient
 * context assembly. The chunk maintains metadata about its
 * position and token count.
 * 
 * @note Thread-safe
 * @performance ≤100µs
 */
void *story_chunk_alloc(const char *text, uint32_t chunk_num, size_t token_count);

/**
 * @brief Free a story chunk
 * @param chunk Chunk handle from story_chunk_alloc()
 * 
 * @note Not thread-safe
 * @performance ≤50µs
 */
void story_chunk_free(void *chunk);

/**
 * @brief Get token array from chunk
 * @param chunk Chunk handle
 * @param out_count Output parameter for token count
 * @return Pointer to token array (owned by chunk), NULL on failure
 * 
 * Returns a pointer to the internal token array. The pointer is
 * valid until the chunk is freed. Do not modify the array.
 * 
 * @note Thread-safe (read-only access)
 * @performance ≤10µs
 */
int32_t *story_chunk_get_tokens(void *chunk, size_t *out_count);

/**
 * @brief Get chunk sequence number
 * @param chunk Chunk handle
 * @return Chunk number, or -1 on error
 * 
 * @note Thread-safe
 * @performance ≤5µs
 */
int32_t story_chunk_get_num(void *chunk);

/**
 * @brief Append a chunk to the story sequence
 * @param story Story state handle
 * @param chunk Chunk to append
 * @return 0 on success, -1 on failure
 * 
 * Adds the chunk to the story's sequence. The story takes ownership
 * of the chunk; do not free it separately.
 * 
 * @note Not thread-safe (requires external synchronization)
 * @performance ≤50µs
 */
int story_chunk_append(void *story, void *chunk);

/**
 * @brief Set persistent memory text for story
 * @param story Story state handle
 * @param memory_text UTF-8 encoded memory text
 * @return 0 on success, -1 on failure
 * 
 * @note Not thread-safe
 * @performance ≤100µs
 */
int story_set_memory(void *story, const char *memory_text);

/**
 * @brief Set author's note for story
 * @param story Story state handle
 * @param note_text UTF-8 encoded author's note
 * @return 0 on success, -1 on failure
 * 
 * @note Not thread-safe
 * @performance ≤100µs
 */
int story_set_authors_note(void *story, const char *note_text);

/**
 * @brief Get world info entries from story
 * @param story Story state handle
 * @param out_count Output parameter for entry count
 * @return Array of world info entry handles (do not free), NULL on failure
 * 
 * @note Thread-safe (read-only)
 * @performance ≤10µs
 */
void **story_get_worldinfo_entries(void *story, size_t *out_count);


/** @} */

/**
 * @defgroup context Context Assembly
 * @{
 */

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
 * Components are concatenated in the correct order for generation.
 * 
 * @note Thread-safe
 * @performance ≤1ms
 */
struct ggml_tensor *ctx_assemble_tensor(
    void *story,
    const struct gen_settings *settings,
    size_t budget
);

/**
 * @brief Retrieve persistent memory context as tensor
 * @param story Story state handle
 * @param max_tokens Maximum tokens to retrieve
 * @return GGML tensor with memory tokens, NULL if no memory
 * 
 * @note Thread-safe
 * @performance ≤200µs
 */
struct ggml_tensor *memory_tensor_retrieve(void *story, size_t max_tokens);

/**
 * @brief Retrieve author's note as tensor
 * @param story Story state handle
 * @param max_tokens Maximum tokens to use
 * @return GGML tensor with author's note tokens, NULL if no note
 * 
 * @note Thread-safe
 * @performance ≤100µs
 */
struct ggml_tensor *authors_note_tensor(void *story, size_t max_tokens);

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
 * @note Thread-safe
 * @performance ≤2ms
 */
struct ggml_tensor *worldinfo_scan_tensor(
    void *story,
    size_t max_tokens,
    const char *context_text
);

/**
 * @brief Get recent story chunks as tensor
 * @param story Story state handle
 * @param max_tokens Maximum tokens to retrieve
 * @return GGML tensor with story chunk tokens, NULL on failure
 * 
 * Retrieves the most recent story chunks up to the token budget.
 * Chunks are retrieved in reverse order (newest first).
 * 
 * @note Thread-safe
 * @performance ≤500µs
 */
struct ggml_tensor *get_recent_chunks_tensor(void *story, size_t max_tokens);

/** @} */

/**
 * @defgroup sampling Token Sampling
 * @{
 */

/**
 * @brief Top-p (nucleus) sampling
 * @param logits Model output logits tensor
 * @param top_p Cumulative probability threshold (0.0-1.0)
 * @param temperature Sampling temperature
 * @return Sampled token ID
 * 
 * Implements nucleus sampling as pure tensor operations.
 * Temperature is applied before probability calculation.
 * 
 * @note Thread-safe
 * @performance ≤500µs
 */
int32_t sample_nucleus_tensor(
    struct ggml_tensor *logits,
    float top_p,
    float temperature
);

/**
 * @brief Top-k sampling
 * @param logits Model output logits tensor
 * @param top_k Number of top tokens to consider
 * @param temperature Sampling temperature
 * @return Sampled token ID
 * 
 * @note Thread-safe
 * @performance ≤500µs
 */
int32_t sample_topk_tensor(
    struct ggml_tensor *logits,
    int32_t top_k,
    float temperature
);

/**
 * @brief Typical sampling (locally typical sampling)
 * @param logits Model output logits tensor
 * @param typical_p Typical probability mass
 * @param temperature Sampling temperature
 * @return Sampled token ID
 * 
 * @note Thread-safe
 * @performance ≤500µs
 */
int32_t sample_typical_tensor(
    struct ggml_tensor *logits,
    float typical_p,
    float temperature
);

/**
 * @brief Apply repetition penalty to logits
 * @param logits Logits tensor to modify (in-place)
 * @param recent_tokens Array of recent token IDs
 * @param token_count Number of recent tokens
 * @param penalty Repetition penalty value (>1.0 = penalty)
 * @param slope Penalty decay slope
 * 
 * Modifies logits in-place to apply repetition penalty based on
 * recent token history. Penalty decreases with distance (slope).
 * 
 * @note Not thread-safe (modifies logits in-place)
 * @performance ≤200µs
 */
void apply_repetition_penalty(
    struct ggml_tensor *logits,
    const int32_t *recent_tokens,
    size_t token_count,
    float penalty,
    float slope
);

/** @} */

/**
 * @defgroup worldinfo World Info Management
 * @{
 */

/**
 * @brief Create a world info entry
 * @param keys Comma-separated keyword list
 * @param content Entry content text
 * @param selective True for keyword-based activation
 * @param constant True for always-active entries
 * @return Entry handle, NULL on failure
 * 
 * @note Thread-safe
 * @performance ≤100µs
 */
void *worldinfo_entry_create(
    const char *keys,
    const char *content,
    bool selective,
    bool constant
);

/**
 * @brief Free a world info entry
 * @param entry Entry handle
 * 
 * @note Not thread-safe
 * @performance ≤50µs
 */
void worldinfo_entry_free(void *entry);

/**
 * @brief Test if entry keywords match context
 * @param entry World info entry handle
 * @param context_text Text to search for keywords
 * @return True if any keyword matches
 * 
 * @note Thread-safe
 * @performance ≤50µs per entry
 */
bool worldinfo_match_keywords(void *entry, const char *context_text);

/**
 * @brief Get entry content text
 * @param entry World info entry handle
 * @return Content string (do not free), NULL on failure
 * 
 * @note Thread-safe (read-only)
 * @performance ≤10µs
 */
const char *worldinfo_entry_get_content(void *entry);

/**
 * @brief Get entry token count
 * @param entry World info entry handle
 * @return Number of tokens in entry content
 * 
 * @note Thread-safe
 * @performance ≤10µs
 */
size_t worldinfo_entry_get_token_count(void *entry);

/**
 * @brief Check if entry is constant (always active)
 * @param entry World info entry handle
 * @return True if entry is always active
 * 
 * @note Thread-safe
 * @performance ≤10µs
 */
bool worldinfo_entry_is_constant(void *entry);

/**
 * @brief Check if entry is selective (keyword-triggered)
 * @param entry World info entry handle
 * @return True if entry is keyword-triggered
 * 
 * @note Thread-safe
 * @performance ≤10µs
 */
bool worldinfo_entry_is_selective(void *entry);


/**
 * @brief Add world info entry to story
 * @param story Story state handle
 * @param entry Entry to add (story takes ownership)
 * @return 0 on success, -1 on failure
 * 
 * @note Not thread-safe
 * @performance ≤50µs
 */
int story_add_worldinfo(void *story, void *entry);

/** @} */

/**
 * @defgroup agent Agent Orchestration
 * @{
 */

/**
 * @brief Agent state structure
 */
struct agent_state {
    char agent_id[64];               /**< Unique agent identifier */
    float cognitive_load;            /**< Current load (0.0-1.0) */
    struct ggml_tensor *memory;      /**< Agent working memory */
    struct ggml_tensor *goals;       /**< Goal stack tensor */
    struct ggml_tensor *attention;   /**< Attention focus weights */
};

/**
 * @brief Agent scheduler tick
 * @param agents Array of agent states
 * @param agent_count Number of agents
 * @param story Story context
 * @param delta_time Time elapsed since last tick (seconds)
 * 
 * Updates agent states and coordinates collaboration.
 * Selects active agent and generates contribution.
 * 
 * @note Thread-safe
 * @performance ≤5ms
 */
void agent_sched_tick(
    struct agent_state *agents,
    size_t agent_count,
    void *story,
    float delta_time
);

/** @} */

/**
 * @defgroup world World Building
 * @{
 */

/**
 * @brief Initialize world graph structure
 * @return World graph handle, NULL on failure
 * 
 * @note Thread-safe
 * @performance ≤100µs
 */
void *world_graph_init(void);

/**
 * @brief Free world graph
 * @param world World graph handle
 * 
 * @note Not thread-safe
 * @performance ≤100µs
 */
void world_graph_free(void *world);

/**
 * @brief Generate procedural location
 * @param world World graph handle
 * @param location_type Type of location (e.g., "city", "dungeon")
 * @param seed Random seed for generation
 * @return GGML tensor with location features, NULL on failure
 * 
 * @note Thread-safe
 * @performance ≤10ms
 */
struct ggml_tensor *generate_location_tensor(
    void *world,
    const char *location_type,
    uint32_t seed
);

/** @} */

#ifdef __cplusplus
}
#endif

#endif /* KOBOLD_KERNEL_H */
