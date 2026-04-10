/***************************************************************************
 * RockPod Apple2026 — shared shell color tokens (iPod Video / Classic only).
 * See DESIGN_SYSTEM.md (separator, tertiary text, loading grammar).
 ***************************************************************************/
#ifndef APPS_APPLE2026_SHELL_H
#define APPS_APPLE2026_SHELL_H

#include "config.h"
#include "lcd.h"

#if (MODEL_NUMBER == 5) || (MODEL_NUMBER == 71)

#define ROCKPOD_APPLE2026_IPOD 1
/* Full-bleed list chrome: viewport is LCD width; apply this indent to row content. */
#define A26_LIST_CONTENT_INSET 16
/* List separator / thin rail (C6C6C8 — Apple opaqueSeparator) */
#define A26_SHELL_RAIL LCD_RGBPACK(198, 198, 200)
/* Active progress segment — tertiary family, not pure black */
#define A26_PROGRESS_FILL LCD_RGBPACK(60, 60, 67)
/* Unfilled progress track — matches WPS `%Vb(E5E5EA)` rail */
#define A26_PROGRESS_TRACK LCD_RGBPACK(229, 229, 234)
/* Statusbar battery “remainder” — calm neutral vs stock LCD_DARKGRAY */
#define A26_BATTERY_REMAIN LCD_RGBPACK(199, 199, 204)
/* Splash “broken theme” panel fill — calm grouped secondary, not stock gray */
#define A26_SPLASH_BROKEN_FILL LCD_RGBPACK(242, 242, 246)

#else

#define ROCKPOD_APPLE2026_IPOD 0

#endif

#endif /* APPS_APPLE2026_SHELL_H */
