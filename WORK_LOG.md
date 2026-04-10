# WORK_LOG.md

## 2026-04-09 — Typography hierarchy pass (18pt / 16pt two-tier system)

**Goal:** Establish a robust, context-aware typographic hierarchy across the entire Apple2026 shell.

**Final hierarchy:**

| Role | Font | Size |
|---|---|---|
| Large title ("Library") | SFProDisplay-Bold | 28px |
| Compact header ("Settings", etc.) | SFProText-Semibold | 16px |
| Standard list (menus, settings, DB categories) | SFProText-Regular | **18px** (was 20px) |
| Dense list (songs, track files, playlist viewer, Cover Flow) | SFProText-Regular | **16px** (new) |
| WPS song title | SFProText-Medium | 16px |
| Secondary metadata (artist/album/time) | SFProText-Regular | 14px |

**New architecture — `rockpod_list_font_tier`:**
- Two-tier enum (`NORMAL` / `DENSE`) declared in `root_menu.h`, defined in `root_menu.c`.
- `NORMAL` (18pt, 32px row floor): main menu, settings, database top-level, music artist folders.
- `DENSE` (16pt, 28px row floor): music album/track folders (dirlevel≥2), playlist viewer, Cover Flow tracklist.
- Tier set by `root_menu.c` at surface dispatch + by `tree.c` after each directory load.
- `apps/gui/list.c`: lazy-loads `16-SFProText-Regular.fnt` on first dense access; adjusts row floor per tier in `list_init_item_height`.
- `apps/gui/bitmap/list.c`: switches `lcd_setfont` around `list_draw` when tier is DENSE; restores after.
- `apps/plugins/pictureflow/pictureflow.c`: both tracklist and album-title fonts updated to `16-SFProText-Regular.fnt`.

**Font rebuild:**
- `16-SFProText-Regular.fnt` added to `tools/apple2026_rebuild_fonts_from_otf.py` JOBS.
- Run `python tools/apple2026_rebuild_fonts_from_otf.py` to generate.

**Files changed:**
- `wps/Apple2026.sbs` — slot 5: 20px → 18px Regular
- `apps/settings_list.c` — DEFAULT_FONTNAME: 20-SFProText-Regular → 18-SFProText-Regular
- `apps/root_menu.h` — `rockpod_list_font_tier_t` enum + extern declaration
- `apps/root_menu.c` — definition + setters at GO_TO_ROOT, GO_TO_MUSICLIB, GO_TO_DBBROWSER, GO_TO_PLAYLIST_VIEWER
- `apps/tree.c` — depth-based tier setter after each directory load
- `apps/gui/list.c` — dense font lazy-load + per-tier floor in `list_init_item_height`
- `apps/gui/bitmap/list.c` — `lcd_setfont` font switch around `list_draw`
- `apps/plugins/pictureflow/pictureflow.c` — 16pt for tracklist + album title
- `tools/apple2026_rebuild_fonts_from_otf.py` — added `16-SFProText-Regular.fnt`
- `DESIGN_SYSTEM.md` — §27.1 and §27.1.1 updated

**Build note:** Requires `python tools/apple2026_rebuild_fonts_from_otf.py` then full rebuild.

**Next:** Build + simulator verification. Screenshots of main menu, settings, music folder (track level), and Cover Flow to confirm hierarchy.

---

## 2026-04-09 (Mini-player bar: premature display fix)

### Root Cause Diagnosed
The bottom "What's Playing" bar was appearing before any song was played due to two compounding bugs in `wps/Apple2026.sbs`:

1. **`%mp` branch ordering was inverted** — The `%mp` skin tag is numeric (0=stop, 1=play, 2=pause). `%?mp<A|B>` with two branches selects A when stopped and B when playing — opposite of the SBS comment which described A as "playing/paused". The 44px mini-player (`%Vd(bottombarsmall)`) was in branch A, so it rendered during **stop** state, not play. The stopped-bar (`%?fn<bottombar|>`) was in branch B, so it rendered during **play** state.

2. **Stale `state->id3` made `%fn` always truthy after first play** — `state->id3` in `wps_state` is only cleared in `wps_state_init()` (called on WPS entry), never when audio stops. After any track played and stopped, `%fn` returned the last track filename (truthy), triggering the 36px stopped-bar on every subsequent cold screen — even before any new track was selected.

### Changed
- **`wps/Apple2026.sbs`** — **CRITICAL FIX (inverted branch logic):** Rewrote `%?mp` VI selection and bottom-bar routing lines to use correct 3-branch structure:
  - Branch 0 (stop): `main_full` viewport, no bottom bar
  - Branch 1 (play): `mainlarge` viewport, 44px mini-player
  - Branch 2 (pause): `mainlarge` viewport, 44px mini-player (paused state)
- **`wps/Apple2026.sbs`** — **CRITICAL FIX (stale-id3 gate removed):** Removed `%?fn<bottombar|>` stopped-bar logic entirely. The stopped state now always yields no bar, unconditionally. The `%fn` stale-id3 ghost is permanently eliminated.
- **`wps/Apple2026.sbs`** — **CLEANUP:** Removed dead `main`/`main_lt` (36px-reserved) viewports, `bottombar` (36px stopped-bar background), `albumart` (stopped-bar album art), `currenttrack` / `currenttrackshiftedleft` viewports — all now unreferenced.
- **`wps/Apple2026.sbs`** — Updated KEY BEHAVIOUR header and all routing comments to accurately describe corrected `%mp` branch semantics.

### Verified (static)
- `%?mp<|play|pause>` (line 50): branch 0 is empty (no bar when stopped), branches 1+2 render `%Vd(bottombarsmall)` + mini-player content.
- `%?mp<stop_full|play_large|pause_large>` (line 42): all three branches correctly route to `main_full_*` or `mainlarge_*` viewports.
- No `%fn` or stale id3 dependency remains in bottom-bar visibility path.
- `player_status_bottom` viewport remains defined but is orphaned (never `%Vd`'d); benign, no display effect.

### Behaviour Contract (post-fix)
| State | Bottom bar | Content viewport |
|---|---|---|
| Cold boot / stopped | None | `main_full` (full height) |
| Stopped after play | None | `main_full` (full height) |
| Playing | 44px mini-player | `mainlarge` |
| Paused (resumable) | 44px mini-player | `mainlarge` |
| FF / Rew | 44px mini-player | `mainlarge` (pause branch) |

### Next
- Install-only build to push SBS change to simdisk: `.\build-sim.ps1 -InstallOnly`
- Launch sim, verify cold screen has no bottom bar, confirm bar appears on play start.

---



### Changed
- **`wps/Apple2026.wps`** — **CRITICAL FIX:** Renamed 4 duplicate `%Vl(timeprogresslossless,...)` viewport labels to unique names (`pl_counter`, `elapsed_time`, `lossless_ind`, `remain_time`). All 4 labels were identical, causing the skin parser to match only the first and silently drop elapsed time, lossless indicator, and remaining time displays. Updated `%Vd` dispatch line to call all 4 by their new names.
- **`wps/Apple2026.wps`** — **ANTI-REGRESSION FIX:** Replaced `%x(ArtCorners,wpsArtCorners.bmp,0,0)` with `%xd(ArtCorners)` to comply with anti-regression contract rule #4 (preloaded images must be drawn via `%xd` only, not `%x` after `%xl`).
- **`wps/Apple2026.wps`** — **PARITY FIX:** Restored WPS artist color from `8E8E93` (secondary gray) to `FF2D55` (Apple red accent). DESIGN_SYSTEM specifies `#FF2D55` for active music artist emphasis on WPS; the gray value was inconsistent with the design contract and Interpod DNA.
- **`wps/Apple2026.wps`** — **NON-ASCII FIX:** Replaced 3 em-dash characters (U+2014) in WPS comments with ASCII hyphen-minus. Complies with anti-regression rule prohibiting non-ASCII in WPS files.
- **`apps/root_menu.c`** — **ICON FIX:** Replaced `Icon_Rockbox` with `Icon_Playlist` for the Cover Flow menu item. `Icon_Rockbox` rendered as the house logo, visually wrong for Cover Flow. `Icon_Playlist` is semantically closer (album/track list).
- **`apps/root_menu.c`** — **ICON FIX:** Replaced `Icon_Audio` with `Icon_Config` for the Database menu item. Database and Music were both showing the red music note (`Icon_Audio`), causing identical icons for two different functions on the root menu.
- **`wps/WPSLIST`** — **COMMENT FIX:** Updated Apple2026 comment to reflect actual SBS large-title viewport dimensions (`28px` SF Pro Display Bold, `30px` viewport band at `y=6`, list content at `y=40`) rather than stale "35px / 52px" from an earlier pass.

### Verified
- **`python tools/audit_apple2026_wps.py`** — exit 0, ALL CHECKS PASSED: non-ASCII (0), no duplicate image IDs, all `%xd` refs resolve, all 3 font slots present, all 15 BMP assets present, `%Cl` inside `%VB` viewport.
- Static: `pl_counter` / `elapsed_time` / `lossless_ind` / `remain_time` labels unique; `%Vd` dispatch references all 4.
- Static: `%xd(ArtCorners)` references the `%xl(ArtCorners,wpsArtCorners.bmp,...)` preload correctly.

### Next
- Build sim (incremental): confirm WPS elapsed + remaining times now render; confirm artist appears in Apple red; confirm Cover Flow and Database icons on root menu.
- Check: WPS volume bar still replaces time/progress when adjusting volume.
- Check: Lossless indicator appears only for lossless formats.

---

## 2026-04-09 (Build system / toolchain audit — second pass, deeper)

### Audit findings — second pass

Fresh skeptical audit of the full build pipeline, toolchain, and asset-sync chain.

**Newly confirmed root causes of slowness (concrete):**
1. `prepare_core_generated_headers()` runs `make -j1` on 10 targets **every incremental build**, even when all are up-to-date. On MSYS2/Windows, make process startup is expensive. Adds ~15-25 sec per build regardless of whether headers changed. Added a stamp to skip when sources haven't changed.
2. `make install` runs unconditionally on every incremental build. `wpsbuild.pl` copies all fonts + WPS + icons on every invocation even when nothing changed. On Windows NTFS this takes 30-60 sec. Resolved by `-InstallOnly` path and by `sync_all_fonts()` being fast (skips unchanged files).
3. `make dep` without `ROCKPOD_SKIP_DEP`: adds 30-60 sec when no headers changed.
4. 7,905 tracked text files have CRLF in working copy (stored LF in index). Each `make` run triggers git warnings for any source file touched. These are noise but cause confusion and slow down parsing of build output.
5. `rockpod-msys.ps1` buffers all output to a temp file and replays at end → builds look completely silent until done; Cursor terminal tracking shows `exit_code: unknown` because the shell session doesn't close.

**Newly confirmed fragility (concrete):**
1. `wpsbuild.pl` (called by `make install`) only copies `%Fl`-referenced fonts. Any font used by PictureFlow plugin, fallback WPS, or future skins is silently NOT copied. Root cause of 17 stale / 1 missing fonts found today.
2. `check_asset_freshness()` in `build-sim.sh` only checked 5 hardcoded fonts — missed the entire PictureFlow font set and any newly added fonts.
3. `verify-sim-install.ps1` staleness check used `rockboxui.exe` mtime as reference, but the binary is built BEFORE `make install` — fonts installed by the same build would always appear "newer than binary" and trigger false [WARN] spam.
4. `22-SFProText-Medium.fnt` was completely absent from runtime — not referenced by any `%Fl` directive, never copied by `wpsbuild.pl`. No automated check caught it.

**Runtime state at start of this session:**
- 17 of 18 repo fonts: STALE (fonts regenerated at 23:02 but `make install` not re-run)
- `22-SFProText-Medium.fnt`: MISSING from runtime
- Apple2026.sbs/.wps: current (manually synced timestamps matched)
- config.cfg font: correct (`20-SFProText-Regular.fnt`)

### Changed
- **`build-sim.sh`**:
  - `check_asset_freshness()` expanded from 5 to 18 fonts (full Apple2026 JOBS list + all size variants)
  - Added `sync_all_fonts()` — copies all `fonts/*.fnt` from repo to runtime after `make install`, filling the `wpsbuild.pl` gap; runs on every build and install-only path
  - Added `--install-only` / `ROCKPOD_INSTALL_ONLY=1` mode: skips configure/dep/compile; runs `make install` + `sync_all_fonts()` + `check_asset_freshness()` only (~30-40 sec vs 2+ min)
  - Added `.rockpod_install_stamp` touch after successful `make install` (used by verify script for accurate staleness reference)
  - Added `.rockpod_headers_stamp` to skip `prepare_core_generated_headers()` when lang/firmware/export sources haven't changed (saves ~15-25 sec per incremental build when headers are current)
- **`build-sim.ps1`** — added `-InstallOnly` switch (passes `ROCKPOD_INSTALL_ONLY=1` to `build-sim.sh`)
- **`rockpod.ps1`** — added `-InstallOnly` to `sim` command; updated help text
- **`tools/verify-sim-install.ps1`**:
  - Added `22-SFProText-Medium.fnt`, `18-SFProText-Regular.fnt`, `19-SFProText-Medium.fnt` to required checks
  - Staleness check now uses `.rockpod_install_stamp` as reference time (falls back to binary mtime when stamp absent)
  - Fixed PowerShell strict mode issue (`$staleFonts.Count` on non-array result)
- **`BUILD.md`** — updated env vars table (`ROCKPOD_INSTALL_ONLY`), fast iteration section, fast install-only section, font-regen workflow, common issues table; added install stamp explanation
- **`build-sim/simdisk/.rockbox/fonts/`** — manually synced 13 stale + 1 missing font from repo (13-SFCompactText-Regular, 15-SFProText-Medium/Semibold, 17-SFProText-Bold, 18-SFProText-Regular, 19-Inter-V-padded, 19-SFProText-Medium/Semibold, 22-SFCompactDisplay-Semibold, 22-SFProText-Medium [was missing], 22-SFProText-Regular, 25-SFProDisplay-Bold, 35-SFProDisplay-Bold)

### Verified
- `.\tools\verify-sim-install.ps1` → **Result: OK** — all 17 required assets [ok], all repo fonts current with last install stamp, Apple2026.sbs runtime current
- `.\build-sim.ps1 -InstallOnly` runs in ~37 sec (vs 125 sec full incremental build)

### Next
- After any C source changes: `.\build-sim.ps1 -Incremental -SkipDep`
- After font/WPS/icon-only changes: `.\build-sim.ps1 -InstallOnly` (fastest path)
- After running `tools/apple2026_rebuild_fonts_from_otf.py`: always follow with `.\build-sim.ps1 -InstallOnly`
- CRLF warning flood: still present (7,905 files have CRLF in working copy). Not blocking, but consider a `.gitattributes` normalization pass if it becomes unmanageable.

---

## 2026-04-08 (Picture Flow — album/artist + tracklist font sizes)

### Changed
- **`fonts/18-SFProText-Regular.fnt`** — from **`SF-Pro-Text-Regular.otf`** (`tools/otf_to_rb12_fnt.py`, track **0.40**); **`tools/apple2026_rebuild_fonts_from_otf.py`** JOBS updated.
- **`apps/plugins/pictureflow/pictureflow.c`** — tracklist **`18-SFProText-Regular.fnt`**; album/artist **`19-SFProText-Medium.fnt`** (slightly larger than tracks); **`pf_album_block_px`** trailing gap **+6 → +3** for less padding above the tracklist.

### Verified
- **`fonts/APPLE2026_FONT_ANALYSIS.md`** regenerated.

---

## 2026-04-09 (Apple2026 UX — Music Left: path match, not dirlevel)

### Changed
- **`apps/tree.c`** — Left at **Music** library root: **`paths_same_directory(tc.currdir, tc.browse->root)`** with **`browse->root`** under **`/Music`**, so **`GO_TO_ROOT`** runs before **`ft_exit()`**. **`ft_exit()`** strips **`/Music/`** to **`/`** (`filetree.c` when the last segment is removed). Prior **`dirlevel == 0`** never matched (**`set_current_file("/Music/")`** yields **`dirlevel == 1`**); **`dirlevel`** alone can also desync from **`currdir`**.
- **`DESIGN_SYSTEM.md`** — §**21A** Left behavior: path equality, not **`dirlevel`**.

### Next
- Sim: **Music** → list at **`/Music/`** → **Left** → main menu (no raw **`/`**).

---

## 2026-04-09 (Apple2026 — Music Left audit: library-only anchor)

### Audit
- **`ft_exit()`** (`filetree.c`): from **`/Music/`**, **`i==1`** sets **`currdir`** to **`/`** — confirms intercept-before-**`ft_exit()`** for **`/Music/`** only.
- **Regression fixed:** **`browse->root`** prefix **`/Music`** was too broad — **`/Music/Artist/`** (resume **`last_music_folder`**) must **not** **`GO_TO_ROOT`** on first Left; use **`path_is_curated_music_library_root()`** (exact **`/Music`** after trailing-slash trim).
- **`Icon_Audio` unsuitable:** enum value **0** matches default-zero **`browse_context.icon`** in many callers — use **`BROWSE_APPLE2026_MUSICLIB`** in **`tree.h`** / **`root_menu.c`** instead.

### Changed
- **`apps/tree.h`**, **`apps/root_menu.c`**, **`apps/tree.c`** — explicit browse flag for main-menu Music; Apple2026 Left guard uses **`path_is_curated_music_library_root()`** + **`paths_same_directory`**.
- **`DESIGN_SYSTEM.md`** — §**21A** resume vs default **`/Music/`** + flag vs Storage.

---

## 2026-04-09 (Music page first-open blank-top gap fix)

### Changed
- **`apps/gui/list.c`** — `list_display_title()` now returns `false` for `ROCKPOD_APPLE2026_IPOD`, so Apple2026 never reserves an in-list title row. SBS/large-title remains the only title system.

### Why
- First entry into Music could temporarily reserve a hidden title line (top blank area), showing 5 rows instead of 6 until navigation refreshed title handoff state.

### Next
- Sim verify: open Music from root first time now shows full row count immediately; back/forward no layout jump.

---

## 2026-04-08 (Wave3_V3 — Apple2026 shell density + Cover Flow typography/tracklist)

### Changed
- **`apps/gui/list.c`** — **`ROCKPOD_APPLE2026_IPOD`** row floor **35px** (was 52px target).
- **`wps/Apple2026.sbs`** — list **slot 5** **`20-SFProText-Regular.fnt`**; large-title band **52px**; **`main_lt` / `mainlarge_lt`** start **y=56**; volume strip viewports moved up (**`-32`/`-30`/`-35`**).
- **`wps/WPSLIST`**, **`apps/settings_list.c`** — default list font **`20-SFProText-Regular.fnt`**.
- **`fonts/20-SFProText-Regular.fnt`** — built via **`tools/apple2026_rebuild_fonts_from_otf.py`** / **`otf_to_rb12_fnt.py`** (same pipeline as 22pt Regular).
- **`apps/plugins/pictureflow/pictureflow.c`** — load **`18-SFProText-Regular`** (tracklist) + **`19-SFProText-Medium`** (album/artist); **`track_list_yh`** uses **`pf_album_block_px`**; **`show_track_list`** uses **`list_row_h`** + compact track font; **`draw_album_text`** uses title font + restore **`FONT_UI`**.
- **`DESIGN_SYSTEM.md`** — list font / row floor text synced.

### Verified
- Static: Picture Flow **`font_load`** paths match shipped **`fonts/*.fnt`** names; **`Apple2026.wps`** not edited (density pass = SBS + list + plugin).

### Next
- Sim (`BUILD.md`): Library ≥4 rows, submenu 5, volume position, CF titles smaller, tracklist ≥6 lines; screenshot **`build-sim/runtime_captures`**.

---

## 2026-04-09 (Apple2026 UX — CF idle → home; Music root back; no / junk)

### Changed
- **`apps/root_menu.c`** — **`pictureflow_scrn`:** **`PLUGIN_OK`** → **`GO_TO_ROOT`** (idle Cover Flow back always **main menu**, not **`GO_TO_PREVIOUS`** / WPS).
- **`apps/tree.c`** — **5 / 71:** **`ACTION_STD_CANCEL`** at **`/Music`** or **`/Music/`** → **`GO_TO_ROOT`** (curated library root; no fall-through to raw **`/`**).
- **`DESIGN_SYSTEM.md`** — §**21A** + Cover Flow stack note.

### Verified
- Static: **`PLUGIN_OK`** is **`0`**; matches **`case PLUGIN_OK`**. Music root path matches **`root_menu.c`** **`/Music/`** browse.

### Next
- Sim: CF from WPS → idle → back → **main menu**; Music → artists → back → back → **main menu** (no **/** junk).

---

## 2026-04-09 (Apple2026 — full-bleed list selector + dividers)

### Changed
- **`wps/Apple2026.sbs`** — **`%Vi(main*)`** viewports use **full LCD width** (`x=0`, default width) so the grey **selector bar** and **list separator** lines span edge-to-edge.
- **`apps/gui/bitmap/list.c`** — **`A26_LIST_CONTENT_INSET` (16px)** added to row `indent` on **`ROCKPOD_APPLE2026_IPOD`** so icons/labels stay aligned with the **Library** large-title margin; **disabled** icon-column separator masking so hairlines reach the **right edge**.
- **`apps/apple2026_shell.h`** — **`A26_LIST_CONTENT_INSET`**.
- **`wps/WPSLIST`** — comment updated.

### Verified
- Logic: `line.c` selector/`separator` use viewport `getwidth()`; full-width `%Vi` widens that region; chevrons still use `vp_w - 10` from the right.

### Next
- Sim: confirm scrollbar + inset still look correct.

---

## 2026-04-09 (Wave 4 — WPS chord contract: MENU short = browse back, long PLAY = quickscreen)

### Changed
- **`apps/gui/wps.c`** — `wps_handle_browse_parent()` shared by **`ACTION_WPS_BROWSE`**; removed long-**PLAY** → Picture Flow; **`ACTION_WPS_MENU`** = main menu only (repeat); party mode blocks **`ACTION_WPS_QUICKSCREEN`** like other overlays.
- **`apps/keymaps/keymap-ipod.c`** — **MENU short** → `ACTION_WPS_BROWSE`; **MENU repeat** → `ACTION_WPS_MENU` (home); **PLAY repeat** → `ACTION_WPS_QUICKSCREEN` (replaces `ACTION_WPS_STOP`); main + remote WPS tables and header comment.
- **`DESIGN_SYSTEM.md`** — §**21A** + WPS matrix row updated for Apple2026 WPS controls.

### Verified
- Static review; sim build per **`BUILD.md`** when convenient.

### Next
- Device/sim: MENU short vs MENU long; long PLAY opens quickscreen; wheel still volume; tree **PLAY repeat** still **`ACTION_TREE_STOP`** (non-WPS).

---

## 2026-04-08 (Wave 4 UX — context stack: WPS return + playlists + PF tracklist)

### Changed
- **`apps/settings.h`** — `PLAYBACK_SOURCE_PLAYLIST_VIEWER` for queue / playlist viewer starts.
- **`apps/tree.c`** — `SHOW_M3U` (playlist catalog) sets `PLAYBACK_SOURCE_PLAYLIST_BROWSER` when starting playback from the tree.
- **`apps/gui/wps.c`** — `ACTION_WPS_BROWSE`: full `playback_source` switch (PF, DB, Music, files, playlists, playlist viewer) before `wps_select_action`.
- **`apps/playlist_viewer.c`** — `playback_source_set(PLAYBACK_SOURCE_PLAYLIST_VIEWER)` on `playlist_start` from viewer / search.
- **`apps/plugins/pictureflow/pictureflow.c`** — resume from WPS with PF source + active audio opens **tracklist** via `skip_animation_to_show_tracks()`.
- **`DESIGN_SYSTEM.md`** — §21A updated for the Apple2026 context-stack contract.

### Verified
- Static review only in this session; full sim build per **`BUILD.md`** (MSYS) recommended.

### Next
- Simulator: DB → WPS → SELECT returns to database; Files outside `/Music` → SELECT returns to previous file tree; playlist catalog → Playlists; queue start → SELECT returns to playlist viewer; PF → WPS → SELECT lands on tracklist.

---

## 2026-04-08 (UI audit + polish — DESIGN_SYSTEM sync, shell chrome, Cover Flow selector)

### Changed
- **`DESIGN_SYSTEM.md`** — Reconciled §**27.1**, §**27.1.1**, §**54.1**, §**54.3**, §**54.4**, §**54.6**, §**54.7** with **live Figma `1:4008`** (via MCP) and current tree: **22-SFProText-Regular**, **52px** row floor, **30×30** tiles, **`ICON_PADDING 4`**, **16/56** large-title band, list **y=60**, selector **E5E5EA**, WPS coordinates from **`wps/Apple2026.wps`**.
- **`wps/Apple2026.sbs`** — Removed header **`player_status`** strip (playback state remains **mini-player** / bottom bar only; less stock-Rockbox header noise).
- **`apps/plugins/pictureflow/pictureflow.c`** — **`draw_gradient`** selection fill **D0D0D4 → E5E5EA** to match shell list selector.

### Verified
- **Figma MCP `get_design_context`** (`JyDHVsT9bqCPjbGEfyUD8d`, `1:4008`): **52px** rows, **16px** inset, **29px** icon cell, **22px Regular** labels, disclosure/chevron tertiary styling.
- Static: **`%xl(P,…)`** still used by **`player_status_bottom`** in SBS.

### Docs
- This entry; **`DESIGN_SYSTEM.md`** as contract update (no duplicate build steps).

### Next
- Simulator: confirm root Library (no double playback glyph), Cover Flow tracklist selection vs main menu selector, stopped vs playing bottom bar.

---

## 2026-04-08 (Library shell parity — verify + sync assets, no churn on good bits)

### Changed
- **`tools/apple2026_symbol_assets.py`** — ran **`python tools/apple2026_symbol_assets.py --supersample 2`** so **`icons/Apple2026Icons.bmp`** matches **30×30** tiles already in code (was stale vs earlier edit).
- **`apps/menus/theme_menu.c`** — **`reset_color()`** on iPod Video/Classic sets **lss/lse** to **E5E5EA** to match **WPSLIST** selector (was generic **`LCD_DEFAULT_LS`** / **`LCD_DEFAULT_BG`**).

### Verified
- **`fonts/22-SFProText-Regular.fnt`** present; list font + **16px** SBS **`%Vi`** inset + **52px** row floor left as-is.
- Font analysis refreshed via **`tools/analyze_rb12_fonts.py`**.

### Next
- Simulator: confirm Library list + icons after theme reload or **`Reset theme colors`** if testing reset path.

---

## 2026-04-08 (Font + symbol regeneration pipeline — analysis + OTF rebuild + supersampled icons)

### Changed
- **`tools/rb12_metrics.py`** — shared RB12 parser + ink/digit metrics for tooling.
- **`tools/analyze_rb12_fonts.py`** — scans `fonts/*.fnt`, writes **`fonts/APPLE2026_FONT_ANALYSIS.md`** (height, ascent, digit span, ink samples).
- **`tools/apple2026_rebuild_fonts_from_otf.py`** — rebuilds Apple2026 SF **`fonts/*.fnt`** from **`Apple Fonts/SF Pro`** and **`Apple Fonts/SF Compact`** via **`tools/otf_to_rb12_fnt.py`** with per-face **`--track`** / **`--space-extra`** (Inter donor fonts unchanged).
- **`tools/apple2026_symbol_assets.py`** — internal **`supersample` (default 2×)** raster before final resize for sharper glyphs; **`--supersample`**, **`--analyze`** CLI; regenerated **`icons/Apple2026Icons.bmp`** and **`wps/Apple2026/*.bmp`**.
- **`Apple Fonts/README.txt`** — documents rebuild + symbol commands.

### Verified
- `python tools/apple2026_rebuild_fonts_from_otf.py` — **14** SF `.fnt` rebuilt (OTFs present).
- `python tools/analyze_rb12_fonts.py` — report written.
- `python tools/apple2026_symbol_assets.py --supersample 2 --analyze` — exit **0**; per-tile ink stats printed.

### Next
- On-menu visual check after firmware picks up new **`22-SFProText-Medium.fnt`** (line height now **27** px font box vs prior build).

---

## 2026-04-08 (Wave3_Overhaul — aggressive Apple Music shell + WPS layout)

### Changed
- **Branch:** `Wave3_Overhaul`.
- **`apps/gui/list.c`** — Apple2026 row floor **`34 → 48`** px (closer to DESIGN_SYSTEM library rhythm on 320px-wide UI).
- **`apps/gui/bitmap/list.c`** — **`ICON_PADDING 12 → 15`**; chevron **`4×9 → 5×10`**, right inset **`8 → 10`**.
- **`tools/apple2026_symbol_assets.py`** — menu tiles **`34×30 → 38×34`**, glyph **`scale 1.0 → 1.06`**; regenerated **`icons/Apple2026Icons.bmp`** and **`wps/Apple2026/*.bmp`**.
- **`wps/Apple2026.sbs`** — large-title band **`y=14,h=46 → y=4,h=56`** (stronger top anchor; list still starts **`y=60`**).
- **`wps/Apple2026.wps`** — title **left** + playlist **right** on one row; **19pt** red artist, **16pt** album; progress/time nudged to **y=224/228**; font slots **10/11** for artist/album.
- **`wps/WPSLIST`** — comments aligned to new row/icon tokens.
- **`DESIGN_SYSTEM.md`** — §27 / §54.3 / §54.4 tokens (48px rows, 68px icon column, chevron, visible-row notes).

### Verified
- `python tools/apple2026_symbol_assets.py` exit **0**.
- **Not run:** `make` / simulator (run per **BUILD.md** on MSYS).

### Next
- Simulator: main menu density, icon crispness, Library title, WPS title/counter/artist hierarchy, album art with embedded covers.

---

## 2026-04-08 (Apple UI polish — list rhythm, SF Pro stack, tracking, hairlines)

### Changed
- **`apps/gui/list.c`** — Apple2026 row floor **`30 → 34`** px (Music-like vertical spacing).
- **`apps/gui/bitmap/list.c`** — **`ICON_PADDING 10 → 12`**; disclosure chevron inset **`6 → 8`** px from viewport right.
- **`apps/settings_list.c`** — default list font **`22-SFProText-Medium`**, default separator **`#C7C7CC`** (iOS hairline).
- **`apps/menus/theme_menu.c`** — reset path separator color aligned to **C7C7CC**.
- **`wps/WPSLIST`**, **`wps/Apple2026.sbs`**, **`wps/Apple2026.wps`** — list font + SBS/WPS slots use **SF Pro Text**; **`list separator height: 1`**, color **c7c7cc**.
- **`tools/otf_to_rb12_fnt.py`** — **`--track`** (global letter-spacing) and **`--space-extra`** (word spacing); regenerated key **`fonts/*.fnt`** with light **`--track`** (0.2 Display Bold, 0.25 Text).
- **`tools/apple2026_font_prep.py`** — SF Pro Text **`sizes`** extended through **22**.
- **`DESIGN_SYSTEM.md`** — §27 / §54.3 tokens (34px rows, 12px icon padding, 58px icon column, chevron inset).

### Notes
- TrueType **pair kerning** (GPOS) is still **not** in Rockbox; advance + bearing + optional tracking approximates polish.

### Verified
- `python tools/otf_to_rb12_fnt.py … --track …` exit 0 for regenerated fonts.

---

## 2026-04-08 (35px Library title font — OTF raster, not `.fnt` upscale)

### Changed
- **`tools/otf_to_rb12_fnt.py`** — FreeType-based RB12 `.fnt` generator from OTF/TTF (same packing idea as `convttf`; no bitmap scaling of an existing `.fnt`).
- **`fonts/35-SFProDisplay-Bold.fnt`** — regenerated from **`Apple Fonts/SF Pro/SF-Pro-Display-Bold.otf`** (`python tools/otf_to_rb12_fnt.py … -p 35`).
- **`tools/scale_rb12_fnt.py`** — removed (upscaling path deprecated).
- **`wps/Apple2026.sbs`**, **`DESIGN_SYSTEM.md`** — docs now reference `otf_to_rb12_fnt.py` / official SF Pro source.
- **`tools/apple2026_font_prep.py`** — SF Pro Display `sizes` extended to **35** for future `convttf` batch runs.
- **`Apple Fonts/README.txt`** — clarifies SF Pro is **vendored in-repo** under `Apple Fonts/SF Pro/`; Apple’s fonts page is reference for license/updates.

### Verified
- `python tools/otf_to_rb12_fnt.py …` exit 0; header reports `h=43`, `ascent=34`, `maxw=34`.

### Next
- Optional: run **`tools/apple2026_font_prep.py`** when MSYS `convttf` + full OTF set are available to align naming with the rest of the font matrix.

---

## 2026-04-08 (Apple2026 strict correction pass — shell + WPS + Music path + menu IA)

### Changed
- **`apps/root_menu.c`**
  - **Music → `/Music/`** (trailing slash): `set_current_file("/Music")` was parsed as file `Music` in `/` (root browse), not the library folder — fixed default + hotswap fallback to **`/Music/`**.
  - **Root menu (MODEL 5 / 71):** removed **Plugins** and **Shortcuts** entries from `menu_table` (still available under Settings / stock paths on other targets).
- **`wps/Apple2026.wps`**
  - Rebuilt toward Interpod-style stack: **album art `%Cd` on main layer** after documenting root cause (full-screen main `%Vb` was painting over backdrop art).
  - **Backdrop `%VB`:** flat `wpsBackdrop` only (no art in buffer).
  - **Metadata:** title, **centred playlist counter** under title, **artist `FF2D55`** (slot 10 `16-SFProText-Medium.fnt`), **album** grey on its own line; progress/time re-anchored to fit 240px height.
- **`wps/Apple2026.sbs`**
  - **Library** band: `y=18`, `h=40`; list `%Vi` `_lt` start **`y=58`**; slot 5 → **`22-SFCompactDisplay-Semibold.fnt`**; root battery text/icon nudged to match band.
- **`wps/WPSLIST`**, **`apps/settings_list.c`**
  - Default menu font **`22-SFCompactDisplay-Semibold.fnt`** (was `20-Inter-SemiBold`).
- **`apps/gui/list.c`**, **`apps/gui/bitmap/list.c`**
  - Row floor **`30px`**; **`ICON_PADDING 10`** (was 26 / 7).
- **`tools/apple2026_symbol_assets.py`** + regenerated outputs
  - Menu tiles **`34×30`**, scale **`1.0`**; **battery** strip redrawn (28×15 frames, slim capsule, green/orange/red fill levels).
- **`DESIGN_SYSTEM.md`**
  - §21A (`/Music/` + root menu IA), §27.1 / §27.1.1 (typography), §54.1 / §54.2 / §54.3 (geometry, battery, list/icon tokens).

### Verified
- `python tools/apple2026_symbol_assets.py` completed; `icons/Apple2026Icons.bmp` and `wps/Apple2026/*.bmp` regenerated.
- Static review: WPS draw order (shell fill → `%Cd` → frame); `tree.c` `set_current_file` path parsing for `/Music/` vs `/Music`.
- **Not run:** simulator / `make` (MSYS toolchain not invoked in this Windows session).

### Docs
- This entry; **`DESIGN_SYSTEM.md`** updates above.

### Next
- Simulator: main menu density, Library title position, **Music opens `/Music` folder**, WPS album art visible, battery glyph, metadata colours.
- Users with **`root_menu` cfg** listing `plugins` / `shortcuts`: tokens ignored until they reset menu or edit cfg.

---

## 2026-04-08 (Apple2026 focused correction/polish pass — WPS, menu shell, icons, typography)

### Changed
- **`wps/Apple2026.wps`**
  - Restored first-frame album-art draw path by removing `%VB` from the art viewport so real art renders directly in the main layer.
  - Tightened metadata stack and moved secondary metadata upward (`y=190`) with larger secondary font slot (`14-SFProText-Regular.fnt`).
  - Moved track number to right side on the same metadata line, same size and gray tone.
  - Replaced bitmap-backed progress rail with flat `noborder` rail (`E5E5EA` base / `6E6E73` fill) to remove right-edge artifact and match volume style.
  - Rebuilt WPS volume overlay rail to the same flat slider language and thickness family as progress.
- **`tools/apple2026_symbol_assets.py` + regenerated assets**
  - Upscaled menu icon tiles to `30x26`, increased glyph scale to `0.96`, reduced inner padding for sharper detail.
  - Kept symbol set coherent but strengthened Settings/System semantics (`gear`, `wrench.fill`) with larger render footprint.
  - Reduced album frame/placeholder radius from `10` to `6` for subtler corners.
  - Regenerated `icons/Apple2026Icons.bmp` and all `wps/Apple2026/*.bmp`.
- **`wps/Apple2026.sbs`**
  - Removed header/list divider line feel (no top hairline bars; no large-title separator line).
  - Removed list viewport cropping by expanding list viewports to full width and full vertical continuation under bottom shell.
  - Moved active playback indicator from top-left to bottom-right mini-player lane (`player_status_bottom`).
  - Added root-specific battery icon/text lanes aligned with `Library` large-title band.
  - Updated SBS volume rail to flat neutral style that visually matches WPS progress rail.
- **`wps/WPSLIST`**
  - Increased Apple2026 default list font to `20-Inter-SemiBold.fnt` for +1/+2px readability push.
  - Lightened selector color (`DADAE0`) and removed menu separators (`list separator height: 0`).
  - Updated Apple2026 icon strip documentation comment to `30x26`.
- **`apps/gui/bitmap/list.c`**
  - Increased icon padding `6 -> 7` to rebalance spacing around larger icons.
- **`apps/gui/list.c`**
  - Raised Apple2026 iPod list row minimum `25 -> 26` to preserve rhythm with larger icons/type.
- **`apps/settings_list.c`**
  - Changed iPod Video/Classic default font to `20-Inter-SemiBold`.

### Verified
- Lint diagnostics: clean on touched files.
- Asset generation: `python tools/apple2026_symbol_assets.py` completed successfully; all expected outputs regenerated.
- Static intent checks:
  - WPS now uses direct album-art drawing path (no `%VB` on art viewport).
  - Progress/volume rails now share flat neutral visual language.
  - Menu separators disabled from theme defaults.
  - Selector token lightened.
  - Playback indicator moved to bottom-right in active mini-player state.

### Docs
- This entry.

### Next
- Run simulator build/check after this full pass.
- Validate target screens:
  - WPS art visibility + progress right-edge artifact removal,
  - metadata/track-number alignment,
  - icon sharpness/scale (Settings/System),
  - full-width lighter selector,
  - no list/header separators,
  - bottom-right play/pause indicator in active lower tab shell.

---

## 2026-04-08 (Wave 4 — Navigation: playback source + Cover Flow back chain)

### Changed
- **`apps/settings.h`:** `enum playback_source` + `global_status.playback_source`; `playback_source_set()`.
- **`apps/root_menu.c`:** `GO_TO_PICTUREFLOW` updates `previous_browser` like other browsers; `playback_source_set()` implementation.
- **`apps/tree.c`:** On `ONPLAY_START_PLAY`, set source to **database** / **Music (`/Music`)** / **files** (iPod 5 / 71 path check).
- **`apps/gui/wps.c`:** WPS **SELECT** → **`GO_TO_PICTUREFLOW`** when `playback_source == PICTUREFLOW` (5 / 71 + tagcache).
- **`apps/plugins/pictureflow/pictureflow.c`:** Set `playback_source` to PictureFlow after `playlist_start` in `start_playback`; **idle/scrolling `PF_BACK`** returns **`PLUGIN_OK`** (exit to main menu) instead of **`PLUGIN_GOTO_WPS`**.

### Verified
- Lint: clean on touched files.
- Build: `build-sim` reported nothing to rebuild in this environment; run full incremental sim build per `BUILD.md` when MSYS `make` picks up changes.

### Docs
- `DESIGN_SYSTEM.md` §21A (this entry).

### Next
- Simulator: CF → track → WPS → SELECT → CF; CF idle Left → main menu; WPS MENU → home; Music → play → WPS → SELECT → `/Music` when source not PF.

---

## 2026-04-08 (Wave 5b — Remove Storage row + hide Picard track index in lists)

### Changed
- **`apps/root_menu.c`:** Removed **Storage** menu item and `storage_browser` (full-disk browse not shown at root).
- **`apps/tree.c` (iPod Video / Classic only):** In the file browser list, **display-only** stripping of leading **`N.`** prefixes on audio files (Picard-style `1. Title.m4a` → show as `Title` with extension rules unchanged). Real filenames unchanged for playback.

### Verified
- Lint: clean on touched files.

### Docs
- `MASTER.md` Wave 5 bullet; this entry.

---

## 2026-04-08 (Wave 5 — Music Library IA / menu simplification)

### Changed
- **`apps/root_menu.h` / `apps/root_menu.c`:** Added `GO_TO_MUSICLIB` — file browser rooted at **`/Music`** with separate `last_music_folder` state, `Icon_Audio` in `browse_context`. Main menu: **Music** first, then Now Playing, Playlists, Cover Flow, **Database**, **Storage** (full FS), Plugins, Shortcuts, Settings, System. Replaced generic **Files** row with **Storage** label + `Icon_file_view_menu`. **`browser_default`** for `MODEL_NUMBER` 5 / 71 returns `GO_TO_MUSICLIB` for “previous browser” / default files browser.
- **`apps/gui/wps.c`:** WPS **SELECT** with “files” option (`wps_select_action` == 3) returns **`GO_TO_MUSICLIB`** on iPod Video/Classic (5 / 71) instead of `GO_TO_FILEBROWSER`.
- **`apps/settings_list.c`:** Default **`wps_select_action`** for 5 / 71: **3** (files) so default matches Music library path above.
- **`DESIGN_SYSTEM.md` §21A:** Documented WPS SELECT → `/Music` browse.
- **`MASTER.md`:** Wave 5 rewritten to match this IA pass (no flat Albums/Songs engine in this wave).

### Verified
- Not run: `make` not on PATH in this Windows shell; run `./rockpod.ps1 sim -Incremental` or `build-sim` + `make` per `BUILD.md` / `AGENTS.md`.

### Docs
- This entry; `MASTER.md` Wave 5; `DESIGN_SYSTEM.md` §21A.

### Next
- Simulator: main menu order, Music → artist folders under `/Music`, Storage → `/`, WPS SELECT → `/Music`, Database still reachable.
- Users with saved `root_menu` config may need to reset menu order or add `music` key to see new defaults.

---

## 2026-04-08 (Wave 3f — Header/title stack tune + inset separators + §54 token sync)

### SBS: Large title band (`wps/Apple2026.sbs`)
- Changed `large_title` viewport background from `F8F8F8` → `FFFFFF`.
  Matches list content background — eliminates the subtle color seam between
  the "Library" title area and the first list row.
- Added `%dr(0,31,-,1,DCDCE0)` at the bottom of the `large_title` viewport.
  Draws a 1px `DCDCE0` separator at screen y=58 (boundary between title band
  and first list row) — clean Apple Music-style visual break.
- Visual stack at root (playing on, large title on):
  ```
  y=0..23   F8F8F8 header chrome
  y=24      DCDCE0 hairline
  y=25      F4F4F4 soft hairline
  y=26      FFFFFF (screen bg, 1px gap)
  y=27..51  FFFFFF + "Library" text (25px SFPro Display Bold)
  y=52..57  FFFFFF (breathing room below text)
  y=58      DCDCE0 separator (bottom of large_title band)
  y=59+     FFFFFF list content
  ```

### list.c: Inset dividers (`apps/gui/bitmap/list.c`)
- In `_default_listdraw_fn`, after `put_line` draws each row (including the
  bottom hairline separator), added a "cover" rectangle at the icon-column
  position: `fillrect(0, y+line_h-1, icon_width, 1)` using the viewport
  background color.
- Effect: the 1px divider line is covered in the icon column (x=0..39 within
  viewport = x=0..55 from screen edge) and remains visible starting at x=40
  (= screen x=56, aligned with the text column).
- This creates Apple Music-style inset separators that begin at the text
  column, not at the left edge. Only runs on color LCD depth≥16 when icons
  are shown and `list_separator_height > 0`.

### DESIGN_SYSTEM.md §54 full sync
- **§54.1:** Rewrote to document Interpod adaptive viewport system. Added all
  `large_title` geometry tokens. Replaced old fixed absolute height tokens
  with `mainlarge`/`main`/`_lt` variants and their negative-height offsets.
  Added architecture constraint note tying `-12`/`-37` to strip/bar heights.
- **§54.1.1:** Rewrote routing table and vertical stack diagram to show actual
  Interpod-based SBS structure (two stacks: playing+LT and stopped+no-LT).
- **§54.3:** Updated `icon_tile_h` from `32` → `25`. Updated `row_h_firmware`
  to `25`. Added `divider_implementation = inset`. Updated all visible row
  counts for 25px rows and new Interpod viewport heights.
- **§54.4:** Added `chevron_cy_formula` and `chevron_cx_formula` for
  derivation transparency. Added selector color tokens.
- **§54.5:** Rewrote to document the Interpod adaptive two-state bottom bar
  (`bottombar` 36px / `bottombarsmall` 11px) and the constraint tying the
  `%Vi` negative offsets to bar heights.

### Verification needed
- [ ] Simulator: root screen shows "Library" in white band with clean separator above first row
- [ ] Root: no visible color seam between title area and list
- [ ] All sub-menu screens: dividers start at text column (after icon), not at left edge
- [ ] Selected row: icon area at separator row shows viewport bg (white) — minor edge case acceptable
- [ ] Non-root screens: header title visible, no large title band
- [ ] Bottom bar: 36px when stopped (art + title), 11px strip when playing

---

## 2026-04-07 (Wave 4 — Apple2026 UX flow: queue shortcut + WPS browse default)

### Changed
- **`apps/keymaps/keymap-ipod.c`:** Mapped `ACTION_WPS_VIEW_PLAYLIST` on **SELECT+MENU** (main WPS; chord listed first so it overrides single-button actions). Remote: **RC_SELECT+RC_MENU** when `BUTTON_REMOTE` is enabled. Comment documents ordering vs browse/menu/hotkey/quickscreen.
- **`apps/settings_list.c`:** For **`MODEL_NUMBER` 5 / 71** (iPod Video / Classic), default **`wps_select_action`** = **1 (database / tag browser)** so SELECT from WPS returns into the Music library by default; other targets unchanged (0 = previous screen).
- **`apps/root_menu.c`:** Comment only: documents **`GO_TO_PREVIOUS_MUSIC`** / **`previous_music`** / WPS vs FM.

### Verified
- Static: keymap chord ordering places `ACTION_WPS_VIEW_PLAYLIST` before `ACTION_WPS_BROWSE` and `ACTION_WPS_MENU` in `button_context_wps`.
- Build: not run in this session (no `make` on host PATH outside MSYS); run `./rockpod.ps1 sim -Incremental` or `build-hw-*` + `make` per `BUILD.md` / `AGENTS.md`.

### Docs
- `DESIGN_SYSTEM.md` — new **§21A Navigation contract (Apple2026)** (terminology, rules, matrix).

### Next
- Simulator: WPS → SELECT+MENU opens current playlist; Play exits viewer to WPS; SELECT from WPS lands in database with new default.
- Optional: user may change **WPS select action** in settings if they prefer previous browser / Cover Flow / files.

---

## 2026-04-08 (Wave 3e — Cover Flow track-tap playback bug fix)

### Bug: tapping a track in the Cover Flow track list did nothing visible

**Root cause 1 — `auto_wps` default:**
`pf_cfg.auto_wps` defaulted to `0` (OFF). In this mode, selecting a track in the
track list calls `start_playback(false)` which starts playback but keeps Cover Flow
on screen — the display does not change, so the user sees no feedback and assumes
nothing happened. The correct Apple Music-like behaviour is mode `2` (VIA_TRACK_LIST):
select track → play + navigate to WPS (Now Playing screen).
- **Fix:** Changed `cfg->auto_wps = 0` → `cfg->auto_wps = 2` in `pictureflow.c` line 772.

**Root cause 2 — `warnon_erase_dynplaylist` default:**
When music was already playing, `warn_on_pl_erase()` in `start_playback()` triggered a
YES/NO confirmation dialog ("Erase the dynamic playlist?") before allowing playback to
start. The user pressing BACK or NO silently cancelled everything — `start_playback`
returned false and Cover Flow stayed on screen with no indication of failure. In Apple
Music tapping a song just plays it; there is no confirmation dialog for replacing
the queue. Changed the default from `true` to `false` so the dialog is opt-in.
- **Fix:** Changed default of `warnon_erase_dynplaylist` in `settings_list.c` from `true` → `false`.

### Files changed
- `apps/plugins/pictureflow/pictureflow.c` — line 772: `auto_wps = 0` → `auto_wps = 2`
- `apps/settings_list.c` — `warnon_erase_dynplaylist` default: `true` → `false`

### Verification needed
- [ ] Open Cover Flow, navigate to an album, open track list, tap a track
- [ ] Should immediately start playback AND navigate to WPS (Now Playing screen)
- [ ] Should work whether or not music is already playing (no confirmation dialog)

---

## 2026-04-08 (Wave 3d — Full Interpod-first merge: SBS + WPS rebuilt from Interpod base)

### Strategy change
User confirmed: start from Interpod's PROVEN, POLISHED code and layer Apple2026 on top — do not
greenfield or diverge. Interpod was "almost perfect." The goal is Interpod PLUS Apple2026 visual
language, not a fresh build that mimics it imperfectly.

### Apple2026.sbs — rebuilt from Interpod Rev.17

Key structural adoption from Interpod:
- **Adaptive bottom bar** (most important): when playing/paused → thin 11px hairline strip at
  bottom (content area expands to 201px); when stopped → full 36px bar showing last-played art +
  track title (content area shrinks to 176px). This mirrors Interpod exactly.
- **Interpod VI routing pattern**: `%?mp<%VI(mainlarge)|%VI(main)>` with negative-height
  viewports (`-12` = 11px strip space, `-37` = 36px bar space). Robust to any screen size.
- **Volume bar in bottom bar zone**: Interpod's 3-part `volumebar` viewport system (speaker icon,
  `vb.bmp` textured fill bar, loud/clip indicator) copied verbatim. Color updated to F8F8F8.
- **Battery/busy/lock**: Interpod's exact positioned viewports kept unchanged.
- **`busyindicatorleft`/`busyindicator`**: Interpod's dual-position busy spinner (left when
  battery % shown, right otherwise) carried forward.

Apple2026 additions on top:
- `%Lo` large title routing: `%?mp<%?Lo<%VI(mainlarge_lt)|%VI(mainlarge)>|%?Lo<%VI(main_lt)|%VI(main)>>`
- Two extra `_lt` VI variants (start at y=59 instead of y=27 to make room for large title)
- `large_title` labeled viewport (y=27..58, 32px, slot 2: 25px SFPro Display Bold, "Library")
- Header title suppressed at root (`%?Lo<|...title logic...>`) — large title takes its place
- Colors: `ededed` → `F8F8F8` everywhere; hairlines `E3E3E3/F3F3F3` → `DCDCE0/F4F4F4`
- Left/right inset: Interpod's 2px → 16px (Apple-like list margins)
- Font slots: {3:15-Inter-Bold, 5:16-Inter-SemiBold} → {2:25-SFPro, 3:16-Inter-SemiBold, 5:19-Inter-V-padded}
- Mini-player track font: slot 5 (now 19px, too tall) → slot 3 (16px, fits 36px bar)
- `albumart` mini bg: `ebeeee` → `F0F0F0`
- `volumebar_small_clip` color: `ED230D` → `FF2D55` (Apple2026 red)

New assets copied from Interpod to `wps/Apple2026/`:
- `vb.bmp` + `vb_backdrop.bmp` — volume bar texture/backdrop
- `pb.bmp` + `pb_active.bmp` — progress bar fill (normal/seeking)
- `pb_backdrop.bmp` + `pb_active_backdrop.bmp` — progress bar backdrops

### Apple2026.wps — rebuilt from Interpod Rev.17

Key structural adoption from Interpod:
- **Art in VB layer** (already fixed in Wave 3b — kept): backdrop pattern for no black bars
- **Custom progress bar bitmaps**: `%pb(0,0,-,4,image,pb.bmp,backdrop,pbi)` + active seek bar
  with `pb_active.bmp` (9px, shown during rewind). Much more polished than `noborder`.
- **Volume bar**: Interpod's single-viewport `vb.bmp` textured fill pattern
- **Repeat/shuffle indicators**: Interpod's exact hotspot positions, right margin (x=238, y=143)
- **Playlist counter**: left margin (x=0, y=140, w=82), `%pp %Sx(of) %pe` localised format
- **`timeprogresslossless`** label re-used for elapsed/lossless/remaining (3 same-label viewports)
- **Artist/album cycling**: Interpod's `%t(5)` alternation between artist/album/composer

Apple2026 additions on top:
- Art size: Interpod's 130x130 → 156x156 (centred x=82 vs x=95)
- Art position kept at y=8 (top 18px under header — intentional Interpod depth effect)
- All metadata coordinates recalculated for 156px art:
  - Title: y=172 h=22 (8px gap from art bottom y=164)
  - Artist: y=196 h=14 (0px below title)
  - Progress: y=212 h=4 (2px below artist)
  - Seeking: y=210 h=9 (centred on progress position)
  - Time: y=218 h=14 (6px below progress)
- Artist color: Interpod's `f24e61` → Apple2026 `FF2D55`
- Font slots: {3:15-Inter-Bold, 8:20-Inter-SemiBold, 9:20-Inter-V} →
  {3:16-Inter-SemiBold, 8:20-Inter-SemiBold, 9:13-Inter-SemiBold}
- Artist text: slot 9 (20px Interpod) → 13px (tighter hierarchy, Apple Music style)
- Artist gets full width (removed side-by-side track position — uses left margin counter instead)
- Removed standalone `25-SFPro` WPS slot (not needed in WPS — only SBS needs it for large title)

### Files changed
- `wps/Apple2026.sbs` — full rewrite from Interpod base (see above)
- `wps/Apple2026.wps` — full rewrite from Interpod base (see above)
- `wps/Apple2026/vb.bmp` — copied from Interpod
- `wps/Apple2026/vb_backdrop.bmp` — copied from Interpod
- `wps/Apple2026/pb.bmp` — copied from Interpod
- `wps/Apple2026/pb_active.bmp` — copied from Interpod
- `wps/Apple2026/pb_backdrop.bmp` — copied from Interpod
- `wps/Apple2026/pb_active_backdrop.bmp` — copied from Interpod

### Verification needed
- [ ] Build sim, confirm no skin parse errors in debug output
- [ ] At root (stopped): large title "Library" + full 36px bottom bar (but no track info if fresh boot)
- [ ] At root (playing): large title + thin 11px strip, content area taller
- [ ] Non-root (playing): compact title in header, thin strip, full content
- [ ] WPS: 156x156 art centred, no black bars, red artist, repeat/shuffle in right margin
- [ ] WPS: progress bar uses pb.bmp texture (not flat color)
- [ ] WPS: volume adjustment shows vb.bmp textured bar
- [ ] Screenshot comparison vs Interpod + Figma Apple Music Library

---

## 2026-04-08 (Wave 3b — Interpod-baseline stabilisation pass)

### Root causes fixed
- **WPS black side bars:** Art was in main layer (no `%VB`). Areas left/right of art box had
  no explicit viewport fill — relied on backdrop BMP loading correctly on hardware. On device,
  backdrop sometimes failed to render, leaving black behind art. Fix: moved art viewport to
  `%VB` (backdrop layer) exactly like Interpod, so art + letterbox areas are baked into the
  backdrop buffer. Main layer then paints chrome on top. Added `%V(0,0,-,-,-)` + `%Vb(F8F8F8)`
  as explicit main-layer context, matching Interpod's proven pattern.
- **Large title showing "Rockbox":** `large_title` viewport used `%Lt` which returns the
  Rockbox string. Since the viewport is gated by `%?Lo` (only shown at root), hardcoded
  "Library" as the display text. No C language changes needed.
- **Rows too short (19px instead of 32px):** `list_init_item_height` was ignoring icon tile
  height on non-touchscreen targets. Added `#if ROCKPOD_APPLE2026_IPOD` minimum of 32px to
  match the icon strip tile height (`ICON_TILE_H = 32`). Viewports in §54 were already sized
  for 32px rows — this fix makes the list engine match them.
- **Settings icon black/wrong:** `root_menu.c` was using `Icon_Submenu_Entered` (chevron.down,
  gray) for the Settings root menu item. Changed to `Icon_General_settings_menu` (gear, red).
- **Several main-menu icons showing as black/gray instead of red:** `_main_icon_tint()` had a
  narrow accent set; only 11 of 32 icons were red. Replaced with an inverted model: all icons
  are red (`CLR_ACCENT`) except structural chrome glyphs (cursor, reverse-cursor, moving,
  submenu indicators) which remain tertiary gray. All assets regenerated.

### Files changed
- `wps/Apple2026.wps` — WPS rebuilt with Interpod VB pattern for art + stable viewport stack
- `wps/Apple2026.sbs` — large_title text hardcoded to "Library"
- `apps/gui/list.c` — include `apple2026_shell.h`; 32px row-height minimum for Apple2026 iPods
- `apps/root_menu.c` — Settings item: `Icon_Submenu_Entered` → `Icon_General_settings_menu`
- `tools/apple2026_symbol_assets.py` — new accent model (all-red except chrome glyphs); assets regenerated
- `icons/Apple2026Icons.bmp`, `wps/Apple2026/*.bmp` — regenerated

### Verified
- Asset script runs clean (0 errors, 19 files generated)
- No linter errors in changed C files
- WPS art VB structure matches Interpod Rev.17 reference

---

## 2026-04-08 (Wave 3c — Font quality fix: Inter replaces SF Pro for all sub-25px slots)

### Root cause of fuzzy text confirmed
Both Interpod (Inter) and our fonts use `depth=1` (4bpp antialiased). The difference is
**TrueType hinting**: Inter was built by Rasmus Andersson specifically for screen rendering at
12-24px — it has complete `cvt`/`fpgm`/`prep` hinting tables that tell FreeType to snap stems
to exact pixel boundaries at each size. SF Pro relies on Apple's proprietary Core Text
rendering engine (AAT hints). FreeType — used by `convttf` — ignores AAT hints entirely.
Result at 13-19px on the iPod's 132 DPI screen: Inter strokes are 1px wide and perfectly
aligned; SF Pro strokes land at fractional positions, producing gray fringe (reads as blur).
At 25px (large title), the effect is negligible — kept SF Pro Display Bold there.

### Changes
- `fonts/16-Inter-SemiBold.fnt` — copied from Interpod 1 (header chrome, slot 3)
- `fonts/19-Inter-V-padded.fnt` — copied from Interpod 1 (body, slot 5; cell height=25px)
- `fonts/20-Inter-SemiBold.fnt` — copied from Interpod 2 (WPS title, slot 8; height=22)
- `fonts/13-Inter-SemiBold.fnt` — copied from Interpod 2 (secondary/metadata, slot 9; height=14)
- `wps/Apple2026.sbs` — font slots 3/5/9 now Inter (slot 2 keeps SF Pro Display 25px)
- `wps/Apple2026.wps` — font slots 3/5/8/9 now Inter; WPS coordinates updated for h=22 title
  - Title: y=172 h=22 (was h=20), artist: y=196 (was y=192), progress: y=212 (was y=210), time: y=218 (was y=224)
- `wps/WPSLIST` — body font: `19-Inter-V-padded.fnt` (was `19-SFProText-Medium.fnt`)
- `tools/apple2026_symbol_assets.py` — `ICON_TILE_H` 32→25 (matches 25px Inter row height)
- `apps/gui/list.c` — row minimum 32→25 (Inter padded font naturally drives 25px rows)
- All icons regenerated at 28×25 tile size

### Verified
- Asset script clean (0 errors, 19 files)
- No linter errors

---

## 2026-04-07 (Wave 3 §54-COMPLIANT CORRECTION: every coordinate verified against design system)

### Changed
- **SBS completely rewritten to match §54 geometry token table exactly:**
  - Header: **26px** (y=0..25) — was wrongly 28px.
  - Large title: **y=27..50** (24px band) — was wrongly y=28, h=30.
  - Content viewports: **y=27/h=177, y=51/h=153, y=27/h=213, y=51/h=189** — all were wrong.
  - Mini-player: **y=204, h=36** — was wrongly y=198, h=42.
  - Mini art: **8,207,30,30** — was wrongly 6,201,36,36.
  - Mini title: **48,212** — was wrongly 48,204.
  - Mini meta: **48,226** — was wrongly 48,224.
  - Mini state: **284,214,20,16** — was wrongly 284,210,20,18.
  - All indicator positions restored to §54.2: lock (24,7,9,12), battery (288,4,27,16), busy (58,9,9,9), player (3,5,15,16).
- **WPS completely rewritten to match §54.6 geometry:**
  - Album art: **156x156 at (82,9)** — was wrongly 170x170 at (75,6).
  - Title: **y=172** — was wrongly y=178.
  - Artist: **y=192** — was wrongly y=200.
  - Progress: **y=210** — was wrongly y=220.
  - Time: **y=224** — was wrongly y=227.
  - All header indicators match SBS exactly.
- **Font slots corrected to §27.1 hierarchy:**
  - Slot 2: **22-SFCompactDisplay-Semibold** (was 25-SFProDisplay-Bold — too large for 24px band).
  - Slot 3: **16-SFProText-Medium** (was 15-SFProText-Semibold — didn't match §33.2 lock).
  - Slot 5: **19-SFProText-Medium** (user body-size override, documented in §27.1.1).
  - Slot 8 (WPS title): **16-SFProText-Medium** (was 17-SFProText-Bold — §33.2 locks WPS title at 16px).
  - Slot 9: **13-SFCompactText-Regular** (was 14-SFProText-Regular — §27.1 locks secondary at 13px).
- **Icon assets regenerated at §54-locked sizes:**
  - Main strip: **22x20** tiles (was wrongly 24x22).
  - playerStatus: **15x16** (was 17x18).
  - holdSlider: **9x12** (was 11x14).
  - batteryStatus: **27x16** (was 29x18).
  - busyIndicator: **9x9** (was 11x11).
  - speaker_loud/mute: **19x17** (was 21x19).
  - albumPlaceholder: **156x156** (was 170x170).
- **WPSLIST comment** updated to reflect 22x20 tiles.
- **DESIGN_SYSTEM.md** §27.1.1 added documenting user body-size override (19px).

### Verified (line-by-line against §54)
- Every SBS viewport coordinate checked against §54.1, §54.2, §54.5, §58.2, §58.5 — all match.
- Every WPS viewport coordinate checked against §54.6, §58.6 — all match.
- Every asset dimension checked against §54 locks — all match.
- All 4 required fonts verified present in `fonts/`.
- No Cabbie leakage: iPod models use Apple2026 WPS/SBS/font/icons/backdrop.
- `dynamic_colors` confirmed false for iPods.
- Icon source confirmed: `Sourced Icons/sf-symbols-master/glyphs` (1672 glyph PNGs available).

### Docs
- This entry; DESIGN_SYSTEM.md §27.1.1 user override.

### Next
- Simulator build + screenshot validation.

---

## 2026-04-07 (Wave 3 practical fit-and-polish pass: font-to-lane clipping, WPS title scale, dividers)

### Changed
- **SBS mini_title**: slot 5 (19px) → **slot 3 (16px)**. 19px font in 16px lane was 3px clipping — would have visibly butchered song titles with descenders.
- **WPS slot 8 (title)**: 16-SFProText-Medium → **19-SFProText-Semibold**. 16px for the WPS song title was too conservative; 19px semibold in 20px lane (1px pad) provides Apple-scale typography the user requires.
- **WPS playlist count**: slot 3 (16px) → **slot 9 (13px)**. 16px in 14px lane was 2px clipping; secondary text should be 13px per hierarchy.
- **WPS time labels** (progress_lane, progress_lane_right): slot 3 → **slot 9 (13px)**. Same 2px clipping issue; time is tertiary text.
- **WPSLIST**: `list separator height: 0` → **`1`**. §54.3/§13 require visible inset dividers (DCDCE0). Height 0 eliminated all dividers entirely.

- **SBS volume overlay (HIDDEN BUG)**: speaker_mute was at viewport-relative (37,211) in a 36px-tall overlay — drawn at y=415 absolute, completely invisible. Fixed to (37,9). Speaker_loud/speaker_too_loud were drawn via %xd inside a 3px-tall volume_bar viewport, clipping 17px icons to 3px. Moved to volume_overlay viewport. %xl positions updated to (270,9) and (300,9) — viewport-relative to volume_overlay.
- **WPS volume overlay**: speaker_mute at viewport-relative (37,4) in 18px overlay — 3px bottom clipping. Fixed to (37,1) matching speaker_loud/too_loud y-offset.

### Verified (font-to-lane audit)
- Every text viewport checked: font px vs lane height.
- No critical clipping after corrections.
- Only marginal: battery_text (16px in 15px, digits-only content — no practical descender risk).
- WPS metadata stack: art ends y=165, title y=172 (7px gap), artist y=192, progress y=210, time y=224 — no overlaps, all transitions clean.
- Mini-player: title (16px in 16px) and meta (13px in 14px) both clean. 2px overlap zone at y=226-227 is per §58.5 design — meta overwrites, acceptable for the compact 36px band.
- SBS volume overlay: speaker and bar now correctly positioned with viewport-relative coords. Speakers in 36px overlay viewport, bar in separate 3px viewport (for color separation).
- WPS volume overlay: all speakers fit within 18px viewport without clipping.
- All SBS/WPS header indicators (player_status 15x16, lock 9x12, sleep 9x12, battery 27x16, busy 9x9) verified to fit their respective viewport dimensions.
- Content viewport bottom edges abut mini-player band (y=204) correctly.

### Docs
- This entry.

### Next
- Rebuild.

---

## 2026-04-07 (Wave 3 FULL REBUILD: typography, icons, geometry, WPS)

### Changed
- **Typography system rebuilt from scratch:**
  - Default list font: **19-SFProText-Medium** (was 16px) — closer to Apple UI body scale.
  - Large title: **25-SFProDisplay-Bold** (was 22px SFCompactDisplay-Semibold) — proper iOS-class large title.
  - Header chrome: **15-SFProText-Semibold** (was 16px Medium) — distinct from body, proportional.
  - WPS title: **17-SFProText-Bold** (new slot 8) — readable track name, distinct from body.
  - WPS metadata: **14-SFProText-Regular** (slot 9) — calm secondary text, not tiny.
  - Installed 6 new `.fnt` files from `Apple Fonts/Generated FNT/Apple2026/` into `fonts/`.
- **Icon system rebuilt:**
  - `tools/apple2026_symbol_assets.py`: tiles **24×22** (was 22×20); padding 1 (was 2); scale 0.96 (was 0.91).
  - WPS symbols enlarged: `playerStatus` **17×18** (was 15×16), `holdSlider` **11×14**, `batteryStatus` **29×18**, `speaker` **21×19**, `busyIndicator` **11×11**, `shuffle/repeat` all +2px.
  - Regenerated all `icons/Apple2026Icons.bmp` and `wps/Apple2026/*.bmp`.
- **SBS geometry fully rebuilt (`Apple2026.sbs`):**
  - Header band: **28px** (was 26px) — fits larger header icons.
  - Large title band: **30px** at y=28 (was 32px at y=27) — 25px Display Bold.
  - Content viewports adjusted: `content_with_mini` at y=28/h=170, `content_with_mini_lt` at y=58/h=140, etc.
  - Mini-player: **42px** (was 36px) at y=198 — 36×36 art, 19px title, 14px artist.
  - Volume overlay: **42px** with **5px** rail (was 36px/3px).
- **WPS fully rebuilt (`Apple2026.wps`):**
  - Album art: **170×170** at x=75, y=6 (was 160×160 at x=80, y=8) — larger, centered.
  - Title: y=178, **17px bold** (was y=170, 16px medium) — much more readable.
  - Artist: y=200, **14px regular, accent `#FF2D55`** (was y=190, 13px) — properly visible.
  - Progress bar: **5px/6px** rail (was 4px/5px).
  - Volume overlay: **22px** tall with **5px** rail.
  - Removed all outdated divider lines, white box overlay, broken framing.
  - albumPlaceholder regenerated at **170×170** (was 160×160).
- **`settings_list.c`:** `DEFAULT_FONTNAME` → `"19-SFProText-Medium"` (was 16px).
- **`WPSLIST`:** Font → `19-SFProText-Medium.fnt`; icon comment updated to 24×22; `list separator height: 0` (cleaner Apple aesthetic).

### Verified
- `python tools/apple2026_symbol_assets.py` exit 0; all 19 assets regenerated with correct dimensions.
- All 10 `.fnt` files present in `fonts/` with correct names (no BDF conflicts).
- No Cabbie/tango leakage in `apps/gui/`, `apps/menus/`, or theme files.
- `dynamic_colors` remains `false` for iPod models.
- SBS viewport geometry: header(28) + large_title(30) + content(140..212) + mini(42) = 240px validated.
- WPS geometry: art(6..175) + title(178..199) + artist(200..217) + progress(220..225) + time(227..240) = clean stack.
- Icon tile math: `Apple2026Icons.bmp` = 24×704 (24px wide, 32 icons × 22px each).

### Docs
- This entry.

### Next
- Simulator build + screenshot validation.
- Visual comparison vs Figma and Apple references.
- Fine-tune if list row rhythm needs adjustment after seeing real font rendering.
- Verify mini-player art + text alignment at 42px height.

---

## 2026-04-07 (Wave 3 major rebuild: type band, icons, WPS, dynamic colors)

### Changed
- `tools/apple2026_symbol_assets.py`: main icon strip **`22×20`** tiles; **accent `#FF2D55`** / **black** / **`#3C3C43`** tints by `Icon_*` index; flat **`wpsBackdrop`** (no top/bottom hairlines); **`160×160`** placeholder + subtle `albumFramed`.
- Regenerated `icons/Apple2026Icons.bmp`, `wps/Apple2026/*.bmp` (script run).
- `wps/Apple2026.sbs`: large-title **`h=32`**, content **`content_*_lt`** at **`y=59`** (`h=145` / `181`); mini title/meta **`x=46`**, **`w=228`**; volume rail **3px**.
- `wps/Apple2026.wps`: **`160×160`** art at **`x=80,y=8`**; **removed** `AlbumFramed` overlay on playing art; **4px/5px** progress; artist line **`#FF2D55`**; **3px** volume overlay; flat shell backdrops.
- `apps/settings_list.c`: **`dynamic_colors` default `false`** for **`MODEL_NUMBER` 5/71** (album-art tinting off for Apple2026 shell).
- `DESIGN_SYSTEM.md`: §9, §27.1, §31, §33.2, §33.2.1 updated for Wave 3 rebuild locks.
- `wps/WPSLIST`: comment on icon strip geometry.

### Verified
- `python tools/apple2026_symbol_assets.py` exit 0; `Apple2026Icons.bmp` size **22×640** (32×20px rows).
- Static: `settings_list.c` conditional wraps `OFFON_SETTING` for `dynamic_colors`.

### Docs
- This entry; `DESIGN_SYSTEM.md` as above.

### Next (screenshot / sim matrix — not run in this session)
- Root menu with **`%Lo`**: large-title truncation, list + **22px** icons.
- Submenus: neutral icon tints; **Settings** list readability.
- **WPS**: no frame overlay; progress/volume thickness; artist/title contrast.
- If list feels **short** vs Figma **52px** rows: future **larger list `.fnt`** (requires new convttf source) or touchscreen-only padding paths.

## 2026-04-07 (Wave 3 micro-polish follow-up: time lanes + large-title inset)

### Changed
- `wps/Apple2026.wps`: `progress_lane` / `progress_lane_right` foreground **`6E6E73`** (was `6F6F73`) — tertiary parity with mini/meta/volume.
- `wps/Apple2026.sbs`: `large_title` viewport right inset **`-16`** (was `-32`) — symmetric 16px gutter, less aggressive truncation on long root titles.
- `DESIGN_SYSTEM.md` §33.2.1: note on large-title `-16`.

### Verified
- Static: no remaining `6F6F73` in `Apple2026.wps`.

### Docs
- `DESIGN_SYSTEM.md` **33.2.1**; this entry.

### Next
- Sim: long `LANG_ROCKBOX_TITLE` / root title; elapsed/remaining readability.

## 2026-04-07 (Wave 3 micro-polish: gutters, tertiary, rails, mini-player)

### Changed
- `wps/Apple2026.wps`: metadata/stack and scrubber **16px** inset (`-16` right); tertiary **`6E6E73`**; progress/volume rail **`E5E5EA`**; `lossless_lane` **118**; mute **x=37**; `%pv` **56,8,208** aligned with SBS.
- `wps/Apple2026.sbs`: mini title/meta **x=46**, width **228**; volume bar **56×208**, rail **E5E5EA**; mute **x=37**.
- `DESIGN_SYSTEM.md` §33.2 + **33.2.1** (micro-polish rules, 16px header notes, mini **x=46**).

### Verified
- Static: `37+19=56` (mute abuts volume bar); `8+30+8=46` (mini text vs art).

### Docs
- `DESIGN_SYSTEM.md` **33.2.1**; this entry.

### Next
- Sim: WPS edges, volume scrub, mini truncation.

## 2026-04-07 (Wave 3 continue: `%Lo` root-menu token + Apple2026.sbs i18n)

### Changed
- `lib/skin_parser/tag_table.h`, `tag_table.c`: new SBS token **`%Lo`** (`SKIN_TOKEN_LIST_TITLE_IS_ROOT`) — true when list title equals `LANG_ROCKBOX_TITLE` (localized main menu name).
- `apps/gui/skin_engine/skin_tokens.c`: evaluate `%Lo` via `sb_get_title` vs `P2STR(ID2P(LANG_ROCKBOX_TITLE))`.
- `apps/gui/skin_engine/skin_parser.c`: parse `%Lo` with same `sb_skin_has_title` hook as `%Lt`.
- `wps/Apple2026.sbs`: large-title / `content_*_lt` routing uses `%?Lo<…>` instead of `%?if(%Lt, =, Rockbox)`.
- `manual/appendix/wps_tags.tex`: document `%Lo`.
- `DESIGN_SYSTEM.md` §27.1: root-menu / `%Lo` rule.

### Verified
- Static: token table and parser cases aligned with `SKIN_TOKEN_LIST_TITLE_IS_ROOT`.

### Docs
- This entry; manual + DESIGN_SYSTEM as above.

### Next
- Build + sim: parse Apple2026.sbs; verify large-title in a non-English language.

## 2026-04-07 (Toolchain audit: exit-code bugfix + rockpod.ps1 dispatch)

### Changed
- `tools/rockpod-msys.ps1`: removed `| Out-Host` — it broke `$LASTEXITCODE` (pipeline ended with Out-Host exit 0, masking bash failures). Bare `& env.exe ... bash -lc` + `return $LASTEXITCODE` (ExtraEnv splat path verified). `BUILD.md` documents this.
- `rockpod.ps1`: `check` only dispatches; `sim`/`hw` use `$?` + explicit `exit` when child returns (check-env uses `exit $code` in-process).

### Verified
- `& env ... bash -lc 'exit 42'` → `$LASTEXITCODE=42`; ExtraEnv branch → `exit 7` return value.

### Docs
- `BUILD.md` “Toolchain script notes”; this entry.

## 2026-04-07 (Wave 3 Apple2026 parity + polish pass — typography, rails, progress, scrollbar)

### Changed
- `wps/Apple2026.sbs` / `wps/Apple2026.wps`: font slot 3 → `16-SFProText-Medium.fnt` (aligned with WPSLIST + default settings); header hairline `E3E3E6` → `DCDCE0` (A26 shell rail).
- `wps/Apple2026.wps`: WPS progress scrubber foreground `9E9EA6` → `3C3C43` (tertiary / `A26_PROGRESS_FILL` parity); volume overlay background `DADADD` → `EDEDED` (mini-player surface continuity).
- `apps/settings_list.c`: default `scrollbar_width` **2** on iPod Video/Classic (5/71) vs 6 elsewhere (matches Apple2026 theme + DESIGN subtle bar).
- `apps/plugins/pictureflow/pictureflow.c`: loading progress active segment `158,158,166` → `60,60,67` (shell tertiary fill parity).
- `tools/apple2026_symbol_assets.py`: `wpsBackdrop` / `usbBackdrop` hairlines and USB frame outline use `220,220,224` rail family; regenerated `wps/Apple2026/wpsBackdrop.bmp`, `usbBackdrop.bmp`.

### Verified
- Static review: `settings_list.c` preprocessor for `scrollbar_width` default; skin `%Fl` slot 3 matches `16-SFProText-Medium.fnt` on disk.

### Docs
- `DESIGN_SYSTEM.md` §27.1 note on slot 3 / 16px alignment; this entry.

### Next
- Simulator: list/header type rhythm, scrollbar width on fresh config, WPS progress + volume overlay, Picture Flow cache bar.

## 2026-04-07 (Toolchain polish: env audit + unified CLI + MSYS helper)

### Changed
- `tools/rockpod-msys.ps1`: shared MSYS2 root resolution (`-MsysRoot` / `ROCKPOD_MSYS_ROOT`), `Invoke-RockpodMsysBash` (later: removed `Out-Host` pipeline — see “Toolchain audit” entry — to preserve correct bash exit codes).
- `tools/rockpod-check-env.sh`: prerequisite audit (make/gcc/perl/python3, `IPC::Open2`, SDL2, `arm-none-eabi-*`, optional zip/ccache); `--sim-only` / `--hw-only`.
- `rockpod-check-env.ps1`, `rockpod.ps1`: Windows entry points (`check` | `sim` | `hw` | `help`).
- `build-sim.ps1` / `build-hw.ps1`: dot-source `rockpod-msys.ps1`; added `-MsysRoot`.
- `build-sim.sh`: optional `ROCKPOD_STRICT_INSTALL=1` fails the script when `make install` fails.
- `BUILD.md`, `AGENTS.md`: audit command, `rockpod.ps1`, MSYS override, strict install.

### Verified
- `sh -n tools/rockpod-check-env.sh`; `rockpod.ps1 help`; `rockpod-check-env.ps1` prints full audit (`Result: OK` when deps present).

### Docs
- This entry; `BUILD.md` / `AGENTS.md` updates.

### Next
- Optional: `ccache` wiring per-target if a configure hook is added later.

## 2026-04-07 (Typography: §27.1 large title + 16px list default)

### Changed
- `wps/Apple2026.sbs`: `%Fl(2,22-SFCompactDisplay-Semibold.fnt)`; `%Vl(large_title,…,2)` (gutter x=16); `%?if(%Lt, =, Rockbox)<%Vd(large_title)|>`; `%VI(content_with_mini_lt)` / `%VI(content_full_lt)` when root title is English `"Rockbox"`; compact header unchanged (slot 3, 15px).
- `wps/Apple2026.wps`: `%Fl(2,22-SFCompactDisplay-Semibold.fnt)` for parity.
- `wps/WPSLIST` Apple2026: default font `16-SFProText-Medium.fnt`.
- `apps/settings_list.c`: iPod 5/71 `DEFAULT_FONTNAME` `16-SFProText-Medium.fnt`.

### Verified
- `fonts/22-SFCompactDisplay-Semibold.fnt` and `fonts/16-SFProText-Medium.fnt` exist in tree.

### Docs
- This entry.

### Next
- Sim: root menu layout + list truncation; locale-safe match for large-title if not `"Rockbox"`; optional `14-SFCompactText-Regular.fnt` when OTF available.

## 2026-04-07 (Build-system investigation: incremental workflow + BUILD.md)

### Changed
- `build-sim.sh` / `build-hw.sh`: optional incremental mode (`-i` / `--incremental` or `ROCKPOD_INCREMENTAL=1`) reuses existing build dir and skips configure when `.rockpod_configure_stamp` matches; optional `ROCKPOD_SKIP_DEP=1` skips `make dep` if `make.dep` exists.
- `build-sim.ps1` / `build-hw.ps1`: `-Incremental` switch passes `ROCKPOD_INCREMENTAL`.
- New `BUILD.md`: end-to-end build flow, dependencies, outputs, slowness/fragility notes, symlinkinstall hint, Apple2026 Python tools called out as manual-only.
- `AGENTS.md`, `CLAUDE.md`: pointer to `BUILD.md`.

### Verified
- `sh -n build-sim.sh build-hw.sh` under MSYS2 bash (syntax OK).

### Docs
- This entry; `BUILD.md` is the primary build reference for this pass.

### Next
- Optional: theme-dev profile trimming `WPSLIST` / packaging scope is a larger product decision; optional `ccache` note already in `BUILD.md`.

## 2026-04-07 (Rockbox-leakage pass: splash chrome + theme separator reset)

### Changed
- `apps/apple2026_shell.h`: added `A26_SPLASH_BROKEN_FILL` for splash “broken theme” panel background.
- `apps/gui/splash.c`: iPod Video/Classic — splash panel border uses `A26_SHELL_RAIL` hairline instead of harsh theme-FG box; broken-theme fill/text use Apple2026 neutrals (`A26_SPLASH_BROKEN_FILL`, `A26_PROGRESS_FILL`) instead of stock light gray/black.
- `apps/menus/theme_menu.c`: `reset_color()` sets `list_separator_color` to `LCD_RGBPACK(220,220,224)` on `MODEL_NUMBER` 5/71 (exact DCDCE0); other targets keep `LCD_LIGHTGRAY`.

### Verified
- Static: preprocessor keeps unconditional `draw_border_viewport()` for non-iPod builds; iPod uses rail border when `depth > 1`.

### Docs
- This entry.

### Next
- Optional: `english.lang` tone pass for empty/error strings; grep `apps/gui` + `apps/menus` for remaining hardcoded `LCD_*` on dialog paths; plugin load strings.

## 2026-04-07 (Wave 3 shell token pass — splash + classic statusbar)

### Changed
- Added `apps/apple2026_shell.h`: shared `LCD_RGBPACK` tokens for iPod Video (`MODEL_NUMBER` 5) / Classic (`MODEL_NUMBER` 71) — rail `DCDCE0`, progress fill tertiary gray, battery remainder neutral.
- `apps/gui/splash.c`: splash progress bar uses Apple2026 rail/fill on RockPod iPod targets (replaces generic light-gray rail + black fill).
- `apps/gui/statusbar.c`: classic statusbar battery “remainder” segment uses `A26_BATTERY_REMAIN` instead of `LCD_DARKGRAY` on those targets.

### Verified
- Static: `ROCKPOD_APPLE2026_IPOD` gates non-iPod builds to prior Rockbox colors.

### Docs
- This entry; `DESIGN_SYSTEM.md` unchanged (tokens already specified there).

### Next
- Grep remaining `LCD_DARKGRAY` / `LCD_LIGHTGRAY` in `apps/` dialogs; optional yesno border alignment to same token header; rebuild sim.

## 2026-04-07 (Wave 3 runtime default theme wiring — Apple2026 active by default)

### Changed
- `apps/settings_list.c`: for `MODEL_NUMBER` 5 (iPod Video) and 71 (iPod Classic 6G/7G), default `wps`/`sbs` are now `Apple2026`, default font `15-SFProText-Medium`, iconsets `Apple2026Icons` + `viewers.6x8x16`, light-shell list colors and flat gray selector aligned with `wps/WPSLIST`, backdrop default `-` (no cabbie backdrop).

### Verified
- Static: `MODEL_NUMBER` 5/71 match `firmware/export/config/ipodvideo.h` and `ipod6g.h`.
- Note: existing `simdisk`/`config.cfg` can still override until reset or delete; use fresh config to see new defaults.

### Docs
- This entry only.

### Next
- Rebuild sim (`./build-sim.ps1`), clear or reset theme config if testing defaults, capture new screenshots.

## 2026-04-07 (Wave 3 icon-system audit + correction pass)

### Changed
- Completed dedicated Apple2026 icon-system correction cycle focused on fringing/safe-box/family coherence.
- Updated `tools/apple2026_symbol_assets.py`:
  - added `_rgba_to_keyed_rgb()` alpha-cut conversion to magenta-keyed BMP export to suppress pink fringe halos.
  - switched symbol resize path to RGBA-first + bicubic/tinted compositing before keyed export.
  - changed strip writer to RGBA composition then keyed export for cleaner edges.
  - tightened `busyIndicator.bmp` generation to reduce rotational clipping risk (`5x5` rays in centered `9x9` frame).
  - restored explicit `losslessIndicator.bmp` generation.
  - removed legacy progress/volume bar bitmap generation (`pb*`, `vb*`) from generator output.
- Regenerated Apple2026 icon assets with updated generator:
  - `icons/Apple2026Icons.bmp`
  - `wps/Apple2026/*.bmp` symbol/state set (player/hold/sleep/repeat/shuffle/speakers/busy/battery/lossless/album/backshell).
- Removed legacy donor-risk leftovers from active Apple2026 runtime icon folder:
  - `pb.bmp`, `pb_backdrop.bmp`, `pb_active.bmp`, `pb_active_backdrop.bmp`,
  - `vb.bmp`, `vb_backdrop.bmp`.

### Verified
- Current active Apple2026 runtime icon folder now contains only Apple2026 symbol-family assets (no `pb*`/`vb*` legacy leftovers).
- Generator run completed successfully and produced expected Apple2026 asset set including `losslessIndicator.bmp`.
- Existing Apple2026 shell files remain wired to symbol-family assets and no donor string regressions were reintroduced.

### Docs
- Logged icon-audit correction cycle in `WORK_LOG.md` as required.

### Next
- Continue icon-state semantic pass (pink/gray/black/white mapping per surface) and run final runtime-icon inventory proof against active WPS/SBS/WPSLIST bindings.

## 2026-04-07 (Wave 3 restart execution block: Apple2026 shell baseline rewrite)

### Changed
- Rewrote `wps/Apple2026.sbs` from scratch to a clean Apple2026 shell baseline using locked geometry/tokens:
  - header band (`0..26`), title lanes (`74/56`), battery/lock/busy anchors, light-shell top bar.
  - explicit content viewport split for with-mini (`y=27,h=177`) and full (`y=27,h=213`) states.
  - rebuilt mini-player shell (`y=204..239`, `36h`) with `30x30` art, title/meta lanes, right play/pause lane.
  - rebuilt ephemeral volume overlay with thin neutral `2px` rail and Apple2026 neutral palette.
- Rewrote `wps/Apple2026.wps` from scratch to a clean Apple2026 Now Playing baseline:
  - retained `156x156` centered art at `x=82,y=9`.
  - rebuilt metadata hierarchy lanes (`title y=172`, `artist y=192`) with SF-first fonts.
  - rebuilt progress/time lanes (`y=210/224`) with thin neutral rail and active-thickness state.
  - preserved lock/battery/status anchors and lossless/state overlays with Apple2026 tone.

### Verified
- Apple2026 runtime files now contain no Interpod donor header/comments or legacy scaffold blocks.
- SF-first font bindings remain active in both rewritten files:
  - `15-SFProText-Medium.fnt`
  - `16-SFProText-Medium.fnt`
  - `13-SFCompactText-Regular.fnt`
- WPS/SBS geometry now follows Wave 3 token locks directly rather than inherited partial structure.

### Docs
- `WORK_LOG.md` updated for this restart execution block.
- No new `DESIGN_SYSTEM.md` lock additions were required in this block (existing tokens were sufficient).

### Next
- Continue Wave 3 restart completion on remaining shell-wide surfaces:
  - loading/fallback/empty consistency pass in core/plugin surfaces,
  - Cover Flow UI alignment-only parity pass,
  - whole-shell consistency sweep and static drift checks against Apple2026 locks.

## 2026-04-07 (Wave 3 completion review snapshot: doc/source parity + readiness)

### 1) WHAT IS FULLY IMPLEMENTED
- Apple2026 runtime shell path is active (`wps/WPSLIST` with Apple2026 WPS/SBS + Apple2026 iconset).
- Apple2026 SF-first font bindings are wired in active Apple2026 surfaces:
  - `15-SFProText-Medium.fnt`, `16-SFProText-Medium.fnt`, `13-SFCompactText-Regular.fnt`.
- Apple2026 symbol/icon replacement pipeline is active:
  - `icons/Apple2026Icons.bmp` + generated `wps/Apple2026/*.bmp` symbol/runtime assets.
- WPS/SBS core composition lock is applied for current Apple2026 surface:
  - large-art WPS coordinates, thin neutral progress language, mini-player lanes, header anchors.
- Secondary/fallback no-build UI replacements applied:
  - splash loading grammar (`apps/gui/splash.c`), yes/no neutralization (`apps/gui/yesno.c`), USB centered takeover composition (`apps/gui/usb_screen.c`), theme separator default neutralization (`apps/menus/theme_menu.c`).
- Boot asset presence is ready in source tree:
  - `apps/bitmaps/native/rockboxlogo.320x98x16.bmp`.

### 2) WHAT IS PARTIALLY IMPLEMENTED
- Whole-shell parity across all listed user-facing surfaces is partially implemented:
  - major Apple2026 shell assets and core WPS/SBS language are in place,
  - but several secondary flows are only covered by prior audit/lock documentation rather than explicit per-surface implementation deltas in this slice.
- Cover Flow UI alignment is partially completed:
  - loading + tracklist selection/progress language updated,
  - broader header/label parity still requires final runtime visual confirmation.
- Design-lock closure is completed in docs, but full visual completion gate is partial without fresh simulator screenshot set against local SVG references.

### 3) WHAT IS STILL MISSING
- Full runtime completion evidence pass (no-build mode was honored):
  - simulator screenshot checkpoint set for all Wave 3 surfaces is still pending in this continuation.
- Explicit final parity pass remains for some secondary user-facing surfaces called out by section 67 audit matrix (playlist/queue/search/radio/shortcuts/deeper settings/filesystem states) to confirm they visually match Apple2026 shell language end-to-end.
- Final stress-matrix (`S1..S7`) screenshot evidence across all required surfaces is still missing in this pass.

### 4) WHERE INHERITED ASSETS STILL REMAIN
- Global platform defaults still reference legacy baseline in core settings code (`apps/settings_list.c` default font macro uses Adobe baseline), outside Apple2026 theme override path.
- In Apple2026 runtime path specifically (`wps/Apple2026*`), current sweeps show no remaining donor references for:
  - `Interpod`, `amusicpod`, `Adobe-Helvetica`, `vb_backdrop/pb_backdrop` legacy dependency strings.

### 5) BIGGEST REMAINING VISUAL OR UX GAPS
- Final whole-product consistency proof is blocked by missing fresh visual evidence run:
  - direct side-by-side confirmation vs local SVG exports for all required surfaces is not yet logged in this no-build slice.
- Secondary-surface UX continuity still needs final implementation-confirmation sweep (not just audit state), especially around playlist/radio/search/context transitions.

### 6) WHETHER THE SHELL IS READY FOR BUILD AND TEST
- **Yes, ready for build and test checkpoint.**
- Source-side Apple2026 font/icon/boot/WPS dependencies required for packaging are present.
- Final “fully complete and native-coherent” sign-off still depends on post-build simulator/device screenshot verification across all required surfaces.

## 2026-04-07 (Wave 3 continuation: lock-resolution + dependency readiness pass)

### Scope
- Continued Wave 3 from current implementation state (no reset).
- Resolved remaining in-doc numeric lock ambiguity and aligned Apple2026 runtime defaults/dependency checks.

### Changes applied
- `DESIGN_SYSTEM.md`
  - resolved section `33.3` checklist to explicit completed state tied to section `33.2`,
  - normalized scrollbar numeric lock wording to match token table (`2px` width, subtle inset behavior).
- `wps/WPSLIST`
  - Apple2026 main default font updated from `16-SFProText-Medium.fnt` to `15-SFProText-Medium.fnt` to match current lock hierarchy for list/header baseline.
- Static dependency-readiness verification executed:
  - confirmed Apple2026 iconset path exists: `icons/Apple2026Icons.bmp`,
  - confirmed Apple2026 required fonts exist: `15/16-SFProText-Medium.fnt`, `13-SFCompactText-Regular.fnt`, `22-SFCompactDisplay-Semibold.fnt`,
  - confirmed boot logo asset exists: `apps/bitmaps/native/rockboxlogo.320x98x16.bmp`,
  - confirmed WPS/SBS referenced Apple2026 bitmap/font dependencies are present (scripted check result: `ALL_APPLE2026_WPS_DEPENDENCIES_PRESENT`).
- Local SVG reference set presence verified for completion comparison:
  - `Sourced Icons/Figma File as SVG.svg`
  - `Sourced Icons/iOS Stocks 07  —◇ Light 🍏.svg`

### Verified (static)
- Apple2026 theme registration remains active and SF-first in `wps/WPSLIST`.
- Apple2026 icon/symbol and font runtime paths required by current WPS/SBS are present.
- No build run in this slice (per no-build instruction), but packaging-critical dependency files are present in source tree.

### Build/runtime status
- Skipped intentionally in this cycle (user-requested no-build mode).

### Files touched
- `DESIGN_SYSTEM.md`
- `wps/WPSLIST`
- `WORK_LOG.md`

### Next action
- Continue Wave 3 completion pass with explicit whole-shell completion review against:
  - `DESIGN_SYSTEM.md`,
  - `MASTER.md`/`AGENTS.md`,
  - local SVG exports,
  - active source hierarchy surfaces (Home/Music/Artists/Albums/Songs/Playlists/Settings/Files/mini-player/WPS/loading/fallback/boot/Cover Flow UI + tracklist).

## 2026-04-07 (Wave 3 continuation: theme default separator neutralization)

### Scope
- Continued Wave 3 secondary/fallback consistency pass.
- Normalized theme reset default separator color to Apple2026 neutral baseline.

### Changes applied
- `apps/menus/theme_menu.c`
  - updated `reset_color()` list separator default:
    - from `LCD_DARKGRAY`
    - to `LCD_LIGHTGRAY`
  - rationale: aligns reset/default behavior with Apple2026 subtle separator direction used in shell/list language.

### Verified (static)
- Change is isolated to theme color reset default and does not alter menu wiring or browse flow.
- IDE includePath squiggle (`3ds/types.h`) is environment-indexing noise, unrelated to this edit.

### Build/runtime status
- Skipped intentionally in this cycle (user-requested no-build mode).

### Files touched
- `apps/menus/theme_menu.c`
- `WORK_LOG.md`

### Next action
- Continue Wave 3 secondary-surface completion checks on remaining user-facing non-plugin paths and lock final parity set.

## 2026-04-07 (Wave 3 continuation: USB takeover surface Apple2026 alignment)

### Scope
- Continued Wave 3 no-build secondary-surface replacement pass.
- Applied Apple2026 shell continuity to USB takeover surface.

### Changes applied
- `apps/gui/usb_screen.c`
  - centered USB logo horizontally within themed parent viewport (replacing right-edge anchoring),
  - keeps existing behavior and HID/title flow unchanged while aligning composition to Apple2026 centered-shell language.

### Verified (static)
- File-level targeted sweep and prior active-surface sweeps remain clean for legacy/donor visual references in modified Apple2026 surfaces.

### Build/runtime status
- Skipped intentionally in this cycle (user-requested no-build mode).

### Files touched
- `apps/gui/usb_screen.c`
- `WORK_LOG.md`

### Next action
- Continue remaining Wave 3 secondary parity checks (playlist/queue/search/radio wording/layout consistency) under Apple2026 token/style lock.

## 2026-04-07 (Wave 3 continuation: fallback/dialog loading-grammar alignment)

### Scope
- Continued Wave 3 no-build implementation for core fallback/dialog surfaces.
- Removed remaining non-Apple2026 visual language in splash/yesno flows and validated active-surface legacy sweep.

### Changes applied
- `apps/gui/splash.c`
  - shifted splash panel spacing to calmer Apple2026 geometry (`RECT_SPACING` from `3` -> `8`),
  - replaced scrollbar-based progress meter with Apple2026 thin neutral rail (`2px`) and darker active fill,
  - replaced vararg talk macros in this unit with explicit `talk_idarray` calls for compatibility-safe voice prompts.
- `apps/gui/yesno.c`
  - replaced saturated touchscreen yes/no frame colors (green/red) with Apple2026 neutral grays:
    - yes frame: `LCD_RGBPACK(208,208,212)`
    - no frame: `LCD_RGBPACK(158,158,166)`

### Verified (static)
- Targeted legacy/style sweep returned no matches in active modified surfaces:
  - query included legacy asset refs (`vb_backdrop`, `pb_backdrop`, donor/font strings) and saturated yes/no frame colors.
  - scope: `apps/gui/splash.c`, `apps/gui/yesno.c`, `apps/plugins/pictureflow/pictureflow.c`
  - result: `0` matches.

### Build/runtime status
- Skipped intentionally in this cycle (user-requested no-build mode).

### Files touched
- `apps/gui/splash.c`
- `apps/gui/yesno.c`
- `WORK_LOG.md`

### Next action
- Continue Wave 3 completion on remaining secondary surface parity (playlist/queue/search/radio/usb/fallback wording consistency) under Apple2026 token/style lock.

## 2026-04-07 (Wave 3 continuation: Apple2026 replacement-first shell enforcement)

### Scope
- Continued Wave 3 implementation in no-build mode.
- Enforced Apple2026-first replacement behavior for remaining inherited visual language in active shell surfaces.

### Changes applied
- Regenerated Apple2026 symbol/runtime assets from SF-symbol sources after generator update:
  - command: `python tools/apple2026_symbol_assets.py`
  - includes new generated runtime glyph strip:
    - `wps/Apple2026/losslessIndicator.bmp`
- WPS/SBS replacement-first cleanup:
  - `wps/Apple2026.wps`
    - removed bitmap-backed volume rail dependencies (`vb_backdrop.bmp`, `pb_backdrop.bmp`, `pb_active_backdrop.bmp` usage path),
    - switched volume lane to Apple2026 thin neutral token language (`2px` rail, neutral inactive + darker active behavior).
  - `wps/Apple2026.sbs`
    - removed `vb_backdrop.bmp` dependency from preload path,
    - switched volume rail to thin neutral token-driven bar rendering.
- Cover Flow UI-only alignment (`apps/plugins/pictureflow/pictureflow.c`):
  - tracklist selected row now uses flat neutral-gray fill (no gradient),
  - tracklist loading state now adds centered thin neutral indicator under wait label,
  - progress bar rendering tightened to Apple2026 thin neutral rail language (`2px`, neutral base + darker active fill).

### Verified (static)
- Apple2026 SF-first font bindings remain active in theme surfaces:
  - `15-SFProText-Medium.fnt`
  - `16-SFProText-Medium.fnt`
  - `13-SFCompactText-Regular.fnt`
- Legacy reference sweep across active Apple2026 shell files returned no matches for inherited paths:
  - search target: `vb_backdrop|pb_backdrop|pb_active_backdrop|vb.bmp|pb.bmp|Adobe-Helvetica|Inter-|Ubuntu-|amusicpod|Interpod`
  - scope: `wps/Apple2026*`
  - result: `0` matches.

### Build/runtime status
- Skipped intentionally in this cycle (user-requested no-build mode).

### Files touched
- `tools/apple2026_symbol_assets.py`
- `icons/Apple2026Icons.bmp`
- `wps/Apple2026/*.bmp` (regenerated, including `losslessIndicator.bmp`)
- `wps/Apple2026.wps`
- `wps/Apple2026.sbs`
- `apps/plugins/pictureflow/pictureflow.c`
- `WORK_LOG.md`

### Next action
- Continue Wave 3 surface completion pass across remaining must-fix secondary/fallback surfaces (playlist/queue/loading/dialog consistency) using Apple2026 token locks, with no fallback to inherited assets unless hard-fail.

## 2026-04-07 (Wave 3 direct replacement pass: Apple2026 symbol-first assets)

### Scope
- Continued Wave 3 implementation with no build run (per current no-build instruction).
- Replaced inherited icon/symbol assets in active Apple2026 path with generated SF-symbol-derived assets.

### Changes applied
- Executed Apple2026 symbol generator:
  - `tools/apple2026_symbol_assets.py`
- Regenerated primary iconset directly from `Sourced Icons/sf-symbols-master/glyphs`:
  - `icons/Apple2026Icons.bmp`
- Regenerated WPS/SBS runtime symbol assets from SF symbols:
  - `wps/Apple2026/playerStatus.bmp`
  - `wps/Apple2026/holdSlider.bmp`
  - `wps/Apple2026/sleep.bmp`
  - `wps/Apple2026/repeat.bmp`
  - `wps/Apple2026/repeatOne.bmp`
  - `wps/Apple2026/repeatShuffle.bmp`
  - `wps/Apple2026/shuffle.bmp`
  - `wps/Apple2026/speaker_loud.bmp`
  - `wps/Apple2026/speaker_mute.bmp`
  - `wps/Apple2026/speaker_too_loud.bmp`
  - `wps/Apple2026/albumFramed.bmp`
  - `wps/Apple2026/albumPlaceholder.bmp`
  - `wps/Apple2026/wpsBackdrop.bmp`
  - `wps/Apple2026/usbBackdrop.bmp`
- Extended generator coverage so inherited runtime fallback sprites are now generated Apple2026-first:
  - `wps/Apple2026/repeatAB.bmp`
  - `wps/Apple2026/busyIndicator.bmp`
  - `wps/Apple2026/batteryStatus.bmp`

### Verified (static)
- Apple2026 theme files already remain on SF-first font bindings:
  - `15-SFProText-Medium.fnt`
  - `16-SFProText-Medium.fnt`
  - `13-SFCompactText-Regular.fnt`
- Regeneration command completed successfully with explicit output list for all replaced assets.

### Build/runtime status
- Skipped intentionally in this cycle (user-requested no-build mode).

### Files touched
- `tools/apple2026_symbol_assets.py`
- `icons/Apple2026Icons.bmp`
- `wps/Apple2026/*.bmp` (regenerated symbol/runtime assets listed above)
- `WORK_LOG.md`

### Next action
- Continue Wave 3 shell pass by replacing remaining inherited visual assets/surfaces where Apple2026 mapping is already locked (no audit-only pause).

## 2026-04-07 (Wave 3 grouped static continuation: core shell + WPS + boot integration)

### Scope
- Continued Wave 3 implementation with **builds intentionally skipped** per user instruction.
- Focused on Sub-wave 3.2/3.4/3.5/3.6 static edits only.

### Changes applied
- Core shell / SBS refinement (`wps/Apple2026.sbs`):
  - added mini-player metadata lane and shifted track/meta layout to preserve right control lane,
  - stabilized mini-player play/pause box behavior,
  - tightened header visual treatment to calmer light-shell top bar,
  - preserved locked anchor behavior for title, lock, battery text/icon, and busy indicator.
- WPS refinement (`wps/Apple2026.wps`):
  - moved to large-art-first layout (`156x156` frame at `x=82,y=9`),
  - aligned title/artist/progress/time lanes to locked Apple2026 Wave 3 coordinates,
  - switched progress rails to thin neutral bars with active state thickness behavior,
  - kept Apple2026 accent token (`#FF2D55`) for artist/accent emphasis.
- Theme cfg-generation support (`wps/wpsbuild.pl`):
  - added parser/output support for `scrollbar` and `scrollbar width` so these tokens are preserved in generated theme cfgs.
- Theme token wiring (`wps/WPSLIST`):
  - Apple2026 now explicitly binds `scrollbar: right`, `scrollbar width: 2`, and subtle separators.
- Cover Flow UI alignment (`apps/plugins/pictureflow/pictureflow.c`):
  - updated loading progress bar styling to Apple2026-neutral language,
  - removed bright green fill,
  - reduced bar thickness and framing to a calm thin indicator,
  - centered width constrained to Apple2026 loading max-width behavior.

### Boot/startup integration (Sub-wave 3.6 static)
- Added iPod S5L boot visual helper in `bootloader/ipod-s5l87xx.c`:
  - centered logo draw on black background,
  - removed default startup banner text from normal startup path,
  - retained fatal-error text paths unchanged.
- Added deterministic boot asset generator:
  - `tools/apple2026_boot_asset.py`
  - source: `Sourced Icons/iPhone-Rebooting.png`
  - output: `apps/bitmaps/native/rockboxlogo.320x98x16.bmp`
- Generated preview artifact for visual inspection:
  - `screenshots/apple2026-boot-logo-320x98-preview.png`

### Design-system contract update
- Resolved WPS geometry ambiguity by updating `DESIGN_SYSTEM.md` section `54.6` to match section `70` refinement:
  - `wps_art_box_default = 156x156`
  - `wps_art_x = 82`
  - `wps_art_y = 9`
  - `wps_title_y = 172`
  - `wps_artist_y = 192`
  - progress/time lanes remain `210/224`.

### Verified (static)
- No reported syntax errors in edited text files via diagnostics checks.
- Boot logo preview confirms centered Apple mark on black for the generated 320x98 boot bitmap strip.

### Build/runtime status
- Skipped intentionally in this cycle (user-requested no-build mode).

### Files touched
- `wps/Apple2026.sbs`
- `wps/Apple2026.wps`
- `wps/WPSLIST`
- `wps/wpsbuild.pl`
- `bootloader/ipod-s5l87xx.c`
- `tools/apple2026_boot_asset.py`
- `apps/bitmaps/native/rockboxlogo.320x98x16.bmp`
- `screenshots/apple2026-boot-logo-320x98-preview.png`
- `DESIGN_SYSTEM.md`
- `apps/plugins/pictureflow/pictureflow.c`
- `WORK_LOG.md`

### Next action
- Continue static Sub-wave 3.3 + remaining 3.2/3.4 lane polish (icons/chevrons/selector/readability safety) before re-enabling Build 2.

## 2026-04-07 (Wave 3 Sub-wave 3.2/3.4 grouped static pass: core-shell anchors)

### Scope
- Post-Build-1 grouped static implementation pass for core shell anchors.
- No build executed in this entry (reserved for Build 2 bundle checkpoint).

### Changes applied
- Extended `wps/wpsbuild.pl` to support generated cfg output for:
  - `scrollbar`
  - `scrollbar width`
- Updated `Apple2026` block in `wps/WPSLIST`:
  - locked scrollbar direction/width (`right`, `2`)
  - subtle separator activation (`list separator height: 1`, neutral separator color)
- Updated `wps/Apple2026.sbs` core-shell lanes:
  - preserved locked header/title/battery text anchors,
  - adjusted battery icon box to fixed token anchor (`288,4,27,16`),
  - reduced mini-player top separator to a single hairline,
  - reserved right lane in mini-player track text to avoid control collision,
  - added explicit mini-player play/pause indicator lane (`x=284,w=20`) tied to playback state,
  - retained Apple2026 accent token in active micro-progress segment.

### Verified (static)
- No parse/lint errors reported for:
  - `wps/wpsbuild.pl`
  - `wps/WPSLIST`
  - `wps/Apple2026.sbs`

### Files touched
- `wps/wpsbuild.pl`
- `wps/WPSLIST`
- `wps/Apple2026.sbs`
- `WORK_LOG.md`

### Build/runtime status
- Not run in this entry.
- Next action: continue grouped shell bundle (remaining Sub-wave 3.2/3.3 elements) before **Build 2**.

## 2026-04-07 (Wave 3 BUILD 1 checkpoint: Apple2026 theme-path proof)

### Scope
- Build 1 only: validate Apple2026 runtime wiring after Sub-wave 3.1 scaffolding.
- No broad shell-polish pass in this checkpoint.

### Commands run (verified)
- `./build-sim.ps1` (initial Build 1 run)
- `./build-sim.ps1` (single rerun after font-reference stability adjustment)

### Build result
- Simulator wrapper reached install marker successfully:
  - `Installing your build in your 'simdisk' dir`
- No terminating `make: ***` fatal error in Build 1 flow.
- CRLF/git warning flood observed; treated as non-fatal noise per project rule.

### Runtime path proof (verified)
- `build-sim/simdisk/.rockbox/themes/Apple2026.cfg` exists
- `build-sim/simdisk/.rockbox/wps/Apple2026.wps` exists
- `build-sim/simdisk/.rockbox/wps/Apple2026.sbs` exists
- `build-sim/simdisk/.rockbox/icons/Apple2026Icons.bmp` exists
- Generated cfg wiring verified:
  - `wps: /.rockbox/wps/Apple2026.wps`
  - `sbs: /.rockbox/wps/Apple2026.sbs`
  - `iconset: /.rockbox/icons/Apple2026Icons.bmp`
  - flat selector + light shell tokens present.

### Simulator launch smoke-check (verified)
- `build-sim/rockboxui.exe` launched successfully (`pid` observed).

### Notes
- Prebuilt Wave 2 SF `.fnt` files are not auto-packaged by this current WPSLIST-driven path.
- For Build 1 stability, Apple2026 SBS/WPS currently use packaged baseline fonts (`15/16-Adobe-Helvetica`) while preserving Apple2026 geometry/state scaffolding.
- Dedicated custom-font packaging integration is queued for later grouped implementation work.

### Screenshots
- Not captured in this checkpoint (theme-path proof + launch smoke-check only).
- Screenshot capture is planned in grouped visual checkpoints (Build 2 and Build 3).

### Files touched
- `wps/WPSLIST`
- `wps/Apple2026.sbs`
- `wps/Apple2026.wps`
- `wps/Apple2026/*`
- `icons/Apple2026Icons.bmp`
- `WORK_LOG.md`

### Next action
- Proceed to Sub-wave 3.2/3.3/3.4 grouped core-shell implementation before Build 2.

## 2026-04-07 (Apple2026 icon-system audit + correction pass)

### Verified
- Runtime main icon strip: `icons/Apple2026Icons.bmp` (32× `Icon_Audio`…`Icon_Rockbox`); WPS/SBS assets under `wps/Apple2026/`; defaults in `apps/settings_list.c` use `viewers.6x8x16` (packaged viewer strip, not SF-normalized in-tree).
- DESIGN_SYSTEM §33.2 battery box `27×16` conflicted with prior `batteryStatus.bmp` frames `27×19` (vertical clip in `%Vl(battery_icon,…,27,16,…)`).

### Changed
- `tools/apple2026_symbol_assets.py`: LANCZOS downscale for glyphs; battery redrawn to `27×16`×10 frames; repeat shuffle/AB use distinct SF names with file-based fallback; `speaker_mute` normalized to `19×17` to match loud tile; busy `rays` resize uses LANCZOS; rotate keeps BICUBIC (Pillow constraint).
- `wps/Apple2026.sbs`, `wps/Apple2026.wps`: `%xl(B,…)` vertical offset `0,4` → `0,0` so the 16px-tall strip is not pushed down inside the header viewport.
- Regenerated: `icons/Apple2026Icons.bmp`, `wps/Apple2026/*.bmp` from the script.

### Next
- Simulator pass: header battery, repeat overlays, volume row alignment; optional future `Apple2026`-styled `viewers` strip + `.icons` to replace legacy `viewers.6x8x16`.

## 2026-04-07 (Wave 3 Sub-wave 3.1 scaffold implementation: theme path wiring)

### Scope
- Implemented Apple2026 theme-path scaffolding only (no broad shell polish yet).
- Objective: make runtime theme loading path valid for Build 1 proof.

### Changes applied
- Registered a new `Apple2026` theme block in `wps/WPSLIST` with explicit `320x240` bindings:
  - `wps.320x240x(16|24|32): Apple2026.wps`
  - `sbs.320x240x(16|24|32): Apple2026.sbs`
  - iconset binding to `icons/Apple2026Icons.bmp`
  - flat selector color model and light-shell base tokens.
- Added new scaffold files:
  - `wps/Apple2026.sbs` (Interpod-derived structural baseline)
  - `wps/Apple2026.wps` (Interpod-derived WPS baseline)
- Wired prepared Wave 2 SF fonts into scaffold skin files:
  - `15-SFProText-Medium.fnt`
  - `16-SFProText-Medium.fnt`
  - `13-SFCompactText-Regular.fnt`
- Updated scaffold accent usage to Apple2026 token (`#FF2D55`) in active SBS/WPS color spots.

### Asset staging completed
- Created `wps/Apple2026/` and staged bitmap bundle from Interpod donor assets.
- Added Apple2026 iconset source to root icons path:
  - `icons/Apple2026Icons.bmp`
- Staged prepared SF `.fnt` assets into `fonts/` for runtime availability.

### Files touched
- `wps/WPSLIST`
- `wps/Apple2026.sbs`
- `wps/Apple2026.wps`
- `wps/Apple2026/*` (staged scaffold bitmaps)
- `icons/Apple2026Icons.bmp`
- `fonts/15-SFProText-Medium.fnt`
- `fonts/16-SFProText-Medium.fnt`
- `fonts/13-SFCompactText-Regular.fnt`
- `fonts/22-SFCompactDisplay-Semibold.fnt`
- `WORK_LOG.md`

### Build/runtime status
- Not run yet in this entry.
- Next action: execute **Build 1** for theme-path proof.

## 2026-04-07 (Wave 3 Sub-wave 3.0 preflight + strict execution plan lock)

### Scope
- Wave 3 preflight only, before broad shell implementation edits.
- Confirmed branch, required-read order, asset/path readiness, and execution sequence.

### Required-read order (verified)
1. `MASTER.md`
2. `AGENTS.md`
3. `DESIGN_SYSTEM.md` (full file)
4. `WORK_LOG.md`

### Branch state (verified)
- Active branch: `Wave3`

### Preflight checks (verified)
- Theme registration source file exists: `wps/WPSLIST`
- Runtime target folders exist:
  - `build-sim/simdisk/.rockbox/themes`
  - `build-sim/simdisk/.rockbox/wps`
  - `build-sim/simdisk/.rockbox/icons`
  - `build-sim/simdisk/.rockbox/fonts`
- Required Wave 3 source assets exist:
  - `Sourced Icons/iPhone-Rebooting.png`
  - `Imported Reference Themes/Interpod/.rockbox/icons/InterNightPod.bmp`
  - `Imported Reference Themes/Interpod 2/.rockbox/wps/Interpod 2.sbs`
  - `Imported Reference Themes/Interpod 2/.rockbox/wps/Interpod 2.wps`
- Prepared Apple2026 font outputs confirmed:
  - `Apple Fonts/Generated FNT/Apple2026/SFCompactDisplay/Semibold/22-SFCompactDisplay-Semibold.fnt`
  - `Apple Fonts/Generated FNT/Apple2026/SFProText/Medium/16-SFProText-Medium.fnt`
  - `Apple Fonts/Generated FNT/Apple2026/SFProText/Medium/15-SFProText-Medium.fnt`
  - `Apple Fonts/Generated FNT/Apple2026/SFCompactText/Regular/13-SFCompactText-Regular.fnt`

### Wave 3 execution plan locked for this run
1. Sub-wave 3.1
   - Register `Apple2026` in `wps/WPSLIST`
   - Add Apple2026 scaffolding files in `wps/` (`.cfg` via WPSLIST generation path, `.sbs`, `.wps`)
   - Wire minimum fonts/icons/assets for runtime loading
2. **BUILD 1** (theme path proof only)
3. Sub-wave 3.2 + 3.3 + 3.4 grouped implementation
   - Header, list geometry, lanes, selector, chevrons, scrollbar, icon integration, mini-player
4. **BUILD 2** (core shell checkpoint)
5. Sub-wave 3.5 + 3.6 + 3.7 grouped implementation
   - WPS, boot image path, loading/fallback shelling, Cover Flow UI alignment only
6. Sub-wave 3.8 whole-shell consistency pass
7. **BUILD 3** (full visual checkpoint)

### Build cadence lock (strict)
- No incremental rebuild churn between grouped bundles.
- Only Build 1 / Build 2 / Build 3 unless a true blocker requires emergency validation.

### Files touched
- `WORK_LOG.md`

### Build/runtime status
- Not run in this entry (preflight/documentation lock only).

## 2026-04-06 (Post-fix confidence rerun: canonical wrappers remain green)

### Scope
- Fast confidence rerun only (no new build-system code changes).
- Canonical path re-validated on Native Windows + MSYS2 UCRT64 wrappers.

### Commands run (verified)
- `./build-sim.ps1` -> exit code `0`
- `./build-hw.ps1 -Target ipod6g` -> exit code `0`

### Artifact checks (verified)
- `build-sim/simdisk/.rockbox/rockbox-info.txt` exists, size `879`, mtime `2026-04-06 22:13:18`
- `build-sim/rockboxui.exe` exists, size `9995481`, mtime `2026-04-06 22:12:22`
- `build-hw-ipod6g/rockbox.zip` exists, size `7855897`, mtime `2026-04-06 22:21:00`
- `build-hw-ipod6g/rockbox.ipod` exists, size `764788`, mtime `2026-04-06 22:19:20`

### Notes
- CRLF/git warning flood remains present in logs and was again non-fatal in successful wrapper runs.
- No canonical-path regression detected in this confidence pass.

### Files touched
- `WORK_LOG.md`

## 2026-04-06 (Top-level MCP Figma URL lock in design docs)

### Scope
- Documentation-only update to ensure the requested Figma reference URL is explicitly saved at top level in design docs.

### Update applied
- Added a new top-level entry in `DESIGN_SYSTEM.md`:
  - `## 3A) Top-level MCP Figma reference`
  - `mcp_com_figma_mcp_use_figma`: `https://www.figma.com/design/JyDHVsT9bqCPjbGEfyUD8d/Apple-Music-UI?node-id=35-9972&t=rOOHiOTV8SE8HN2c-4`
  - locked node mapping: `35:9972`

### Notes
- Direct browser fetch of this Figma URL is WebGL-gated in-session; URL/value was still preserved exactly in docs.

### Files touched
- `DESIGN_SYSTEM.md`
- `WORK_LOG.md`

### Build/runtime status
- Not run in this pass (documentation-only change).

## 2026-04-06 (Wave 2 focused Now Playing reference-ingestion pass: iOS current-player)

### Scope
- Wave 2 design-system pass only (no broad implementation).
- Added one critical Apple Music Now Playing reference to improve WPS/mini-player/control language.

### Reference inputs
- Figma URL (node `35:9972`) was provided but not directly renderable via browser scrape in-session.
- User-supplied exported SVG used as authoritative geometry source:
  - `Sourced Icons/iOS Stocks 07  —◇ Light 🍏.svg`
- Interpod lineage re-checked for adaptation grounding:
  - `Imported Reference Themes/Interpod/.rockbox/wps/Interpod.wps`
  - `Imported Reference Themes/Interpod 2/.rockbox/wps/Interpod 2.wps`
  - `Imported Reference Themes/amusicpodds/.rockbox/wps/amusicpodds.wps`
  - corresponding `.sbs` files for lower-shell/volume behavior.

### What was extracted from the new reference
- Portrait iPhone composition (`390x844`) with large near-full-width art card.
- Strong title/artist hierarchy below art.
- Triad transport controls with center play/pause optical emphasis.
- Thin progress rail + compact thumb language.
- Secondary volume slider language and lower action row semantics.

### Design-system lock update
- Added `## 70) Current iOS Now Playing ingestion lock (Figma node 35:9972 via SVG reference)` to `DESIGN_SYSTEM.md`.
- New section includes:
  - preserve/adapt/reject rules,
  - iPod-form-factor compression strategy,
  - Interpod vs Interpod2 vs amusicpodds adaptation mapping,
  - playback control and slider implementation-facing token rules,
  - explicit inherit/reject matrix for Wave 3 execution.

### Outcome
- Apple2026 Now Playing direction is now explicitly informed by current Apple Music language,
  but translated to iPod constraints and Interpod strengths instead of literal phone-copy layout.

### Files touched
- `DESIGN_SYSTEM.md`
- `WORK_LOG.md`

### Build/runtime status
- Not run in this pass (design-system lock update only).

## 2026-04-06 (Wave 2 full-glyph review completion + environment-step freeze workaround)

### Scope
- Complete the requested all-glyph review for prepared Apple2026 fonts.
- Keep scope within Wave 2 typography/font readiness only.

### Execution issue observed
- The Python environment handoff step repeatedly appeared frozen/blocked in-session
  (configure action cancelled/stalled), preventing forward progress when used as the sole path.

### Workaround and completion path
- Executed the generator/audit directly with the known working interpreter and MSYS runtime PATH:
  - `C:/Python314/python.exe tools/apple2026_font_prep.py`
- Regeneration completed successfully (`144/144`) and produced all inventory/preview/glyph artifacts.

### Glyph-audit bug fixes applied
- Updated `tools/apple2026_font_prep.py` glyph integrity logic to avoid false rejects from
  non-printing codepoints in the scanned range.
- Added printable-glyph gate for integrity checks and excluded expected blank codepoints
  (`U+0020`, `U+00A0`, `U+00AD`, control range handling).

### Final all-glyph result (verified)
- `APPLE2026_GLYPH_AUDIT.md` summary after rerun:
  - Primary: `144`
  - Fallback: `0`
  - Reject: `0`
- Per-font full glyph sheets present under:
  - `Apple Fonts/Generated FNT/Apple2026/glyph_sheets/`

### Files touched
- `tools/apple2026_font_prep.py`
- `DESIGN_SYSTEM.md` (added section 69 full-glyph audit lock)
- `WORK_LOG.md`

### Build/runtime status
- Font-generation/audit runtime completed successfully in this pass.
- No broad simulator/hardware shell changes executed in this pass.

## 2026-04-06 (Wave 1 strict build-environment recovery pass)

### Scope
- Strict build-readiness recovery only (no UI/theme/performance work).
- Canonical path locked to **Native Windows + MSYS2 UCRT64**.
- Target focus locked to **ipod6g** (+ simulator) per current project need.

### Failure isolation results (verified)
- Reproduced build in direct MSYS2 bash (no wrapper abstraction) and captured full logs.
- Observed `make: Circular ... dependency dropped` and CRLF/git warning flood; verified these are noisy and non-fatal in successful runs.
- Identified real wrapper-level issue:
  - `build-hw.ps1` could stop early on benign stderr (`NativeCommandError`) before exit-code evaluation.

### Corrective action applied (smallest fix)
- Updated wrappers to evaluate success by process exit code instead of treating stderr text as fatal:
  - `build-hw.ps1`
  - `build-sim.ps1`
- Kept explicit non-zero exit enforcement (`throw` on non-zero) to preserve fail-fast behavior on true errors.

### Validation (verified)
- Direct canonical shell build succeeded:
  - command: `./build-hw.sh ipod6g` (inside MSYS2 UCRT64 bash)
  - package marker present: `ZIP rockbox.zip`
- Wrapper parity build succeeded after fix:
  - command: `./build-hw.ps1 -Target ipod6g`
  - exit code: `0`
- Simulator wrapper build succeeded after fix:
  - command: `./build-sim.ps1`
  - install marker present: `Installing your build in your 'simdisk' dir`

### Artifact state (verified)
- `build-hw-ipod6g/rockbox.zip` exists
- `build-hw-ipod6g/rockbox.ipod` exists
- `build-hw-ipod6g/rockbox-info.txt` exists
- `build-sim/rockboxui.exe` exists
- `build-sim/simdisk/.rockbox/rockbox-info.txt` exists

### Documentation alignment updates
- Updated `Pasted markdown (3).md` (`PROJECT RESET HANDOFF MASTER`) to match actual repo reality:
  - removed stale `tools/windows-shims/*` references,
  - switched to root wrappers (`build-hw.ps1`, `build-sim.ps1`),
  - corrected expected artifacts,
  - added warning-noise vs fatal-error guidance.

### Current canonical status
- **Canonical path is green:** Native Windows + MSYS2 UCRT64.
- Do not pivot to WSL unless canonical path regresses with true repeatable fatal errors.

## 2026-04-06 (Wave 2 font-asset preparation and readiness pass)

### Scope
- Strict Wave 2 pass focused only on typography asset readiness before broad Wave 3 shell work.
- No broad shell implementation started.

### Actions completed
- Re-audited typography lock in `DESIGN_SYSTEM.md` (sections 27, 28, 29, 65, 66).
- Re-inventoried approved source families under `Apple Fonts/`:
  - SF Pro Display/Text
  - SF Compact Display/Text
  - New York (reviewed, not used for primary generation set)
- Built and validated converter path (`tools/convttf.exe`) in MSYS2 UCRT runtime.
- Added automated generation/analysis script:
  - `tools/apple2026_font_prep.py`
- Generated broad curated Apple2026 `.fnt` library into:
  - `Apple Fonts/Generated FNT/Apple2026/`

### Output summary
- Total generated candidates: `144`
- Quality status:
  - `140` primary
  - `3` fallback
  - `1` reject
- Family coverage:
  - SF Pro Display (`19-25`, Regular/Medium/Semibold/Bold)
  - SF Compact Display (`19-25`, Regular/Medium/Semibold/Bold)
  - SF Pro Text (`10-19`, Regular/Medium/Semibold/Bold)
  - SF Compact Text (`8-19`, Regular/Medium/Semibold/Bold)

### Quality/readability validation
- Applied automated readability filters (density, punctuation clarity, digit width floors,
  micro-size heavy-weight risk).
- Generated role preview sheets for all required typography roles:
  - `Apple Fonts/Generated FNT/Apple2026/previews/role_*.png`
- Explicit reject in this pass:
  - `08-SFCompactText-Bold.fnt` (`micro_bold_muddy_risk`)

### Documentation outputs
- Added Wave 2 font readiness lock section to `DESIGN_SYSTEM.md`:
  - `## 68) Wave 2 font-asset preparation lock (font-system readiness)`
- Generated inventory artifacts:
  - `Apple Fonts/Generated FNT/Apple2026/APPLE2026_FONT_INVENTORY.md`
  - `Apple Fonts/Generated FNT/Apple2026/apple2026_font_inventory.csv`
  - `Apple Fonts/Generated FNT/Apple2026/apple2026_font_inventory.json`

### Next task queue
1. Use this prepared set as default source for Wave 3 surface-by-surface font picks.
2. Avoid ad hoc regeneration unless a hard requirement falls outside prepared ranges.
3. Keep fallback Inter/Ubuntu `.fnt` files as contingency only.

## 2026-04-06 (Wave 2 full user-facing runtime audit pass)

### Scope
- Performed one more major whole-product Wave 2 audit focused on all user-facing
  surfaces reachable while running Rockbox.
- Audit includes core shell, plugin, dialog, fallback, USB, and boot/startup-adjacent
  user-visible paths.

### Evidence basis (code-level)
- Core runtime/navigation: `apps/root_menu.c`, `apps/tree.c`, `apps/menus/main_menu.c`,
  `apps/menus/settings_menu.c`
- Playback/music paths: `apps/gui/wps.c`, `apps/onplay.c`, `apps/tagtree.c`,
  `apps/playlist_viewer.c`, `apps/playlist_catalog.c`
- Modal/fallback: `apps/gui/splash.c`, `apps/gui/yesno.c`, `apps/lang/english.lang`
- Secondary surfaces: `apps/radio/radio.c`, `apps/radio/radio_skin.c`,
  `apps/shortcuts.c`, `apps/gui/usb_screen.c`
- Cover Flow UI/loading references: `apps/plugins/pictureflow/pictureflow.c`
- Boot/startup references: `bootloader/show_logo.c`, `bootloader/ipod-s5l87xx.c`

### DESIGN_SYSTEM update
- Added `## 67) Full user-facing runtime audit lock (Wave 2 whole-product pass)`
  to `DESIGN_SYSTEM.md`.
- Added required 8-part structure:
  1) full inventory,
  2) primary flagship surfaces,
  3) secondary surfaces,
  4) fallback/dialog/empty surfaces,
  5) biggest inconsistencies,
  6) Wave 3 must-fix surfaces,
  7) deferred surfaces,
  8) documentation update plan.

### Outcome
- Wave 2 now has explicit whole-product user-facing surface coverage, not only
  primary list/WPS shells.
- Must-fix and deferred boundaries are now documented for Wave 3 execution discipline.

### Build / runtime status
- Not run in this pass (audit/spec lock documentation pass only).

### Next task queue
1. Enforce section `67` as a mandatory coverage checklist during every Wave 3 validation step.
2. Resolve listed must-fix inconsistencies before claiming any whole-product UI pass complete.
3. Keep deferred items blocked per branch boundaries.

## 2026-04-06 (Wave 2 high-risk string stress-matrix lock pass)

### Scope
- Continued Wave 2 planning only.
- Added a strict pre-implementation stress-matrix layer for long-string readability,
  truncation behavior, and lane collision prevention.

### What was added
- Added `## 66) High-risk string stress matrix (pre-implementation lock)` to `DESIGN_SYSTEM.md`.
- Defined canonical stress IDs (`S1..S7`) spanning long title/artist/album/playlist/file labels,
  punctuation edge cases, and missing-metadata fallback labels.
- Mapped stress-string application across key surfaces:
  - Home/Artists/Albums/Songs/Playlists,
  - Settings/Files,
  - album page tracklist,
  - WPS/mini-player,
  - Cover Flow tracklist,
  - loading/fallback states.
- Added explicit stress pass/fail gates and screenshot evidence requirements tied to stress IDs.

### Intent
- Ensure Wave 3 starts with predefined clipping/overlap stress tests,
  reducing implementation-time guesswork and regressions.

### Files touched
- `DESIGN_SYSTEM.md`
- `WORK_LOG.md`

### Build / runtime status
- Not run in this pass (planning/spec lock only).

### Next task queue
1. Enforce section 66 stress checks at every Wave 3 validation step.
2. Record stress IDs (`S1..S7`) in screenshot notes for pass/fail evidence.
3. Block progression for any surface failing stress checks until corrected.

## 2026-04-06 (Wave 2 readability/overlap prevention guardrails pass)

### Scope
- Extended Wave 2 planning with explicit UI/UX best-practice implementation guardrails.
- No broad runtime/theme implementation changes in this pass.

### What was added
- Added a dedicated safety-lock section to `DESIGN_SYSTEM.md`:
  - `## 65) UI/UX best-practice safety lock (readability + overlap prevention)`
- New mandatory rule groups include:
  - readability floors by surface,
  - overlap-prevention hard-fail criteria,
  - truncation/marquee priority logic,
  - spacing minimums and lane clearances,
  - hierarchy safety for small-screen adaptation,
  - simulator validation best practices,
  - device-realism safety bias rules.

### Intent
- Reduce Wave 3 guesswork around readability and layout safety.
- Prevent polished-shell regressions (crowding, clipping, lane collisions, muddy text) before implementation scaling.

### Files touched
- `DESIGN_SYSTEM.md`
- `WORK_LOG.md`

### Build / runtime status
- Not run in this pass (planning/spec lock only).

### Next task queue
1. Enforce section 65 gates as part of Wave 3 step validation.
2. Treat any overlap/clipping event as fail until corrected.
3. Keep screen-by-screen evidence logging tied to sections 58-65.

## 2026-04-06 (Wave 2 implementation-grid expansion pass)

### Scope
- Continued strict Wave 2 planning without broad implementation edits.
- Expanded pre-implementation planning from token list to full execution blueprint.

### Planning expansions completed
- Converted isolated geometry tokens into a full implementation grid system:
  - global shell grid,
  - header grid,
  - list row grid,
  - icon/text/chevron/scrollbar lane grid,
  - mini-player grid,
  - WPS grid,
  - Cover Flow label/loading grid,
  - boot/loading grid.
- Added screen-by-screen token application map for:
  - Home/Music/Artists/Albums/Songs/Playlists,
  - Settings/Files,
  - album list/album page,
  - WPS/mini-player,
  - Cover Flow browse/loading/tracklist,
  - fallback/loading/boot surfaces.
- Added exact file-by-file Wave 3 execution order with dependency gates and deferred-file policy.
- Added per-step validation checklist with capture requirements, pass/fail criteria, and common mistake checks.
- Added stricter boot/loading implementation workflow boundaries (theme-driven vs code-driven).
- Added full user-flow coherence rules and hard drift-prevention rule set.

### DESIGN_SYSTEM additions
- Added sections `58` through `64` to `DESIGN_SYSTEM.md`.

### Files touched
- `DESIGN_SYSTEM.md`
- `WORK_LOG.md`

### Build / runtime status
- Not run in this pass (planning/spec lock only).

### Next task queue
1. Use sections `58-64` as mandatory execution checklist when Wave 3 scaffolding starts.
2. Block any surface implementation lacking explicit lane/token mapping.
3. Validate each Wave 3 step with required screenshot set before continuing.

## 2026-04-06 (Wave 2 strict pre-implementation exactness pass)

### Scope
- Pre-implementation planning only (no broad Wave 3 theme implementation edits).
- Goal: remove coordinate/layout ambiguity before Wave 3 begins.

### What was audited
- Rockbox theme construction model:
  - cfg/wps/sbs/fms responsibilities,
  - viewport and conditional layout patterns,
  - limits of theme control vs core rendering.
- Sourced implementation patterns:
  - Interpod, Interpod 2, amusicpodds construction methods,
  - PictureFlow plugin draw paths (`apps/plugins/pictureflow/pictureflow.c`),
  - core splash/loading behavior (`apps/gui/splash.c`),
  - target bootloader behavior (`bootloader/ipod-s5l87xx.c`, `bootloader/show_logo.c`).

### Exactness layer added to design lock
- Added strict pre-implementation sections `53` to `57` in `DESIGN_SYSTEM.md` covering:
  - construction-control mapping,
  - exact geometry tokens for `320x240`,
  - surface-by-surface prep constraints,
  - cropping/spacing/polish risk safeguards,
  - exact Wave 3 prep sequence and validation order.

### Boot image planning (required new asset)
- Asset: `Sourced Icons/iPhone-Rebooting.png`.
- Verified dimensions: `640x1136`.
- Locked workflow:
  - compose to black `320x240` canvas,
  - centered Apple logo,
  - no startup text,
  - avoid naive full-frame non-uniform scaling.

### Key no-drift contract
- If a coordinate/token/lane is not explicitly locked in `DESIGN_SYSTEM.md`,
  implementation for that surface is blocked.

### Files touched
- `DESIGN_SYSTEM.md`
- `WORK_LOG.md`

### Build / runtime status
- Not run in this pass (planning/spec lock only).

### Next task queue
1. Execute only Wave 3 scaffolding steps that map to locked sections 53-57.
2. Keep per-surface screenshot validation tied to token table before accepting implementation changes.
3. Block any layout improvisation not backed by explicit tokens.

## 2026-04-07 (Wave 0 packaging/install stabilization)

### Scope
- Continued native Windows/MSYS2 stabilization after compile-path recovery.
- Targeted the remaining packaging/install failure (`rockpod/-`, `fonts/-`) without introducing Wave 3 UI changes.

### Root Cause (Verified)
- `wps/wpsbuild.pl` had fragile value handling in theme asset copy paths:
  - icon path extraction depended on a regex capture (`$1`) that could be stale/empty,
  - theme values containing whitespace around `-` were not normalized before copy decisions.
- This allowed invalid source/destination path fragments to propagate into package/install copy operations.

### Fixes Applied
- Hardened `wps/wpsbuild.pl`:
  - added `trim_value()` and normalized incoming theme values,
  - guarded backdrop/font/icon copy helpers against empty/`-` values,
  - replaced fragile icon-path capture usage with explicit `icons/<file>` extraction and validation,
  - ensured copy helpers no-op safely on invalid placeholders.

### Validation Results (Verified)
- Simulator wrapper (`./build-sim.ps1`):
  - reaches `Creating rockbox-info.txt`,
  - reaches `Installing your build in your 'simdisk' dir`,
  - no recurrence of `cp ... /rockpod/-` or `fonts/-` errors.
- Hardware wrapper (`./build-hw.ps1 -Target ipod6g`):
  - reaches `Creating rockbox-info.txt`,
  - reaches `ZIP rockbox.zip`,
  - no recurrence of packaging `-` path errors.
- Simulator runtime smoke launch:
  - `build-sim/rockboxui.exe` starts successfully (process creation verified).

### Current State
- Wave 0 build reliability blocker has moved from **active packaging failure** to **green native sim/hw packaging path** for validated targets.
- `ipodvideo` full hardware pass remains pending (not yet run in this stabilization slice).

### Files Touched
- `wps/wpsbuild.pl`
- `WORK_LOG.md`

## 2026-04-06 (Wave 2 full-product interface coverage pass)

### Scope
- Expanded Wave 2 from core shell/list rules to full-product interface coverage.
- This pass remains design-system/UX-spec only (no performance and no Cover Flow architecture work).

### New coverage areas locked
- Boot/startup design-system rules (including intended Apple-like reboot presentation).
- Loading/wait-state system across core splash and PictureFlow loading states.
- Full-surface contracts for:
  - home/root,
  - music lists,
  - album list,
  - album page,
  - now playing / WPS,
  - mini-player,
  - Cover Flow UI,
  - Cover Flow tracklist,
  - settings,
  - filesystem lists,
  - fallback/empty states.
- Complete end-to-end user-flow continuity lock.

### Boot image review (new asset)
- Reviewed `Sourced Icons/iPhone-Rebooting.png`.
- Verified header dimensions from file bytes: `640x1136`.
- Locked adaptation direction for iPod startup:
  - black `320x240` canvas,
  - centered Apple mark,
  - no extra startup text in flagship visual mode.

### Selector/scrollbar normalization update
- Added explicit iOS-like guidance into design lock:
  - default active row selection is solid neutral gray (non-gradient),
  - thin right-edge gray scrollbar baseline,
  - pink accent (`#FF2D55`) reserved for music-emphasis states, not default list selection.

### DESIGN_SYSTEM.md expansion result
- Added sections `34` through `52` for full-product Wave 2 coverage and completion gate.
- Added implementation-facing references for startup/loading/PictureFlow surfaces.

### Files touched
- `DESIGN_SYSTEM.md`
- `WORK_LOG.md`

### Build / runtime status
- Not run in this pass (documentation and planning lock only).

### Next task queue
1. Snap remaining ambiguous numeric anchors (header/chevron/scrollbar/battery/mini-player/loading).
2. Begin Wave 3 scaffolding with the expanded full-surface lock.
3. Validate each surface step with simulator screenshots once build path is green.

## 2026-04-06 (Wave 2 -> Wave 3 readiness planning pass)

### Scope
- Implementation-readiness audit only (no broad Wave 3 UI implementation yet).
- Goal: verify whether Wave 2 is specific/stable enough to execute Wave 3 without drift.

### Readiness Findings
- Fully locked and safe now:
  - source hierarchy + donor priority,
  - list geometry tokens (`52/56/48`),
  - inset/divider tokens (`16/76/50`, `0.5px`),
  - flat selector direction and Apple2026 accent token (`#FF2D55`),
  - scrollbar-on/right/subtle direction,
  - glyph-primary icon strategy and icon-state color logic,
  - Interpod base DNA + Interpod2/amusicpodds donor boundaries.
- Still ambiguous (must lock before full shell completion):
  - numeric header alignment anchors,
  - chevron exact placement,
  - final scrollbar width/inset token,
  - battery icon scale and battery-text relation,
  - mini-player exact geometry,
  - loading-state viewport geometry,
  - per-surface final font-size snaps where ranges still exist.

### Wave 3 Implementation Surface Map (locked)
- Theme registration/config source of truth:
  - `wps/WPSLIST`
- New Apple2026 shell files (to be added via WPSLIST flow):
  - `.cfg`, `.sbs`, `.wps`
- Runtime deployment/validation path:
  - `build-sim/simdisk/.rockbox/themes/`
  - `build-sim/simdisk/.rockbox/wps/`
  - `build-sim/simdisk/.rockbox/icons/`
  - `build-sim/simdisk/.rockbox/fonts/`
- Donor reference baselines (read-only extraction sources):
  - `Imported Reference Themes/Interpod/...`
  - `Imported Reference Themes/Interpod 2/...`
  - `Imported Reference Themes/amusicpodds/...`

### Ordered Wave 3 Execution Plan
1. theme scaffolding + token wiring
2. header system
3. list geometry/insets
4. chevron/divider/icon integration
5. selector + scrollbar behavior
6. mini-player continuity
7. WPS alignment
8. loading/empty-state shell
9. whole-shell consistency audit

### Validation Plan
- Rebuild simulator after each major implementation step.
- Capture screenshot sets per step (header, list, icons/chevrons/dividers,
  selector+scrollbar, mini-player, WPS, loading state).
- Compare every set against:
  1) Figma nodes `1:4008`, `1:475`, `1:5998`
  2) Apple references in `MASTER.md`
  3) Interpod baseline
- Mark each step pass/fail with explicit mismatch notes.

### Drift Prevention Lock
- No visual implementation without a corresponding `DESIGN_SYSTEM.md` rule.
- Missing numeric rule = block implementation and lock doc first.
- `WORK_LOG.md` must record screenshots, pass/fail, unresolved deltas, next action.

### Go / No-Go
- **GO** for Wave 3 foundation scaffolding and already-locked token implementation.
- **NO-GO** for full Wave 3 completion until all ambiguous numeric locks are added.

### Files Touched
- `DESIGN_SYSTEM.md`
- `WORK_LOG.md`

## 2026-04-06 (Wave 2 symbol-source determination)

### Scope
- Finalized explicit decision for symbol source strategy:
  - SF-family glyph symbols vs imported icon libraries.

### Determination
- Primary winner: **SF-family glyph symbols** for main UI iconography.
- Imported libraries remain secondary/fallback for tiny status/system edge cases and compatibility.

### Reasoning (implementation-facing)
- Glyph symbols align best with typography lock, preserving Apple-like optical consistency.
- Glyph route scales and recolors more coherently across state sets.
- Imported packs still valuable for validated tiny runtime status assets.

### Source Priority Lock
1. SF glyph symbols (primary)
2. `sf-symbols-master` candidate bitmaps (secondary masters)
3. Interpod/Interpod2 imported icon packs (status/system fallback)
4. amusicpodds icons (targeted-only donor)

### Files Touched
- `DESIGN_SYSTEM.md`
- `WORK_LOG.md`

## 2026-04-06 (amusicpodds comparative deep pass)

### Scope
- Deep comparative audit: `Interpod` vs `Interpod 2` vs `amusicpodds`
- Required focus categories completed:
  1) list geometry
  2) album list behavior
  3) mini-player/lower shell continuity
  4) top navigation/header behavior
  5) icon style/symbol choice
  6) separator treatment
  7) active/inactive color logic
  8) album page composition
  9) scrollbar/selector behavior
  10) overall Apple Music shell alignment

### Inputs Re-verified
- Re-read Figma source nodes:
  - `1:4008` (library shell)
  - `1:475` (album list)
  - `1:5998` (album page)
- Re-read theme files:
  - `Interpod.cfg`, `Interpod.sbs`, `Interpod.wps`
  - `Interpod 2.cfg`, `Interpod 2.sbs`, `Interpod 2.wps`
  - `amusicpodds.cfg`, `amusicpodds.sbs`, `amusicpodds.wps`

### Key Determinations (explicit)
- `Interpod` remains strongest overall base (light shell + full-package cohesion).
- `Interpod 2` is strongest polish/state donor (flat selector behavior, cleaner state handling).
- `amusicpodds` is strongest targeted donor (typography/icon direction) but not base-shell donor.

### Where amusicpodds is closer to Apple Music
- SF Compact-driven typography voice and compact readability experiments.
- Music-first icon semantics and some playback info spacing choices.
- Album-art prominence in WPS composition.

### Where amusicpodds is not closer
- Dark global shell inversion conflicts with Apple2026 light-shell/Figma baseline.
- `scrollbar: off` conflicts with subtle-scrollbar requirement.
- `statusbar: off` baseline conflicts with current Apple2026 shell strategy.
- Accent token drift (`f24e36`) conflicts with Apple2026 accent (`#FF2D55`).

### Spec Updates Applied
- Added explicit three-way comparison section to `DESIGN_SYSTEM.md`:
  - Interpod 1 vs Interpod 2 vs amusicpodds
  - strengths by category
  - inherit/reject map per category
  - final inheritance package and explicit rejects
- Added implementation gate section with per-surface acceptance criteria:
  - library root gate
  - album list gate
  - album page gate
  - lower-shell/mini-player gate
  - donor-compliance gate
- Added token-level donor mapping section:
  - core shell token defaults
  - selection/scroll token defaults
  - typography/icon/lower-shell donor mapping
  - hard rejection token list

### Inheritance Lock (for implementation waves)
- Keep pure Interpod DNA:
  - light-shell base
  - shell coherence
  - lower-shell continuity model
- Pull from Interpod 2:
  - flat selector model
  - state/polish refinements
- Pull from amusicpodds (limited):
  - SF Compact legibility studies
  - select symbol candidates from `amusicpod.bmp`
  - compact playback spacing cues
- Reject from amusicpodds for flagship default:
  - dark-shell base
  - scrollbar-off
  - statusbar-off
  - legacy accent red token

### Build / Runtime Status
- Not run in this pass (documentation/specification-only).

### Next Task Queue
1. Translate inheritance lock into concrete Apple2026 token/state implementation plan (without crossing into Cover Flow/perf branches).
2. Define per-surface acceptance criteria for library, album list, and album page based on this comparison lock.
3. Continue simulator-validated UI implementation once build path is green.

## 2026-04-07

### Scope
- Wave 1 / Wave 2 design documentation pass only
- No implementation edits outside documentation
- No Cover Flow/performance/caching work

### Verified Inputs Re-reviewed
- `MASTER.md` hierarchy and branch boundaries
- User Figma target nodes: `1:4008`, `1:475`, `1:5998` (previously extracted geometry/state data reused)
- Apple references (HIG + support pages) including: Typography, Icons, SF Symbols, Color, Layout, Toolbars, Tab bars, Scroll views, Disclosure controls, Lists and tables, Search fields, Sidebars
- Imported theme set: `Interpod`, `Interpod 2`, `amusicpodds`, `adwaitapod`, `adwaitapod_simplified`, `iClassic_v1.1`, `iPodOS`, `iPone`, `iRB_Modern`

### Documentation Changes
- Rewrote `DESIGN_SYSTEM.md` into a strict, implementation-facing design lock document.
- Added explicit numeric geometry rules for:
  - library rows (`52px`),
  - album rows (`56px`),
  - track rows (`48px`),
  - key insets (`16px`, `76px`, `50px`),
  - hero art (`270px`),
  - separator thickness (`0.5px`).
- Added formal sections for:
  - source hierarchy,
  - Apple principles,
  - Interpod preservation,
  - imported-theme extraction,
  - typography/color/icons/selector/scrollbar/divider/chevron rules,
  - mini-player/tab-bar composition,
  - loading/empty states,
  - anti-patterns,
  - future-agent checklist and validation protocol.

### Verified vs Assumed
- Verified:
  - core geometry tokens and composition rhythm from prior direct Figma extraction,
  - imported theme config/layout direction from prior file audit,
  - Apple guideline principles from fetched pages listed above.
- Assumed:
  - none newly introduced in this pass; this was a synthesis/lock pass using verified prior evidence.

### Files Touched
- `DESIGN_SYSTEM.md`
- `WORK_LOG.md`

### Build / Simulator Status
- Not run in this pass (documentation-only session).

### Next Task Queue
1. Use this expanded `DESIGN_SYSTEM.md` as the single UI lock for subsequent shell implementation waves.
2. During implementation, validate each major surface against Figma/Apple references and log deltas.
3. Keep branch boundaries strict: defer Cover Flow optimization/performance architecture.

## 2026-04-06

### Scope
- Wave 0 and Wave 1 only
- Environment/build validation first
- Simulator validation second
- Design/source audit baseline third
- No Cover Flow optimization work

### Confirmed Decisions
- `MASTER.md` remains the primary source of truth
- `Apple2026` is the flagship classification
- Original `Interpod` remains the strongest base theme
- Figma nodes `1:4008`, `1:475`, and `1:5998` are the strongest visual authority
- Local asset roots are:
  - `Apple Fonts/`
  - `Sourced Icons/`
  - `Imported Reference Themes/`
  - `Sample Music Folder with Library Structure/`

### Build Workflow Progress
- Added Windows wrappers:
  - `build-sim.ps1`
  - `build-hw.ps1`
- Standardized wrappers on MSYS2 `UCRT64` launch instead of plain `MSYS_NT`
- Forced a combined PATH so the hosted SDL tools and `arm-none-eabi-*` toolchain can both be found
- Updated shell scripts to use portable job detection with `JOBS` override
- Patched `tools/configure` so ARM selection accepts `arm-none-eabi-*`
- Patched `build-hw.sh` to default `CROSS_COMPILE=arm-none-eabi-`

### Current Build State
- Hardware toolchain detection is working:
  - `ipod6g` configure now resolves `arm-none-eabi-gcc 13.3.0`
- Environment-level blocker is resolved:
  - previous `arm-elf-eabi-*` failure is no longer the primary issue
- Dependency generation/build order has been hardened:
  - `build-sim.sh` and `build-hw.sh` now run `make dep` explicitly
  - both scripts pre-generate key headers before parallel compile (`lang_enum.h`, `lang/lang.h`, `sysfont.h`, `bitmaps/rockboxlogo.h`, `bitmaps/default_icons.h`, etc.)
- `make.dep` parser instability (`multiple target patterns`) is no longer the active blocker in current runs
- Generated-header races (`bitmaps/rockboxlogo.h`, `lang_enum.h`) are resolved for main compile flow
- Simulator compile now reaches completion of core and plugin compilation and produces `build-sim/rockboxui.exe`
- Simulator executable launch smoke test succeeded on Windows (`Start-Process` returned a valid PID)
- Hardware `ipod6g` build now reaches zip phase (`ZIP rockbox.zip`)
- `ipodvideo` smoke validation was not run because `ipod6g` is not yet green

### Active Packaging / Install Blocker
- Both simulator `make install` and hardware packaging currently report:
  - `cp: cannot stat '/c/.../rockpod/-': No such file or directory`
  - `ERROR: Error opening file: /c/.../rockpod/fonts/-`
- This appears in buildzip/install packaging stage, after successful compilation.
- Build artifact status is therefore:
  - compile artifacts: **verified present** (`rockboxui.exe`, hardware objects/zip stage)
  - packaging/install stage: **still unstable**

### WSL Fallback Status (Verified)
- WSL fallback is now accepted as secondary canonical build path if native Windows remains unstable.
- Current machine status check:
  - `wsl --status` returns `WSL_E_WSL_OPTIONAL_COMPONENT_REQUIRED`
  - message indicates WSL optional component install is pending and system reboot may be required
- Current blocker to WSL continuation:
  - reboot required before Ubuntu provisioning and WSL-based toolchain steps can proceed

### Build-System Files ToucheOpenRouterd
- `tools/configure`
- `tools/root.make`
- `firmware/firmware.make`
- `apps/apps.make`
- `apps/lang/lang.make`
- `apps/bitmaps/bitmaps.make`
- `apps/plugins/bitmaps/pluginbitmaps.make`
- `build-sim.sh`
- `build-hw.sh`
- `build-sim.ps1`
- `build-hw.ps1`

### Design Audit Baseline
- Figma findings locked into `DESIGN_SYSTEM.md`
- Imported theme set inventoried:
  - `Interpod`
  - `Interpod 2`
  - `amusicpodds`
  - `adwaitapod`
  - `adwaitapod_simplified`
  - `iClassic_v1.1`
  - `iPodOS`
  - `iPone`
  - `iRB_Modern`
- `Apple Fonts/SF Pro` confirmed with full Display/Text/Rounded families
- `Sourced Icons/Figma File as SVG.svg` confirmed
- `Sourced Icons/sf-symbols-master` confirmed as the main symbol inventory
- Sample music library confirmed with album-artist -> album -> track structure and album covers

### Simulator / Screenshot Status
- Simulator launch not completed
- No screenshots captured in this pass
- Screenshot comparison remains pending until generated-asset builds are stable

### Next Task Queue
1. Reboot Windows so WSL optional component can finish activation
2. Re-check `wsl --status` and `wsl -l -v`; if healthy, provision Ubuntu path
3. If native Windows is still unstable, switch canonical build flow to WSL Ubuntu
4. Isolate and fix the buildzip/install `fonts/-` and `rockpod/-` packaging-source issue
5. Re-run simulator validation and capture baseline screenshots once packaging/install is stable

---

### Wave 3 — ecosystem adaptation note + progress-rail parity (2026-04-07)
- **Design intent:** Documented in `DESIGN_SYSTEM.md` §33.7.1 — Figma/iOS references define *language*
  (hierarchy, separators, polish); **§54** iPod tokens are authoritative for shipped geometry; goal is
  same ecosystem, not literal phone clone.
- **Code:** `A26_PROGRESS_TRACK` (`E5E5EA`) added in `apps/apple2026_shell.h`; splash loading bar rail
  uses it (`apps/gui/splash.c`). Picture Flow indexing/loading rails aligned to same token
  (`apps/plugins/pictureflow/pictureflow.c` — `draw_progressbar`, `show_track_list_loading`).
- **Verified:** Logic-only / token alignment; simulator screenshot pass still pending packaging stability.
- **Next:** Continue Wave 3 per §33.5 (remaining shell surfaces); build when `make install`/zip path is green.

### Wave 3 — shell stack documentation + mini-player token alignment (2026-04-07)
- **`DESIGN_SYSTEM.md` §54.1 / new §54.1.1:** Replaced ambiguous `content_h_without_footer` with SBS-accurate
  viewport heights; documented `%?mp` / `%?Lo` routing and vertical stack for `wps/Apple2026.sbs`.
- **`wps/Apple2026.sbs`:** Mini-player title/meta text lanes `x` **46→48**, width **228→226** to match §54.5
  `mini_player_title_x = 48` (right edge unchanged at 274).
- **Verified:** Arithmetic `27+177=204`, `51+153=204`, `51+189=240` (stopped + large title) consistent with routing.
- **Next:** Screenshot pass for list+mini and root large-title when build is green; optional viewers icon strip parity.

### Wave 3 — cross-reference verification pass vs reference themes + geometry fixes (2026-04-07)

**Audit scope:** Compared Apple2026 `.sbs`/`.wps` coordinates against both DESIGN_SYSTEM.md
(§54/§27.1) and the available reference theme files (`adwaitapod_dark_simplified`,
`Themify_2`). No Interpod/Interpod2 theme files exist in-tree; these two themes served
as the only structural reference for viewport patterns.

**Reference theme observations (structural, not stylistic):**
- Both refs use 24-25px headers; Apple2026's 26px is intentional and documented.
- Neither ref uses a bottom mini-player bar — both use sidebar widgets. Apple2026's
  bottom mini-player is an Apple Music-inspired design choice, documented in §54.5.
- Both refs place metadata BESIDE left-aligned art (horizontal layout). Apple2026 places
  metadata BELOW centered art (Apple Music vertical stack). Intentional per §70.5.2.
- Both refs place playlist counter on the RIGHT side, not overlapping art.
- Themify_2 uses 30px row height; adwaitapod uses 20-22px rows.

**Issues found and corrected:**

1. **Large title band: 24px→32px** — §27.1 explicitly states the Wave 3 rebuild uses a
   32px-tall large-title band (y=27..58) with list content starting at y=59. The previous
   SBS used the old §54.1 values (24px band, content at y=51). Fixed:
   - `%Vl(large_title,16,27,-16,24,2)` → `%Vl(large_title,16,27,-16,32,2)`
   - `%Vi(content_with_mini_lt,0,51,-,153,-)` → `%Vi(content_with_mini_lt,0,59,-,145,-)`
   - `%Vi(content_full_lt,0,51,-,189,-)` → `%Vi(content_full_lt,0,59,-,181,-)`
   - 22px font in 32px band gives 5px padding per side — much more Apple-like.
   - Updated §54.1 in DESIGN_SYSTEM.md: `content_y_large_title = 59`,
     `list_viewport_h_with_mini_lt = 145`, `list_viewport_h_no_mini_lt = 181`.

2. **Playlist counter: moved from art zone to artist line** — user confirmed the old
   viewport at `%V(16,-100,64,14,9)` (absolute y=140) was creating a visible white
   rectangle in the art zone. Relocated to right-aligned on the artist line:
   - Removed old `%V(16,-100,64,14,9)` playlist counter.
   - Narrowed artist viewport from `-16` (288px) to `224px` to make room.
   - Added `%V(248,192,56,18,9)` — right-aligned "%pp/%pe" in tertiary gray (6E6E73),
     same y-line as artist text. Clean Apple-like format.

**Coordinates confirmed correct (all other areas):**
- Header: (0,0,-,26) with hairline, title at (74,5), battery at (288,4) — all match §54.2.
- Content viewports (non-LT): y=27, h=177/213 — match §54.1.
- Mini-player: y=204, h=36, art (8,207), title (48,212), meta (48,226), playpause (284,214) — all match §54.5.
- WPS: art 156x156 at (82,9), title y=172, progress y=210, time y=224 — all match §54.6.
- Volume overlay: both SBS and WPS speaker icons at correct viewport-relative positions.

**Verified:** Full line-by-line SBS and WPS coordinate audit against §54, §27.1, and reference theme structural patterns.

### Wave 3 — Apple Music visual-parity pass (2026-04-07)

**Goal:** Direct image comparison between Apple Music Library reference screenshot and
current iPod build photo. Correct the visual deltas to bring the main menu much closer
to the Apple Music design ecosystem.

**Key findings from direct image comparison:**
- Apple Music shows 5-6 tall rows; iPod showed 9 cramped rows.
- Apple Music has 16px left inset; iPod icons were flush to screen edge.
- Apple Music has generous icon-to-text gap; iPod had 2px gap.
- Apple Music large title dominates; iPod had competing header + large title.
- Apple Music icons are all red/pink; iPod mixed red/black/gray.

**Changes made:**

1. **Row height 20→32px** — changed icon tile height in `tools/apple2026_symbol_assets.py`
   from `ICON_TILE_H=20` to `ICON_TILE_H=32`. Since Rockbox row height =
   `max(font_height, icon_height)`, 32px tiles drive 32px rows. Visible items drop from
   9 to 5-6, matching Apple Music density.

2. **Icon padding 1→6px** — changed `ICON_PADDING` in `apps/gui/bitmap/list.c` from 1 to 6.
   Adds 6px before and 6px after each icon in the list, creating icon column width of
   22+12=34px. Proper icon-to-text gap now exists.

3. **List viewport inset** — all four `%Vi` content viewports in `Apple2026.sbs` changed
   from `x=0, w=full` to `x=16, w=-16` (i.e., `%Vi(...,16,...,-16,...)`). This creates
   16px left and right margins, matching Apple Music's inset. Dividers naturally span only
   288px (viewport width), creating inset dividers without code changes.

4. **Large title font 22→25px Bold** — SBS slot 2 changed from `22-SFCompactDisplay-Semibold`
   to `25-SFProDisplay-Bold`. The large title "Rockbox" now dominates the screen like Apple
   Music's "Library" dominates its view.

5. **Header title hidden on root** — when `%Lo` (root screen), the SBS header title text
   viewport is not drawn. This removes the redundant double "Rockbox" effect (header +
   large title both showing "Rockbox"). The header still shows battery, play status, and
   busy indicators. On non-root screens, the header title resumes as before.

6. **Icon tint: black→gray** — removed the `CLR_ON_LIGHT` (black) icon category entirely.
   Icons that were black (Folder, Cursor, Submenu) are now tertiary gray (`3C3C43`).
   Expanded accent set to include Folder (1), Plugin (9), System menu (24), Playback
   menu (25) for stronger red/pink emphasis at top-level.

7. **Icon regeneration** — ran `apple2026_symbol_assets.py` with updated tile dimensions
   and tinting. All 32 icon tiles regenerated at 22x32 with adjusted padding.

**Documentation updated:**
- `DESIGN_SYSTEM.md` §54.1: added `list_viewport_x=16`, `list_viewport_w=288`, `right_inset=16`.
- `DESIGN_SYSTEM.md` §54.1.1: documented header-title-hidden-on-root behavior.
- `DESIGN_SYSTEM.md` §54.3: replaced abstract Figma-derived geometry with actual Rockbox
  implementation values: `icon_tile_h=32`, `icon_padding=6`, `icon_column_w=34`,
  `text_start_x=50`, visible row counts per viewport mode.
- `DESIGN_SYSTEM.md` §27.1: updated large title from 22px Compact to 25px Pro Display Bold.
- `wps/WPSLIST`: updated comment to reflect 22x32 tile dimensions.

**Files changed:**
- `apps/gui/bitmap/list.c` — ICON_PADDING 1→6
- `tools/apple2026_symbol_assets.py` — tile height, tinting, padding
- `wps/Apple2026.sbs` — font slot 2, viewport insets, header routing
- `wps/WPSLIST` — comment update
- `icons/Apple2026Icons.bmp` — regenerated
- `wps/Apple2026/*` — all WPS assets regenerated
- `DESIGN_SYSTEM.md` — geometry tokens updated
- `WORK_LOG.md` — this entry

**Expected visual result:**
- Root menu shows bold "Rockbox" title dominating top, no competing header text.
- Menu rows are 32px tall with ~5-6 visible items (was 9).
- Icons are inset 22px from screen edge (16px viewport + 6px padding).
- 12px gap between icon right edge and text start.
- Dividers span viewport width (288px), naturally inset 16px from each screen edge.
- Red/pink accent on music-first icons; gray on secondary/settings icons.
- No black icons anywhere.

**Next:** Hardware build and on-device verification.

### Wave 4 — Major correction pass (menu + WPS + Cover Flow) (2026-04-07)

**Goal:** Comprehensive correction pass addressing user's 14-point list of outstanding
issues across main menu, WPS, and Cover Flow. Direct visual comparison against Apple
Music reference screenshot and iPod screen photo.

**Changes made:**

1. **DESIGN_SYSTEM.md icon_tile_w 22→28** — previous pass changed the icon tile width
   in the Python script but failed to update the design token table. §54.3 now correctly
   documents `icon_tile_w=28`, `icon_column_w=40`, `text_start_x=56`.

2. **WPSLIST comment 22x32→28x32** — updated icon strip dimensions comment to match
   actual 28x32 tile size from the generation script.

3. **WPS first-play rendering bug FIXED** — root cause identified: the album art viewport
   in `Apple2026.wps` had `%VB` (output-to-backdrop-buffer) flag, causing art to render to
   the backdrop framebuffer instead of the main display. On first WPS entry, the backdrop
   buffer was empty, so the art area showed blank/black. On re-entry, the cached backdrop
   had art from the previous render. Fix: removed `%VB` from the art viewport. Art now
   renders directly to the main display, visible on first frame. Also added explicit
   `%Vf(000000)%Vb(F8F8F8)` to the backdrop viewport as defensive fallback.

4. **Right-side chevrons IMPLEMENTED** — added C-level chevron drawing to
   `apps/gui/bitmap/list.c` in `_default_listdraw_fn()`. After each `put_line()` call,
   a 4x9 pixel ">" chevron is drawn at the right edge of the list text viewport using
   `display->drawline()`. Color: `C7C7CC` (light gray, Apple-subtle). Positioned at
   `vp_width - 10` horizontally, vertically centered in the row. Only drawn on color
   displays (`HAVE_LCD_COLOR && depth >= 16`) and non-title items. This was previously
   identified as impossible with Rockbox's bar selector style — solved by drawing the
   chevron after the standard line rendering.

5. **Cover Flow: fullscreen by default** — changed `show_statusbar` default from `true`
   to `false` in `apps/plugins/pictureflow/pictureflow.c`. Cover Flow now launches
   without the SBS header, using the full 320x240 screen. Eliminates the white bar
   under the header that covered album cover tops.

6. **Cover Flow: "Cover Flow" title removed** — all 4 `sb_set_persistent_title("Cover Flow",...)`
   calls changed to empty string. With statusbar disabled, this is redundant, but also
   ensures no title shows if user manually re-enables statusbar.

7. **Icon regeneration** — ran `apple2026_symbol_assets.py` with the corrected
   `ICON_TILE_W=28, ICON_TILE_H=32, padding=2, scale=0.92`. All icons regenerated
   at 28x32 with ~23px artwork centered in each tile.

**Documentation updated:**
- `DESIGN_SYSTEM.md` §54.3: `icon_tile_w` 22→28, derived values updated.
- `DESIGN_SYSTEM.md` §54.4: chevron tokens updated to match C implementation
  (4x9px drawline, `C7C7CC`, inset 6).
- `wps/WPSLIST`: comment updated to 28x32.
- `WORK_LOG.md`: this entry.

**Files changed:**
- `apps/gui/bitmap/list.c` — right-side chevron drawing code
- `apps/plugins/pictureflow/pictureflow.c` — show_statusbar=false, title text removed
- `wps/Apple2026.wps` — removed `%VB` from art viewport, added explicit colors to backdrop
- `wps/WPSLIST` — comment update
- `icons/Apple2026Icons.bmp` — regenerated
- `wps/Apple2026/*` — all WPS assets regenerated
- `DESIGN_SYSTEM.md` — §54.3 icon_tile_w, §54.4 chevron tokens
- `WORK_LOG.md` — this entry

**Known limitations documented (not fixable in theme layer):**
- **Font kerning/tracking:** Rockbox `.fnt` format (BDF-derived) does not support
  kerning pairs. The `convttf` tool that converts TTF→BDF→FNT drops kerning tables.
  Letter pairs like ab, li, lu, am, ar will appear too tight. Fixing this requires
  modifying the font renderer or `convttf` tool, which is beyond UI/UX scope.
- **22px body font:** No 22px SF Pro Text TTF source was found in `Apple Fonts/`
  for generation. Current body font remains 19px. If a TTF source becomes available,
  `convttf` can generate the 22px variant.

**Expected visual results:**
- Right-side light gray chevrons on all list items.
- Cover Flow launches fullscreen without header bar or white gap.
- WPS renders correctly on first song play (no black bars / missing art).
- Menu icons at 28x32 tiles with ~23px artwork.

**Remaining items for next pass:**
- On-device visual verification of all changes.
- Potential 22px body font if TTF source is located.
- WPS layout refinement (Interpod-grounded improvements).

### WPS Master Rebuild — Apple2026 WPS stop-regression pass (2026-04-08)

**Goal:** Full stop-regression rebuild of `wps/Apple2026.wps` from Interpod's proven
structural baseline. Prior WPS kept regressing (blank art on first open, cropped times,
font-missing fallback, duplicate image IDs, non-ASCII encoding issues, misaligned metadata).

**Root causes identified (full history audit):**
1. `%VB` removed from art viewport in a prior pass ("fix" for first-open blank art) — this was
   the WRONG fix. Removing `%VB` from the art viewport breaks Rockbox's album art compositor.
   The correct fix is to keep `%VB` on the art viewport (Interpod's proven pattern) and ensure
   `%Cl`/`%Cd` live inside that viewport.
2. `16-SFProText-Regular.fnt` referenced — this file does not exist in `fonts/`. Font-missing
   causes the skin parser to fail and fall back to the default WPS.
3. `albumShadow.bmp` preloaded with `%xl(AlbumShadow,...)` AND drawn with `%x(AlbumShadow,...)`
   — duplicate image ID causes parse failure and WPS fallback.
4. Non-ASCII characters (em-dashes U+2014) in comments — some Rockbox parser versions
   fail on non-ASCII bytes in WPS files even in comments.
5. Over-engineering: extra viewport layers, experimental shadow assets, 5 font slots — each
   additional complexity added another failure surface.

**Rebuild approach:**
- `wps/Apple2026.wps` completely rewritten from Interpod's source as strict structural baseline
- Applied only the specific requested changes on top of Interpod's proven structure
- Verified every change against audit script before accepting

**Changes from Interpod baseline:**
- Art: 130x130 -> 150x150 (+15%), centered at x=85 (was x=95 for 130px art)
- Font slot 3: `14-SFProText-Regular.fnt` (was `15-Inter-Bold.fnt`)
- Font slot 8: `20-SFProText-Regular.fnt` (was `20-Inter-SemiBold.fnt`)
- Font slot 9: `16-SFProText-Medium.fnt` (was `20-Inter-V.fnt`)
- Artist/album split into two separate viewports (Interpod combined them in one)
- Artist color: `FF2D55` Apple red (Interpod: `F24E61`)
- Album: separate gray line below artist
- Playlist counter: right-aligned on title line (Interpod: separate top row `%V(18,-100,...)`)
- `albumFramed.bmp` NOT used (it is 130x130 and would misrender at 150x150)

**Anti-regression audit results (python tools/audit_apple2026_wps.py):**
- A. Non-ASCII: 0 chars. PASS
- B. Image IDs: no duplicates; all %xd refs resolve. PASS
- C. Fonts: all 3 referenced .fnt files exist on disk. PASS
- D. BMP assets: all 19 referenced .bmp files exist on disk. PASS
- E. %VB art viewport: %Cl confirmed inside %VB viewport. PASS

**Files changed:**
- `wps/Apple2026.wps` — complete rebuild from Interpod baseline
- `tools/audit_apple2026_wps.py` — improved audit script (multi-frame %xl aware)
- `DESIGN_SYSTEM.md` §54.6 — updated with locked geometry, font slots, and 10 anti-regression rules

**WPS anti-regression contract (do not violate):**
1. %VB must stay on the art viewport
2. %Cl and %Cd must be inside the %VB viewport
3. Font slots 3/8/9 only; no reference to non-existent .fnt files
4. No duplicate image IDs
5. No non-ASCII characters (including comments)
6. albumShadow.bmp: if preloaded, must be drawn via %xd only (not %x)
7. albumFramed.bmp: only valid for 130x130 art
8. Run audit script before committing any future WPS change

**Next:** On-device or simulator verification of WPS layout.

### Wave 4 — Bounded-stack navigation (loop prevention) (2026-04-09)

**Goal:** Prevent the WPS back-path from re-entering a stale content chain when
the user accesses "Now Playing" from Main Menu after already backing out of that
chain. Eliminates the Main Menu -> WPS -> Cover Flow -> Main Menu infinite loop.

**Root cause identified:**
`playback_source` is a session-global tag stamped when playback starts. It
persists until new playback starts from a different surface. When a user backed
all the way out of a content chain (e.g. Cover Flow -> tracklist -> WPS -> Cover
Flow -> Main Menu) and then re-entered WPS from "Now Playing" on Main Menu, the
stale `playback_source` (still `PICTUREFLOW`) would route them back into Cover
Flow -- a chain they had already closed. This created a circular navigation loop.

**Design principle:** WPS back-path must depend on **how** WPS was entered this
time, not just on where playback was started. Main Menu is a stable ceiling.
Re-entering WPS from Main Menu is a "flat entry" -- back returns to Main Menu.

**Implementation:**
1. Added `bool wps_entered_from_root` global in `apps/root_menu.c`, declared
   `extern` in `apps/root_menu.h`.
2. Set `wps_entered_from_root = (last_screen == GO_TO_ROOT)` in the root menu
   dispatch loop before `GO_TO_WPS` is loaded. Covers both `CONFIG_TUNER` and
   non-tuner paths.
3. Added gatekeeper at top of `wps_handle_browse_parent()` in `apps/gui/wps.c`:
   if flag is `true`, returns `GO_TO_ROOT` without consulting `playback_source`.
   All existing source-aware routing preserved for content-chain entries.

**Entry-path verification (all correct):**
- Main Menu -> "Now Playing" -> WPS: `last_screen == GO_TO_ROOT` -> flag=true -> back=Main Menu.
- Cover Flow -> play -> WPS: `last_screen == GO_TO_PICTUREFLOW` -> flag=false -> back=Cover Flow.
- Music -> play -> WPS: `last_screen == GO_TO_MUSICLIB` -> flag=false -> back=Music.
- Database -> play -> WPS: `last_screen == GO_TO_DBBROWSER` -> flag=false -> back=Database.
- Playlist catalog -> play -> WPS: `last_screen == GO_TO_PLAYLISTS_SCREEN` -> flag=false -> back=Playlists.
- Playlist viewer -> play -> WPS: `last_screen == GO_TO_PLAYLIST_VIEWER` -> flag=false -> back=Playlist viewer.
- Boot auto-resume -> WPS: `last_screen == GO_TO_ROOT` -> flag=true -> back=Main Menu.
- MENU long (Home) from WPS, then "Now Playing": flag=true -> back=Main Menu.

**Files changed:**
- `apps/root_menu.h` -- added `extern bool wps_entered_from_root` declaration
- `apps/root_menu.c` -- added flag definition + setter in `GO_TO_WPS` dispatch
- `apps/gui/wps.c` -- added gatekeeper in `wps_handle_browse_parent()`
- `DESIGN_SYSTEM.md` -- added bounded-stack navigation subsection to section 21A
- `WORK_LOG.md` -- this entry

**Next:** Build verification (simulator and/or hardware).

---

### WPS Correction Pass (fresh-eyes photo review) (2026-04-09)

**Trigger:** User photo of on-device WPS revealed multiple visual bugs.

**Bugs identified from photo:**

1. **Thick black border around art** - caused by `wpsArtCorners.bmp` corner mask
   viewport (`%V(82,5,156,156,-)`) with white background (`%Vb(FFFFFF)`) that was 3px
   larger on each side than the 150x150 art viewport. The magenta-keyed corner mask
   was not rendering correctly, leaving a visible white/dark frame artifact.
2. **Song title way too big** - font slot 8 (20px Medium) dominated the whole bottom
   zone and made the composition feel unbalanced.
3. **Album title cropping into progress bar** - three separate text lines
   (title 20px + artist 16px + album 14px = 50px) plus progress bar and time row
   all competed in 82px below the art. Album line was running into the progress bar.
4. **Bottom zone too cramped** - no breathing room between any elements.
5. **Album art missing (placeholder)** - expected on real hardware when tracks have
   no embedded art; placeholder was visible but functional.

**Fixes applied:**

- `wpsArtCorners.bmp` corner overlay viewport **removed entirely** - clean square art,
  no border artifact. Simplest reliable fix; rounded corners can be revisited later.
- Art stays **150x150 at x=85, y=8** (perfectly centered on 320px screen) - user
  confirmed they like this size.
- Title font: **slot 8 (20px) -> slot 9 (16px Medium)** - reduced to stop dominating.
- Artist + Album **collapsed to one alternating line** (Interpod pattern): two named
  viewports (`artist_line` red / `album_line` gray) at same y position with inverse
  `%t(5)` subline timing. Saves 14-16px vertical height.
- Bottom zone **rebalanced** with gaps between every element:
  - Title y=162 (gap 4px from art bottom)
  - Artist/Album y=183 (gap 4px from title)
  - Progress bar y=203 (gap 4px from artist/album)
  - Time row y=211 (gap 4px from progress bar)
  - 15px bottom padding remaining
- Volume bar coordinates updated to match new bottom zone.

**Audit result:** ALL CHECKS PASSED (non-ASCII, image IDs, fonts, BMPs, %VB).

**Files changed:**
- `wps/Apple2026.wps` -- WPS correction pass

**Anti-regression note:** `wpsArtCorners.bmp` remains on disk as an asset but is
no longer referenced in the WPS. Do not re-add unless art viewport dimensions are
verified to match the corner mask bitmap exactly (it was sized for 150x150 but the
overlay was 156x156 causing misalignment).

**Next:** Simulator build + screenshot verification of new layout.

---

### Major Apple2026 Polish Pass — System-Level Rebuild (2026-04-09)

**Goal:** Comprehensive system-level polish pass addressing 14 user-reported issues.
This pass went beyond theme-layer patches into core Rockbox code where needed.

**Root causes identified and fixed:**

1. **System-wide text clipping** — SBS viewport heights were sized to nominal font
   point sizes (e.g., "16pt" = 16px viewport) instead of actual RB12 bitmap heights
   (16pt font = 20px bitmap). Every viewport using font slot 3 was clipping 3-5px;
   the large title viewport clipped 1px of "Library."

2. **WPS progress bar regression** — Bitmap pill bars were removed in a prior pass
   (due to a right-edge artifact) and replaced with code-drawn flat rectangles.
   Rockbox has no native rounded-rect primitive, so bitmap-based bars are required
   for the pill shape.

3. **Music library back-navigation regression** — `path_is_curated_music_library_root()`
   was checking `browse->root` (which could be a deep resumed path like
   `/Music/Artist/Album/`) instead of `tc.currdir`. When `browse->root` was deep,
   the intercept at `/Music/` never fired, and users fell through to filesystem
   root `/` seeing Calendar/Contacts/Notes.

**Changes made:**

1. **SBS viewport height corrections** (Apple2026.sbs):
   - `large_title`: h=30 -> h=32 (font slot 2, RB12 h=31)
   - `title` / `titlewide`: h=17 -> h=20 (font slot 3, RB12 h=20)
   - `batterytext` / `batterytext_root`: h=15 -> h=20
   - `mp_track` / `mp_track_noart`: h=16 -> h=20
   - Header background: 28px -> 30px
   - Content viewport starts adjusted: y=29/40 -> y=30/38
   - Battery icon positions moved up 2-4px (user requirement #4)
   - All icon/indicator y-positions adjusted to match new header geometry

2. **WPS complete rebuild** (Apple2026.wps):
   - All viewport heights corrected for actual RB12 font heights
   - Title VP: h=17 -> h=20 (font slot 9, RB12 h=20)
   - Artist/Album VP: h=16 -> h=18 (font slot 3 = 14pt, RB12 h=18)
   - Battery text VP: h=15 -> h=18
   - Playlist counter VP: h=14 -> h=18
   - Elapsed/remaining time VPs: height corrected to 18
   - Progress bars: restored bitmap pill bars (pb.bmp, pb_backdrop.bmp,
     pb_active.bmp, pb_active_backdrop.bmp) via %xl preloads + image/backdrop params
   - Volume bar: restored bitmap pill bars (vb.bmp, vb_backdrop.bmp)
   - Bottom-zone layout recalculated for corrected font heights

3. **Music library back-navigation fix** (apps/tree.c):
   - Changed intercept at `ACTION_STD_CANCEL` to check `tc.currdir` against
     `/Music/` instead of `browse->root`. Now catches the `/Music/` boundary
     regardless of the resumed depth, preventing fall-through to filesystem root.

4. **Icon color model rework** (tools/apple2026_symbol_assets.py):
   - Changed from mixed red/grey to: all icons red EXCEPT structural nav chrome
     (cursor, submenu chevrons, moving indicator). Main menu now reads as a
     strong red Apple Music-style icon surface.
   - Icon scale reduced from 1.0 to 0.88, padding increased from 1 to 3,
     giving better proportion with both 18pt and 16pt text tiers.

5. **Semantic music icons** (apps/gui/icon.h, apps/tree.c, apple2026_symbol_assets.py):
   - Added `Icon_Artist` (person.fill) and `Icon_Album` (square.stack.fill) to
     the themable_icons enum (iPod targets only, guarded by MODEL_NUMBER).
   - Icon strip extended from 32 to 34 tiles.
   - `tree_get_fileicon()` now returns `Icon_Artist` for directories at music
     library depth 0 and `Icon_Album` at depth 1+, when `BROWSE_APPLE2026_MUSICLIB`
     flag is set.

6. **Menu density improvement** (apps/gui/list.c):
   - Normal tier row floor: 32px -> 30px (gains ~1 visible row with mini-player)
   - Dense tier row floor: 30px -> 28px (gains ~1 visible track row)
   - With 30px rows + 38px large title + 44px mini-player:
     root+playing shows 5 items (was 4). Root+stopped shows 6 (was 5).

7. **Icon asset regeneration** (icons/Apple2026Icons.bmp + all wps/Apple2026/*.bmp):
   - Regenerated via apple2026_symbol_assets.py with updated color model + scale.
   - 34-tile strip verified (all tiles have ink content).

**Files changed:**
- `wps/Apple2026.sbs` — viewport heights, header geometry, battery position
- `wps/Apple2026.wps` — complete rebuild with corrected heights + pill bars
- `wps/WPSLIST` — updated geometry comments
- `apps/tree.c` — back-navigation fix + semantic music icons
- `apps/gui/list.c` — row floor reduction (32->30 normal, 30->28 dense)
- `apps/gui/icon.h` — added Icon_Artist, Icon_Album
- `tools/apple2026_symbol_assets.py` — icon color model + scale + new icons
- `icons/Apple2026Icons.bmp` — regenerated (34 tiles)
- `wps/Apple2026/*` — all WPS assets regenerated

**WPS audit result:** ALL CHECKS PASSED (non-ASCII, image IDs, fonts, BMPs, %VB).

**What required core Rockbox changes vs theme-level:**
- CORE: `apps/gui/icon.h` (new icon enum entries), `apps/gui/list.c` (row floors),
  `apps/tree.c` (navigation intercept + icon assignment)
- THEME: `Apple2026.sbs`, `Apple2026.wps`, `WPSLIST`, icon/asset generation

**What still remains:**
- On-device or simulator visual verification of all changes
- Verify pill bar BMPs render without right-edge artifact at new dimensions
- Verify `Icon_Artist` and `Icon_Album` render correctly in music browser
- Fine-tuning of artist/album subline timing if still unstable
- Settings menu icon grey distinction (currently all red except nav chrome;
  runtime context-aware tinting would require icon rendering code changes)

**Next:** Build verification (simulator and/or hardware).

---

## 2026-04-10 — Music-library back-navigation deep audit and fix

**User report:** "The flow from music to albums and then back still returns me to the file menu sometimes" — intermittent regression.

**Deep audit findings (4 bugs identified):**

**Bug 1 — `browse_current` poisoned the resume path for `GO_TO_MUSICLIB`.**
When `Settings → General Settings → File Browser → Follow Playlist` is ON and the user returns from WPS, the old code set `folder = current_track_path` (e.g. `/Music/Artist/Album/Song.mp3`). This opened the music session at the album folder depth, bypassing the curated-root logic. Fixed by removing the `browse_current` / `last_screen == GO_TO_WPS` branch for `GO_TO_MUSICLIB` entirely — the music library always resumes at the last-visited music folder (validated under `/Music/`) or the library root.

**Bug 2 — `last_music_folder` was not validated to stay inside `/Music/`.**
The post-browse save only reset to `/` when there was no second separator. A weird non-Music path with a separator would persist. Fixed by checking `strncmp(last_music_folder, "/Music", 6)` on both entry and exit.

**Bug 3 — `GO_TO_PREVIOUS` from the music library browse could open `GO_TO_FILEBROWSER`.**
`dirbrowse()` returns `GO_TO_PREVIOUS` when `ft_load` fails on a stale path. In `load_screen()`, `GO_TO_PREVIOUS` restores `last_screen` to whatever was before Music. If that was `GO_TO_FILEBROWSER = 0`, root_menu routes to the file browser. Fixed by intercepting `GO_TO_PREVIOUS` from `GO_TO_MUSICLIB` and mapping it to `GO_TO_ROOT`.

**Bug 4 — Apple2026 tree.c guard lacked `dirlevel <= 1` safety.**
Added `tc.dirlevel <= 1` to the guard to ensure it only fires at the music root level, not from a deep subfolder with a miscounted dirlevel.

**Files changed:**
- `apps/root_menu.c` — removed `browse_current` path for MUSICLIB, strengthened `last_music_folder` validation, added `GO_TO_PREVIOUS → GO_TO_ROOT` intercept
- `apps/tree.c` — added `dirlevel <= 1` guard condition

**Expected behavior after fix:**
- Music → Artists view → back: goes to main menu (1 press from library root)
- Music → Artist → Albums → back: Artists (1), then back → main menu (1)
- Never exposes the raw filesystem browser

