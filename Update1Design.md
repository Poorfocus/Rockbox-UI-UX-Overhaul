# Update1Design.md -- Apple2026 Update 1 Design Authority

Branch: `update-1`
Baseline: `release` branch (post-OpusDesignPolish)
Historical reference: `DESIGN_SYSTEM.md`, `OpusDesign.md` (read-only context)

---

## Philosophy

Apple2026 Update 1 is a broad community-driven polish pass that goes beyond
theme-layer tweaks into core Rockbox code, font pipeline, icon system,
navigation behavior, and Cover Flow consistency. Every change must push the
shell closer to a calm, premium, music-first Apple-designed iPod OS from 2026.

---

## Active Design Tokens (320x240, inherited + updated)

### Color System (unchanged from OpusDesign)

| Token | Value | Usage |
|-------|-------|-------|
| Shell background | `#FFFFFF` | All surfaces |
| Primary text | `#000000` | Titles, row labels |
| Secondary text | `#6E6E73` | Metadata, timestamps |
| Tertiary text | `#3C3C43` at 60% | Sublabels, disabled |
| Accent | `#FF2D55` | Interactive, active |
| Selector bar | `#E5E5EA` | Flat bar, r=4 |
| Separator | `#C6C6C8` | 1px dividers |
| Progress track | `#E5E5EA` | Unfilled bars |
| Progress fill | `#3C3C43` | Filled segments |

### Typography (inherited)

| Slot | Font | Size | Usage |
|------|------|------|-------|
| 2 | SF Pro Display Bold | 28px | Large title |
| 3 | SF Pro Text Semibold | 16px | Header, mini-player |
| 5 | SF Pro Text Regular | 18px | List rows (normal tier) |
| 6 | SF Pro Text Regular | 16px | Dense tier (tracks) |
| 8 | SF Pro Text Medium | 20px | WPS song title |
| 9 | SF Pro Text Medium | 16px | WPS artist |

---

## Update 1 Design Decisions

### D-U1: Dynamic Row Height (fill-to-bottom)

Row height is no longer a static floor. It is computed dynamically so the
visible items fill the available content zone completely, eliminating the
awkward empty gap at the bottom of the screen.

Formula: `row_height = available_height / floor(available_height / min_row_height)`

Where `available_height` accounts for header band (40px root / 28px non-root)
and bottom bar (44px playing / 0px stopped).

This keeps the same number of visible items but distributes the leftover
pixels evenly across all rows, giving each row more generous padding.

### D-U2: Battery Text Formatting

- Font: slot 6 (16px) instead of slot 5 (18px) on SBS
- Format: `60%` not `60 %` (no space before percent sign)
- Match WPS battery text size for cross-screen consistency

### D-U3: Hold / Sleep Icon Positioning

Move hold and sleep timer icons to the right side of the header, near
the battery indicator, but keep them left of the battery percentage so
they never overlap the large title on root or the numeric battery text.

### D-U4: Repeat Mode Icons

Each repeat state gets a unique, visually distinct icon:
- Off: no icon shown
- Repeat All: loop arrows (`repeat`)
- Repeat One: loop arrows with "1" badge (`repeat.1`)
- Shuffle: crossed arrows (`shuffle`)
- A-B Repeat: A-B badge

### D-U5: Transport Icon Convention

Apple's convention: show the ACTION icon, not the STATE icon.
- Playing -> show pause icon (press to pause)
- Paused -> show play icon (press to play)
Current implementation is correct. No change needed.

### D-U6: Cover Flow Text Color

Album/artist text in Cover Flow must remain readable during scroll
transitions. Minimum darkness clamped so text never fades to white/invisible.

### D-U7: Menu Structure

Root menu (Apple2026):
1. Music
2. Cover Flow
3. Resume Playback / Now Playing
4. Equalizer
5. Playlists
6. Database
7. Settings (now includes System submenu)
8. Extras (Plugins, Shortcuts, Recording)

### D-U8: Quick Screen

- No clock display (override SBS header for this screen)
- Title "Quick Screen" shown in header position
- No mini-player shown during Quick Screen

### D-U9: Year Metadata in WPS

When `%iy` (year tag) is present, display it in the whitespace beside
the album art. Small, secondary-color text. Only shown when tag exists.

### D-U10: Font Coverage Expansion

Primary fonts: Latin-1 + Latin Extended-A/B + Cyrillic + Greek
CJK: separate fallback font via Rockbox font cache system

---

## Scope Boundaries (inherited)

- No Cover Flow performance/caching optimization
- No RAM/prefetch architecture work
- No tagcache schema changes (artist sort tags deferred)
- UI/UX/design-system/navigation/font/icon only

---

## Deferred Items and Known Limitations

### Center-Button Seeking (Deferred)

Not implemented in Update 1. Would require a new WPS state machine
(`WPS_STATE_SCRUB`) where the scroll wheel seeks within the track.
Recommended as an opt-in setting in a future branch to avoid breaking
existing muscle memory.

### Artist Sort Tags (Out of Scope)

Rockbox `mp3entry` has no sort tag fields. Adding TSOP/TSO2/TSOA support
requires extending metadata parsers, tagcache schema, and database browser.
Multi-week project deferred to a dedicated metadata branch.

### CJK Font Support (Partial)

Primary fonts expanded to include Cyrillic, Greek, Latin Extended.
For CJK (Japanese, Chinese, Korean), users should:
1. Place a CJK .fnt file in `/fonts/` (Noto Sans CJK or GNU Unifont)
2. Set Font Cache Size >= 64KB in Display settings
3. Rockbox loads missing glyphs on demand from the glyph cache

### WPS Context Plugin

Already functional via SELECT long-press → context menu → plugin launch.
No code change needed. Documented in worklog.

### Transport Icon Convention

Apple's convention (and stock iPod's): show the ACTION icon, not the STATE.
Playing → pause icon (press to pause). Paused → play icon (press to play).
Current implementation is correct. Documented, no change.
