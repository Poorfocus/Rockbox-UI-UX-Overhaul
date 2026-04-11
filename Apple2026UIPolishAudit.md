# Apple2026 UI Polish & Design System Audit
**Date:** 2026-04-11
**Type:** Deep Static Audit
**Target:** Apple2026 Branch (iPod Video/Classic 320x240)

## 1. Audit Scope & Core Design Goals
This audit evaluates the Apple2026 branch against strict native Apple UI/UX principles, focusing on typography balance, spatial rhythm, and micro-composition.
**Core Goals:**
- **Calm, Apple-like Intentionality:** No arbitrary margins, visual crowding, or raw tech-exposed layers.
- **Pixel-Perfect Typography Sizing & Hierarchy:** Clean line spacing and avoiding cut-off ascenders/descenders.
- **Consistent Shell Rhythm:** Stable margins across diverse file views and WPS.

## 2. Typography System Findings
The recent stabilization of two-tier font sizes (Dense 16pt / Normal 18pt) establishes a strong baseline, but critical stability risks remain:

* **[Critical] Font Height vs. Viewport Clipping Bounds:** 
  The `.wps` and `.sbs` files define text viewports that exactly hug the font's nominal pixel height. Examples: 
  - `%Vl(title,74,5,-74,20,3)` used for the 20px header title.
  - `%V(18,-80,-18,20,9)` for WPS 20px track title.
  *Why it matters:* Any minor shift in font converter tracking, or descender-heavy songs (like titles ending in "p" and "g"), will brutally clip at the viewport edge. Apple-native typography relies on generous bounding boxes, not razor-thin clipping masks.
* **[High] Typographic Density Clash on Lockscreen:**
  The Lockscreen clock is 35pt (`h=43`) placed at `y=42`. The Lockscreen date is 14pt placed at `y=90`. This produces an overly tight 5px vertical gap between giant display text and metadata, making the composition feel cramped instead of using Apple's standard airy lockscreen spacing.
* **[Medium] Hardcoded Header Constraints:**
  The top header (`titlewide`) truncates at `56px` inward, and standard headers truncate at `74px` inward. When the battery or sleep-timer is absent, this space is wasted, forcing unnecessary marquee scrolling for moderately long track/menu titles.

## 3. Spacing & Rhythm System Findings
Spacing logic is currently fragmented between `.wps` hardcodes and `list.c` geometry hooks, causing serious holistic inconsistencies:

* **[Critical] Compositional Margin Mismatch (List vs. Mini-Player):**
  The global list horizontal inset is defined as `16px`. However, the mini-player in `.sbs` hardcodes album art at `x=8` (`%Vl(mp_albumart,8,-38,32,32,-)`). 
  *Why it matters:* This creates immediate visual tension where the bottom layer visibly breaks the primary left vertical bounding guide of the entire UI system above it. The mini-player margin must match the list margin for a cohesive shell.
* **[Critical] Vertical Density Collapse in WPS Bottom Zone:** 
  The total height reserved for WPS bottom controls spans tightly from `y=160` down to `y=226`.
  - Gap between Title and Artist is `2px`.
  - Gap between Artist and Scrubber is `3px`.
  - Gap between Scrubber and Time is `3px`.
  *Why it matters:* The metadata stack is completely squashed at the bottom edge, while the top half of the screen has a vast 150px of empty "hero" space around the art. This violates the "Calm" Apple principle, producing a crowded bottom-edge and unbalanced vertical rhythm.
* **[High] The Lockscreen "Blank Box" Hack:**
  To solve a WPS regression regarding album art pointers, the lockscreen notification card's art was recently overridden with a solid gray fill (`%dr(0,0,-,-,F2F2F7)`). 
  *Why it matters:* The card feels entirely broken. A gray box implies an image failed to load, failing the premium feel. We must fix the renderer to support secondary art sizes properly, or completely remove the broken box.

## 4. UI Principles & Component Logic
* **[High] Custom Drawn Chevron Over-engineering vs. Consistency:** 
  The list right-chevron is manually drawn pixel-by-pixel via a `drawpixel` array in `apps/gui/bitmap/list.c`. While mathematically precise, it's brittle and visually distinct from the normalized, asset-based symbols established for Apple2026.
* **[Medium] The Volume Bar Context Switch:** 
  In the WPS, the volume bar replaces the *exact* coordinate zone of the elapsed time and scrubber. When volume is adjusted, the UI jarringly snaps out the scrubber and snaps in the volume bar, breaking UI permanence. Apple Music typically overlays volume smoothly or shares a rail gracefully.

## 5. Micro-Polish Checklist (The 1px details)
* **[Micro] P/P Baseline Misalignment:** The Mini-player play icon (`%Vl(mp_playpause,-30,-31...`) sits at `y=-31`. A `44px` tall mini-player minus `31` leaves `13px` above, resting `1px` optically higher than the actual text baselines `y=-32`.
* **[Micro] Color Tone Drift:** `.wps` uses `#8E8E93`, `#6E6E73`, and `#3C3C43` interchangeably for secondary metadata. Apple Music strictly standardizes these gray palettes.
* **[Micro] Separator Line Masking:** `list.c` handles inset separators by erasing `A26_LIST_CONTENT_INSET + list_info->icon_width + ICON_PADDING`. This dynamic masking can wobble depending on the exact icon bounds, creating misaligned hairline separators compared to fixed `16px` or `76px` UI guidelines.

## 6. Recommended Order of Operations for UI Polish Work
1. **Unify the Shell Margin (Critical):** Update `Apple2026.sbs` to move the Mini-player Album Art to start exactly at `x=16` so it perfectly mirrors the master list inset.
2. **Rescue Viewport Bounds:** Pad `y` heights by `+4px` on all `.sbs` and `.wps` text viewports to definitively prevent ascender/descender clipping.
3. **Re-balance the WPS Vertical Rhythm:** Distribute the heavy bottom WPS zone more evenly. Place Title at `y=-95`, Artist at `y=-70`, and distance the scrubber gracefully to relieve bottom crowding.
4. **Deprecate the Hardcoded Chevron:** Rewrite the `list.c` chevron injection to use a standard loaded `sf-symbol` asset.
5. **Revisit Notification Architecture:** Halt the use of the gray lockscreen placeholder block until multiple `%Cl` render targets can be supported natively without regression.
