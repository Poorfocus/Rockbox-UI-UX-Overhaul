/***************************************************************************
*             __________               __   ___.
*   Open      \______   \ ____   ____ |  | _\_ |__   _______  ___
*   Source     |       _//  _ \_/ ___\|  |/ /| __ \ /  _ \  \/  /
*   Jukebox    |    |   (  <_> )  \___|    < | \_\ (  <_> > <  <
*   Firmware   |____|_  /\____/ \___  >__|_ \|___  /\____/__/\_ \
*                     \/            \/     \/    \/            \/
* $Id$
*
* Copyright (C) 2007 Jonathan Gordon
*
* This program is free software; you can redistribute it and/or
* modify it under the terms of the GNU General Public License
* as published by the Free Software Foundation; either version 2
* of the License, or (at your option) any later version.
*
* This software is distributed on an "AS IS" basis, WITHOUT WARRANTY OF ANY
* KIND, either express or implied.
*
****************************************************************************/
#ifndef __ROOT_MENU_H__
#define __ROOT_MENU_H__

#include "config.h"
#include "gcc_extensions.h"

void root_menu(void) NORETURN_ATTR;
struct menu_table {
    char *string;
    const struct menu_item_ex *item;
};

struct menu_table *root_menu_get_options(int *nb_options);

enum {
    /* from old menu api, but still required*/
    MENU_ATTACHED_USB = -10,
    MENU_SELECTED_EXIT = -9,

    GO_TO_ROOTITEM_CONTEXT = -5,
    GO_TO_PREVIOUS_MUSIC = -4,
    GO_TO_PREVIOUS_BROWSER = -3,
    GO_TO_PREVIOUS = -2,
    GO_TO_ROOT = -1,
    GO_TO_FILEBROWSER = 0,
#ifdef HAVE_TAGCACHE
    GO_TO_DBBROWSER,
#endif
    GO_TO_WPS,
    GO_TO_MAINMENU,
#ifdef HAVE_RECORDING
    GO_TO_RECSCREEN,
#endif
#if CONFIG_TUNER
    GO_TO_FM,
#endif
    GO_TO_RECENTBMARKS,
    GO_TO_PLUGIN,
    /* Do Not add any items above here unless you want it to be able to 
       be the "start screen" after a boot up. The setting in settings_list.c
       will need editing if this is the case. */
    GO_TO_BROWSEPLUGINS,
    GO_TO_TIMESCREEN,
    GO_TO_PLAYLISTS_SCREEN,
    GO_TO_PLAYLIST_VIEWER,
    GO_TO_SYSTEM_SCREEN,
    GO_TO_SHORTCUTMENU,
#ifdef HAVE_TAGCACHE
    GO_TO_PICTUREFLOW,
#endif
    /* Apple2026: browse Picard library at /Music (distinct from full storage). */
    GO_TO_MUSICLIB,
    GO_TO_EQUALIZER,
};
#ifndef PLUGIN
extern struct menu_item_ex root_menu_;

void root_menu_load_from_cfg(void* setting, char *value);
char* root_menu_write_to_cfg(void* setting, char*buf, int buf_len);
void root_menu_set_default(void* setting, void* defaultval);
bool root_menu_is_changed(void* setting, void* defaultval);

/* Apple2026: true when WPS was entered from the root menu (Now Playing /
 * resume) rather than from a browse-to-play chain.  wps_handle_browse_parent
 * checks this so "back from WPS" returns to Main Menu instead of re-opening
 * the stale playback_source chain the user already backed out of. */
extern bool wps_entered_from_root;

/* Apple2026: two-tier list font system.
 *
 * NORMAL (18pt SFProText Regular) — navigational lists:
 *   main menu, settings, database top-level categories, music artist folders
 *
 * DENSE  (16pt SFProText Regular) — content/track lists:
 *   song files inside album folders, playlist viewer, database track results
 *   Cover Flow tracklist uses its own font load (pictureflow.c) but matches.
 *
 * Set by root_menu.c at surface dispatch and by tree.c on depth change.
 * Read by list.c to select font + row floor (32px normal / 28px dense).
 */
typedef enum {
    ROCKPOD_LIST_FONT_NORMAL = 0,
    ROCKPOD_LIST_FONT_DENSE  = 1,
} rockpod_list_font_tier_t;

extern rockpod_list_font_tier_t rockpod_list_font_tier;
#endif


#endif /* __ROOT_MENU_H__ */
