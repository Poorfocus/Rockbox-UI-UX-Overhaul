# OpusDesign.md — Apple2026 Design Polish Authority

Branch: `OpusDesignPolish`
Baseline: Audit completed 2026-04-08 on previous branch.
Historical reference: `DESIGN_SYSTEM.md`, `WORK_LOG.md` (read-only on this branch).

---

## Philosophy

The Apple2026 shell must feel like a music-focused Apple iPod OS designed in 2026:
premium, calm, intentional, coherent, deeply polished, visually modern, cleanly
hierarchical, and adapted to iPod hardware without feeling compromised.

Every surface — from root menu to WPS to Cover Flow tracklist — must pass a
blind-test: if you saw a screenshot without branding, would you assume this was
a polished Apple product, or a custom firmware skin?

---

## Active Design Tokens (320x240)

### Color System

| Token | Value | Usage |
|-------|-------|-------|
| Shell background | `#FFFFFF` | All surfaces, header, WPS, bottom bar |
| Primary text | `#000000` | Titles, row labels |
| Secondary text | `#6E6E73` | Metadata, timestamps, album info |
| Tertiary text | `#3C3C43` at 60% | Sublabels, disabled states |
| Accent | `#FF2D55` | Interactive elements, active indicators |
| Selector bar | `#E5E5EA` | Flat bar, r=4 rounded corners |
| Separator | `#C6C6C8` | 1px horizontal dividers (Apple opaqueSeparator) |
| Progress track | `#E5E5EA` | Unfilled progress/volume bars |
| Progress fill | `#3C3C43` | Filled progress segment |
| Art placeholder | `#F2F2F7` | Album art fallback background |

### Typography

| Slot | Font | Size | Usage |
|------|------|------|-------|
| 2 | SF Pro Display Bold | 28px | Large title ("Library") |
| 3 | SF Pro Text Semibold | 16px | Header chrome, mini-player |
| 5 | SF Pro Text Regular | 20px | List rows (default) |
| 8 (WPS) | SF Pro Text Medium | 20px | Song title |
| 9 (WPS) | SF Pro Text Medium | 16px | Artist name |
| 3 (WPS) | SF Pro Text Regular | 14px | Album, times, playlist |

### Layout (SBS)

| Element | Position | Size |
|---------|----------|------|
| Compact header | y=0 | 26px tall (non-root only) |
| Large title band | y=0 | 40px tall (root only, replaces header) |
| Content start (root) | y=40 | to bottom minus strip/bar |
| Content start (non-root) | y=27 | to bottom |
| Bottom bar (stopped) | bottom | 36px tall |
| Bottom strip (playing) | bottom | 44px mini-player |

### WPS Layout

| Element | Position | Size |
|---------|----------|------|
| Album art | x=85, y=8 | 150×150, r=6 rounded via wpsArtCorners.bmp overlay |
| Song title | y=-82 | 20px Medium, full width |
| Artist | y=-61 | 16px Medium, gray |
| Album | y=-44 | 14px Regular, tertiary gray |
| Progress bar | y=-29 | 3px inactive / 5px active, pill, `E5E5EA` track / `3C3C43` fill |
| Time + counter | y=-20 | Elapsed left \| N of M center \| -Remaining right |

### Icons

| Parameter | Value |
|-----------|-------|
| Tile size | 30x30 |
| Icon padding | 6px each side |
| Supersampling | 4x |
| Internal padding | 4px each side |
| Alpha compositing | White-background pre-blend, cutoff at alpha 40 |
| Accent icons | `#FF2D55` (root menu items) |
| Chrome icons | `#3C3C43` (settings, utility) |

---

## Task Sequence (Opus Polish)

| # | Task | Status |
|---|------|--------|
| 1 | Unify background to pure white (FFFFFF) | DONE |
| 2 | Merge double-header on root | DONE |
| 3 | Reduce large title to 25px (from 35px) | DONE → upgraded to 28px (Task 15) |
| 4 | Add real mini-player when playing | DONE |
| 5 | Increase icon supersampling to 4x | DONE |
| 6 | Replace drawline chevrons with bitmap | DONE |
| 7 | Add tracking to font pipeline | DONE (pipeline ready, pending OTF rebuild) |
| 8 | Fix WPS artist color to gray | DONE |
| 9 | Fix battery CGD display | DONE |
| 10 | Separator color correction | DONE |
| 11 | Replace Tango viewer icons | DONE (disabled — cleaner without file type icons) |
| 12 | Album art shadow on WPS | DONE |
| 13 | Style Quick Screen / Context Menu / Splash | DONE (inherits theme; deep restyle deferred) |
| 14 | Cover Flow visual continuity | DONE (colors inherited; deep polish deferred to CF branch) |
| 15 | Switch large title to 28px font | DONE |
| 16 | Enable inset separators for Apple2026 | DONE |
| 17 | Bump row height from 35px to 38px | DONE |
| 18 | WPS song title to Medium weight font | DONE |
| 19 | Increase icon-to-text gap (4 → 6px) | DONE |
| 20 | Selector bar rounded corners (r=4) | DONE |
| R1 | WPS album art rounded corners (wpsArtCorners.bmp overlay) | DONE |
| R2 | WPS progress bar — Apple Music pill style | DONE |
| R3 | WPS layout — full-width title, playlist counter in time row | DONE |
| R4 | Icons — semantic remap, gray for settings, unique glyphs | DONE |
| R5 | Quick Screen — pixel-art directional indicators | DONE |
| R6 | USB screen — "Connected" label in Apple2026 colors | DONE |
| R7 | Yes/No dialog — separator + color-coded OK/Cancel buttons | DONE |
| R8 | Remove "Rockbox" text from non-root header | DONE |
| R9 | Volume overlay — clean 5px pill bar, unified A26 colors | DONE |
| R10 | Scrollbar — 3px default, A26 separator color | DONE |

---

## Decision Log

### D1: Pure White Shell (Task 1)

**Decision:** All background surfaces changed from `#F8F8F8` to `#FFFFFF`.

**Rationale:** Apple Music and iOS system apps use pure white backgrounds.
The `#F8F8F8` tint created a "status bar chrome" feel inherited from Interpod
that read as dated and non-Apple. Pure white creates visual continuity between
header, content, and bottom bar — the shell disappears and content feels
primary.

**Files changed:** `Apple2026.sbs` (28 occurrences), `Apple2026.wps` (15 occurrences),
`apple2026_symbol_assets.py` (4 occurrences: wpsBackdrop, usbBackdrop, albumFramed,
albumPlaceholder). Bottom bar shadow hairlines (`F4F4F4`) removed. WPS volume bar
zone changed from `EDEDED` to `FFFFFF`. Album art placeholder changed from
`EAEAEA`/`F0F0F0` to `F2F2F7` (Apple system grouped background — subtly visible
on white without looking dirty).
