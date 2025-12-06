/**
 * @file test_story_management.c
 * @brief Tests for story management functions
 */

#include "kobold_kernel.h"
#include <stdio.h>
#include <string.h>
#include <assert.h>

/**
 * @brief Test story creation and freeing
 */
int test_story_create_free(void) {
    int ret = kobold_memory_init(256);
    if (ret != 0) {
        return -1;
    }
    
    void *story = story_create();
    if (!story) {
        fprintf(stderr, "Failed to create story\n");
        kobold_memory_shutdown();
        return -1;
    }
    
    story_free(story);
    
    kobold_memory_shutdown();
    return 0;
}

/**
 * @brief Test chunk allocation and freeing
 */
int test_story_chunk_alloc_free(void) {
    int ret = kobold_memory_init(256);
    if (ret != 0) {
        return -1;
    }
    
    const char *text = "Once upon a time in a fantasy world...";
    void *chunk = story_chunk_alloc(text, 0, 10);
    if (!chunk) {
        fprintf(stderr, "Failed to allocate chunk\n");
        kobold_memory_shutdown();
        return -1;
    }
    
    /* Verify chunk properties */
    int32_t chunk_num = story_chunk_get_num(chunk);
    if (chunk_num != 0) {
        fprintf(stderr, "Incorrect chunk number: %d\n", chunk_num);
        story_chunk_free(chunk);
        kobold_memory_shutdown();
        return -1;
    }
    
    size_t token_count;
    int32_t *tokens = story_chunk_get_tokens(chunk, &token_count);
    if (!tokens || token_count != 10) {
        fprintf(stderr, "Incorrect token count: %zu\n", token_count);
        story_chunk_free(chunk);
        kobold_memory_shutdown();
        return -1;
    }
    
    story_chunk_free(chunk);
    
    kobold_memory_shutdown();
    return 0;
}

/**
 * @brief Test chunk appending to story
 */
int test_story_chunk_append(void) {
    int ret = kobold_memory_init(256);
    if (ret != 0) {
        return -1;
    }
    
    void *story = story_create();
    if (!story) {
        kobold_memory_shutdown();
        return -1;
    }
    
    /* Create and append multiple chunks */
    void *chunk1 = story_chunk_alloc("First chunk", 0, 2);
    void *chunk2 = story_chunk_alloc("Second chunk", 1, 2);
    void *chunk3 = story_chunk_alloc("Third chunk", 2, 2);
    
    if (!chunk1 || !chunk2 || !chunk3) {
        fprintf(stderr, "Failed to allocate chunks\n");
        if (chunk1) story_chunk_free(chunk1);
        if (chunk2) story_chunk_free(chunk2);
        if (chunk3) story_chunk_free(chunk3);
        story_free(story);
        kobold_memory_shutdown();
        return -1;
    }
    
    ret = story_chunk_append(story, chunk1);
    if (ret != 0) {
        fprintf(stderr, "Failed to append chunk1\n");
        story_chunk_free(chunk2);
        story_chunk_free(chunk3);
        story_free(story);
        kobold_memory_shutdown();
        return -1;
    }
    
    ret = story_chunk_append(story, chunk2);
    if (ret != 0) {
        fprintf(stderr, "Failed to append chunk2\n");
        story_chunk_free(chunk3);
        story_free(story);
        kobold_memory_shutdown();
        return -1;
    }
    
    ret = story_chunk_append(story, chunk3);
    if (ret != 0) {
        fprintf(stderr, "Failed to append chunk3\n");
        story_free(story);
        kobold_memory_shutdown();
        return -1;
    }
    
    story_free(story);
    
    kobold_memory_shutdown();
    return 0;
}

/**
 * @brief Test setting story memory
 */
int test_story_set_memory(void) {
    int ret = kobold_memory_init(256);
    if (ret != 0) {
        return -1;
    }
    
    void *story = story_create();
    if (!story) {
        kobold_memory_shutdown();
        return -1;
    }
    
    const char *memory = "This is the persistent memory context for the story.";
    ret = story_set_memory(story, memory);
    if (ret != 0) {
        fprintf(stderr, "Failed to set memory\n");
        story_free(story);
        kobold_memory_shutdown();
        return -1;
    }
    
    story_free(story);
    
    kobold_memory_shutdown();
    return 0;
}

/**
 * @brief Test setting author's note
 */
int test_story_set_authors_note(void) {
    int ret = kobold_memory_init(256);
    if (ret != 0) {
        return -1;
    }
    
    void *story = story_create();
    if (!story) {
        kobold_memory_shutdown();
        return -1;
    }
    
    const char *note = "[Author's note: Write in a fantasy style]";
    ret = story_set_authors_note(story, note);
    if (ret != 0) {
        fprintf(stderr, "Failed to set author's note\n");
        story_free(story);
        kobold_memory_shutdown();
        return -1;
    }
    
    story_free(story);
    
    kobold_memory_shutdown();
    return 0;
}
