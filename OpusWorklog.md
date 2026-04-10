# OpusWorklog.md — Execution Log for OpusDesignPolish Branch

---

## 2026-04-09 — Task 1: Unify Background to Pure White

**Goal:** Eliminate all `#F8F8F8` off-white backgrounds; establish `#FFFFFF` as
the universal surface color across all Apple2026 UI.

### Changes

**`wps/Apple2026.sbs`**
- All `%Vf(F8F8F8)` and `%Vb(F8F8F8)` changed to `FFFFFF` (28 occurrences)
- Removed `%dr(0,1,-,1,F4F4F4)` shadow hairlines from both bottom bars (no longer needed on white)
- Album art fallback in bottom bar changed from `F0F0F0` to `F2F2F7`
- Updated header comment from "F8F8F8 shell" to "FFFFFF shell"

**`wps/Apple2026.wps`**
- All `%Vb(F8F8F8)` changed to `FFFFFF` (15 occurrences)
- Album art placeholder background changed from `EAEAEA` to `F2F2F7`
- Volume bar zone changed from `EDEDED` to `FFFFFF`

**`tools/apple2026_symbol_assets.py`**
- `wpsBackdrop.bmp` generation: `(248,248,248)` → `(255,255,255)`
- `usbBackdrop.bmp` generation: `(248,248,248)` → `(255,255,255)`
- `albumFramed.bmp` generation: `(248,248,248)` → `(255,255,255)`
- `albumPlaceholder.bmp` generation: `(248,248,248,255)` → `(255,255,255,255)`

### Verification

- Grep confirms zero remaining `F8F8F8` in SBS, WPS, or Python assets
- No C code changes needed (no `F8F8F8` in `.c` or `.h` files)
- `WPSLIST` already specified `background color: ffffff` — consistent
- `F2F2F7` chosen for art placeholders (Apple's systemGroupedBackground)

### Status: COMPLETE

---

## 2026-04-09 — Task 3: Reduce Large Title Font

**Goal:** Scale the large title from the oversized 35px to a proportionate 25px.

### Changes

**`wps/Apple2026.sbs`**
- Font slot 2: changed from `35-SFProDisplay-Bold.fnt` to `25-SFProDisplay-Bold.fnt`
- Large title viewport: y=8, h=28 (was y=2, h=40) — vertically centered in 40px band

**`tools/apple2026_rebuild_fonts_from_otf.py`**
- Added `28-SFProDisplay-Bold.fnt` job for future use when OTF sources available

### Rationale

35px on a 320px screen is 10.9% of width. Apple Music uses ~34pt on 390pt = 8.7%.
25px = 7.8% — slightly conservative but avoids looking oversized. 28px (8.75%) is
the ideal and has been added to the font pipeline for future generation.

The 40px band height is retained for breathing room even though 25px font only
needs ~30px. This creates a comfortable 8px top / 7px bottom padding.

### Status: COMPLETE

---

## 2026-04-09 — Task 2: Merge Double-Header on Root

**Goal:** Eliminate the wasteful 26px compact header + 52px large title at root.
Replace with a single 40px title band that holds both "Library" and battery/status.

### Changes

**`wps/Apple2026.sbs`**
- Large title band: changed from y=4, h=52 to y=2, h=40
- Content viewports `mainlarge_lt` and `main_lt`: start at y=40 (was y=56)
- Battery icon root variant: repositioned from y=22 to y=10 (centered in 40px)
- Battery text root variant: repositioned from y=26 to y=12 (centered in 40px)
- 26px header background remains (white-on-white, invisible at root)
- Header title viewports remain (only drawn for non-root via `%Lo` conditional)
- Updated key behaviour comments

### Space Reclaimed

- Old root: 56px consumed (26px header + 30px effective title offset)
- New root: 40px consumed (single unified band)
- Net gain: **16px** of content area at root menu

### Known Trade-offs

- Lock icon (y=7) and large title text (starts y=2) may overlap at root when
  hold is engaged. This is a rare state and acceptable for now. A robust fix
  would require root-specific lock/sleep/busy viewport variants.
- The 26px header viewport still draws at root but is invisible (white on white).
  This is harmless and avoids complex conditional viewport tricks.

### Status: COMPLETE

---

## 2026-04-09 — Task 4: Add Real Mini-Player When Playing

**Goal:** Replace the 11px hairline strip with a 44px mini-player bar showing
album art, track title, and play/pause indicator during playback.

### Changes

**`wps/Apple2026.sbs`**
- `bottombarsmall`: changed from 11px to 44px height
- Added 4 new viewports: `mp_albumart` (32x32), `mp_track` (16px scrolling),
  `mp_track_noart` (shifted left), `mp_playpause` (right-aligned play/pause icon)
- Updated routing logic to show mini-player content when playing and not adjusting volume
- Content viewports `mainlarge`/`mainlarge_lt`: height changed from `-1` to `-44`
- Content viewports `main`/`main_lt`: height changed from `-1` to `-36`
- Volume bars for playing state repositioned to center in 44px bar
- Removed `filledbottombarsmall` placeholder (replaced by mini-player content)

### Layout

Playing state mini-player (44px):
- y=196..239 (absolute)
- 1px separator at top (DCDCE0)
- Album art: 32x32 at x=8, y=-38 (centered vertically)
- Track title: 16px at x=48, y=-30, scrolling
- Play/pause: 15x16 at x=-30, y=-30

### Status: COMPLETE

---

## 2026-04-09 — Task 5: Increase Icon Supersampling to 4x

**Goal:** Improve icon crispness and edge quality.

### Changes

**`tools/apple2026_symbol_assets.py`**
- `_GLOBAL_SS`: 2 -> 4
- `--supersample` CLI default: 2 -> 4
- `_render_symbol_tile` default padding: 2px -> 4px
- `_rgba_to_keyed_rgb`: rewritten to composite onto white before thresholding
  (alpha cutoff lowered from 160 to 40)

### Status: COMPLETE

---

## 2026-04-09 — Task 6: Replace Drawline Chevrons with Pixel-Art AA

**Goal:** Replace crude 1px `drawline` chevrons with a hand-placed pixel-art
chevron using per-pixel anti-aliasing.

### Changes

**`apps/gui/bitmap/list.c`**
- Replaced 2x `drawline` calls with a 22-entry static pixel table
- Each entry: `{dx, dy, is_aa}` — main stroke in `C7C7CC`, AA fringe in `E3E3E5`
- Chevron size: 6x12px (was 5x10px)
- Uses `display->drawpixel()` with `DRMODE_FG` for precise per-pixel control
- AA color is 50% blend between stroke color and white background

### Rationale

Rockbox's `drawline` uses Bresenham rasterization with no anti-aliasing. On a
320x240 screen at the sizes used for disclosure chevrons (5-7px wide), the
aliasing is extremely visible and looks amateur.

The pixel-art approach gives complete control over every pixel. The AA fringe
pixels (E3E3E5) create a perceived smoothness that matches iOS-quality
rendering at this resolution. The static table is computed once and reused
per-row with minimal overhead.

### Status: COMPLETE

---

## 2026-04-09 — Task 7: Font Tracking Pipeline

**Goal:** Ensure font generation pipeline has proper tracking values for Apple-like spacing.

### Changes

**`tools/apple2026_rebuild_fonts_from_otf.py`**
- 20px Regular tracking: 0.45 -> 0.50 (more open for list readability)
- 14px Regular tracking: 0.30 -> 0.35 (more open for small text)
- Pipeline already supports `--track` and `--space-extra` parameters

### Note
Fonts must be regenerated when Apple Fonts OTF sources are available.
Run: `python tools/apple2026_rebuild_fonts_from_otf.py`

### Status: COMPLETE (pipeline ready, pending OTF rebuild)

---

## 2026-04-09 — Task 8: Fix WPS Artist Color

**Goal:** Change artist color from red accent to neutral secondary gray.

### Changes
**`wps/Apple2026.wps`**
- Artist viewport `%Vf`: `FF2D55` -> `8E8E93` (Apple systemGray)

### Rationale
Apple Music shows artist name in muted gray on Now Playing, not red.
Red is reserved for interactive elements.

### Status: COMPLETE

---

## 2026-04-09 — Task 9: Fix Battery CGD Display

**Goal:** Show "100%" instead of "CGD" when battery is full.

### Changes
**`wps/Apple2026.sbs`**: 3 occurrences of `CGD` -> `100%%`
**`wps/Apple2026.wps`**: 1 occurrence of `CGD` -> `100%%`

### Status: COMPLETE

---

## 2026-04-09 — Task 10: Separator Color Correction

**Goal:** Unify all separator/rail colors to Apple's `opaqueSeparator` value.

### Changes
- SBS bottom bar `%dr` separators: `DCDCE0` -> `C6C6C8`
- WPSLIST `list separator color`: `c7c7cc` -> `C6C6C8`
- C header `A26_SHELL_RAIL`: `(220,220,224)` -> `(198,198,200)`
- Python asset outlines: `(220,220,224)` -> `(198,198,200)`

### Status: COMPLETE

---

## 2026-04-09 — Task 11: Disable Viewer Icons

**Goal:** Remove visual clash from stock Rockbox viewer icons.

### Changes
**`wps/WPSLIST`**: `viewers iconset..+x(16|24|32):` set to `-` (disabled)

### Rationale
Apple Music doesn't show file type icons. Removing the 6x8 Tango icons
eliminates the most visible "Rockbox leakage" in file browser views.

### Status: COMPLETE

---

## 2026-04-09 — Task 12: Album Art Shadow on WPS

**Goal:** Add subtle depth to album art on Now Playing screen.

### Changes
**`tools/apple2026_symbol_assets.py`**
- WPS backdrop now includes a baked-in shadow ring at the fixed art position
  (85,8 -> 150x150). Uses 4 concentric rounded rectangles with decreasing
  alpha (20,15,10,5) composited onto white.
- Added `albumShadow.bmp` generation (standalone shadow asset)

### Status: COMPLETE

---

## 2026-04-09 — Tasks 13-14: Dialogs and Cover Flow

**Task 13 (Dialogs):** Splash, yesno, and context menu inherit white background
and black text from the SBS theme viewport. Splash already has Apple2026-specific
border and progress styling in C code. Deep structural restyling deferred.

**Task 14 (Cover Flow):** Colors inherited from global settings (bg=FFFFFF,
fg=000000, selector=E5E5EA, separator=C6C6C8). Custom fonts already loaded
(18px Regular tracklist, 19px Medium titles). Deep Cover Flow polish belongs to
the dedicated CF branch per AGENTS.md branch boundaries.

### Status: COMPLETE

---

## Task 15: Switch large title to 28px font

**Goal:** Upgrade large title from 25px (the interim value after initial 35→25 reduction) to 28px, the ideal proportion — 8.75% of 320px screen width, matching Apple Music's large-title-to-viewport ratio.

**Changes:**
- `wps/Apple2026.sbs`: Font slot 2 changed from `25-SFProDisplay-Bold.fnt` to `28-SFProDisplay-Bold.fnt`.
- `wps/Apple2026.sbs`: Large title viewport adjusted from `y=8, h=28` to `y=6, h=30` — gives 6px top padding + 30px viewport (2px breathing room around 28px glyphs) + 4px bottom padding = 40px band. Slightly top-biased weight matches Apple's visual centering.

**Rationale:** 25px was a cautious reduction from the oversized 35px. Now that the 28px `.fnt` has been generated, it's the sweet spot: legible, authoritative, proportional.

### Status: COMPLETE

---

## Task 16: Enable inset separators for Apple2026

**Goal:** Apple Music separators don't start at the screen edge — they start at the text column, leaving the icon column clean. The existing inset-separator code was behind `#if !ROCKPOD_APPLE2026_IPOD` (inverted guard) which disabled it for our target.

**Changes:**
- `apps/gui/bitmap/list.c`: Replaced `#if !ROCKPOD_APPLE2026_IPOD` block with `#if ROCKPOD_APPLE2026_IPOD` / `#else` structure. Apple2026 path erases `A26_LIST_CONTENT_INSET + icon_width + ICON_PADDING` pixels from the left of each separator hairline. Non-Apple2026 path keeps the original `icon_width`-only erasure.

**Rationale:** Inset separators are a defining iOS pattern. The guard was inverted, likely from an early iteration where the inset width wasn't tuned. Now it accounts for the 16px content inset + icon column + padding.

### Status: COMPLETE

---

## Task 17: Bump row height from 35px to 38px

**Goal:** Increase vertical breathing room per list row. 35px gave adequate density but felt tighter than Apple Music. 38px provides ~9px padding around the 20px font.

**Changes:**
- `apps/gui/list.c`: `A26` floor changed from `35` to `38`.

**Row counts at 38px:**
- Root stopped: 164px / 38 = 4 rows
- Root playing: 156px / 38 = 4 rows
- Non-root stopped: 177px / 38 = 4 rows
- Non-root playing: 169px / 38 = 4 rows

4 visible rows is proportionally comparable to Apple Music's ~9 rows on a 5.8" iPhone.

### Status: COMPLETE

---

## Task 18: WPS song title to Medium weight font

**Goal:** Apple Music shows the song title in a medium/semibold weight to distinguish it from the lighter artist and album lines below. Our WPS used Regular for both title and artist.

**Changes:**
- `wps/Apple2026.wps`: Font slot 8 changed from `20-SFProText-Regular.fnt` to `20-SFProText-Medium.fnt`.

**Rationale:** Establishes clear visual hierarchy on the Now Playing screen: Medium-weight title > Regular-weight artist (gray) > Regular-weight album (smaller).

### Status: COMPLETE

---

## Task 19: Increase icon-to-text gap (4 → 6px)

**Goal:** Widen the gap between the icon tile and the text label in list rows. 4px felt cramped; 6px gives Apple-like breathing room.

**Changes:**
- `apps/gui/bitmap/list.c`: `ICON_PADDING` changed from `4` to `6`, `ICON_PADDING_S` from `"4"` to `"6"`.
- `apps/gui/bitmap/list.c`: Inset separator erase width updated to include `ICON_PADDING` in the calculation (`A26_LIST_CONTENT_INSET + icon_width + ICON_PADDING`), so the separator aligns exactly with the text column.

### Status: COMPLETE

---

## Task 20: Selector bar rounded corners (r=4)

**Goal:** Apple Music's selection highlight has rounded corners. Rockbox draws selector bars as sharp rectangles. Implement visual rounding by erasing corner pixels.

**Changes:**
- `apps/gui/line.c`: Added `#if ROCKPOD_APPLE2026_IPOD` post-pass after the `fillrect` switch block. For `STYLE_COLORBAR`, `STYLE_INVERT`, and `STYLE_GRADIENT` bars, a quarter-circle mask erases corner pixels using the viewport background color:
  - r=4 profile: row 0 erases 4px, row 1 erases 2px, rows 2-3 erase 1px each
  - Applied to all four corners (TL, TR, BL, BR)

**Rationale:** Without native rounded-rect primitives, pixel erasure against the background is the standard Rockbox technique for visual rounding. r=4 is subtle but clearly visible at 320x240 — matches the 4px corner radius Apple uses for list row highlights on iOS.

### Status: COMPLETE

---

## R1: WPS Album Art Rounded Corners

**Goal:** Give album art the rounded-corner treatment Apple uses on cover art. Rockbox can't clip bitmaps at runtime, so the fix is a 156×156 magenta-keyed overlay (`wpsArtCorners.bmp`) drawn on top of the art that paints white in the four corner regions.

**Changes:**
- `tools/apple2026_symbol_assets.py`: Added `wpsArtCorners.bmp` generation — r=6 rounded rect drawn with opaque border, then corner pixels outside the curve filled white; everything else is transparent key.
- `wps/Apple2026.wps`: Added `%xl(ArtCorners,wpsArtCorners.bmp,...)` preload and an overlay viewport at `x=82, y=5, w=156, h=156` drawn after the art.

**Rationale:** r=6 matches `albumFramed.bmp` corner radius. 3px outset beyond art boundary ensures corners cover the full art edge.

### Status: COMPLETE

---

## R2: WPS Progress Bar Redesign

**Goal:** Replace Interpod's bitmap-textured progress bars (`pb.bmp`, `pb_active.bmp`) with clean Apple Music pill bars.

**Changes:**
- `wps/Apple2026.wps`: Replaced `%pb(...image,pb.bmp,backdrop,pbi)` with `%pb(0,0,-,3,noborder)` at h=3 (inactive) and `%pb(0,0,-,5,noborder)` at h=5 (active).
- Colors: `%Vf(3C3C43)` (fill) / `%Vb(E5E5EA)` (track) — matches progress token in design system.
- Removed `vbd`, `pbi`, `pbd` preloads (no longer used).
- Time row shifted from y=-18 to y=-20 (4px gap from new 5px active bar).

**Rationale:** Bitmap textures looked inherited/crude at 320×240. Clean flat pill is the Apple Music language.

### Status: COMPLETE

---

## R3: WPS Layout Rebalance

**Goal:** Free the song title from the inline playlist counter that was stealing 104px of its horizontal space.

**Changes:**
- `wps/Apple2026.wps`: Title viewport widened to full width (`-18` right margin instead of `-104`).
- Removed standalone playlist counter viewport on title line.
- New playlist counter viewport added with name `timeprogresslossless` (shares show/hide routing with time row) at `x=107, w=106, y=-20` — centered between elapsed and remaining time.
- Lossless indicator shifted right to `x=200, w=33` to avoid overlap.

**Rationale:** Title deserves the full width. "N of M" belongs near the time controls, not competing with the track name.

### Status: COMPLETE

---

## R4: Icon Semantic Remap + Color Audit

**Goal:** Fix three icons that all used `gear`, two that both used `slider.horizontal.3`, and the all-red treatment that made settings icons look like music content.

**Changes:**
- `tools/apple2026_symbol_assets.py`:
  - `_main_icon_tint`: accent red now only for content items (indices 0,2,4,10,11,12,14,21,28,30); all others gray.
  - Icon remapping: `memorychip`→Firmware, `textformat.size`→Font, `puzzlepiece.extension.fill`→Plugin, `dial.medium`→Menu_setting, `ellipsis.circle`→Menu_functioncall, `wrench.and.screwdriver.fill`→System_menu. All with fallbacks via `_glyph_name()`.
- Assets regenerated cleanly — all 32 tiles have ink.

**Rationale:** Red icons should signal "music content", gray signals "configuration/navigation". Unique glyphs per concept makes the icon set readable rather than repetitive.

### Status: COMPLETE

---

## R5: Quick Screen Directional Indicators

**Goal:** Replace stock 7×8 mono `bitmap_icons_7x8` arrow glyphs with clean pixel-art arrows using A26 colors.

**Changes:**
- `apps/gui/quickscreen.c`: Added `#if ROCKPOD_APPLE2026_IPOD` block in `gui_quickscreen_draw()`. For color displays, draws 9×6px (up/down) and 6×9px (left/right) arrows using `drawpixel()` with `LCD_RGBPACK(0x3C, 0x3C, 0x43)`. Fallback path unchanged for non-A26 targets.
- Added `apple2026_shell.h` include.

**Rationale:** 7×8 monochrome arrows are the most visibly "stock Rockbox" element in the Quick Screen.

### Status: COMPLETE

---

## R6: USB Screen "Connected" Label

**Goal:** Add an Apple-style "Connected" label below the USB logo.

**Changes:**
- `apps/gui/usb_screen.c`: Added `#if ROCKPOD_APPLE2026_IPOD` block in `usb_screens_draw()` that renders "Connected" in `6E6E73` gray, centered below the logo viewport.
- Added `apple2026_shell.h` include (guarded).

**Rationale:** A blank white screen with just a USB plug icon doesn't say anything. "Connected" echoes iOS's connected-to-iTunes language.

### Status: COMPLETE

---

## R7: Yes/No Dialog Apple Styling

**Goal:** Replace stock "Confirm with SELECT / Cancel with any other button" text with Apple-style button labels.

**Changes:**
- `apps/gui/yesno.c`: Added `#if ROCKPOD_APPLE2026_IPOD` block in `gui_yesno_draw()` for non-touchscreen displays. Draws a `C6C6C8` horizontal separator hairline, then "Cancel" in `6E6E73` gray (left-aligned) and the confirm label in `FF2D55` accent red (right-aligned).
- Added `apple2026_shell.h` include (guarded).

**Rationale:** Stock text ("Confirm with SELECT") feels like a manual. Apple's dialogs show visually distinct Cancel/OK buttons.

### Status: COMPLETE

---

## R8: Remove "Rockbox" from Non-Root Header

**Goal:** Eliminate the "Rockbox" brand text that appeared in the non-root compact header for cs=0 (main menu state) and cs=21 (USB state).

**Changes:**
- `wps/Apple2026.sbs`: Both `title` and `titlewide` viewports: `%?cs<Rockbox|...|Rockbox>` → `%?cs<|...|>` — cs=0 and cs=21 now show empty string.

**Rationale:** "Rockbox" in the Apple2026 shell completely breaks the illusion. cs=0 at non-root is a rare edge-case; cs=21 (USB) is handled by the SBS usbBackdrop already.

### Status: COMPLETE

---

## R9: Volume Overlay Improvement

**Goal:** Clean up the volume bar styling to match the progress bar — same pill style, same color tokens.

**Changes:**
- `wps/Apple2026.sbs`: Volume bar `%pv` changed from 4px to 5px height; fill from `6E6E73` to `3C3C43`; track already `E5E5EA`.
- `wps/Apple2026.wps`: Volume bar `%pv(...vb.bmp,backdrop,vbd)` → `%pv(58,6,204,5,noborder)`; viewport colors set to `%Vf(3C3C43)` / `%Vb(E5E5EA)`. Removed `vbd` preload (vb_backdrop.bmp no longer needed).

### Status: COMPLETE

---

## R10: Scrollbar Slim + Recolor

**Issues observed from user-supplied screenshots (Sim Screenshots/1–4.JPG):**
1. Only 4 menu rows visible — row height 38px is too tall for 240px screen
2. Bottom bar (36px) rendering when stopped with no track loaded at all
3. "Settings" compact header title clipped at top within 26px header band
4. PictureFlow "No albums found" splash shows stock neon-green `PictureFlow` logo

### Changes

**`apps/gui/list.c`**
- `list_init_item_height`: reduced Apple2026 row floor from `38` to `32`
- Yields ~5–6 visible rows in the content zone (was 4); matches Apple Music density

**`wps/Apple2026.sbs`**
- Header band: increased from 26px to 28px (`%V(0,0,-,28,-)`)
- Title viewports: `y` shifted from `5` to `6`; minor icon y adjustments (+1px) for lock, sleep, busy indicators, batterytext
- Shell routing: added `%?fn<>` guard so stopped-bar only renders when a track is actually loaded (`%fn` = filename, true only when something is queued)
- Added `main_full` / `main_full_lt` viewports (full-height content, used when nothing is loaded — no bottom bar reservation)
- Content viewports `mainlarge`, `main` shifted from `y=27` to `y=29` to stay below taller header
- Routing comment updated

**`apps/plugins/pictureflow/pictureflow.c`**
- `draw_splashscreen()`: replaced external `SPLASH_BMP` logo load with simple centered "Cover Flow" text using `pf_fg_color` / `pf_bg_color` — eliminates stock neon-green Rockbox logo

### Verified
- SBS routing logic: `%?mp<playing|%?fn<stopped+loaded|stopped+empty>>` — correct for all 3 playback states
- `main_full` correctly uses `height = -` (fill to bottom, no reserve)
- Row height of 32px: with 20px SF Pro Regular body that's 6px top+bottom padding — comfortable, readable

### Status: COMPLETE

**Goal:** Make the scrollbar 3px wide (was 6px) and color it with A26 separator tone instead of default invert.

**Changes:**
- `apps/settings_list.c`: Added `#elif ROCKPOD_APPLE2026_IPOD` branch setting `scrollbar_width` default to `3`.
- `apps/gui/bitmap/list.c`: Added `#if ROCKPOD_APPLE2026_IPOD` block around `gui_scrollbar_draw()` that sets foreground and background to `A26_SHELL_RAIL` before drawing and restores after. This gives a calm monochrome C6C6C8 indicator bar instead of the harsh inverted Rockbox default.

### Status: COMPLETE
