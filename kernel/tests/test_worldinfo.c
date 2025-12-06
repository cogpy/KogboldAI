/**
 * @file test_worldinfo.c
 * @brief Tests for world info management functions
 */

#include "kobold_kernel.h"
#include <stdio.h>
#include <string.h>
#include <assert.h>

/**
 * @brief Test world info entry creation and destruction
 */
int test_worldinfo_entry_create_free(void) {
    /* Test basic creation */
    void *entry = worldinfo_entry_create(
        "dragon, castle",
        "A mighty dragon guards the ancient castle.",
        true,  /* selective */
        false  /* not constant */
    );
    
    if (!entry) {
        fprintf(stderr, "Failed to create world info entry\n");
        return -1;
    }
    
    worldinfo_entry_free(entry);
    
    /* Test constant entry */
    void *constant_entry = worldinfo_entry_create(
        NULL,
        "This is a fantasy world.",
        false,  /* not selective */
        true    /* constant */
    );
    
    if (!constant_entry) {
        fprintf(stderr, "Failed to create constant entry\n");
        return -1;
    }
    
    worldinfo_entry_free(constant_entry);
    
    /* Test invalid cases */
    void *null_content = worldinfo_entry_create("key", NULL, true, false);
    if (null_content != NULL) {
        fprintf(stderr, "Should have rejected NULL content\n");
        worldinfo_entry_free(null_content);
        return -1;
    }
    
    void *selective_no_keys = worldinfo_entry_create(NULL, "content", true, false);
    if (selective_no_keys != NULL) {
        fprintf(stderr, "Should have rejected selective entry without keys\n");
        worldinfo_entry_free(selective_no_keys);
        return -1;
    }
    
    return 0;
}

/**
 * @brief Test keyword matching
 */
int test_worldinfo_keyword_matching(void) {
    void *entry = worldinfo_entry_create(
        "dragon, knight, sword",
        "Content about dragon and knight.",
        true,  /* selective */
        false  /* not constant */
    );
    
    if (!entry) {
        fprintf(stderr, "Failed to create entry\n");
        return -1;
    }
    
    /* Test matching keywords (case-insensitive) */
    if (!worldinfo_match_keywords(entry, "The DRAGON attacked the village.")) {
        fprintf(stderr, "Should have matched 'DRAGON'\n");
        worldinfo_entry_free(entry);
        return -1;
    }
    
    if (!worldinfo_match_keywords(entry, "A brave knight appeared.")) {
        fprintf(stderr, "Should have matched 'knight'\n");
        worldinfo_entry_free(entry);
        return -1;
    }
    
    if (!worldinfo_match_keywords(entry, "He drew his sword.")) {
        fprintf(stderr, "Should have matched 'sword'\n");
        worldinfo_entry_free(entry);
        return -1;
    }
    
    /* Test non-matching text */
    if (worldinfo_match_keywords(entry, "The wizard cast a spell.")) {
        fprintf(stderr, "Should not have matched\n");
        worldinfo_entry_free(entry);
        return -1;
    }
    
    /* Test empty context */
    if (worldinfo_match_keywords(entry, "")) {
        fprintf(stderr, "Empty context should not match\n");
        worldinfo_entry_free(entry);
        return -1;
    }
    
    worldinfo_entry_free(entry);
    return 0;
}

/**
 * @brief Test constant entries
 */
int test_worldinfo_constant_entry(void) {
    void *entry = worldinfo_entry_create(
        NULL,
        "This is always included.",
        false,  /* not selective */
        true    /* constant */
    );
    
    if (!entry) {
        fprintf(stderr, "Failed to create constant entry\n");
        return -1;
    }
    
    /* Constant entries should always match */
    if (!worldinfo_match_keywords(entry, "Any text at all")) {
        fprintf(stderr, "Constant entry should always match\n");
        worldinfo_entry_free(entry);
        return -1;
    }
    
    if (!worldinfo_match_keywords(entry, "")) {
        fprintf(stderr, "Constant entry should match even empty context\n");
        worldinfo_entry_free(entry);
        return -1;
    }
    
    worldinfo_entry_free(entry);
    return 0;
}

/**
 * @brief Test world info integration with story
 */
int test_worldinfo_story_integration(void) {
    /* Initialize memory system */
    if (kobold_memory_init(64) != 0) {
        fprintf(stderr, "Failed to initialize memory\n");
        return -1;
    }
    
    /* Create story */
    void *story = story_create();
    if (!story) {
        fprintf(stderr, "Failed to create story\n");
        kobold_memory_shutdown();
        return -1;
    }
    
    /* Create world info entries */
    void *entry1 = worldinfo_entry_create(
        "dragon",
        "A fierce dragon lives in the mountains.",
        true, false
    );
    
    void *entry2 = worldinfo_entry_create(
        "castle",
        "An ancient castle stands on the hill.",
        true, false
    );
    
    void *entry3 = worldinfo_entry_create(
        NULL,
        "This is a fantasy world.",
        false, true  /* constant */
    );
    
    if (!entry1 || !entry2 || !entry3) {
        fprintf(stderr, "Failed to create entries\n");
        if (entry1) worldinfo_entry_free(entry1);
        if (entry2) worldinfo_entry_free(entry2);
        if (entry3) worldinfo_entry_free(entry3);
        story_free(story);
        kobold_memory_shutdown();
        return -1;
    }
    
    /* Add entries to story */
    if (story_add_worldinfo(story, entry1) != 0) {
        fprintf(stderr, "Failed to add entry1\n");
        worldinfo_entry_free(entry1);
        worldinfo_entry_free(entry2);
        worldinfo_entry_free(entry3);
        story_free(story);
        kobold_memory_shutdown();
        return -1;
    }
    
    if (story_add_worldinfo(story, entry2) != 0) {
        fprintf(stderr, "Failed to add entry2\n");
        worldinfo_entry_free(entry2);
        worldinfo_entry_free(entry3);
        story_free(story);
        kobold_memory_shutdown();
        return -1;
    }
    
    if (story_add_worldinfo(story, entry3) != 0) {
        fprintf(stderr, "Failed to add entry3\n");
        worldinfo_entry_free(entry3);
        story_free(story);
        kobold_memory_shutdown();
        return -1;
    }
    
    /* Verify entries were added */
    size_t count;
    void **entries = story_get_worldinfo_entries(story, &count);
    
    if (!entries || count != 3) {
        fprintf(stderr, "Expected 3 entries, got %zu\n", count);
        story_free(story);
        kobold_memory_shutdown();
        return -1;
    }
    
    /* Story takes ownership, so just free story */
    story_free(story);
    kobold_memory_shutdown();
    
    return 0;
}

/**
 * @brief Test helper functions
 */
int test_worldinfo_helpers(void) {
    void *entry = worldinfo_entry_create(
        "test",
        "Test content for world info.",
        true, false
    );
    
    if (!entry) {
        fprintf(stderr, "Failed to create entry\n");
        return -1;
    }
    
    /* Test content getter */
    const char *content = worldinfo_entry_get_content(entry);
    if (!content || strcmp(content, "Test content for world info.") != 0) {
        fprintf(stderr, "Content mismatch\n");
        worldinfo_entry_free(entry);
        return -1;
    }
    
    /* Test token count (should estimate) */
    size_t token_count = worldinfo_entry_get_token_count(entry);
    if (token_count == 0) {
        fprintf(stderr, "Token count should not be zero\n");
        worldinfo_entry_free(entry);
        return -1;
    }
    
    /* Test selective flag */
    if (!worldinfo_entry_is_selective(entry)) {
        fprintf(stderr, "Entry should be selective\n");
        worldinfo_entry_free(entry);
        return -1;
    }
    
    /* Test constant flag */
    if (worldinfo_entry_is_constant(entry)) {
        fprintf(stderr, "Entry should not be constant\n");
        worldinfo_entry_free(entry);
        return -1;
    }
    
    worldinfo_entry_free(entry);
    return 0;
}
