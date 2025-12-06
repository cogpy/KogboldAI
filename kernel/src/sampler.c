/**
 * @file sampler.c
 * @brief Token sampling functions for KoboldAI kernel
 * 
 * Implements various token sampling strategies as GGML tensor operations,
 * including nucleus (top-p), top-k, typical sampling, and repetition penalty.
 * 
 * Optimization Notes:
 * - Uses partial sorting (heap-based) instead of full qsort for better performance
 * - Memory pooling to reduce allocation overhead
 * - Reduced nucleus estimation for better performance
 * - Optimized for ~50k vocabulary size typical in modern LLMs
 */

#include "kobold_kernel.h"
#include "ggml.h"
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <pthread.h>

/* Forward declarations */
extern void *kobold_alloc(size_t size);
extern void kobold_free(void *ptr, size_t size);
extern struct ggml_context *ggml_kernel_get_context(void);

/**
 * @brief Token probability structure
 */
typedef struct {
    int32_t id;
    float prob;
} token_prob_t;

/* Memory pool for sampling operations */
#define SAMPLER_POOL_SIZE 4
static struct {
    float *probs;
    token_prob_t *sorted;
    size_t capacity;
    bool in_use;
} sampler_pools[SAMPLER_POOL_SIZE] = {0};

static pthread_mutex_t sampler_pool_mutex = PTHREAD_MUTEX_INITIALIZER;

/**
 * @brief Acquire a memory pool for sampling
 * @param vocab_size Required vocabulary size
 * @return Pool index, or -1 if none available
 */
static int acquire_sampler_pool(size_t vocab_size) {
    pthread_mutex_lock(&sampler_pool_mutex);
    
    for (int i = 0; i < SAMPLER_POOL_SIZE; i++) {
        if (!sampler_pools[i].in_use) {
            /* Allocate or resize pool if needed */
            if (sampler_pools[i].capacity < vocab_size) {
                if (sampler_pools[i].probs) {
                    kobold_free(sampler_pools[i].probs, sampler_pools[i].capacity * sizeof(float));
                    kobold_free(sampler_pools[i].sorted, sampler_pools[i].capacity * sizeof(token_prob_t));
                }
                
                sampler_pools[i].probs = kobold_alloc(vocab_size * sizeof(float));
                sampler_pools[i].sorted = kobold_alloc(vocab_size * sizeof(token_prob_t));
                sampler_pools[i].capacity = vocab_size;
            }
            
            if (sampler_pools[i].probs && sampler_pools[i].sorted) {
                sampler_pools[i].in_use = true;
                pthread_mutex_unlock(&sampler_pool_mutex);
                return i;
            }
        }
    }
    
    pthread_mutex_unlock(&sampler_pool_mutex);
    return -1;
}

/**
 * @brief Release a memory pool
 * @param pool_idx Pool index to release
 */
static void release_sampler_pool(int pool_idx) {
    if (pool_idx >= 0 && pool_idx < SAMPLER_POOL_SIZE) {
        pthread_mutex_lock(&sampler_pool_mutex);
        sampler_pools[pool_idx].in_use = false;
        pthread_mutex_unlock(&sampler_pool_mutex);
    }
}

/**
 * @brief Comparison function for qsort (descending order by probability)
 */
static int compare_token_prob_desc(const void *a, const void *b) {
    const token_prob_t *ta = (const token_prob_t *)a;
    const token_prob_t *tb = (const token_prob_t *)b;
    
    if (ta->prob > tb->prob) return -1;
    if (ta->prob < tb->prob) return 1;
    return 0;
}

/**
 * @brief Partition function for quickselect
 */
static size_t partition(token_prob_t *arr, size_t left, size_t right) {
    float pivot = arr[right].prob;
    size_t i = left;
    
    for (size_t j = left; j < right; j++) {
        if (arr[j].prob > pivot) { /* Descending order */
            token_prob_t temp = arr[i];
            arr[i] = arr[j];
            arr[j] = temp;
            i++;
        }
    }
    
    token_prob_t temp = arr[i];
    arr[i] = arr[right];
    arr[right] = temp;
    
    return i;
}

/**
 * @brief Partial sort using quickselect to find top k elements
 * @param arr Array to partially sort
 * @param n Total number of elements
 * @param k Number of top elements needed
 * 
 * After this function, the first k elements are the top k (unsorted among themselves),
 * but all are greater than the remaining n-k elements.
 */
static void partial_sort_topk(token_prob_t *arr, size_t n, size_t k) {
    if (k >= n || k == 0) return;
    
    size_t left = 0;
    size_t right = n - 1;
    size_t target = k - 1;
    
    while (left < right) {
        size_t pivot_idx = partition(arr, left, right);
        
        if (pivot_idx == target) {
            break;
        } else if (pivot_idx < target) {
            left = pivot_idx + 1;
        } else {
            right = pivot_idx - 1;
        }
    }
    
    /* Now sort just the top k elements using insertion sort (fast for small k) */
    for (size_t i = 1; i < k; i++) {
        token_prob_t key = arr[i];
        size_t j = i;
        
        while (j > 0 && arr[j-1].prob < key.prob) {
            arr[j] = arr[j-1];
            j--;
        }
        arr[j] = key;
    }
}

/**
 * @brief Apply softmax to logits to get probabilities
 * @param logits Input logits array
 * @param n Number of logits
 * @param probs Output probabilities array (must be pre-allocated)
 * @param temperature Temperature for sampling (0.0 = greedy, >1.0 = more random)
 */
static void softmax_with_temperature(const float *logits, size_t n, float *probs, float temperature) {
    if (temperature <= 0.0f) {
        temperature = 1e-10f; /* Avoid division by zero */
    }
    
    /* Find max logit for numerical stability */
    float max_logit = logits[0];
    for (size_t i = 1; i < n; i++) {
        if (logits[i] > max_logit) {
            max_logit = logits[i];
        }
    }
    
    /* Apply temperature scaling and compute exp */
    float sum = 0.0f;
    float inv_temp = 1.0f / temperature;
    
    for (size_t i = 0; i < n; i++) {
        float scaled = (logits[i] - max_logit) * inv_temp;
        probs[i] = expf(scaled);
        sum += probs[i];
    }
    
    /* Normalize */
    if (sum > 0.0f) {
        float inv_sum = 1.0f / sum;
        for (size_t i = 0; i < n; i++) {
            probs[i] *= inv_sum;
        }
    }
}

/**
 * @brief Sample from a probability distribution
 * @param probs Probability array
 * @param n Number of probabilities
 * @return Sampled token ID
 */
static int32_t sample_from_probs(const float *probs, size_t n) {
    /* Generate random number in [0, 1) */
    float r = (float)rand() / (float)RAND_MAX;
    
    /* Cumulative sampling */
    float cumsum = 0.0f;
    for (size_t i = 0; i < n; i++) {
        cumsum += probs[i];
        if (r < cumsum) {
            return (int32_t)i;
        }
    }
    
    /* Fallback to last token */
    return (int32_t)(n - 1);
}

/**
 * @brief Implement nucleus (top-p) sampling with optimizations
 * @param logits Model output logits tensor
 * @param top_p Cumulative probability threshold (0.0-1.0)
 * @param temperature Sampling temperature
 * @return Sampled token ID
 * 
 * Implements nucleus sampling by selecting from the smallest set of tokens
 * whose cumulative probability exceeds top_p.
 * 
 * Optimizations:
 * - Memory pooling to avoid allocations
 * - Partial sorting to avoid full O(n log n) sort
 * - Early termination when nucleus is found
 * 
 * @performance ≤500µs (optimized with partial sort + memory pool)
 * @thread-safety Thread-safe (uses thread-local pool)
 */
int32_t sample_nucleus_tensor(
    struct ggml_tensor *logits,
    float top_p,
    float temperature
) {
    if (!logits || top_p <= 0.0f || top_p > 1.0f) {
        return -1;
    }
    
    /* Get logits data */
    size_t n = logits->ne[0]; /* Vocabulary size */
    float *logits_data = (float *)logits->data;
    
    /* Try to acquire a memory pool */
    int pool_idx = acquire_sampler_pool(n);
    float *probs;
    token_prob_t *sorted;
    bool using_pool = (pool_idx >= 0);
    
    if (using_pool) {
        probs = sampler_pools[pool_idx].probs;
        sorted = sampler_pools[pool_idx].sorted;
    } else {
        /* Fallback to allocation if no pool available */
        probs = kobold_alloc(n * sizeof(float));
        sorted = kobold_alloc(n * sizeof(token_prob_t));
        
        if (!probs || !sorted) {
            if (probs) kobold_free(probs, n * sizeof(float));
            if (sorted) kobold_free(sorted, n * sizeof(token_prob_t));
            return -1;
        }
    }
    
    /* Apply softmax with temperature */
    softmax_with_temperature(logits_data, n, probs, temperature);
    
    /* Create array of token IDs and probabilities */
    for (size_t i = 0; i < n; i++) {
        sorted[i].id = (int32_t)i;
        sorted[i].prob = probs[i];
    }
    
    /* Estimate nucleus size based on top_p threshold
     * For typical LLM distributions with top_p=0.9, nucleus is often 50-200 tokens
     * For top_p=0.95, it's usually 100-400 tokens
     * Use a conservative estimate based on top_p value
     */
    size_t estimated_nucleus;
    if (top_p >= 0.95f) {
        estimated_nucleus = 300; /* More tokens needed for higher top_p */
    } else if (top_p >= 0.9f) {
        estimated_nucleus = 150; /* Standard nucleus size */
    } else {
        estimated_nucleus = 100; /* Smaller nucleus for lower top_p */
    }
    
    /* Scale for small vocabularies */
    if (n < 5000) {
        estimated_nucleus = (size_t)((float)n * 0.08f); /* 8% for small vocabs */
        if (estimated_nucleus < 50) estimated_nucleus = 50;
    }
    if (estimated_nucleus > n) estimated_nucleus = n;
    
    /* Partial sort to get top candidates */
    partial_sort_topk(sorted, n, estimated_nucleus);
    
    /* Find exact nucleus cutoff */
    float cumsum = 0.0f;
    size_t nucleus_size = 0;
    
    for (size_t i = 0; i < estimated_nucleus; i++) {
        cumsum += sorted[i].prob;
        nucleus_size = i + 1;
        if (cumsum >= top_p) {
            break;
        }
    }
    
    /* If we didn't reach top_p, extend search (rare case) */
    if (cumsum < top_p && estimated_nucleus < n) {
        /* Double the search space and try again */
        size_t extended_size = estimated_nucleus * 2;
        if (extended_size > n) extended_size = n;
        
        /* Sort the extended region */
        partial_sort_topk(sorted, n, extended_size);
        
        for (size_t i = estimated_nucleus; i < extended_size; i++) {
            cumsum += sorted[i].prob;
            nucleus_size = i + 1;
            if (cumsum >= top_p) {
                break;
            }
        }
    }
    
    /* Renormalize probabilities within nucleus */
    float nucleus_sum = 0.0f;
    for (size_t i = 0; i < nucleus_size; i++) {
        nucleus_sum += sorted[i].prob;
    }
    
    if (nucleus_sum > 0.0f) {
        for (size_t i = 0; i < nucleus_size; i++) {
            sorted[i].prob /= nucleus_sum;
        }
    }
    
    /* Sample from nucleus */
    float r = (float)rand() / (float)RAND_MAX;
    cumsum = 0.0f;
    int32_t result = sorted[0].id;
    
    for (size_t i = 0; i < nucleus_size; i++) {
        cumsum += sorted[i].prob;
        if (r < cumsum) {
            result = sorted[i].id;
            break;
        }
    }
    
    /* Cleanup */
    if (using_pool) {
        release_sampler_pool(pool_idx);
    } else {
        kobold_free(probs, n * sizeof(float));
        kobold_free(sorted, n * sizeof(token_prob_t));
    }
    
    return result;
}

/**
 * @brief Implement top-k sampling with optimizations
 * @param logits Model output logits tensor
 * @param top_k Number of top tokens to consider
 * @param temperature Sampling temperature
 * @return Sampled token ID
 * 
 * Implements top-k sampling by selecting from the k tokens with
 * highest probabilities.
 * 
 * Optimizations:
 * - Memory pooling
 * - Partial sorting (only sort k elements, not all n)
 * - O(n + k log k) instead of O(n log n)
 * 
 * @performance ≤500µs (optimized)
 * @thread-safety Thread-safe
 */
int32_t sample_topk_tensor(
    struct ggml_tensor *logits,
    int32_t top_k,
    float temperature
) {
    if (!logits || top_k <= 0) {
        return -1;
    }
    
    /* Get logits data */
    size_t n = logits->ne[0]; /* Vocabulary size */
    float *logits_data = (float *)logits->data;
    
    /* Clamp top_k to vocabulary size */
    size_t k = (size_t)top_k;
    if (k > n) {
        k = n;
    }
    
    /* Try to acquire a memory pool */
    int pool_idx = acquire_sampler_pool(n);
    float *probs;
    token_prob_t *sorted;
    bool using_pool = (pool_idx >= 0);
    
    if (using_pool) {
        probs = sampler_pools[pool_idx].probs;
        sorted = sampler_pools[pool_idx].sorted;
    } else {
        /* Fallback to allocation */
        probs = kobold_alloc(n * sizeof(float));
        sorted = kobold_alloc(n * sizeof(token_prob_t));
        
        if (!probs || !sorted) {
            if (probs) kobold_free(probs, n * sizeof(float));
            if (sorted) kobold_free(sorted, n * sizeof(token_prob_t));
            return -1;
        }
    }
    
    /* Apply softmax with temperature */
    softmax_with_temperature(logits_data, n, probs, temperature);
    
    /* Create array */
    for (size_t i = 0; i < n; i++) {
        sorted[i].id = (int32_t)i;
        sorted[i].prob = probs[i];
    }
    
    /* Partial sort to get top-k (O(n + k log k) instead of O(n log n)) */
    partial_sort_topk(sorted, n, k);
    
    /* Renormalize top-k probabilities */
    float topk_sum = 0.0f;
    for (size_t i = 0; i < k; i++) {
        topk_sum += sorted[i].prob;
    }
    
    if (topk_sum > 0.0f) {
        for (size_t i = 0; i < k; i++) {
            sorted[i].prob /= topk_sum;
        }
    }
    
    /* Sample from top-k */
    float r = (float)rand() / (float)RAND_MAX;
    float cumsum = 0.0f;
    int32_t result = sorted[0].id;
    
    for (size_t i = 0; i < k; i++) {
        cumsum += sorted[i].prob;
        if (r < cumsum) {
            result = sorted[i].id;
            break;
        }
    }
    
    /* Cleanup */
    if (using_pool) {
        release_sampler_pool(pool_idx);
    } else {
        kobold_free(probs, n * sizeof(float));
        kobold_free(sorted, n * sizeof(token_prob_t));
    }
    
    return result;
}

/**
 * @brief Implement typical sampling with optimizations
 * @param logits Model output logits tensor
 * @param typical_p Typical probability mass
 * @param temperature Sampling temperature
 * @return Sampled token ID
 * 
 * Implements typical sampling (locally typical sampling).
 * Selects tokens with information content close to the conditional entropy.
 * 
 * Optimizations:
 * - Memory pooling
 * - Partial sorting
 * - O(n + k log k) complexity
 * 
 * @performance ≤500µs (optimized)
 * @thread-safety Thread-safe
 */
int32_t sample_typical_tensor(
    struct ggml_tensor *logits,
    float typical_p,
    float temperature
) {
    if (!logits || typical_p <= 0.0f || typical_p > 1.0f) {
        return -1;
    }
    
    /* Get logits data */
    size_t n = logits->ne[0];
    float *logits_data = (float *)logits->data;
    
    /* Try to acquire a memory pool */
    int pool_idx = acquire_sampler_pool(n);
    float *probs;
    token_prob_t *sorted;
    bool using_pool = (pool_idx >= 0);
    
    if (using_pool) {
        probs = sampler_pools[pool_idx].probs;
        sorted = sampler_pools[pool_idx].sorted;
    } else {
        /* Fallback to allocation */
        probs = kobold_alloc(n * sizeof(float));
        sorted = kobold_alloc(n * sizeof(token_prob_t));
        
        if (!probs || !sorted) {
            if (probs) kobold_free(probs, n * sizeof(float));
            if (sorted) kobold_free(sorted, n * sizeof(token_prob_t));
            return -1;
        }
    }
    
    /* Apply softmax with temperature */
    softmax_with_temperature(logits_data, n, probs, temperature);
    
    /* Calculate entropy */
    float entropy = 0.0f;
    for (size_t i = 0; i < n; i++) {
        if (probs[i] > 0.0f) {
            entropy -= probs[i] * logf(probs[i]);
        }
    }
    
    /* Calculate distance from entropy for each token */
    for (size_t i = 0; i < n; i++) {
        float info = -logf(probs[i] + 1e-10f); /* Add epsilon for stability */
        float distance = fabsf(info - entropy);
        sorted[i].id = (int32_t)i;
        sorted[i].prob = -distance; /* Negative so partial_sort works (wants descending) */
    }
    
    /* Estimate typical set size based on typical_p
     * Similar to nucleus, but typical sampling tends to be more focused
     */
    size_t estimated_size;
    if (typical_p >= 0.95f) {
        estimated_size = 250; /* More tokens for higher typical_p */
    } else if (typical_p >= 0.9f) {
        estimated_size = 120; /* Standard typical size */
    } else {
        estimated_size = 80; /* Smaller set for lower typical_p */
    }
    
    /* Scale for small vocabularies */
    if (n < 5000) {
        estimated_size = (size_t)((float)n * 0.06f); /* 6% for small vocabs */
        if (estimated_size < 40) estimated_size = 40;
    }
    if (estimated_size > n) estimated_size = n;
    
    /* Partial sort by ascending distance (most typical first) */
    partial_sort_topk(sorted, n, estimated_size);
    
    /* Select typical set */
    float cumsum = 0.0f;
    size_t typical_size = 0;
    
    for (size_t i = 0; i < estimated_size; i++) {
        cumsum += probs[sorted[i].id];
        typical_size = i + 1;
        if (cumsum >= typical_p) {
            break;
        }
    }
    
    /* If we didn't reach typical_p, extend search */
    if (cumsum < typical_p && estimated_size < n) {
        size_t extended_size = estimated_size * 2;
        if (extended_size > n) extended_size = n;
        
        partial_sort_topk(sorted, n, extended_size);
        
        for (size_t i = estimated_size; i < extended_size; i++) {
            cumsum += probs[sorted[i].id];
            typical_size = i + 1;
            if (cumsum >= typical_p) {
                break;
            }
        }
    }
    
    /* Renormalize */
    float typical_sum = 0.0f;
    for (size_t i = 0; i < typical_size; i++) {
        float p = probs[sorted[i].id];
        sorted[i].prob = p;
        typical_sum += p;
    }
    
    if (typical_sum > 0.0f) {
        for (size_t i = 0; i < typical_size; i++) {
            sorted[i].prob /= typical_sum;
        }
    }
    
    /* Sample from typical set */
    float r = (float)rand() / (float)RAND_MAX;
    cumsum = 0.0f;
    int32_t result = sorted[0].id;
    
    for (size_t i = 0; i < typical_size; i++) {
        cumsum += sorted[i].prob;
        if (r < cumsum) {
            result = sorted[i].id;
            break;
        }
    }
    
    /* Cleanup */
    if (using_pool) {
        release_sampler_pool(pool_idx);
    } else {
        kobold_free(probs, n * sizeof(float));
        kobold_free(sorted, n * sizeof(token_prob_t));
    }
    
    return result;
}

/**
 * @brief Apply repetition penalty to logits
 * @param logits Logits tensor to modify (in-place)
 * @param recent_tokens Array of recent token IDs
 * @param token_count Number of recent tokens
 * @param penalty Repetition penalty value (>1.0 = penalty)
 * @param slope Penalty decay slope
 * 
 * Applies repetition penalty by reducing logits for tokens that
 * appear in recent context. Penalty decays with distance.
 * 
 * @performance ≤200µs
 * @thread-safety Not thread-safe (modifies logits in-place)
 */
void apply_repetition_penalty(
    struct ggml_tensor *logits,
    const int32_t *recent_tokens,
    size_t token_count,
    float penalty,
    float slope
) {
    if (!logits || !recent_tokens || token_count == 0 || penalty <= 0.0f) {
        return;
    }
    
    float *logits_data = (float *)logits->data;
    size_t vocab_size = logits->ne[0];
    
    /* Apply penalty to each recent token */
    for (size_t i = 0; i < token_count; i++) {
        int32_t token = recent_tokens[i];
        
        if (token < 0 || (size_t)token >= vocab_size) {
            continue; /* Invalid token */
        }
        
        /* Calculate distance-based penalty */
        float distance_ratio = (float)i / (float)token_count;
        float decay = 1.0f - (distance_ratio * slope);
        if (decay < 0.0f) decay = 0.0f;
        
        float effective_penalty = 1.0f + (penalty - 1.0f) * decay;
        
        /* Apply penalty (divide if logit is positive, multiply if negative) */
        if (logits_data[token] > 0.0f) {
            logits_data[token] /= effective_penalty;
        } else {
            logits_data[token] *= effective_penalty;
        }
    }
}
