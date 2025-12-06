# KoboldAI Kernel Function Manifest

This document specifies all kernel functions for the KoboldAI GGML implementation.
Each function is designed to replace Python logic with high-performance C/C++ tensor operations.

## Version

**Manifest Version:** 1.0.0  
**Target API Version:** KoboldAI 1.19.2+  
**GGML Version:** Compatible with llama.cpp master  
**Last Updated:** 2025-12-06

---

## Function Categories

### 1. Story Management (`story_management.c`)

Story management functions handle the core story state, chunks, and memory.

#### `story_create()`

```c
void *story_create(void);
```

**Purpose:** Allocates and initializes a new story state structure.  
**Returns:** Opaque handle to story state, NULL on failure.  
**Performance Target:** ≤50µs  
**Thread Safety:** Thread-safe (allocates independent state)  
**Status:** NOT_IMPLEMENTED  

---

#### `story_free()`

```c
void story_free(void *story);
```

**Purpose:** Frees all memory associated with a story state.  
**Parameters:**
  - `story`: Story state handle from `story_create()`
**Performance Target:** ≤100µs  
**Thread Safety:** Not thread-safe (caller must ensure no concurrent access)  
**Status:** NOT_IMPLEMENTED  

---

#### `story_chunk_alloc()`

```c
void *story_chunk_alloc(const char *text, uint32_t chunk_num, size_t token_count);
```

**Purpose:** Allocates a story chunk as a GGML tensor for efficient context assembly.  
**Parameters:**
  - `text`: UTF-8 encoded story text
  - `chunk_num`: Sequence number in story (0-based)
  - `token_count`: Number of tokens in chunk
**Returns:** Opaque chunk handle, NULL on failure.  
**Performance Target:** ≤100µs  
**Thread Safety:** Thread-safe  
**Status:** NOT_IMPLEMENTED  

**Implementation Notes:**
- Tokenizes text into tensor format
- Stores metadata (chunk number, token count)
- Registers chunk in story graph for context assembly

---

#### `story_chunk_free()`

```c
void story_chunk_free(void *chunk);
```

**Purpose:** Frees memory associated with a story chunk.  
**Parameters:**
  - `chunk`: Chunk handle from `story_chunk_alloc()`
**Performance Target:** ≤50µs  
**Thread Safety:** Not thread-safe  
**Status:** NOT_IMPLEMENTED  

---

#### `story_chunk_get_tokens()`

```c
int32_t *story_chunk_get_tokens(void *chunk, size_t *out_count);
```

**Purpose:** Returns pointer to token array for a chunk.  
**Parameters:**
  - `chunk`: Chunk handle
  - `out_count`: Output parameter for token count
**Returns:** Pointer to token array (owned by chunk), NULL on failure.  
**Performance Target:** ≤10µs  
**Thread Safety:** Thread-safe (read-only access)  
**Status:** NOT_IMPLEMENTED  

---

#### `story_chunk_append()`

```c
int story_chunk_append(void *story, void *chunk);
```

**Purpose:** Appends a chunk to the story sequence.  
**Parameters:**
  - `story`: Story state handle
  - `chunk`: Chunk to append
**Returns:** 0 on success, -1 on failure.  
**Performance Target:** ≤50µs  
**Thread Safety:** Not thread-safe (requires external synchronization)  
**Status:** NOT_IMPLEMENTED  

---

### 2. Context Assembly (`context_assembly.c`)

Context assembly functions build the generation context from story components.

#### `ctx_assemble_tensor()`

```c
struct ggml_tensor *ctx_assemble_tensor(
    void *story,
    const struct gen_settings *settings,
    size_t budget
);
```

**Purpose:** Assembles generation context from memory, author's note, world info, and story chunks.  
**Parameters:**
  - `story`: Story state handle
  - `settings`: Generation settings (includes context preferences)
  - `budget`: Maximum token count for context
**Returns:** GGML tensor containing assembled context tokens, NULL on failure.  
**Performance Target:** ≤1ms  
**Thread Safety:** Thread-safe  
**Status:** NOT_IMPLEMENTED  

**Implementation Notes:**
- Allocates tokens according to budget percentages:
  - Memory: 15%
  - Author's Note: 5%
  - World Info: 20%
  - Story Chunks: 60%
- Concatenates components in correct order
- Handles edge cases (empty components, budget overflow)

---

#### `memory_tensor_retrieve()`

```c
struct ggml_tensor *memory_tensor_retrieve(void *story, size_t max_tokens);
```

**Purpose:** Retrieves persistent memory context as a tensor.  
**Parameters:**
  - `story`: Story state handle
  - `max_tokens`: Maximum tokens to retrieve
**Returns:** GGML tensor with memory tokens, NULL if no memory.  
**Performance Target:** ≤200µs  
**Thread Safety:** Thread-safe  
**Status:** NOT_IMPLEMENTED  

---

#### `authors_note_tensor()`

```c
struct ggml_tensor *authors_note_tensor(void *story, size_t max_tokens);
```

**Purpose:** Retrieves author's note as a tensor.  
**Parameters:**
  - `story`: Story state handle
  - `max_tokens`: Maximum tokens to use
**Returns:** GGML tensor with author's note tokens, NULL if no note.  
**Performance Target:** ≤100µs  
**Thread Safety:** Thread-safe  
**Status:** NOT_IMPLEMENTED  

---

#### `worldinfo_scan_tensor()`

```c
struct ggml_tensor *worldinfo_scan_tensor(
    void *story,
    size_t max_tokens,
    const char *context_text
);
```

**Purpose:** Scans world info entries for keyword matches and assembles relevant entries.  
**Parameters:**
  - `story`: Story state handle
  - `max_tokens`: Maximum tokens for world info
  - `context_text`: Recent context for keyword matching
**Returns:** GGML tensor with world info tokens, NULL if no matches.  
**Performance Target:** ≤2ms  
**Thread Safety:** Thread-safe  
**Status:** NOT_IMPLEMENTED  

**Implementation Notes:**
- Implements keyword scanning algorithm
- Handles selective vs. constant world info entries
- Priority-based entry selection when budget exceeded

---

### 3. Token Sampling (`sampler.c`)

Sampling functions implement various token selection strategies as tensor operations.

#### `sample_nucleus_tensor()`

```c
int32_t sample_nucleus_tensor(
    struct ggml_tensor *logits,
    float top_p,
    float temperature
);
```

**Purpose:** Implements top-p (nucleus) sampling as pure tensor operations.  
**Parameters:**
  - `logits`: Model output logits tensor
  - `top_p`: Cumulative probability threshold (0.0-1.0)
  - `temperature`: Sampling temperature
**Returns:** Sampled token ID.  
**Performance Target:** ≤500µs  
**Thread Safety:** Thread-safe  
**Status:** NOT_IMPLEMENTED  

---

#### `sample_topk_tensor()`

```c
int32_t sample_topk_tensor(
    struct ggml_tensor *logits,
    int32_t top_k,
    float temperature
);
```

**Purpose:** Implements top-k sampling.  
**Parameters:**
  - `logits`: Model output logits
  - `top_k`: Number of top tokens to consider
  - `temperature`: Sampling temperature
**Returns:** Sampled token ID.  
**Performance Target:** ≤500µs  
**Thread Safety:** Thread-safe  
**Status:** NOT_IMPLEMENTED  

---

#### `sample_typical_tensor()`

```c
int32_t sample_typical_tensor(
    struct ggml_tensor *logits,
    float typical_p,
    float temperature
);
```

**Purpose:** Implements typical sampling (locally typical sampling).  
**Parameters:**
  - `logits`: Model output logits
  - `typical_p`: Typical probability mass
  - `temperature`: Sampling temperature
**Returns:** Sampled token ID.  
**Performance Target:** ≤500µs  
**Thread Safety:** Thread-safe  
**Status:** NOT_IMPLEMENTED  

---

#### `apply_repetition_penalty()`

```c
void apply_repetition_penalty(
    struct ggml_tensor *logits,
    const int32_t *recent_tokens,
    size_t token_count,
    float penalty,
    float slope
);
```

**Purpose:** Applies repetition penalty to logits based on recent tokens.  
**Parameters:**
  - `logits`: Logits tensor to modify (in-place)
  - `recent_tokens`: Array of recent token IDs
  - `token_count`: Number of recent tokens
  - `penalty`: Repetition penalty value (>1.0 = penalty)
  - `slope`: Penalty decay slope
**Performance Target:** ≤200µs  
**Thread Safety:** Not thread-safe (modifies logits in-place)  
**Status:** NOT_IMPLEMENTED  

---

### 4. World Info Management (`worldinfo.c`)

World info functions manage keyword-based context injection.

#### `worldinfo_entry_create()`

```c
void *worldinfo_entry_create(
    const char *keys,
    const char *content,
    bool selective,
    bool constant
);
```

**Purpose:** Creates a world info entry.  
**Parameters:**
  - `keys`: Comma-separated keyword list
  - `content`: Entry content text
  - `selective`: True for selective (keyword-based) activation
  - `constant`: True for always-active entries
**Returns:** Entry handle, NULL on failure.  
**Performance Target:** ≤100µs  
**Thread Safety:** Thread-safe  
**Status:** NOT_IMPLEMENTED  

---

#### `worldinfo_entry_free()`

```c
void worldinfo_entry_free(void *entry);
```

**Purpose:** Frees a world info entry.  
**Performance Target:** ≤50µs  
**Thread Safety:** Not thread-safe  
**Status:** NOT_IMPLEMENTED  

---

#### `worldinfo_match_keywords()`

```c
bool worldinfo_match_keywords(void *entry, const char *context_text);
```

**Purpose:** Tests if entry keywords match the given context.  
**Parameters:**
  - `entry`: World info entry handle
  - `context_text`: Text to search for keywords
**Returns:** True if any keyword matches.  
**Performance Target:** ≤50µs per entry  
**Thread Safety:** Thread-safe  
**Status:** NOT_IMPLEMENTED  

---

### 5. Memory Management (`memory.c`)

Memory management functions for efficient tensor allocation and pooling.

#### `kobold_memory_init()`

```c
int kobold_memory_init(size_t pool_size_mb);
```

**Purpose:** Initializes kernel memory system with a memory pool.  
**Parameters:**
  - `pool_size_mb`: Memory pool size in megabytes
**Returns:** 0 on success, -1 on failure.  
**Performance Target:** ≤10ms (initialization)  
**Thread Safety:** Not thread-safe (call once at startup)  
**Status:** NOT_IMPLEMENTED  

---

#### `kobold_memory_shutdown()`

```c
void kobold_memory_shutdown(void);
```

**Purpose:** Shuts down memory system and frees all resources.  
**Performance Target:** ≤50ms  
**Thread Safety:** Not thread-safe (call once at shutdown)  
**Status:** NOT_IMPLEMENTED  

---

#### `kobold_memory_stats()`

```c
void kobold_memory_stats(struct memory_stats *out_stats);
```

**Purpose:** Returns current memory usage statistics.  
**Parameters:**
  - `out_stats`: Output structure for statistics
**Performance Target:** ≤10µs  
**Thread Safety:** Thread-safe  
**Status:** NOT_IMPLEMENTED  

---

### 6. Agent Orchestration (`agent_orchestrator.c`)

Agent functions for multi-agent collaboration (Phase 3).

#### `agent_sched_tick()`

```c
void agent_sched_tick(
    struct agent_state *agents,
    size_t agent_count,
    void *story,
    float delta_time
);
```

**Purpose:** Updates agent states and coordinates collaboration.  
**Performance Target:** ≤5ms  
**Thread Safety:** Thread-safe  
**Status:** PLANNED (Phase 3)  

---

### 7. World Building (`world_builder.c`)

World building functions for procedural generation (Phase 3).

#### `world_graph_init()`

```c
void *world_graph_init(void);
```

**Purpose:** Initializes a world graph structure.  
**Returns:** World graph handle, NULL on failure.  
**Performance Target:** ≤100µs  
**Thread Safety:** Thread-safe  
**Status:** PLANNED (Phase 3)  

---

#### `generate_location_tensor()`

```c
struct ggml_tensor *generate_location_tensor(
    void *world,
    const char *location_type,
    uint32_t seed
);
```

**Purpose:** Procedurally generates a location as a feature tensor.  
**Performance Target:** ≤10ms  
**Thread Safety:** Thread-safe  
**Status:** PLANNED (Phase 3)  

---

## Data Structures

### `gen_settings`

```c
struct gen_settings {
    float temperature;        // 0.0-2.0, default 0.7
    float top_p;             // 0.0-1.0, default 0.9
    int32_t top_k;           // 0=disabled, default 0
    float top_a;             // 0.0-1.0, default 0.0
    float tfs;               // 0.0-1.0, default 1.0
    float typical;           // 0.0-1.0, default 1.0
    float rep_pen;           // 1.0=none, >1.0=penalty
    int32_t rep_pen_range;   // Lookback tokens
    float rep_pen_slope;     // Penalty decay
    int32_t max_length;      // Max generation tokens
    int32_t max_context;     // Context window size
    bool use_memory;
    bool use_authors_note;
    bool use_world_info;
};
```

### `memory_stats`

```c
struct memory_stats {
    size_t total_bytes;      // Total allocated
    size_t used_bytes;       // Currently used
    size_t peak_bytes;       // Peak usage
    size_t num_allocations;  // Active allocations
};
```

### `agent_state`

```c
struct agent_state {
    char agent_id[64];
    float cognitive_load;          // 0.0-1.0
    struct ggml_tensor *memory;    // Agent working memory
    struct ggml_tensor *goals;     // Goal stack tensor
    struct ggml_tensor *attention; // Attention weights
};
```

---

## Performance Targets Summary

| Operation | Target Latency | Priority |
|-----------|---------------|----------|
| Story Chunk Alloc | ≤100µs | CRITICAL |
| Context Assembly | ≤1ms | CRITICAL |
| World Info Scan | ≤2ms | HIGH |
| Nucleus Sampling | ≤500µs | CRITICAL |
| Top-K Sampling | ≤500µs | HIGH |
| Repetition Penalty | ≤200µs | MEDIUM |
| Memory Retrieve | ≤200µs | HIGH |
| Agent Tick | ≤5ms | MEDIUM |

---

## Implementation Phases

### Phase 1: Foundation (CURRENT)
- Story Management core functions
- Context Assembly primitives
- Basic memory management
- Unit tests and benchmarks

### Phase 2: Sampling
- All sampling strategies
- Repetition penalty
- Logit manipulation utilities
- Performance optimization

### Phase 3: Advanced Features
- World Info matching optimization
- Agent orchestration
- World building primitives
- Coherence checking

### Phase 4: Optimization
- Vectorization (SIMD)
- Memory pooling
- Cache optimization
- Parallel processing

---

## Notes

- All functions must be Doxygen-documented
- All pointer parameters must be validated
- UTF-8 encoding assumed for all text
- Thread safety annotations are mandatory
- Performance targets are for typical hardware (modern x86-64 CPU)
- GGML context management is implementation-defined
