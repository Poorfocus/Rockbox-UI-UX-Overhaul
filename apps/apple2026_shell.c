/***************************************************************************
 * RockPod Apple2026 - shared shell runtime helpers.
 ***************************************************************************/

#include "apple2026_shell.h"

#include <string.h>

#include "settings.h"

#if ROCKPOD_APPLE2026_IPOD
bool apple2026_theme_selected(void)
{
    return !strcmp(global_settings.wps_file, ROCKBOX_DIR "/wps/Apple2026.wps")
        || !strcmp(global_settings.sbs_file, ROCKBOX_DIR "/wps/Apple2026.sbs");
}

bool apple2026_quicksettings_enabled(void)
{
    return apple2026_theme_selected();
}
#endif
