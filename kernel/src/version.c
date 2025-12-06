/**
 * @file version.c
 * @brief Version information for KoboldAI kernel
 */

#include "kobold_kernel.h"
#include <stdio.h>

/**
 * @brief Get kernel version string
 * @return Version string in format "MAJOR.MINOR.PATCH"
 */
const char *kobold_kernel_version(void) {
    static char version_buf[32];
    snprintf(version_buf, sizeof(version_buf), "%d.%d.%d",
             KOBOLD_KERNEL_VERSION_MAJOR,
             KOBOLD_KERNEL_VERSION_MINOR,
             KOBOLD_KERNEL_VERSION_PATCH);
    return version_buf;
}

/**
 * @brief Initialize generation settings with defaults
 * @param settings Settings structure to initialize
 * 
 * Sets all fields to sensible default values matching KoboldAI's
 * Python defaults.
 */
void gen_settings_init_default(struct gen_settings *settings) {
    if (!settings) return;
    
    settings->temperature = 0.7f;
    settings->top_p = 0.9f;
    settings->top_k = 0;
    settings->top_a = 0.0f;
    settings->tfs = 1.0f;
    settings->typical = 1.0f;
    settings->rep_pen = 1.0f;
    settings->rep_pen_range = 64;
    settings->rep_pen_slope = 0.0f;
    settings->max_length = 80;
    settings->max_context = 2048;
    settings->use_memory = true;
    settings->use_authors_note = true;
    settings->use_world_info = true;
}
