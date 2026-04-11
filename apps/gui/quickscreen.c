/***************************************************************************
 *             __________               __   ___.
 *   Open      \______   \ ____   ____ |  | _\_ |__   _______  ___
 *   Source     |       _//  _ \_/ ___\|  |/ /| __ \ /  _ \  \/  /
 *   Jukebox    |    |   (  <_> )  \___|    < | \_\ (  <_> > <  <
 *   Firmware   |____|_  /\____/ \___  >__|_ \|___  /\____/__/\_ \
 *                     \/            \/     \/    \/            \/
 * $Id$
 *
 * Copyright (C) 2008 by Jonathan Gordon
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

#include <stdio.h>
#include "config.h"
#include "system.h"
#include "icons.h"
#include "font.h"
#include "kernel.h"
#include "misc.h"
#include "sound.h"
#include "action.h"
#include "settings_list.h"
#include "lang.h"
#include "playlist.h"
#include "viewport.h"
#include "audio.h"
#include "quickscreen.h"
#include "talk.h"
#include "list.h"
#include "option_select.h"
#include "debug.h"
#include "shortcuts.h"
#include "appevents.h"
#if ROCKPOD_APPLE2026_IPOD
#include "apple2026_shell.h"
#endif

 /* 1 top, 1 bottom, 2 on either side, 1 for the icons
  * if enough space, top and bottom have 2 lines */
#define MIN_LINES 5
#define MAX_NEEDED_LINES 10
 /* pixels between the 2 center items minimum or between text and icons,
  * and between text and parent boundaries */
#define MARGIN 10
#define CENTER_ICONAREA_SIZE (MARGIN+8*2)

struct gui_quickscreen
{
    const struct settings_list *items[QUICKSCREEN_ITEM_COUNT];
};

static bool redraw;

static void quickscreen_update_callback(unsigned short id,
                                        void *data, void *userdata)
{
    (void)id;
    (void)data;
    (void)userdata;

    redraw = true;
}

static void quickscreen_fix_viewports(struct gui_quickscreen *qs,
                                        struct screen *display,
                                        struct viewport *parent,
                                        struct viewport
                                                  vps[QUICKSCREEN_ITEM_COUNT],
                                        struct viewport *vp_icons)
{
    int char_height, width, pad = 0;
    int left_width = 0, right_width = 0, vert_lines;
    unsigned char *s;
    int nb_lines = viewport_get_nb_lines(parent);

    /* nb_lines only returns the number of fully visible lines, small screens
        or really large fonts could cause problems with the calculation below.
     */
    if (nb_lines == 0)
        nb_lines++;

    char_height = parent->height/nb_lines;

    /* center the icons VP first */
    *vp_icons = *parent;
    vp_icons->width = CENTER_ICONAREA_SIZE; /* abosulte smallest allowed */
    vp_icons->x = parent->x;
    vp_icons->x += (parent->width-CENTER_ICONAREA_SIZE)/2;

    vps[QUICKSCREEN_BOTTOM] = *parent;
    vps[QUICKSCREEN_TOP] = *parent;
    /* depending on the space the top/buttom items use 1 or 2 lines */
    if (nb_lines < MIN_LINES)
        vert_lines = 1;
    else
        vert_lines = 2;
    vps[QUICKSCREEN_TOP].y = parent->y;
    vps[QUICKSCREEN_TOP].height = vps[QUICKSCREEN_BOTTOM].height
            = vert_lines*char_height;
    vps[QUICKSCREEN_BOTTOM].y
            = parent->y + parent->height - vps[QUICKSCREEN_BOTTOM].height;

    /* enough space vertically, so put a nice margin */
    if (nb_lines >= MAX_NEEDED_LINES)
    {
        vps[QUICKSCREEN_TOP].y += MARGIN;
        vps[QUICKSCREEN_BOTTOM].y -= MARGIN;
    }

    vp_icons->y = vps[QUICKSCREEN_TOP].y
            + vps[QUICKSCREEN_TOP].height;
    vp_icons->height = vps[QUICKSCREEN_BOTTOM].y - vp_icons->y;

    /* adjust the left/right items widths to fit the screen nicely */
    if (qs->items[QUICKSCREEN_LEFT])
    {
        s = P2STR(ID2P(qs->items[QUICKSCREEN_LEFT]->lang_id));
        left_width = display->getstringsize(s, NULL, NULL);
    }
    if (qs->items[QUICKSCREEN_RIGHT])
    {
        s = P2STR(ID2P(qs->items[QUICKSCREEN_RIGHT]->lang_id));
        right_width = display->getstringsize(s, NULL, NULL);
    }

    width = MAX(left_width, right_width);
    if (width*2 + vp_icons->width > parent->width)
    {   /* crop text viewports */
        width = (parent->width - vp_icons->width)/2;
    }
    else
    {   /* add more gap in icons vp */
        int excess = parent->width - vp_icons->width - width*2;
        if (excess > MARGIN*4)
        {
            pad = MARGIN;
            excess -= MARGIN*2;
        }
        vp_icons->x -= excess/2;
        vp_icons->width += excess;
    }

    vps[QUICKSCREEN_LEFT] = *parent;
    vps[QUICKSCREEN_LEFT].x = parent->x + pad;
    vps[QUICKSCREEN_LEFT].width = width;

    vps[QUICKSCREEN_RIGHT] = *parent;
    vps[QUICKSCREEN_RIGHT].x = parent->x + parent->width - width - pad;
    vps[QUICKSCREEN_RIGHT].width = width;

    vps[QUICKSCREEN_LEFT].height = vps[QUICKSCREEN_RIGHT].height
            = 2*char_height;

    vps[QUICKSCREEN_LEFT].y = vps[QUICKSCREEN_RIGHT].y
            = parent->y + (parent->height/2) - char_height;

    /* shrink the icons vp by a few pixels if there is room so the arrows
       aren't drawn right next to the text */
    if (vp_icons->width > CENTER_ICONAREA_SIZE*2)
    {
        vp_icons->width -= CENTER_ICONAREA_SIZE*2/3;
        vp_icons->x += CENTER_ICONAREA_SIZE*2/6;
    }
    if (vp_icons->height > CENTER_ICONAREA_SIZE*2)
    {
        vp_icons->height -= CENTER_ICONAREA_SIZE*2/3;
        vp_icons->y += CENTER_ICONAREA_SIZE*2/6;
    }

    /* text alignment */
    vps[QUICKSCREEN_LEFT].flags &= ~VP_FLAG_ALIGNMENT_MASK; /* left-aligned */
    vps[QUICKSCREEN_TOP].flags    |= VP_FLAG_ALIGN_CENTER;  /* centered */
    vps[QUICKSCREEN_BOTTOM].flags |= VP_FLAG_ALIGN_CENTER;  /* centered */
    vps[QUICKSCREEN_RIGHT].flags  &= ~VP_FLAG_ALIGNMENT_MASK;/* right aligned*/
    vps[QUICKSCREEN_RIGHT].flags  |= VP_FLAG_ALIGN_RIGHT;
}

#if ROCKPOD_APPLE2026_IPOD
static void quickscreen_get_item_text(const struct settings_list *item,
                                      char *buf, size_t buf_size,
                                      const unsigned char **title,
                                      const unsigned char **value)
{
    int temp;

    *title = (const unsigned char *)"";
    *value = (const unsigned char *)"";
    if (!item)
        return;

    *title = P2STR(ID2P(item->lang_id));
    temp = option_value_as_int(item);
    *value = option_get_valuestring(item, buf, buf_size, temp);
}

static void quickscreen_fix_viewports_apple2026(
        struct viewport *parent,
        struct viewport vps[QUICKSCREEN_ITEM_COUNT],
        struct viewport *vp_icons,
        struct viewport *vp_volume)
{
    int line_height = font_get(parent->font)->height;
    int zone_height = line_height * 2 + 4;
    int top_margin = 12;
    int side_pad = 18;
    int center_gap = 44;
    int volume_gap = 18;
    int volume_width = parent->width - 112;
    int volume_y = parent->y + parent->height - 16;
    int bottom_y = volume_y - zone_height - volume_gap;
    int middle_y = parent->y + (parent->height - zone_height) / 2 - 2;
    int top_width = parent->width - 72;
    int side_width = (parent->width - (side_pad * 2) - center_gap) / 2;

    if (top_width < 120)
        top_width = parent->width;
    if (side_width < 96)
        side_width = 96;
    if (volume_width < 80)
        volume_width = parent->width - 32;

    vps[QUICKSCREEN_TOP] = *parent;
    vps[QUICKSCREEN_TOP].x = parent->x + (parent->width - top_width) / 2;
    vps[QUICKSCREEN_TOP].y = parent->y + top_margin;
    vps[QUICKSCREEN_TOP].width = top_width;
    vps[QUICKSCREEN_TOP].height = zone_height;
    vps[QUICKSCREEN_TOP].flags &= ~VP_FLAG_ALIGNMENT_MASK;
    vps[QUICKSCREEN_TOP].flags |= VP_FLAG_ALIGN_CENTER;

    vps[QUICKSCREEN_BOTTOM] = *parent;
    vps[QUICKSCREEN_BOTTOM].x = vps[QUICKSCREEN_TOP].x;
    vps[QUICKSCREEN_BOTTOM].y = bottom_y;
    vps[QUICKSCREEN_BOTTOM].width = top_width;
    vps[QUICKSCREEN_BOTTOM].height = zone_height;
    vps[QUICKSCREEN_BOTTOM].flags &= ~VP_FLAG_ALIGNMENT_MASK;
    vps[QUICKSCREEN_BOTTOM].flags |= VP_FLAG_ALIGN_CENTER;

    vps[QUICKSCREEN_LEFT] = *parent;
    vps[QUICKSCREEN_LEFT].x = parent->x + side_pad;
    vps[QUICKSCREEN_LEFT].y = middle_y;
    vps[QUICKSCREEN_LEFT].width = side_width;
    vps[QUICKSCREEN_LEFT].height = zone_height;
    vps[QUICKSCREEN_LEFT].flags &= ~VP_FLAG_ALIGNMENT_MASK;

    vps[QUICKSCREEN_RIGHT] = *parent;
    vps[QUICKSCREEN_RIGHT].x = parent->x + parent->width - side_pad - side_width;
    vps[QUICKSCREEN_RIGHT].y = middle_y;
    vps[QUICKSCREEN_RIGHT].width = side_width;
    vps[QUICKSCREEN_RIGHT].height = zone_height;
    vps[QUICKSCREEN_RIGHT].flags &= ~VP_FLAG_ALIGNMENT_MASK;
    vps[QUICKSCREEN_RIGHT].flags |= VP_FLAG_ALIGN_RIGHT;

    *vp_icons = *parent;
    vp_icons->width = center_gap;
    vp_icons->height = center_gap;
    vp_icons->x = parent->x + (parent->width - center_gap) / 2;
    vp_icons->y = parent->y + (parent->height - center_gap) / 2 - 4;

    *vp_volume = *parent;
    vp_volume->width = volume_width;
    vp_volume->height = 8;
    vp_volume->x = parent->x + (parent->width - volume_width) / 2;
    vp_volume->y = volume_y;
}

static void quickscreen_draw_arrow_apple2026(struct screen *display,
                                             struct viewport *vp_icons,
                                             enum quickscreen_item item)
{
    int x = 0;
    int y = 0;

    switch (item)
    {
        case QUICKSCREEN_TOP:
        {
            static const signed char pts[] = {
                4,0,
                3,1,4,1,5,1,
                2,2,3,2,4,2,5,2,6,2,
                1,3,2,3,3,3,4,3,5,3,6,3,7,3,
                0,4,1,4,2,4,6,4,7,4,8,4,
            };
            x = (vp_icons->width - 9) / 2;
            y = 1;
            for (int i = 0; i < (int)(sizeof(pts)/2); ++i)
                display->drawpixel(x + pts[i * 2], y + pts[i * 2 + 1]);
            break;
        }
        case QUICKSCREEN_BOTTOM:
        {
            static const signed char pts[] = {
                0,0,1,0,2,0,6,0,7,0,8,0,
                1,1,2,1,3,1,4,1,5,1,6,1,7,1,
                2,2,3,2,4,2,5,2,6,2,
                3,3,4,3,5,3,
                4,4,
            };
            x = (vp_icons->width - 9) / 2;
            y = vp_icons->height - 6;
            for (int i = 0; i < (int)(sizeof(pts)/2); ++i)
                display->drawpixel(x + pts[i * 2], y + pts[i * 2 + 1]);
            break;
        }
        case QUICKSCREEN_LEFT:
        {
            static const signed char pts[] = {
                0,4,
                1,3,1,4,1,5,
                2,2,2,3,2,4,2,5,2,6,
                3,1,3,2,3,3,3,4,3,5,3,6,3,7,
                4,0,4,1,4,2,4,6,4,7,4,8,
            };
            x = 1;
            y = (vp_icons->height - 9) / 2;
            for (int i = 0; i < (int)(sizeof(pts)/2); ++i)
                display->drawpixel(x + pts[i * 2], y + pts[i * 2 + 1]);
            break;
        }
        case QUICKSCREEN_RIGHT:
        {
            static const signed char pts[] = {
                4,4,
                3,3,3,4,3,5,
                2,2,2,3,2,4,2,5,2,6,
                1,1,1,2,1,3,1,4,1,5,1,6,1,7,
                0,0,0,1,0,2,0,6,0,7,0,8,
            };
            x = vp_icons->width - 6;
            y = (vp_icons->height - 9) / 2;
            for (int i = 0; i < (int)(sizeof(pts)/2); ++i)
                display->drawpixel(x + pts[i * 2], y + pts[i * 2 + 1]);
            break;
        }
        default:
            break;
    }
}

static void quickscreen_draw_item_apple2026(const struct settings_list *item,
                                            struct screen *display,
                                            struct viewport *vp)
{
    char buf[MAX_PATH];
    const unsigned char *title;
    const unsigned char *value;

    if (!item)
        return;

    quickscreen_get_item_text(item, buf, sizeof(buf), &title, &value);

    display->set_viewport(vp);
    display->set_foreground(A26_TEXT_SECONDARY);
    display->puts(0, 0, title);
    display->set_foreground(A26_TEXT_PRIMARY);
    display->puts(0, 1, value);
}

static void gui_quickscreen_draw_apple2026(
        const struct gui_quickscreen *qs,
        struct screen *display,
        struct viewport *parent,
        struct viewport vps[QUICKSCREEN_ITEM_COUNT],
        struct viewport *vp_icons,
        struct viewport *vp_volume)
{
    int minvol;
    int maxvol;
    int curvol;
    int range;
    int fill = 0;
    int cx;
    int cy;
    struct viewport *last_vp = display->set_viewport(parent);

    display->set_background(A26_SHELL_BG);
    display->set_foreground(A26_TEXT_PRIMARY);
    display->clear_viewport();

    cx = (vp_icons->x - parent->x) + (vp_icons->width / 2);
    cy = (vp_icons->y - parent->y) + (vp_icons->height / 2);

    display->set_viewport(parent);
    display->set_foreground(A26_SHELL_RAIL);
    display->vline(cx, cy - 28, cy - 10);
    display->vline(cx, cy + 10, cy + 28);
    display->hline(cx - 28, cx - 10, cy);
    display->hline(cx + 10, cx + 28, cy);

    display->set_viewport(vp_icons);
    display->set_foreground(A26_TEXT_TERTIARY);
    if (qs->items[QUICKSCREEN_TOP])
        quickscreen_draw_arrow_apple2026(display, vp_icons, QUICKSCREEN_TOP);
    if (qs->items[QUICKSCREEN_BOTTOM])
        quickscreen_draw_arrow_apple2026(display, vp_icons, QUICKSCREEN_BOTTOM);
    if (qs->items[QUICKSCREEN_LEFT])
        quickscreen_draw_arrow_apple2026(display, vp_icons, QUICKSCREEN_LEFT);
    if (qs->items[QUICKSCREEN_RIGHT])
        quickscreen_draw_arrow_apple2026(display, vp_icons, QUICKSCREEN_RIGHT);

    quickscreen_draw_item_apple2026(qs->items[QUICKSCREEN_TOP],
                                    display, &vps[QUICKSCREEN_TOP]);
    quickscreen_draw_item_apple2026(qs->items[QUICKSCREEN_LEFT],
                                    display, &vps[QUICKSCREEN_LEFT]);
    quickscreen_draw_item_apple2026(qs->items[QUICKSCREEN_RIGHT],
                                    display, &vps[QUICKSCREEN_RIGHT]);
    quickscreen_draw_item_apple2026(qs->items[QUICKSCREEN_BOTTOM],
                                    display, &vps[QUICKSCREEN_BOTTOM]);

    minvol = sound_min(SOUND_VOLUME);
    maxvol = sound_max(SOUND_VOLUME);
    curvol = sound_current(SOUND_VOLUME);
    range = maxvol - minvol;
    if (range > 0)
        fill = (vp_volume->width * (curvol - minvol)) / range;
    if (fill < 0)
        fill = 0;
    if (fill > vp_volume->width)
        fill = vp_volume->width;

    display->set_viewport(vp_volume);
    display->set_foreground(A26_PROGRESS_TRACK);
    display->fillrect(0, 2, vp_volume->width, 4);
    if (fill > 0)
    {
        display->set_foreground(A26_PROGRESS_FILL);
        display->fillrect(0, 2, fill, 4);
    }

    display->set_viewport(parent);
    display->update_viewport();
    display->set_viewport(last_vp);
}
#endif /* ROCKPOD_APPLE2026_IPOD */

static void gui_quickscreen_draw(const struct gui_quickscreen *qs,
                                 struct screen *display,
                                 struct viewport *parent,
                                 struct viewport vps[QUICKSCREEN_ITEM_COUNT],
                                 struct viewport *vp_icons)
{
    int i;
    char buf[MAX_PATH];
    unsigned const char *title, *value;
    int temp;
    struct viewport *last_vp = display->set_viewport(parent);
    display->clear_viewport();

    for (i = 0; i < QUICKSCREEN_ITEM_COUNT; i++)
    {
        struct viewport *vp = &vps[i];
        if (!qs->items[i])
            continue;
        display->set_viewport(vp);

        title = P2STR(ID2P(qs->items[i]->lang_id));
        temp = option_value_as_int(qs->items[i]);
        value = option_get_valuestring(qs->items[i],
                                       buf, MAX_PATH, temp);

        if (viewport_get_nb_lines(vp) < 2)
        {
            char text[MAX_PATH];
            snprintf(text, MAX_PATH, "%s: %s", title, value);
            display->puts_scroll(0, 0, text);
        }
        else
        {
            display->puts_scroll(0, 0, title);
            display->puts_scroll(0, 1, value);
        }
    }
    /* draw the icons */
    display->set_viewport(vp_icons);

#if ROCKPOD_APPLE2026_IPOD
    /* Apple2026 Quick Screen directional indicators: clean geometric arrows
     * drawn pixel-by-pixel using system color tokens instead of 7x8 mono glyphs. */
    if (display->depth >= 16)
    {
        unsigned arrow_col = LCD_RGBPACK(0x3C, 0x3C, 0x43); /* A26 tertiary */
        unsigned arrow_aa  = LCD_RGBPACK(0x8E, 0x8E, 0x93); /* A26 secondary (AA) */
        int cx = vp_icons->width  / 2;
        int cy = vp_icons->height / 2;

        display->set_drawmode(DRMODE_FG);
        display->set_foreground(arrow_col);

        /* Up arrow — 9px wide, 6px tall, centered horizontally at top */
        if (qs->items[QUICKSCREEN_TOP] != NULL)
        {
            int ax = cx - 4, ay = 2;
            /* pixel rows from tip to base */
            static const signed char up_arrow[] = {
                4,0, /* tip */
                3,1,4,1,5,1,
                2,2,3,2,4,2,5,2,6,2,
                1,3,2,3,3,3,5,3,6,3,7,3,
                0,4,1,4,7,4,8,4,
                0,5,1,5,7,5,8,5, /* base row */
            };
            for (int k = 0; k < (int)(sizeof(up_arrow)/2); k++)
                display->drawpixel(ax + up_arrow[k*2], ay + up_arrow[k*2+1]);
        }

        /* Down arrow — same shape, reflected */
        if (qs->items[QUICKSCREEN_BOTTOM] != NULL)
        {
            int ax = cx - 4, ay = vp_icons->height - 8;
            static const signed char dn_arrow[] = {
                0,0,1,0,7,0,8,0,
                0,1,1,1,7,1,8,1,
                1,2,2,2,3,2,5,2,6,2,7,2,
                2,3,3,3,4,3,5,3,6,3,
                3,4,4,4,5,4,
                4,5,
            };
            for (int k = 0; k < (int)(sizeof(dn_arrow)/2); k++)
                display->drawpixel(ax + dn_arrow[k*2], ay + dn_arrow[k*2+1]);
        }

        /* Right arrow — 6px wide, 9px tall */
        if (qs->items[QUICKSCREEN_RIGHT] != NULL)
        {
            int ax = vp_icons->width - 8, ay = cy - 4;
            static const signed char rt_arrow[] = {
                0,4,
                0,3,1,3,1,5,
                0,2,1,2,2,2,2,6,1,6,
                0,1,1,1,2,1,3,1,3,7,2,7,1,7,
                0,0,1,0,2,0,3,0,4,0,4,8,3,8,2,8,1,8,
                5,4,
            };
            for (int k = 0; k < (int)(sizeof(rt_arrow)/2); k++)
                display->drawpixel(ax + rt_arrow[k*2], ay + rt_arrow[k*2+1]);
        }

        /* Left arrow */
        if (qs->items[QUICKSCREEN_LEFT] != NULL)
        {
            int ax = 2, ay = cy - 4;
            static const signed char lt_arrow[] = {
                5,4,
                4,3,5,3,4,5,5,5,
                3,2,4,2,5,2,3,6,4,6,5,6,
                2,1,3,1,4,1,5,1,2,7,3,7,4,7,5,7,
                1,0,2,0,3,0,4,0,5,0,1,8,2,8,3,8,4,8,5,8,
                0,4,
            };
            for (int k = 0; k < (int)(sizeof(lt_arrow)/2); k++)
                display->drawpixel(ax + lt_arrow[k*2], ay + lt_arrow[k*2+1]);
        }

        display->set_foreground(arrow_col);
    }
    else
#endif /* ROCKPOD_APPLE2026_IPOD */
    {
    if (qs->items[QUICKSCREEN_TOP] != NULL)
    {
        display->mono_bitmap(bitmap_icons_7x8[Icon_UpArrow],
            (vp_icons->width/2) - 4, 0, 7, 8);
    }
    if (qs->items[QUICKSCREEN_RIGHT] != NULL)
    {
        display->mono_bitmap(bitmap_icons_7x8[Icon_FastForward],
            vp_icons->width - 8, (vp_icons->height/2) - 4, 7, 8);
    }
    if (qs->items[QUICKSCREEN_LEFT] != NULL)
    {
        display->mono_bitmap(bitmap_icons_7x8[Icon_FastBackward],
            0, (vp_icons->height/2) - 4, 7, 8);
    }
    if (qs->items[QUICKSCREEN_BOTTOM] != NULL)
    {
        display->mono_bitmap(bitmap_icons_7x8[Icon_DownArrow],
            (vp_icons->width/2) - 4, vp_icons->height - 8, 7, 8);
    }
    }

    display->set_viewport(parent);
    display->update_viewport();
    display->set_viewport(last_vp);
}

static void talk_qs_option(const struct settings_list *opt, bool enqueue)
{
    if (!global_settings.talk_menu || !opt)
        return;

    if (enqueue)
        talk_id(opt->lang_id, enqueue);
    option_talk_value(opt, option_value_as_int(opt), enqueue);
}

/*
 * Does the actions associated to the given button if any
 *  - qs : the quickscreen
 *  - button : the key we are going to analyse
 * returns : true if the button corresponded to an action, false otherwise
 */
static bool gui_quickscreen_do_button(struct gui_quickscreen * qs, int button)
{
    int item;
    bool previous = false;
    switch(button)
    {
        case ACTION_QS_TOP:
            item = QUICKSCREEN_TOP;
            break;

        case ACTION_QS_LEFT:
            item = QUICKSCREEN_LEFT;
            previous = true;
            break;

        case ACTION_QS_DOWN:
            item = QUICKSCREEN_BOTTOM;
            previous = true;
            break;

        case ACTION_QS_RIGHT:
            item = QUICKSCREEN_RIGHT;
            break;

        default:
            return false;
    }

    if (qs->items[item] == NULL)
        return false;

    option_select_next_val(qs->items[item], previous, true);
    talk_qs_option(qs->items[item], false);
    return true;
}

#ifdef HAVE_TOUCHSCREEN
static int quickscreen_touchscreen_button(void)
{
    struct gesture_event gevent;
    if (!action_gesture_get_event(&gevent))
        return ACTION_NONE;

    switch (gevent.id) {
    case GESTURE_TAP:
    case GESTURE_HOLD:
        break;
    default:
        return ACTION_NONE;
    }

    enum { left=1, right=2, top=4, bottom=8 };

    int bits = 0;

    if(gevent.x < LCD_WIDTH/3)
        bits |= left;
    else if(gevent.x > 2*LCD_WIDTH/3)
        bits |= right;

    if(gevent.y < LCD_HEIGHT/3)
        bits |= top;
    else if(gevent.y > 2*LCD_HEIGHT/3)
        bits |= bottom;

    switch(bits) {
    case top:
        return ACTION_QS_TOP;
    case bottom:
        return ACTION_QS_DOWN;
    case left:
        return ACTION_QS_LEFT;
    case right:
        return ACTION_QS_RIGHT;
    default:
        return ACTION_STD_CANCEL;
    }
}
#endif

static int gui_syncquickscreen_run(struct gui_quickscreen * qs, int button_enter, bool *usb)
{
    int button;
    struct viewport parent[NB_SCREENS];
    struct viewport vps[NB_SCREENS][QUICKSCREEN_ITEM_COUNT];
    struct viewport vp_icons[NB_SCREENS];
#if ROCKPOD_APPLE2026_IPOD
    struct viewport vp_volume[NB_SCREENS];
#endif
    int ret = QUICKSCREEN_OK;
    /* To quit we need either :
     *  - a second press on the button that made us enter
     *  - an action taken while pressing the enter button,
     *    then release the enter button*/
    bool can_quit = false;

    push_current_activity(ACTIVITY_QUICKSCREEN);
    redraw = false;

    add_event_ex(GUI_EVENT_NEED_UI_UPDATE, false, quickscreen_update_callback, NULL);

    FOR_NB_SCREENS(i)
    {
        screens[i].set_viewport(NULL);
        screens[i].scroll_stop();
        viewportmanager_theme_enable(i, true, &parent[i]);
#if ROCKPOD_APPLE2026_IPOD
        quickscreen_fix_viewports_apple2026(&parent[i], vps[i], &vp_icons[i],
                                            &vp_volume[i]);
        skin_update(CUSTOM_STATUSBAR, i, SKIN_REFRESH_ALL);
        gui_quickscreen_draw_apple2026(qs, &screens[i], &parent[i], vps[i],
                                       &vp_icons[i], &vp_volume[i]);
#else
        quickscreen_fix_viewports(qs, &screens[i], &parent[i], vps[i], &vp_icons[i]);
        gui_quickscreen_draw(qs, &screens[i], &parent[i], vps[i], &vp_icons[i]);
        skin_update(CUSTOM_STATUSBAR, i, SKIN_REFRESH_ALL);
#endif
    }
    *usb = false;
    /* Announce current selection on entering this screen. This is all
       queued up, but can be interrupted as soon as a setting is
       changed. */
    cond_talk_ids(VOICE_QUICKSCREEN);
    talk_qs_option(qs->items[QUICKSCREEN_TOP], true);
    if (qs->items[QUICKSCREEN_TOP] != qs->items[QUICKSCREEN_BOTTOM])
        talk_qs_option(qs->items[QUICKSCREEN_BOTTOM], true);
    talk_qs_option(qs->items[QUICKSCREEN_LEFT], true);
    if (qs->items[QUICKSCREEN_LEFT] != qs->items[QUICKSCREEN_RIGHT])
        talk_qs_option(qs->items[QUICKSCREEN_RIGHT], true);

#ifdef HAVE_TOUCHSCREEN
    action_gesture_reset();
#endif
    while (true) {
        if (redraw)
        {
            redraw = false;
            FOR_NB_SCREENS(i)
            {
#if ROCKPOD_APPLE2026_IPOD
                skin_update(CUSTOM_STATUSBAR, i, SKIN_REFRESH_ALL);
                gui_quickscreen_draw_apple2026(qs, &screens[i], &parent[i],
                                               vps[i], &vp_icons[i],
                                               &vp_volume[i]);
#else
                gui_quickscreen_draw(qs, &screens[i], &parent[i],
                                     vps[i], &vp_icons[i]);
                skin_update(CUSTOM_STATUSBAR, i, SKIN_REFRESH_ALL);
#endif
            }
        }
        button = get_action(CONTEXT_QUICKSCREEN, HZ/5);
#ifdef HAVE_TOUCHSCREEN
        if (button == ACTION_TOUCHSCREEN)
            button = quickscreen_touchscreen_button();
#endif
        if (default_event_handler(button) == SYS_USB_CONNECTED)
        {
            *usb = true;
            break;
        }
        if (gui_quickscreen_do_button(qs, button))
        {
            ret |= QUICKSCREEN_CHANGED;
            can_quit = true;
            redraw = true;
        }
        else if (button == button_enter)
            can_quit = true;
        else if (button == ACTION_QS_VOLUP) {
            adjust_volume(1);
#if ROCKPOD_APPLE2026_IPOD
            redraw = true;
#else
            FOR_NB_SCREENS(i)
                skin_update(CUSTOM_STATUSBAR, i, SKIN_REFRESH_NON_STATIC);
#endif
        }
        else if (button == ACTION_QS_VOLDOWN) {
            adjust_volume(-1);
#if ROCKPOD_APPLE2026_IPOD
            redraw = true;
#else
            FOR_NB_SCREENS(i)
                skin_update(CUSTOM_STATUSBAR, i, SKIN_REFRESH_NON_STATIC);
#endif
        }
        else if (button == ACTION_STD_CONTEXT)
        {
            ret |= QUICKSCREEN_GOTO_SHORTCUTS_MENU;
            break;
        }
        if ((button == button_enter) && can_quit)
            break;

        if (button == ACTION_STD_CANCEL)
            break;
    }
    /* Notify that we're exiting this screen */
    cond_talk_ids_fq(VOICE_OK);
    FOR_NB_SCREENS(i)
    {   /* stop scrolling before exiting */
        for (int j = 0; j < QUICKSCREEN_ITEM_COUNT; j++)
            screens[i].scroll_stop_viewport(&vps[i][j]);
        viewportmanager_theme_undo(i, !(ret & QUICKSCREEN_GOTO_SHORTCUTS_MENU));
    }

    if (ret & QUICKSCREEN_GOTO_SHORTCUTS_MENU) /* Eliminate flashing of parent during */
        pop_current_activity_without_refresh();   /* transition to Shortcuts */
    else
        pop_current_activity();

    remove_event_ex(GUI_EVENT_NEED_UI_UPDATE, quickscreen_update_callback, NULL);

    return ret;
}

int quick_screen_quick(int button_enter)
{
    struct gui_quickscreen qs;
    bool usb = false;

    for (int i = 0; i < 4; ++i)
    {
        qs.items[i] = global_settings.qs_items[i];

        if (!is_setting_quickscreenable(qs.items[i]))
            qs.items[i] = NULL;
    }

    int ret = gui_syncquickscreen_run(&qs, button_enter, &usb);
    if (ret & QUICKSCREEN_CHANGED)
        settings_save();
    if (usb)
        return QUICKSCREEN_IN_USB;
    return ret & QUICKSCREEN_GOTO_SHORTCUTS_MENU ? QUICKSCREEN_GOTO_SHORTCUTS_MENU :
                                                   QUICKSCREEN_OK;
}

/* stuff to make the quickscreen configurable */
bool is_setting_quickscreenable(const struct settings_list *setting)
{
    if (!setting)
        return true;

    /* to keep things simple, only settings which have a lang_id set are ok */
    if (setting->lang_id < 0 || (setting->flags & F_BANFROMQS))
        return false;

    switch (setting->flags & F_T_MASK)
    {
        case F_T_BOOL:
            return true;
        case F_T_INT:
        case F_T_UINT:
            return (setting->RESERVED != NULL);
        default:
            return false;
    }
}
