/**
 * @file sampler.c
 * @brief Token sampling functions for KoboldAI kernel
 * 
 * Implements various token sampling strategies as GGML tensor operations,
 * including nucleus (top-p), top-k, typical sampling, and repetition penalty.
 */

#include "kobold_kernel.h"
#include "ggml.h"
#include <stdlib.h>
#include <string.h>
#include <math.h>

/* Forward declarations */
extern void *kobold_alloc(size_t size);
extern void kobold_free(void *ptr, size_t size);
extern struct ggml_context *ggml_kernel_get_context(void);

/**
 * @brief Comparison function for qsort (descending order by probability)
 */
typedef struct {
    int32_t id;
    float prob;
} token_prob_t;

static int compare_token_prob_desc(const void *a, const void *b) {
    const token_prob_t *ta = (const token_prob_t *)a;
    const token_prob_t *tb = (const token_prob_t *)b;
    
    if (ta->prob > tb->prob) return -1;
    if (ta->prob < tb->prob) return 1;
    return 0;
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
    for (size_t i = 0; i < n; i++) {
        float scaled = (logits[i] - max_logit) / temperature;
        probs[i] = expf(scaled);
        sum += probs[i];
    }
    
    /* Normalize */
    if (sum > 0.0f) {
        for (size_t i = 0; i < n; i++) {
            probs[i] /= sum;
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
 * @brief Implement nucleus (top-p) sampling
 * @param logits Model output logits tensor
 * @param top_p Cumulative probability threshold (0.0-1.0)
 * @param temperature Sampling temperature
 * @return Sampled token ID
 * 
 * Implements nucleus sampling by selecting from the smallest set of tokens
 * whose cumulative probability exceeds top_p.
 * 
 * @performance ≤500µs
 * @thread-safety Thread-safe
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
    
    /* Allocate working arrays */
    float *probs = kobold_alloc(n * sizeof(float));
    token_prob_t *sorted = kobold_alloc(n * sizeof(token_prob_t));
    
    if (!probs || !sorted) {
        if (probs) kobold_free(probs, n * sizeof(float));
        if (sorted) kobold_free(sorted, n * sizeof(token_prob_t));
        return -1;
    }
    
    /* Apply softmax with temperature */
    softmax_with_temperature(logits_data, n, probs, temperature);
    
    /* Create sorted array of token IDs and probabilities */
    for (size_t i = 0; i < n; i++) {
        sorted[i].id = (int32_t)i;
        sorted[i].prob = probs[i];
    }
    
    /* Sort by probability (descending) */
    qsort(sorted, n, sizeof(token_prob_t), compare_token_prob_desc);
    
    /* Find nucleus cutoff */
    float cumsum = 0.0f;
    size_t nucleus_size = 0;
    
    for (size_t i = 0; i < n; i++) {
        cumsum += sorted[i].prob;
        nucleus_size = i + 1;
        if (cumsum >= top_p) {
            break;
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
    kobold_free(probs, n * sizeof(float));
    kobold_free(sorted, n * sizeof(token_prob_t));
    
    return result;
}

/**
 * @brief Implement top-k sampling
 * @param logits Model output logits tensor
 * @param top_k Number of top tokens to consider
 * @param temperature Sampling temperature
 * @return Sampled token ID
 * 
 * Implements top-k sampling by selecting from the k tokens with
 * highest probabilities.
 * 
 * @performance ≤500µs
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
    if ((size_t)top_k > n) {
        top_k = (int32_t)n;
    }
    
    /* Allocate working arrays */
    float *probs = kobold_alloc(n * sizeof(float));
    token_prob_t *sorted = kobold_alloc(n * sizeof(token_prob_t));
    
    if (!probs || !sorted) {
        if (probs) kobold_free(probs, n * sizeof(float));
        if (sorted) kobold_free(sorted, n * sizeof(token_prob_t));
        return -1;
    }
    
    /* Apply softmax with temperature */
    softmax_with_temperature(logits_data, n, probs, temperature);
    
    /* Create sorted array */
    for (size_t i = 0; i < n; i++) {
        sorted[i].id = (int32_t)i;
        sorted[i].prob = probs[i];
    }
    
    /* Sort by probability (descending) */
    qsort(sorted, n, sizeof(token_prob_t), compare_token_prob_desc);
    
    /* Renormalize top-k probabilities */
    float topk_sum = 0.0f;
    for (int32_t i = 0; i < top_k; i++) {
        topk_sum += sorted[i].prob;
    }
    
    if (topk_sum > 0.0f) {
        for (int32_t i = 0; i < top_k; i++) {
            sorted[i].prob /= topk_sum;
        }
    }
    
    /* Sample from top-k */
    float r = (float)rand() / (float)RAND_MAX;
    float cumsum = 0.0f;
    int32_t result = sorted[0].id;
    
    for (int32_t i = 0; i < top_k; i++) {
        cumsum += sorted[i].prob;
        if (r < cumsum) {
            result = sorted[i].id;
            break;
        }
    }
    
    /* Cleanup */
    kobold_free(probs, n * sizeof(float));
    kobold_free(sorted, n * sizeof(token_prob_t));
    
    return result;
}

/**
 * @brief Implement typical sampling
 * @param logits Model output logits tensor
 * @param typical_p Typical probability mass
 * @param temperature Sampling temperature
 * @return Sampled token ID
 * 
 * Implements typical sampling (locally typical sampling).
 * Selects tokens with information content close to the conditional entropy.
 * 
 * @performance ≤500µs
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
    
    /* Allocate working arrays */
    float *probs = kobold_alloc(n * sizeof(float));
    token_prob_t *sorted = kobold_alloc(n * sizeof(token_prob_t));
    
    if (!probs || !sorted) {
        if (probs) kobold_free(probs, n * sizeof(float));
        if (sorted) kobold_free(sorted, n * sizeof(token_prob_t));
        return -1;
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
        float info = -logf(probs[i]);
        float distance = fabsf(info - entropy);
        sorted[i].id = (int32_t)i;
        sorted[i].prob = distance;
    }
    
    /* Sort by distance (ascending - typical tokens first) */
    qsort(sorted, n, sizeof(token_prob_t), compare_token_prob_desc);
    
    /* Select typical set */
    float cumsum = 0.0f;
    size_t typical_size = 0;
    
    for (size_t i = 0; i < n; i++) {
        cumsum += probs[sorted[i].id];
        typical_size = i + 1;
        if (cumsum >= typical_p) {
            break;
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
    kobold_free(probs, n * sizeof(float));
    kobold_free(sorted, n * sizeof(token_prob_t));
    
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
