# Update 1 Header Regression Forensics

Branch: `update-1` (working tree on top of `release` HEAD `12615b8883`)

---

## 1. Exact Symptom

The Apple2026 SBS-driven header (large "Library" title at root, compact
centered title on submenus, battery/lock indicators, mini-player bar) was
regressing to minimal stock Rockbox statusbar behavior on some or all
screens. This means the entire custom SBS either failed to load or was
being overridden by the fallback statusbar.

When the SBS fails to load:
- `sbs_loaded[screen]` stays `false`
- `sb_skin_get_info_vp()` returns NULL
- `viewport_set_defaults()` falls through to `viewport_set_fullscreen()`
- Lists draw from y=0, covering the full 240px height
- The stock `%wi` inbuilt statusbar renders (thin bar with tiny icons)

This matches "regressing to minimal Rockbox-default behavior."

---

## 2. Root Cause

**Skin buffer exhaustion caused by Adwaitapod-derived full-screen bitmap
preloads.**

### How Rockbox skin loading works

1. `skin_data_load()` obtains a workspace buffer from `plugin_get_buffer()`
2. The `.sbs` file is read into the front of this buffer
3. The remainder becomes the **skin buffer** (`skin_buffer_init()`)
4. All parsed tokens, viewports, conditional trees, AND decoded bitmap
   pixel data are allocated from this single flat buffer via
   `skin_buffer_alloc()`
5. `load_skin_bitmaps()` iterates every `%xl()` preload and decodes each
   BMP into the skin buffer at native LCD depth (16bpp for iPod)
6. If **any single** `skin_buffer_alloc()` fails (returns NULL because
   `size > skin_buffer_freespace()`), the bitmap load fails
7. `skin_data_load()` then calls `skin_data_reset()` and returns `false`
8. `skin_load()` falls back to the failsafe default SBS

### What the Adwaitapod-derived changes added

The update-1 working tree added lockscreen and quickscreen overlays to the
SBS, which required 10 new `%xl()` image preloads:

| Image | Dimensions | Decoded 16bpp | Purpose |
|-------|-----------|---------------|---------|
| **Wallpaper.bmp** | **320×240** | **153,600 bytes** | Lockscreen background |
| LockNotification.bmp | 288×70 | 40,320 bytes | Notification card |
| LockNotifPlay.bmp | 12×14×2 | 672 bytes | Play/pause badge |
| LockBatWarn.bmp | small | ~400 bytes | Low battery card |
| QSButtonActive.bmp | 130×36 | 9,360 bytes | QS button (active) |
| QSButtonInactive.bmp | 130×36 | 9,360 bytes | QS button (inactive) |
| QSArrowUp.bmp | small | ~400 bytes | QS arrow |
| QSArrowDown.bmp | small | ~400 bytes | QS arrow |
| QSArrowLeft.bmp | small | ~400 bytes | QS arrow |
| QSArrowRight.bmp | small | ~400 bytes | QS arrow |

**Total new decoded bitmap cost: ~215,312 bytes (~210 KB)**

The pre-existing SBS already consumed ~162 KB of decoded bitmap data
(dominated by the 320×240 usbBackdrop.bmp at 153,600 bytes).

Combined total with Wallpaper.bmp: **~377 KB** of decoded bitmap data
alone, before any token/viewport/conditional overhead.

This exceeded the available skin buffer and caused `load_skin_bitmaps()`
to fail. The SBS fell back to the default, producing the header
regression.

### Why Wallpaper.bmp was the tipping point

A single 320×240×24bpp BMP decodes to 153,600 bytes of 16bpp pixel data.
The pre-existing usbBackdrop.bmp was the same size but was already
budgeted into the working baseline. Adding a second full-screen image
(Wallpaper.bmp) roughly doubled the large-image cost and pushed the total
past the buffer limit.

---

## 3. How the Adwaitapod Merge Contributed

The Adwaitapod-derived features (lockscreen overlay, custom quickscreen,
hold-state AOD) are architecturally sound but were implemented using a
pattern that works on themes with smaller asset budgets. Adwaitapod's
own SBS is simpler (fewer base assets, smaller icon sheets) so it had
headroom for full-screen preloads. Apple2026's SBS was already asset-heavy
(the usbBackdrop.bmp alone is 153 KB decoded), leaving no room for a
second full-screen image.

The Adwaitapod features themselves are NOT the problem. The memory cost
of their bitmap implementation is.

### Features preserved (not thrown away)

- Homescreen lockscreen overlay (cs=1 + hold)
- Custom quickscreen overlay (cs=10)
- Lockscreen notification card with album art
- Quick screen pill buttons with active/inactive states
- QS volume bar, setting labels, and value display
- Theme defaults for QS item assignments
- `skin_update()` calls in quickscreen.c for SBS refresh
- `SKIN_TOKEN_LIST_TITLE_IS_ROOT` cold-start fix
- Dynamic row height fill-to-bottom
- All menu restructuring (Extras submenu, System folded into Settings)

---

## 4. Why Prior Attempts Likely Missed It

1. **Focused on rendering logic, not loading** — prior debugging traced
   header viewport selection, `%Lo` behavior, and conditional routing.
   The SBS conditional logic is correct. The problem was upstream: the
   SBS never finished loading in the first place.

2. **debugwps.err was stale** — the debug log was from a build BEFORE
   the new bitmap preloads were added (timestamp 11:49 PM vs binary at
   12:10 AM). It showed the simpler SBS loading successfully, which was
   misleading.

3. **Assets existed on disk** — all BMP files were present in both the
   source tree and the runtime install directory. The failure was not
   "file missing" but "buffer too small to hold decoded pixel data."

4. **The error is silent in non-debug builds** — `skin_buffer_alloc()`
   calls `skin_error(MEMORY_LIMIT_EXCEEDED)` which only produces output
   in debug/verbose builds. The DEBUGF message "Not enough skin buffer"
   only appears in DEBUG builds. Normal simulator builds may not show it.

5. **The symptom looks like a theme/routing bug** — when the SBS falls
   back to default, the visual result looks like a theme configuration
   error, not a memory problem. This led investigation toward
   conditionals, viewport definitions, and screen routing instead of the
   asset pipeline.

---

## 5. Exact Files / Systems Involved

### Direct cause
- `wps/Apple2026.sbs` — `%xl(K,Wallpaper.bmp,0,0)` preload (now removed)
- `lib/skin_parser/skin_buffer.c` — `skin_buffer_alloc()` returns NULL
- `apps/gui/skin_engine/skin_parser.c` — `load_skin_bitmaps()` returns
  false, `skin_data_load()` resets and falls back

### Affected downstream
- `apps/gui/statusbar-skinned.c` — `sbs_loaded` stays false
- `apps/gui/viewport.c` — `viewport_set_defaults()` returns fullscreen
- All list/menu screens — draw from y=0, obliterating header area

### Files changed in update-1 working tree (confirmed safe)
- `apps/gui/skin_engine/skin_tokens.c` — cold-start `%Lo` fix (correct)
- `apps/gui/statusbar-skinned.c` — debug logging only (simulator)
- `apps/gui/skin_engine/skin_engine.c` — debug logging only (simulator)
- `apps/gui/skin_engine/skin_parser.c` — debug logging + refactor (safe)
- `apps/gui/quickscreen.c` — `skin_update()` for QS overlay (correct)
- `apps/gui/list.c` — dynamic row height (correct)
- `apps/gui/usb_screen.c` — Apple2026 USB label styling (correct)
- `apps/root_menu.c` — Extras submenu + System removal (correct)
- `apps/menus/main_menu.c` — `file_exists()` guard (correct)
- `apps/onplay.c` — `file_exists()` guard (correct)
- `wps/WPSLIST` — QS defaults (correct)
- `wps/wpsbuild.pl` — QS config emission (correct)

---

## 6. What Was Fixed

### Primary fix (user-applied)
Removed `%xl(K,Wallpaper.bmp,0,0)` from the SBS preload list and
replaced the `home_lock_wallpaper` viewport content with a drawn white
rectangle: `%dr(0,0,-,-,FFFFFF)`. This saves 153,600 bytes of decoded
bitmap from the skin buffer while preserving identical visual output
(the lockscreen background is solid white).

The same change was applied to the WPS lockscreen.

### Estimated SBS bitmap budget after fix

| Category | Decoded bytes |
|----------|--------------|
| Pre-existing base assets | ~8,600 |
| usbBackdrop.bmp (320×240) | 153,600 |
| Lockscreen assets (no Wallpaper) | ~41,400 |
| Quickscreen assets | ~20,320 |
| **Total** | **~224,000 (~219 KB)** |

This is ~153 KB less than the broken state and should fit within the
skin buffer.

---

## 7. Anti-Regression Safeguards

### Rule: No full-screen bitmap preloads in the SBS

The SBS skin buffer must hold ALL decoded bitmaps simultaneously. A
single 320×240 16bpp image costs 153,600 bytes. The SBS already carries
one (usbBackdrop.bmp). Adding a second full-screen preload will exhaust
the buffer.

**Never add another `%xl()` preload for a 320×240 BMP in the SBS.**

Use `%dr()` (draw rectangle) for solid-color backgrounds instead.

### Rule: Monitor total preload budget

Before adding new `%xl()` preloads to the SBS, estimate the decoded
16bpp cost: `width × height × 2 bytes`. Keep the total well under
300 KB to leave headroom for token/viewport overhead.

### Rule: Test with debug builds after SBS changes

Build with `DEBUG_SKIN_ENGINE` or look for "Not enough skin buffer" in
debug output after any SBS asset changes. The `A26 skin_data_load fail=`
messages added in the update-1 working tree will also report bitmap/font
failures in simulator builds.

### Rule: Verify SBS loaded before concluding header bugs

If headers regress, first check whether the SBS loaded at all:
1. Look for `A26 skin_load ... loaded=1 fallback=0` in debug output
2. If `loaded=0` or `fallback=1`, the SBS failed to load — check assets
3. Only investigate rendering/routing if the SBS confirmed loaded

---

## 8. What to Check First in the Next Build

1. Rebuild simulator: `.\build-sim.ps1 -Incremental -SkipDep`
2. Run `.\tools\verify-sim-install.ps1`
3. Launch simulator
4. Verify: root menu shows "Library" large title (not stock statusbar)
5. Navigate to Settings — verify compact header with centered title
6. If music is playing, verify 44px mini-player bar at bottom
7. Engage hold — verify lockscreen overlay with white background
8. Open quickscreen — verify custom QS overlay

If headers still regress after the Wallpaper.bmp removal, the remaining
bitmap budget may still be too large. Next reduction targets in order:
1. Replace `usbBackdrop.bmp` preload with `%dr()` drawn rectangle
2. Replace QSButton bitmaps with `%dr()` drawn rectangles with text
3. Simplify LockNotification.bmp dimensions

---

## 9. Architectural Note

The Rockbox skin buffer model (single flat allocator, all-or-nothing
bitmap loading, no lazy/conditional preloading) is inherently fragile
for asset-heavy skins. The `Apple2026ArchitectureAudit.md` documents
this as a long-term limitation. For now, the mitigation is to keep the
SBS bitmap budget lean and use `%dr()` for large solid areas.
