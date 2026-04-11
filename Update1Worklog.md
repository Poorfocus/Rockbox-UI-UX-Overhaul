# Update1Worklog.md -- Execution Log for update-1 Branch

---

## 2026-04-10 -- Branch creation

**Branch:** `update-1` created from `release` HEAD.

**Documents created:**
- `Update1Design.md` -- design authority for this pass
- `Update1Worklog.md` -- this file

---

## 2026-04-11 -- Major Quick Screen rewrite

### Root cause audit

The Apple2026 Quick Screen had become architecturally unstable because two
different systems were drawing it at once:
- Rockbox native Quick Screen still rendered from `apps/gui/quickscreen.c`
- `wps/Apple2026.sbs` drew a second full custom Quick Screen overlay for
  `current screen == ACTIVITY_QUICKSCREEN`

The supposed hidden native viewport was also not actually hidden:
- `qs_empty` was positioned at `180,0,88,61`, which is still on-screen
- the native Quick Screen was therefore still clearing and repainting a
  visible rectangle underneath the SBS overlay

This was the leading cause of the black-box flicker and unstable redraw
behavior.

### Rebuild approach

**Files changed:** `apps/gui/quickscreen.c`, `wps/Apple2026.sbs`,
`apps/apple2026_shell.h`, `tools/apple2026_lockscreen_assets.py`

Rebuilt Apple2026 Quick Screen around a single visible renderer:
- SBS now provides shell/header behavior only
- Quick Screen content itself is now drawn directly in
  `apps/gui/quickscreen.c`
- removed the pill-button overlay model
- removed the `qs_empty` hidden-viewport workaround
- added a real `qs_content` viewport below the compact header

### New Quick Screen design

The new Quick Screen is intentionally simpler:
- clean text-first 4-direction layout
- subtle center directional indicators
- thin bottom volume rail
- white background with black primary text and gray secondary labels
- no giant red pills
- no bitmap-driven chrome required for the active Quick Screen path

### Validation

Executed:

```text
.\build-sim.ps1 -Incremental -SkipDep
.\build-sim.ps1 -InstallOnly
.\tools\verify-sim-install.ps1
```

Result:
- simulator build completed successfully
- installed Apple2026 SBS/WPS copies are current
- `verify-sim-install` returned `Result: OK`

Not yet verified interactively in this CLI pass:
- live Quick Screen behavior in the simulator while entering from stopped and
  playing states
- on-screen confirmation that black-box flicker is fully gone

---

## 2026-04-11 -- Quick Screen regression stabilization

### Root cause audit

The simplified Apple2026 Quick Screen still had one brittle dependency left:
its native body geometry depended on the SBS-selected info viewport.

That handoff was unsafe because `apps/gui/quickscreen.c` captured the themed
parent viewport before `skin_update()` had switched the SBS to the quickscreen
content lane. The shell could therefore paint the white quickscreen area while
the native body still drew against stale viewport state.

### Stabilization approach

**Files changed:** `apps/gui/quickscreen.c`, `DESIGN_SYSTEM.md`,
`QuickScreenRegressionAudit.md`

Stabilized the Apple2026 Quick Screen by removing that remaining body-level
dependency on SBS info-viewport routing:
- the SBS still owns shell/header behavior
- the quickscreen body now uses a deterministic content frame in code
- redraw recomputes that fixed body frame every time

### Expected effect

- readable body text no longer depends on `qs_content` activation timing
- white shell fill can no longer appear without a matching body draw target
- quickscreen behavior should be consistent across reboot and shell-state
  transitions

---

## 2026-04-11 -- Quick Screen fallback rebase

### Why the custom path was dropped

Even after the stabilization pass, Apple2026 Quick Screen was still carrying
more custom surface logic than it had earned:
- a dedicated `qs_content` SBS lane still existed
- Apple2026-specific quickscreen body layout/draw code was still active
- simulator evidence for the new custom body remained weak

At that point the safer product decision was to stop defending the custom body
experiment and rebase onto the more stable Interpod-style baseline.

### What changed

**Files changed:** `apps/gui/quickscreen.c`, `wps/Apple2026.sbs`,
`QuickScreenRegressionAudit.md`, `DESIGN_SYSTEM.md`

Rebased Apple2026 Quick Screen to:
- fixed Apple2026 parent viewport below the compact header
- native Rockbox quickscreen body layout/draw path
- SBS shell-only behavior with no dedicated quickscreen body viewport

This intentionally trades visual ambition for stability and readability.

### Verification status

Executed:

```text
.\build-sim.ps1 -Incremental -SkipDep
.\build-sim.ps1 -InstallOnly
.\tools\verify-sim-install.ps1
```

Result:
- simulator build/install passed
- source/runtime quickscreen contract no longer uses `qs_content`
- active Apple2026 quickscreen path now uses native body rendering again

Not yet fully verified interactively:
- manual long-PLAY quickscreen open in the simulator/device
- direct visual confirmation of the restored readable body after this rebase

---

## 2026-04-10 -- Phase 1: Foundation

### Dynamic Row Height (list.c)

**Files changed:** `apps/gui/list.c`

Modified `list_init_item_height()` Apple2026 block to compute row height
dynamically instead of using a static floor. Formula:

```text
n = available_height / min_row_height
row_height = available_height / n
```

This preserves the same number of visible items but distributes leftover
pixels evenly, eliminating the dead gap at the bottom of list screens.
Works for both NORMAL tier (30px floor) and DENSE tier (28px floor).

### Battery Text Fix (SBS + WPS)

**Files changed:** `wps/Apple2026.sbs`, `wps/Apple2026.wps`

- SBS battery text changed from slot 3 to slot 6 for a more compact look
- Removed the space before `%` in the formatted battery percentage
- Applied to both regular and root-only SBS battery text viewports
- Applied to WPS battery text formatting as well

### Hold / Sleep Icon Repositioning (SBS)

**Files changed:** `wps/Apple2026.sbs`

Moved hold and sleep timer icons from the left side of the header to the
right side near the battery indicator while keeping them left of the
numeric battery text:
- Lock icon: `(24,6)` -> `(-82,6)`
- Sleep timer: `(42,6)` -> `(-94,6)`

This removes the root-title overlap without creating a new collision with
the numeric battery text.

---

## 2026-04-10 -- Phase 2: Icon and State Display Fixes

### Repeat Mode Icon Redesign (WPS)

**Files changed:** `wps/Apple2026.wps`

Simplified the `%mm` repeat mode display so each mode shows exactly one
distinct icon instead of layering multiple overlapping icons:
- Off: nothing shown
- Repeat All: `%xd(Ra)` only
- Repeat One: `%xd(X)` only
- Shuffle: `%xd(Y)` only
- A-B Repeat: `%xd(Z)` only

### Volume Overlay Alignment (WPS)

**Files changed:** `wps/Apple2026.wps`

Adjusted `speaker_mute` from `y=8` to `y=5` so the icon centers on the
same vertical midpoint as the volume rail.

### Transport Icon Convention -- SUPERSEDED

This note was later intentionally reversed for Apple2026 iPod ergonomics.

Current desired behavior:
- Playing state -> show play icon
- Paused state -> show pause icon

See `WORK_LOG.md` and `BuildClaimMismatchAudit.md` for the later transport
mapping adjustment pass.

### Cover Flow Text Color Fix (pictureflow.c)

**Files changed:** `apps/plugins/pictureflow/pictureflow.c`

Added a minimum brightness clamp in `pf_color_mix()` so album and artist
text does not fade to near-white during scroll transitions.

### Cover Flow Tracklist Spacing (pictureflow.c)

**Files changed:** `apps/plugins/pictureflow/pictureflow.c`

Added a gap between the bottom of the visible tracklist and the album-text
area for bottom-aligned album name layouts.

### Cover Flow Wraparound Fix (pictureflow.c)

**Files changed:** `apps/plugins/pictureflow/pictureflow.c`

Improved tracklist wrap behavior in two ways:
- wrapping to the last track now guards `list_start` against underflow
- repeat-scroll events (`PF_NEXT_REPEAT` / `PF_PREV_REPEAT`) stop at the
  edges instead of wrapping immediately

This matches the main list behavior more closely.

---

## 2026-04-10 -- Phase 3: Menu Structure and Navigation

### System Menu Removed from Root (root_menu.c)

**Files changed:** `apps/root_menu.c`

Removed `system_menu_` from the Apple2026 root menu table. System remains
available through Settings.

### Extras Menu Created (root_menu.c)

**Files changed:** `apps/root_menu.c`

Added `MAKE_MENU(extras_submenu, "Extras", ...)` containing:
- Plugins (`rocks_browser`)
- Shortcuts (`shortcut_menu`)
- Recording (`rec`) when the target supports it

New root menu order:
1. Music
2. Cover Flow
3. Now Playing / Resume Playback
4. Equalizer
5. Playlists
6. Database
7. Settings
8. Extras

### Menu/Back Button Audit -- DOCUMENTED, NO CHANGE

iPod button mappings were reviewed and left unchanged.

### Quick Screen Header Consistency (SBS)

**Files changed:** `wps/Apple2026.sbs`

Implemented the full Quick Screen shell behavior in the SBS itself:
- header title forced to `Quick Screen`
- clock path suppressed while Quick Screen is active
- mini-player and volume strip suppressed while Quick Screen is active

This uses the real header lane and avoids drawing over Quick Screen
content.

---

## 2026-04-10 -- Phase 4: WPS Enhancements

### Year Metadata Display (WPS)

**Files changed:** `wps/Apple2026.wps`

Added a year viewport beside the album art that shows `%iy` when present.

### USB Screen Redesign (usb_screen.c)

**Files changed:** `apps/gui/usb_screen.c`

Enhanced the Apple2026 USB screen with:
- stronger black `Connected` label
- secondary hint text: `Eject before disconnecting`
- tighter vertical spacing

### WPS Context Plugin -- VERIFIED, DOCUMENTED

Long-press SELECT still opens the WPS context menu and plugins can still
be launched from that path.

---

## 2026-04-10 -- Phase 5: Font Pipeline and Internationalization

### Font Range Expansion (apple2026_rebuild_fonts_from_otf.py)

**Files changed:** `tools/apple2026_rebuild_fonts_from_otf.py`

- Added `--start` and `--limit` CLI arguments for Unicode range control
- Expanded the default range to `U+0020..U+052F`
- Coverage now includes Latin-1, Latin Extended, Greek, Cyrillic, and
  Cyrillic Supplement

Fonts must be rebuilt for the runtime to pick up the expanded glyph set.

### Runtime Font Rebuild Completed

Executed:

```text
python tools/apple2026_rebuild_fonts_from_otf.py
```

Result:
- 19 Apple2026 `.fnt` files rebuilt successfully
- runtime font sizes increased as expected for the expanded Unicode range
- simulator install verification later confirmed the rebuilt fonts were
  copied into `build-sim/simdisk/.rockbox/fonts/`

### CJK Font Fallback -- DOCUMENTED

Full CJK support remains a glyph-cache / fallback-font path rather than a
primary bundled font path.

---

## 2026-04-10 -- Phase 6: Documentation and Future Items

### Center-Button Seeking -- FEASIBILITY DOCUMENTED

Still deferred. Requires a dedicated WPS scrub state and should be opt-in.

### Artist Sort Tag -- LIMITATION DOCUMENTED

Still deferred. Requires metadata parser, tagcache schema, and database
sort changes across the stack.

---

## 2026-04-10 -- Validation

Executed:

```text
.\build-sim.ps1 -Incremental -SkipDep
.\tools\verify-sim-install.ps1
```

Result:
- simulator build completed successfully
- `verify-sim-install` returned `Result: OK`
- Apple2026 fonts, SBS, WPS, iconset, and key runtime assets are current
  in the installed simulator tree

Not yet verified interactively:
- live simulator navigation and screenshots for Quick Screen, Cover Flow,
  USB screen, and header overlap states

---

## 2026-04-10 -- Cold-start root header fix

**Files changed:** `apps/gui/skin_engine/skin_tokens.c`

Observed issue: on a fresh simulator launch, the `Library` large-title
band could render in a partially cropped state with list rows starting too
high. After navigating away and back, it corrected itself.

Root cause:
- Apple2026 SBS root layout depends on `%Lo`
 
---

## 2026-04-10 -- Adwaitapod extraction continuation

### Audit result

The Adwaitapod extraction plan was only partially implemented before this
pass.

Already present:
- WPS-side Apple2026 lockscreen asset pack and a partial WPS lockscreen
  layer
- lockscreen and quickscreen bitmap generation script
- Quick Screen header title override in the SBS

Missing or incomplete:
- SBS root-menu lockscreen / AOD routing
- full custom Quick Screen overlay using `%Q*` tags
- generated theme defaults for `disable main menu scrolling` and Quick
  Screen item assignments
- locale-aware date formatting on the Apple2026 lockscreen paths
- WPS lockscreen still incorrectly depended on `battery display = graphic`

### SBS lockscreen / AOD added

**Files changed:** `wps/Apple2026.sbs`

Implemented a real homescreen lockscreen for `cs == 1` when hold is on:
- normal list viewport is replaced with a tiny hidden viewport
- full lockscreen uses `Wallpaper.bmp`, Apple2026 notification card chrome,
  a centered SF Pro clock, localized date, battery icon, and sleep timer
- low-battery state now swaps in a dedicated warning card instead of
  showing the music card
- AOD mode is selected when `backlight on button hold` is `off`

### Custom Quick Screen overlay added

**Files changed:** `wps/Apple2026.sbs`

Implemented the Apple2026 Quick Screen overlay structure:
- uses the tiny hidden quickscreen viewport workaround so Rockbox's
  hardcoded quickscreen stays active but visually suppressed
- draws 4 Apple-style pill control zones using `%QT/%Qt/%QL/%Ql/%QR/%Qr`
  and `%QB/%Qb`
- left button highlights when shuffle is on, right button highlights when
  repeat is not off
- shows now-playing summary and a bottom volume rail

### WPS lockscreen cleaned up

**Files changed:** `wps/Apple2026.wps`

- removed the `battery display = graphic` feature gate so lockscreen
  behavior now follows hold state directly
- made WPS lockscreen and AOD date formatting locale-aware using the
  Adwaitapod language-order pattern
- added AOD artist line
- upgraded low-battery lockscreen handling from icon-only to a proper
  text-bearing notification card

### Theme defaults added

**Files changed:** `wps/WPSLIST`, `wps/wpsbuild.pl`

Added generated theme config defaults:
- `disable main menu scrolling: on`
- `qs top: brightness`
- `qs left: shuffle`
- `qs right: repeat`
- `qs bottom: sleeptimer duration`

Additional generator fix:
- `wpsbuild.pl` previously ignored these keys because they were not in its
  config-output whitelist
- patched `wpsbuild.pl` so the generated `Apple2026.cfg` now actually emits
  these Apple2026 defaults at install time
- `SKIN_TOKEN_LIST_TITLE_IS_ROOT` only returned true when the current SBS
  title text matched `LANG_ROCKBOX_TITLE`
- on the first cold render, the activity was already `ACTIVITY_MAINMENU`
  but the title text could still be unset, so the non-root viewport was
  chosen for one frame cycle

Fix:
- treat `ACTIVITY_MAINMENU` as root immediately in
  `SKIN_TOKEN_LIST_TITLE_IS_ROOT`, then fall back to the old title-string
  comparison for the legacy path

---

## 2026-04-11 -- Default settings / first-run experience pass

### Defaults reviewed before changes

Reviewed source-of-truth and default-setting paths:
- `MASTER.md`
- `BUILD.md`
- `DESIGN_SYSTEM.md`
- `WORK_LOG.md`
- this `Update1Worklog.md`
- `apps/settings_list.c`
- `wps/WPSLIST`
- `wps/wpsbuild.pl`
- generated `build-sim/simdisk/.rockbox/themes/Apple2026.cfg`

### Lockscreen default behavior corrected

**Files changed:** `apps/settings_list.c`

Verified root cause in source:
- Apple2026 shell rules already use `backlight on button hold = off` as the
  AOD-selection path
- generic hold-switch defaults in `apps/settings_list.c` were still setting
  `backlight on button hold` to `off`
- `firmware/backlight.c` maps that value to an immediate hold-state
  backlight timeout of `-1`

Resulting fix:
- Apple2026 iPod targets now default `backlight on button hold` to
  `normal`, so the full lockscreen remains visible for the standard
  backlight timeout on first boot instead of collapsing immediately into the
  AOD path

### 1 px dividers enabled in the compiled default path

**Files changed:** `apps/settings_list.c`

- Apple2026 iPod targets now default `list separator height` to `1`
- this makes reset/first-run behavior match the Apple2026 generated theme
  config instead of relying on theme-load alone

### Generated theme font aligned to the live Apple2026 list system

**Files changed:** `wps/WPSLIST`

- changed generated Apple2026 theme font from
  `20-SFProText-Regular.fnt` to `18-SFProText-Regular.fnt`
- this now matches:
  - `apps/settings_list.c` Apple2026 default font
  - `wps/Apple2026.sbs` slot 5 list font
  - current `DESIGN_SYSTEM.md` typography lock

### Validation

Executed:

```text
.\build-sim.ps1 -Incremental -SkipDep
.\build-sim.ps1 -InstallOnly
.\tools\verify-sim-install.ps1
```

Result:
- simulator build/install completed successfully
- `verify-sim-install` returned `Result: OK`
- generated `Apple2026.cfg` now includes:
  - `font: /.rockbox/fonts/18-SFProText-Regular.fnt`
  - `list separator height: 1`
  - existing Apple2026 Quick Screen defaults and
    `disable main menu scrolling: on`

Verified but not interactive:
- source-level lockscreen cause and fix are confirmed
- install-time theme defaults are confirmed in generated output

Not yet verified interactively:
- fresh clean-config simulator/device run showing the full lockscreen staying
  up for the normal backlight timeout after engaging hold
- fresh clean-config run showing the 18px list font and 1 px dividers
  without relying on old runtime `config.cfg`

---

## Audit Correction (2026-04-11)

The earlier Update 1 notes for:
- battery text density / formatting
- hold + sleep icon repositioning
- repeat-state icon simplification
- mute icon alignment

were audited against committed source, simulator runtime, and published
hardware zips during the Apple2026 build-vs-claims verification pass.

Result:
- those fixes had been documented as shipped, but they were **not** actually
  present in the committed Apple2026 skin source or in the published
  custom-named release zips at the time of audit
- the fixes are now present and verified in:
  - `build-sim/simdisk/.rockbox`
  - `build-hw-ipod6g/rockbox.zip`
  - `build-hw-ipodvideo/rockbox.zip`
- the stale custom-named zips were removed after rebuild

See `BuildClaimMismatchAudit.md` for the full source-vs-artifact comparison,
root cause, and release verification safeguards.
