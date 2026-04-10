# DESIGN_SYSTEM.md

## 1) Purpose
- This is the visual-system authority for the `Apple2026` branch direction.
- It defines strict UI/UX rules for shell, hierarchy, typography, iconography, spacing, and state behavior.
- This document is implementation-facing: future agents should be able to build from it without guessing.
- Scope: UI/UX/design-system/navigation only (no Cover Flow optimization, no deep performance architecture).

## 2) Classification and branch boundaries
- Flagship classification: `Apple2026`.
- Base DNA: original `Interpod`.
- This branch must not perform Cover Flow optimization, cache architecture tuning, or RAM/prefetch redesign.

## 3) Source-of-truth hierarchy (non-negotiable)
1. User Figma file `Apple-Music-UI` nodes: `1:4008`, `1:475`, `1:5998`
2. Apple references in `MASTER.md` (HIG + Apple Music control/symbol references)
3. Original `Interpod`
4. `Imported Reference Themes/`
5. Local source assets (`Apple Fonts/`, `Sourced Icons/`, `sf-symbols-master`)

If sources conflict, choose the higher source.

## 3A) Top-level MCP Figma reference
- `mcp_com_figma_mcp_use_figma`: `https://www.figma.com/design/JyDHVsT9bqCPjbGEfyUD8d/Apple-Music-UI?node-id=35-9972&t=rOOHiOTV8SE8HN2c-4`
- Primary locked node for this reference: `35:9972`.

## 4) Verified Figma findings (expanded)

### 4.1 Library shell (`1:4008`)
- Core frame: `390 x 844` reference composition.
- Large-title top hierarchy with white shell and restrained accent behavior.
- Primary row height: `52px`.
- Row horizontal inset: `16px`.
- Leading icon container: `29px`.
- Icon-to-title gap: `8px`.
- Dividers: `0.5px`, inset to content rhythm (not full-bleed).
- Persistent mini-player above tab bar; compact, light-surface, single-line title emphasis.
- Tab bar is icon-first with active accent and subdued inactive state.

### 4.2 Album list (`1:475`)
- Row height: `56px`.
- Album art per row: `48px` square.
- Text/divider leading inset rhythm: `76px`.
- Compact top navigation arrangement (back on left, lightweight actions on right).
- Uses same footer shell language as library (mini-player + tab bar continuity).

### 4.3 Album page (`1:5998`)
- Hero art: `270px` square with soft depth/shadow.
- Metadata stack is centered and spacing-led, not chrome-led.
- Two primary action pills: equal width, soft-neutral background, accent icon/text.
- Pill radius: `8px`.
- Track row height: `48px`.
- Track divider leading inset: `50px`.
- Secondary "More by" horizontal card group under track list.

## 5) Apple principles (expanded, operational)
- Prioritize content legibility over decorative chrome.
- Use semantic color behavior: accent for emphasis, neutral tones for structure, separators for grouping.
- Keep bars/toolbars/tab bars uncluttered; only high-frequency actions remain visible.
- Prefer familiar system symbols; avoid novelty glyphs.
- Preserve predictable grouping in bars: leading navigation, trailing actions, avoid mixed ambiguous groupings.
- Tab bars are for top-level navigation, not actions.
- Disclosure indicator (chevron) means hierarchy navigation; info-like affordances are not substitutes.
- Scroll indicators and separators should clarify structure, not dominate it.

## 6) Interpod preservation rules
- Preserve Interpod’s strongest characteristics:
  - coherent full-shell thinking,
  - music-first focus,
  - strong now-playing compositional backbone.
- Do not erase Interpod identity; evolve it toward Figma/Apple precision.

## 7) Imported theme comparative findings
- `Interpod`: strongest base coherence, keep as structural DNA.
- `Interpod 2`: good refinement in state treatment and density; best donor for polish details.
- `amusicpodds`: closest Apple Music experimentation; useful reference for compact shell ideas.
- `adwaitapod` / `adwaitapod_simplified`: useful restraint/coverage ideas; reject GNOME-heavy personality.
- `iClassic_v1.1` / `iPodOS`: useful stock-iPod hierarchy cues; reject legacy skeuomorphic heaviness.
- `iPone`: cautionary reference; reject fake-phone framing.
- `iRB_Modern`: useful cleanup references; reject generic-modern drift.

## 7A) Explicit comparison: Interpod 1 vs Interpod 2 vs amusicpodds (Apple Music alignment)

This section is the required inheritance map for Apple2026. Interpod 1 remains base DNA.

### Category 1 — list geometry
- Figma anchor: `52px` library rows, `56px` album rows, `16px` base inset, thin inset dividers.
- `amusicpodds` closer than Interpod 1 in one area: stronger compact-SF typography tuning for dense list readability (`21/18/14` SF Compact family files).
- `amusicpodds` not closer than Interpod 2 overall: dark shell baseline (`background color: 000000`) and no scrollbar (`scrollbar: off`) conflict with Apple2026 light shell.
- Interpod 1 stronger overall: light shell base (`background color: ffffff`) with stable top-status layout.
- Interpod 2 polish advantage: cleaner, less gradient-heavy list state defaults than Interpod 1.
- Apple2026 inherit:
  - from Interpod 1: light-shell list baseline,
  - from Interpod 2: cleaner state rendering,
  - from amusicpodds: SF Compact legibility study only (not full dark-shell geometry).

### Category 2 — album list behavior
- Figma anchor: `56px` rows, `48px` art, `76px` text/divider inset, trailing disclosure logic.
- `amusicpodds` closer than Interpod 1: stronger music-first typography voice in list contexts.
- `amusicpodds` not closer than Interpod 2 on shell behavior: no scrollbar and dark background reduce Apple Music parity for Apple2026 target.
- Interpod 1 stronger overall: safer baseline for light-mode list shell integration.
- Interpod 2 polish advantage: more controlled active state color bar behavior.
- Apple2026 inherit:
  - keep Figma album-list geometry as canonical,
  - use amusicpodds only as typography/icon candidate source,
  - do not import amusicpodds shell/background model.

### Category 3 — mini-player / lower shell continuity
- Figma anchor: persistent mini-player above tab bar with stable continuity.
- Interpod 1 strength: explicit bottom transport bar logic in `.sbs` with album art + track + dynamic volume overlay.
- Interpod 2 strength: same continuity model with cleaner condensed behavior and better adaptive track width handling.
- `amusicpodds` closer than Interpod 1 in one detail: strong bottom playback readability contrast in dark mode.
- `amusicpodds` not closer than Interpod 2 overall: lacks the same light-shell continuity model required by Figma.
- Apple2026 inherit:
  - pure Interpod/Interpod2 lower-shell continuity model,
  - optional amusicpodds readability spacing cues only.

### Category 4 — top navigation/header behavior
- Figma anchor: large-title/compact-nav hierarchy with restrained trailing actions.
- Interpod 1 stronger overall: cleaner top-level bar semantics and less ornamented top strip logic.
- Interpod 2 polish advantage: tighter title handling and improved activity/battery coexistence.
- `amusicpodds` closer than Interpod 1 in one area: explicit custom top-strip information density control.
- `amusicpodds` not closer than Interpod 2 overall: title/clock alternation and high-density status treatment are less Apple Music-like for this target.
- Apple2026 inherit:
  - keep Interpod structure,
  - use Interpod 2 text/state handling polish,
  - reject amusicpodds alternation-heavy top strip behavior.

### Category 5 — icon style and symbol choice
- Figma/Apple anchor: SF-like symbols, restrained weight, consistent optical sizing.
- `amusicpodds` closer than Interpod 1: stronger SF Compact/SF-like ecosystem alignment and music-first icon bias.
- `amusicpodds` roughly equal to Interpod 2 for core semantics, but still less aligned in final shell due dark styling and older accent red.
- Interpod 1 stronger overall: cohesive full-pack icon integration with existing shell states.
- Interpod 2 polish advantage: cleaner icon/state pairing in modernized pass.
- Apple2026 inherit:
  - Interpod family coherence as default,
  - amusicpodds icon candidates for symbol meaning only,
  - normalize all imported symbols through Apple2026 weight/padding pipeline.

### Category 6 — separator treatment
- Figma anchor: `0.5px` subtle separators with content-aligned inset.
- Interpod 1/2 are both closer than amusicpodds in baseline shell readability because they keep clear light-surface line logic.
- `amusicpodds` is not closer than either Interpod in separator behavior for Apple2026 target.
- Interpod 2 polish advantage: less visually busy transitions around shell separators.
- Apple2026 inherit:
  - Interpod separator discipline,
  - Interpod 2 subtlety,
  - reject amusicpodds dark-heavy separator context for flagship.

### Category 7 — active/inactive color logic
- Figma/Apple anchor: sparse accent (`#FF2D55`) + neutral inactive gray.
- Interpod 2 closer than Interpod 1: flat active selector (`f24e61`) is cleaner than Interpod 1 gradient selector.
- `amusicpodds` closer than Interpod 1 in selector simplicity (single-color red bar), but not closer than Interpod 2 because global dark inversion and `f24e36` accent drift from Apple2026 palette.
- Interpod 1 stronger overall: stable legacy state package coverage.
- Apple2026 inherit:
  - Interpod 2-style flat selector behavior,
  - strict Apple2026 accent token (`#FF2D55`) and neutral inactive states,
  - reject Interpod 1 gradient selector and amusicpodds dark-global inversion.

### Category 8 — album page composition
- Figma anchor: large hero, centered metadata, dual action pills, `48px` track rows, `50px` divider inset.
- Interpod 2 closer than Interpod 1: stronger centered-art + metadata polish and cleaner progress presentation.
- `amusicpodds` closer than Interpod 1 in album-art prominence and SF typography character.
- `amusicpodds` not closer than Interpod 2 overall for Apple2026 because dark shell and legacy red accent conflict with Figma light-mode composition.
- Apple2026 inherit:
  - Interpod 2 structural polish for hero/metadata rhythm,
  - amusicpodds typography tone references only,
  - keep Figma geometry and action-pill model as strict final target.

### Category 9 — scrollbar and selector behavior
- Figma/Apple anchor: subtle scrollbar as tertiary aid; clean non-noisy selector.
- Interpod 1/2 both superior to amusicpodds for scrollbar parity (`scrollbar: right`, width `8` vs `off`).
- Interpod 2 wins selector behavior (flat color bar) over Interpod 1 gradient.
- `amusicpodds` is not closer than Interpod 2 in this category.
- Apple2026 inherit:
  - keep visible subtle right scrollbar model,
  - adopt flat selector behavior,
  - reject scrollbar-off as default flagship behavior.

### Category 10 — overall “feels like Apple Music” shell outcome
- Interpod 1 strongest overall foundation for Apple2026 due coherent light-shell DNA and system-level completeness.
- Interpod 2 best polish/details/state donor.
- `amusicpodds` best targeted donor for Apple Music-like typography/icon direction and some playback/readability cues, not for base shell replacement.

### Exact inheritance package (final)
- Keep pure Interpod DNA:
  - light-shell foundation,
  - full-shell coherence,
  - robust lower-shell continuity behavior.
- Pull from Interpod 2:
  - flat selector behavior,
  - cleaner state transitions,
  - tighter title/track fitting logic.
- Pull from amusicpodds (deliberate, limited):
  - SF Compact legibility experiments for constrained text zones,
  - selected symbol semantics from `amusicpod.bmp` as candidate source,
  - compact playback information spacing cues.

### Explicit rejects per theme
- Reject from Interpod 1:
  - gradient selector default (`bar (gradient)` with two-tone fill).
- Reject from Interpod 2:
  - none at structural level; only reject any divergence from Apple2026 accent token and Figma geometry.
- Reject from amusicpodds:
  - dark global shell inversion (`background color: 000000`, `foreground color: ffffff`),
  - scrollbar-off default,
  - statusbar-off baseline,
  - legacy accent red token (`f24e36`) as flagship accent.

## 8) Typography system
- Title XL (large library title): `34/41`, bold class.
- Section/list emphasis title: `22/22` equivalent optical target.
- Body primary: `17/22`.
- Secondary/support text: `13/16`.
- Tab label micro text: `10/12`.
- Font family baseline:
  - Primary: `SF Pro Text` (body/list),
  - Display: `SF Pro Display` (large headers),
  - Secondary candidate only if conversion clarity wins: `SF Compact`.
- Rounded variants are reference-only unless explicitly re-approved.

## 9) Color system and semantics
- Accent (interactive active): `#FF2D55`.
- Primary text: near-black/black.
- Tertiary text family: `#3C3C43` opacity-derived variants.
- Backgrounds: white + very light gray only.
- Separators: neutral, low-contrast, `0.5px`.
- Color usage rule: accent is sparse and meaningful; never full-screen pink treatment.
- **Album-art dynamic colors:** default `off` on iPod Video/Classic (`MODEL_NUMBER` 5/71) so list/WPS chrome stays on the fixed Apple2026 neutrals; `dynamic_colors` may still be enabled in **Settings → Theme** for experimentation.

## 10) Global spacing and geometry tokens
- Shell horizontal gutter baseline: `16px`.
- Divider strategy: inset to content column (no full-bleed separators in core list surfaces).
- List density classes:
  - Library list: `52px` rows,
  - Album list: `56px` rows,
  - Track list: `48px` rows.
- Icon/text pair spacing: `8px` minimum in list-leading structures.

## 11) Header and top-bar rules
- Library root uses large-title hierarchy.
- Sub-surfaces use compact top bar with clear back affordance and restrained trailing controls.
- Do not crowd top bars with low-priority actions.
- Header action symbols are simple, borderless, and semantically obvious.

## 12) List row hierarchy rules
- Rows must be immediately scannable in one pass (title first, metadata second).
- Keep row text concise; avoid dense multiline stacks unless explicitly needed.
- Leading visual anchor is stable per list type:
  - menu symbol block (library),
  - album art block (album list),
  - index/track metadata block (track list).

## 13) Divider and separator rules
- Weight: `0.5px`.
- Use inset separators aligned to text/content columns (`16px`, `76px`, `50px` contexts per screen).
- Separators communicate grouping rhythm and must remain visually quiet.
- No heavy boxed list containers in the flagship shell.

## 14) Selector and focus-state rules
- Selection should feel calm and native, not neon or beveled.
- Prefer flat/subtle highlight treatment over glossy gradient bars.
- Keep selector contrast sufficient for readability while preserving Apple-like restraint.
- Selected-state color should harmonize with accent logic, not compete with content.

## 15) Scrollbar rules
- Scrollbars are tertiary orientation aids.
- Keep width/contrast subtle and stable across equivalent list surfaces.
- Avoid high-contrast, heavy, or ornamental scrollbar skins.
- No visual conflict between right-edge chevron/controls and scrollbar area.

## 16) Icon and symbol rules
- Primary symbol source: `Sourced Icons/sf-symbols-master` plus Figma-extracted reference forms.
- Choose symbols by semantic clarity first, then optical fit.
- Normalize each symbol for:
  - weight,
  - padding,
  - scale,
  - low-resolution legibility.
- Avoid mixed icon families, skeuomorphic glyphs, emoji-like forms, and random fills.

## 17) Chevron and disclosure rules
- Chevron is hierarchical disclosure only.
- Chevron must remain tertiary (small, quiet, right-aligned, subdued neutral tone).
- Do not overload chevrons with accent unless representing a true active emphasis state.
- Avoid oversized or thick chevrons that become dominant row content.

## 18) Mini-player and tab-bar composition rules
- Mini-player is persistent above tab bar in main music navigation surfaces.
- Mini-player must keep:
  - compact art anchor,
  - single-line title priority,
  - restrained transport control emphasis,
  - consistent vertical rhythm with tab bar.
- Tab bar:
  - top-level navigation only,
  - icon-first treatment,
  - accent on selected tab,
  - subdued neutral inactive tabs.

## 19) Loading, empty, and transition-state rules
- Loading UI must feel shell-native (no generic boxed/debug-like dialog style).
- Use calm typography, minimal framing, and consistent shell spacing.
- Empty/error states must preserve same typography and separator rhythm as populated screens.
- Transition states must avoid jarring color inversions or novelty effects.

## 20) Album-list and album-page composition rules
- Album list enforces `56px`/`48px` row-art rhythm with `76px` text/divider inset.
- Album page enforces `270px` hero, centered metadata stack, two equal action pills, `48px` track rows with `50px` divider inset.
- "More by" horizontal section remains secondary and must not overpower track hierarchy.

## 21) Anti-patterns (explicit rejects)
- Fake iPhone frame language.
- Full skeuomorphic nostalgia shells.
- GNOME-like heavy desktop chrome.
- Generic modern UI flattening that ignores Interpod lineage.
- Oversaturated accent usage.
- Mixed icon packs without normalization.
- Thick/high-contrast separators and heavy box borders.

## 21A) Navigation contract (Apple2026) — iPod Video / Classic

Hardware vocabulary: **wheel scroll** on **WPS** = **volume** (`ACTION_WPS_VOLUP` / `ACTION_WPS_VOLDOWN`); **wheel scroll** on lists = move highlight. **MENU** (top) / **PLAY** (bottom) are separate from wheel rotation.

### Core rules
- **Play from lists / main menu / tree** (`ACTION_TREE_WPS`): resolves through `GO_TO_PREVIOUS_MUSIC` to the playback surface (Now Playing / `wpsscrn` resume flow). On builds without FM, this is effectively **WPS**.
- **Playback source (`global_status.playback_source`):** RAM session flag set when playback **starts** from a browse/plugin path. Enum: `NONE`, `PICTUREFLOW`, `MUSICLIB`, `FILEBROWSER`, `DATABASE`, `PLAYLIST_BROWSER` (playlist catalog / `.m3u` tree), `PLAYLIST_VIEWER` (current playlist / queue / search-from-viewer). Used so **context-preserving back** returns through the **meaningful parent** instead of a single fixed destination.
- **WPS — SELECT** and **WPS — MENU short** (both `ACTION_WPS_BROWSE` in `keymap-ipod.c`): **Same handler** (`wps_handle_browse_parent()` in `apps/gui/wps.c`). If `playback_source != NONE`, leave WPS to the matching surface (PictureFlow, database, `/Music/`, previous file tree, playlists, playlist viewer, etc.). If **`NONE`**, use **Settings → WPS select action** (`wps_select_action`), including optional **open Cover Flow** when that setting requests it. **Apple2026 default on 5 / 71:** `wps_select_action` favors **Music** (`GO_TO_MUSICLIB`) when no tagged source.
- **Cover Flow re-entry from WPS:** When `playback_source == PICTUREFLOW` and audio is playing, opening Cover Flow from this browse path starts on the **album tracklist** (not idle grid) where implemented (`pictureflow.c` after `set_initial_slide`).
- **Main menu (5 / 71):** **Plugins** and **Shortcuts** are **not** listed at root (`apps/root_menu.c`); **Cover Flow** remains available from the **main menu** and navigation, not from a dedicated long-Play chord on WPS.
- **File browser list (5 / 71):** Leading Picard-style track indices in filenames (`1. `, `12. ` before the title) are **hidden in the list only**; on-disk names and playback are unchanged.
- **WPS — MENU repeat** (`ACTION_WPS_MENU`): **main menu (Home)** — `GO_TO_ROOT`. Short **MENU** is **not** home; it is **browse parent** (see above).
- **WPS — PLAY repeat** (`ACTION_WPS_QUICKSCREEN`): **Quick screen** (shuffle, repeat, display/brightness-style utilities, volume nudge within quickscreen, etc.). **PLAY short** remains **play/pause** (`ACTION_WPS_PLAY`). Long **PLAY** no longer opens Cover Flow; Picture Flow is not bound to that chord.
- **WPS — SELECT + MENU** (`ACTION_WPS_VIEW_PLAYLIST`): **current playlist / queue** (playlist viewer). Mapped first in the WPS keymap so the chord wins over single-button SELECT or MENU.
- **Browse / tree — Left** (`ACTION_STD_CANCEL`): up one level or toward root; **Right** = enter. **Curated Music library folder** (`browse->root` is exactly **`/Music`** or **`/Music/`**, default in `root_menu.c`): **Left** returns to **main menu** (`GO_TO_ROOT`), not **`ft_exit()`** to raw **`/`** (calendars, contacts, notes, …). On **5 / 71**, `root_menu.c` sets **`BROWSE_APPLE2026_MUSICLIB`** on the **`browse_context`** for **main-menu Music only**; `apps/tree.c` requires that flag plus **`path_is_curated_music_library_root(browse->root)`** and **`paths_same_directory(currdir, browse->root)`** — **Storage** can share **`/Music/`** as **`root`** without the flag. If Music was opened at a **resumed** path (e.g. **`/Music/Artist/`**), **Left** uses **`ft_exit()`** until **`currdir`** is **`/Music/`**, then **Left** exits as above. **`ft_exit()`** on **`/Music/`** alone would strip to **`/`** (`filetree.c`).
- **Playback ended / `do_wps_exit`:** if **Browse Current Track** is on, may return to the **previous browser**; otherwise **previous screen**. Document this when explaining “where did it go?”

### Bounded-stack navigation (loop prevention)

The navigation model is a **bounded stack** with Main Menu as a stable ceiling.

**Problem solved:** without this guard, the following loop existed:
Main Menu -> Now Playing -> WPS -> back (source=PF) -> Cover Flow -> back -> Main Menu -> Now Playing -> WPS -> back -> Cover Flow -> ... (infinite).

**Rule:** WPS back-path depends on **how** WPS was entered, not only on where playback was started.

| WPS entry method | `wps_entered_from_root` | Back from WPS |
|---|---|---|
| "Now Playing" from Main Menu | `true` | Main Menu (`GO_TO_ROOT`) |
| PLAY (resume) from Main Menu | `true` | Main Menu (`GO_TO_ROOT`) |
| Boot auto-resume to WPS | `true` | Main Menu (`GO_TO_ROOT`) |
| Cover Flow -> play track | `false` | Cover Flow tracklist (via `playback_source`) |
| Music -> play track | `false` | Music folder (via `playback_source`) |
| Database -> play track | `false` | Database (via `playback_source`) |
| Playlist catalog -> play | `false` | Playlists (via `playback_source`) |
| Playlist viewer -> play | `false` | Playlist viewer (via `playback_source`) |

**Implementation:** `root_menu.c` sets `wps_entered_from_root = (last_screen == GO_TO_ROOT)` before dispatching `GO_TO_WPS`. `wps_handle_browse_parent()` in `apps/gui/wps.c` checks this flag first; if `true`, returns `GO_TO_ROOT` without consulting `playback_source`. All existing source-aware routing is preserved for content-chain entries.

**Stack lifecycle:**
1. Content chain is **created** when playback starts from a browsing surface (source is stamped).
2. Content chain is **active** while the user navigates within it (WPS -> source -> parent -> ...).
3. Content chain is **closed** when the user reaches Main Menu (via back-navigation or Home).
4. Re-entering WPS from Main Menu is a **flat entry** -- back returns to Main Menu.
5. Content chain is **replaced** when new playback starts from a different surface.

### Interaction matrix (reference)

| Surface | Play | Scroll | Left | Right | Select | Menu | Select+Menu |
|---------|------|--------|------|-------|--------|------|-------------|
| Main menu / tree | Previous music → WPS | Prev/next row | Back / up | Enter | Enter item | Main menu / root | Hotkey (tree) |
| WPS | Play/pause; **long Play** = quickscreen | Vol | Skip/seek | Skip/seek | Browse parent (same as **MENU short**) | **MENU long** = Home | **Queue / playlist** |
| Playlist viewer | Exit to WPS (OK) | Move | Cancel / exit | — | Enter track | — | — |
| Settings (context) | — | Inc/dec | Prev setting | Next setting | OK | Cancel | — |

Cover Flow: track pick → WPS per plugin `auto_wps` (Wave 3: `auto_wps = 2`). **Idle grid — Left / back (`PLUGIN_OK`):** `pictureflow_scrn` returns **`GO_TO_ROOT`** so the user always lands on **main menu / Library**, even when Cover Flow was entered from WPS (Apple2026 — `apps/root_menu.c`). Stack intent: **WPS → tracklist → Cover Flow → main menu**. No performance work in this branch.

## 22) Future-agent implementation checklist
- Validate every visual change against:
  1) Figma nodes `1:4008`, `1:475`, `1:5998`,
  2) Apple references,
  3) Interpod lineage.
- Preserve numeric geometry tokens unless an evidence-backed change is documented.
- Keep typography hierarchy intact; do not ad-hoc resize text classes.
- Keep mini-player/tab-bar compositional continuity across library/album surfaces.
- Log all intentional deviations with reason and source.

## 23) Validation protocol
- Required visual checkpoints (simulator/hardware when available):
  - Library root,
  - album artist/album list,
  - album page,
  - now playing,
  - mini-player + tab bar,
  - loading state.
- For each checkpoint, record:
  - what matches spec,
  - what deviates,
  - whether deviation is intentional.

## 24) Current lock status
- This specification is the active design lock for Apple2026 UI/UX work.
- Any rule changes require explicit doc update in `DESIGN_SYSTEM.md` and change log entry in `WORK_LOG.md`.

## 25) Surface acceptance criteria (implementation gate)

Use this gate before considering any Apple2026 UI surface "done".

### 25.1 Library root gate
- Must use light-shell baseline with Interpod structural DNA.
- Must match Figma anchors:
  - `52px` rows,
  - `16px` horizontal insets,
  - `0.5px` inset separators,
  - tertiary chevrons.
- Selector must be flat/non-gradient.
- Scrollbar must be visible, subtle, and right-aligned.
- Must preserve mini-player + tab-bar continuity.

### 25.2 Album list gate
- Must match Figma anchors:
  - `56px` row height,
  - `48px` cover block,
  - `76px` text/divider inset rhythm.
- Must preserve concise two-line hierarchy and trailing disclosure behavior.
- Must not use dark global shell inversion.
- Typography may borrow amusicpodds compact legibility tuning only if it does not break Figma hierarchy.

### 25.3 Album page gate
- Must match Figma anchors:
  - `270px` hero-art target (scaled proportionally where required by device constraints),
  - centered metadata stack,
  - dual equal action pills,
  - `48px` track rows,
  - `50px` track-divider inset.
- Must keep Interpod 2 polish model for track/title fitting and state clarity.
- Must keep Apple2026 accent token (`#FF2D55`) for primary emphasis.

### 25.4 Lower shell / mini-player gate
- Must preserve Interpod-style persistent lower-shell continuity.
- Must present compact art + single-line title + restrained transport controls.
- Must support volume/state overlays without breaking geometry.
- Must avoid shell mode-jumps that visually detach list and playback surfaces.

### 25.5 Theme donor compliance gate
- Interpod 1 = base shell and structural default.
- Interpod 2 = polish/state donor.
- amusicpodds = limited donor (SF Compact legibility and selected icon semantics only).
- Hard reject defaults from amusicpodds:
  - `background color: 000000`,
  - `statusbar: off`,
  - `scrollbar: off`,
  - legacy accent token `f24e36` as flagship accent.

## 26) Token-level donor mapping (implementation defaults)

This mapping is the default implementation contract when translating theme sources into Apple2026.

### 26.1 Core shell tokens
- `background color`: force light (`#FFFFFF` family), donor: Interpod baseline.
- `foreground color`: dark text family (`#000000` + tertiary `#3C3C43` variants), donor: Figma/Apple.
- `statusbar`: visible/top-aligned by default, donor: Interpod/Interpod 2.
- `ui viewport`: preserve Interpod structural approach; tune dimensions only to satisfy Figma spacing targets.

### 26.2 Selection and scroll tokens
- `selector type`: flat color bar (no gradient), donor: Interpod 2.
- `selector color`: neutral iOS-like gray for default list selection state.
- `selector accent usage`: `#FF2D55` reserved for true music-emphasis actions/states,
  not as the global default row-selection color.
- `selector text`: white on active bar where required for readability.
- `scrollbar`: on/right/subtle; retain Interpod right-edge model and tune width for optical balance.

### 26.3 Typography tokens
- Primary body/list family: SF Pro Text-derived hierarchy.
- Display/title family: SF Pro Display-derived hierarchy.
- Allowed amusicpodds donor use:
  - SF Compact bitmap sizing/legibility experiments in constrained zones only.
- Disallowed:
  - full theme-wide font swap that breaks Figma hierarchy ratios.

### 26.4 Icon tokens
- Baseline icon family coherence: Interpod package discipline.
- Polish/state icon behavior: Interpod 2 refinements.
- Candidate semantic symbol intake: amusicpodds icon ideas + `sf-symbols-master`.
- All imported icons must pass normalization:
  - stroke/fill weight match,
  - optical size match,
  - padding grid match,
  - active/inactive state mapping.

### 26.5 Lower-shell tokens
- Persistent mini-player model: Interpod/Interpod 2 structural behavior.
- Playback readability micro-spacing: amusicpodds cues may be reused if they do not alter light-shell continuity.
- Tab bar selection semantics: Apple2026 accent-on-active, gray-on-inactive.

### 26.6 Rejection tokens (hard)
- Gradient selector default from Interpod 1.
- Dark-shell base tokens from amusicpodds.
- `scrollbar: off` and `statusbar: off` as flagship defaults.
- Legacy red `f24e36` as primary Apple2026 accent.

## 27) Wave 2 typography lock (font system first)

Typography is locked before spacing/icon finalization. All row geometry and icon sizing inherit from this section.

### 27.1 Locked hierarchy (Apple2026 on iPod target)
- **Skin/runtime alignment:** SBS/WPS font **slot 3** (compact header + mini-player chrome) uses **`16-SFProText-Semibold.fnt`**. **WPSLIST** default list font and **`settings_list.c` `DEFAULT_FONTNAME`** (5 / 71) use **`18-SFProText-Regular.fnt`** (SF Pro Text Regular at **18px**, reduced from 20px for hierarchy; **~0.40** tracking — see **`tools/apple2026_rebuild_fonts_from_otf.py`**); SBS **slot 5** matches. Fonts are built with **`tools/otf_to_rb12_fnt.py`** (advance + `bitmap_left`, optional **`--track`**). Firmware list row floor **`35px`** (`apps/gui/list.c`, `ROCKPOD_APPLE2026_IPOD`, Wave3_V3 density) + **`ICON_PADDING 4`** each side in **`apps/gui/bitmap/list.c`** (§54.3). Pair kerning (GPOS) is not available in RB12; tracking approximates openness.
- **Root main menu (large-title band):** use SBS tag **`%Lo`** (true when `LANG_ROCKBOX_TITLE` matches the status-bar list title) — do not compare **`%Lt`** to the English string `Rockbox`; that breaks non-English locales.
- Large title / flagship header (Apple ~34pt class, Figma SF Pro Display Bold reference):
  - **Runtime:** `28-SFProDisplay-Bold.fnt` in a **`30px`-tall** SBS `%Vl(large_title,…)` band **`(16,6,-16,30,2)`**; list content viewports for **`%Lo`** begin at **`y=40`**. Built with **`tools/otf_to_rb12_fnt.py`** from **`Apple Fonts/SF Pro/SF-Pro-Display-Bold.otf`**. Header title text is hidden on root (`%Lo`) to avoid redundant double-title. (`35-SFProDisplay-Bold.fnt` exists in `fonts/` as future upgrade to a full 56px band.)
- Section/list primary title (Apple 22 class):
  - **Lock:** `15–16px` medium/semibold.
  - **Primary candidate:** regenerated `SF Pro Text` at 16.
  - **Fallback:** `16-Inter-V.fnt` or `16-Inter-SemiBold.fnt`.
- Body primary (Apple 17 class):
  - **Lock:** `15px` regular/medium.
- Secondary/metadata (Apple 13 class):
  - **Lock:** `13–14px`.
  - **Primary candidates:** `14-SFCompactText-Regular.fnt`, `13-SFCompactText-Bold.fnt`.
- Micro/tab captions (Apple 10 class):
  - **Lock:** `10–11px` equivalent readability floor using compact cuts.

### 27.2 Mini-player / tracklist text lock
- Mini-player title: `15–16px` medium.
- Mini-player secondary/meta: `13px`.
- Tracklist title: `15px`.
- Track numbers/aux meta: `13px`.

### 27.1.1 Typography scale (Apple2026 hierarchy pass)
Standard five-level type scale for iPod 320x240 targets:

| Role | Font | Size | Where |
|---|---|---|---|
| Large title / hero | SFProDisplay-Bold | **28px** | Root `Library` band only (SBS slot 2) |
| Compact header | SFProText-Semibold | **16px** | Sub-surface titles (SBS slot 3) |
| Standard list items | SFProText-Regular | **18px** | Menus, settings, DB categories (SBS slot 5 / DEFAULT_FONTNAME) |
| Dense list items | SFProText-Regular | **16px** | Track/song files, playlist viewer, Cover Flow tracklist (dense tier) |
| WPS song title | SFProText-Medium | **16px** | Now Playing title (WPS slot 9) |
| Secondary metadata | SFProText-Regular | **14px** | WPS artist/album/time, mini-player track (WPS slot 3) |

- **Floor:** 14px for secondary detail only. 16px is the floor for interactive/primary text.
- **Two-tier font architecture (`rockpod_list_font_tier`):**
  - `ROCKPOD_LIST_FONT_NORMAL` — navigational menus (root, settings, DB top-level, music artist level). Row floor **32px**. Font: 18pt Regular.
  - `ROCKPOD_LIST_FONT_DENSE` — content/track lists (album/song folders at `dirlevel≥2`, playlist viewer, Cover Flow). Row floor **30px** (matches 30×30px `Apple2026Icons.bmp` tile height; no clipping). Font: 16pt Regular loaded lazily by `list.c`.
  - Tier is set by `root_menu.c` at surface dispatch and `tree.c` on depth change. Read by `apps/gui/list.c` and `apps/gui/bitmap/list.c`.
- **Cover Flow tracklist + album title:** `16-SFProText-Regular.fnt` (matches dense tier).

### 27.3 Practical rendering rule
- If two sizes are close, use the larger readable size.
- Reject any cut that renders muddy/thin in anti-aliased output.
- Inter remains fallback compatibility family, not flagship Apple2026 voice.

## 28) Apple-to-iPod typography scaling logic

### 28.1 Scaling model
- Reference frame: Figma `390x844`.
- Target hardware: iPod `320x240`.
- Raw geometric height scaling is not usable for typography due orientation and UI model differences.
- Preserve **hierarchy ratios** and semantic levels; adapt absolute px to readability floor.

### 28.2 Practical size translation window
- Effective typographic translation window: ~`0.65–0.75` of Apple reference sizes, then snapped to crisp `.fnt` outputs.
- Examples used for lock:
  - 34 → 22
  - 22 → 15–16
  - 17 → 13–15 (context dependent)
  - 13 → 10–13 (metadata floors)

### 28.3 Preserved vs adapted
- Preserved exactly:
  - hierarchy order,
  - relative emphasis steps,
  - title/body/secondary semantic roles.
- Adapted due hardware:
  - absolute px floors,
  - anti-aliasing readability constraints,
  - compact raster clarity limits.

## 29) Font converter regeneration protocol (Wave 2 lock)

Use converter tooling to generate missing sizes instead of forcing poor nearest presets.

### 29.1 Tool and defaults
- Use `tools/convttf.c` workflow (Rockbox `convttf` utility).
- Supports pixel-size targeting (`-p`), trimming (`-x`, `-Ta/-Td/-Ta/-Td`), spacing (`-c`, `-r`), and lighter hinting (`-L`).
- Output: `.fnt` (`RB12`), anti-aliased depth supported (`header.depth=1`, 4-bit path).

### 29.2 Regeneration policy
- Generate exact sizes for locked hierarchy first (22, 16, 15, 14, 13).
- For each generated font:
  - validate stem/counter clarity,
  - validate punctuation and digits,
  - validate long-title truncation behavior,
  - reject muddy/light variants.

### 29.3 Candidate families
- Preferred: SF Compact Display + SF Pro Text + SF Compact Text.
- Secondary: Inter family fallback.
- Rejected by default:
  - rounded novelty cuts for flagship,
  - light cuts that blur at locked sizes.

## 30) Wave 2 icon-source lock

### 30.1 Required icon categories
- Home/root menu, Music, Artists, Albums, Songs, Playlists, Cover Flow, Now Playing,
  Settings, System, Files, Search, Queue/current playlist,
  mini-player transport (play/pause/next/prev), chevrons/disclosures,
  loading/activity, utility/status (battery/lock/repeat/shuffle/volume).

### 30.2 Best current sources by category
- Home/root menu: Interpod/Interpod2 `InterNightPod.bmp` base.
- Music/Songs: `sf-symbols-master` `music.note`.
- Artists: `sf-symbols-master` `person`/`person.fill`.
- Albums/Cover groups: `sf-symbols-master` `rectangle.stack`/`rectangle.stack.fill`.
- Playlists/Queue: `sf-symbols-master` `music.note.list` or `list.bullet`.
- Settings/System: `sf-symbols-master` `gear`.
- Files: `sf-symbols-master` `folder`/`folder.fill`.
- Search: `sf-symbols-master` `magnifyingglass`.
- Transport: `play.fill`, `pause.fill`, `forward.fill`, `backward.fill` candidates.
- Disclosure: `chevron.right` (plain, non-circled).
- Loading/status utility: Interpod/Interpod2 runtime-proven status glyph sets.
- amusicpodds contribution: targeted semantic/icon ideas only, not base-pack replacement.

### 30.3 Glyph symbols vs imported icon library (final determination)

**Decision:** For Apple2026, SF-family **glyph symbols are better as the primary symbol system**;
imported icon libraries are secondary/fallback and should be used selectively.

#### Why glyph symbols win for primary UI icons
- Typography-coupled coherence: symbol weight/optical rhythm tracks the locked font hierarchy.
- Better Apple-native feel: SF glyph forms align with Apple reference semantics and proportions.
- Cleaner scaling workflow: regenerate fonts at locked sizes instead of manually re-rastering every icon size.
- State tinting consistency: same symbol can be rendered in Pink/Gray/Black/White sets with less drift.

#### Where imported library icons still win
- Runtime-proven tiny status assets (battery/lock/repeat/shuffle/activity) already validated in Rockbox theme flows.
- Legacy edge cases where glyph coverage or readability at tiny sizes is insufficient.
- Surface-specific compatibility during transition phases.

#### Source priority order (mandatory)
1. SF-family glyph symbols from locked Apple2026 font set (primary).
2. `sf-symbols-master` symbol bitmaps as candidate masters when glyph route is insufficient.
3. Interpod/Interpod2 imported icon packs for tiny status/system fallbacks.
4. amusicpodds icon candidates only when semantically stronger and normalization-safe.

#### Mixing rule
- Do not mix unmatched glyph/icon styles within the same UI surface.
- If a surface uses glyph symbols, use glyph symbols consistently for that surface's primary action/navigation set.
- Imported fallback icons must be optically normalized to the active glyph family before use.

## 31) Icon color/state logic lock
- Pink/Red set (`#FF2D55`): active music emphasis and selected navigation state.
- Gray set: passive/disclosure/secondary and inactive hierarchy states (`#3C3C43` on light lists for settings/system icons in the main strip).
- Black set: primary symbols on light surfaces for max clarity (folder, cursors, submenu chevrons).
- White set: inverse-only contexts (dark overlays/special surfaces).
- Prohibited: arbitrary per-icon tinting without semantic state meaning.
- **Implementation:** `tools/apple2026_symbol_assets.py` applies **per-index** tints to `icons/Apple2026Icons.bmp` (music-first row indices vs navigation vs settings).

## 32) Icon optimization / regeneration plan (implementation)

1. Source selection by category.
2. Semantic mapping: one canonical meaning per UI function.
3. Typography-coupled target sizing from section 27 lock.
4. Optical normalization (weight, mass, corner behavior).
5. iPod-safe scaling (integer-friendly raster targets).
6. Padding/inset normalization across row/tab/player contexts.
7. Silhouette cleanup (simplify overly detailed symbols).
8. Anti-cropping safeguards (safe boxes + clipping checks).
9. Color-state generation (Pink/Gray/Black/White variants).
10. Simulator validation and runtime replacement of legacy mismatched icons.

### 32.1 Validation gates for icon batches
- Must remain crisp at locked size.
- Must not crop in any assigned container.
- Must maintain family coherence with neighboring icons.
- Must pass semantic-color rules in section 31.

## 33) Wave 2 -> Wave 3 readiness gate (implementation planning lock)

This section defines whether Wave 2 is specific enough for Wave 3 shell implementation and
what must be locked before full execution.

### 33.1 Wave 2 elements fully locked (safe to implement now)
- Source hierarchy and donor priority are locked (sections 3, 7A, 26).
- Core list geometry tokens are locked:
  - library `52px`, album list `56px`, track list `48px`.
- Core inset/divider tokens are locked:
  - shell inset `16px`, album list text/divider inset `76px`, track divider inset `50px`, separator `0.5px`.
- Selector direction is locked:
  - flat/non-gradient, neutral iOS-like gray default selection bar.
- Accent policy is locked:
  - `#FF2D55` is emphasis-only (music-active semantics), not default list selection.
- Scrollbar direction is locked:
  - visible, right-aligned, subtle (no scrollbar-off flagship default).
- Icon strategy is locked:
  - SF glyph symbols primary; imported icon libraries fallback by priority order (section 30.3).
- Icon semantic state palette is locked:
  - Pink active, Gray passive, Black primary-on-light, White inverse-only (section 31).
- Mini-player/tab-bar continuity rule is locked at behavioral level (section 18).
- Donor rejection rules are locked (section 26.6).

### 33.2 Wave 2 ambiguity resolution lock (completed for Wave 3 completion)
- Header size/alignment (locked):
  - header container: `x=0, y=0, h=26`,
  - title viewport: `y=5, h=17`,
  - compact title baseline class: `font slot 3 (16px SF Pro Text Medium, matches WPSLIST default)`,
  - trailing status/action lane anchor: `battery box x=288, y=4, w=27, h=16`.
- Chevron placement (locked):
  - right inset: `8px`,
  - vertical centering: row midpoint with optical nudge `-1px` if needed by glyph.
- Icon reserve width (locked):
  - main strip tiles: **`22×20`px** (`icons/Apple2026Icons.bmp`); with `ICON_PADDING` **1px** the list icon column is **24px** wide — close to the Figma **29px** icon container on a 320px canvas.
  - icon-to-title gap: **`8px`** (text starts after icon column + padding).
- Scrollbar numeric token (locked):
  - side: `right`,
  - width: `2px`,
  - right-edge spacing: `2px` (subtle inset thin-indicator behavior).
- Battery indicator scale (locked):
  - icon strip frame size: `27x16`,
  - battery text lane: `x=-70, y=5, w=38, h=15`,
  - lock icon lane: `x=24, y=7, w=9, h=12`.
- Mini-player numeric geometry (locked):
  - expanded mini-player container: `h=36` (`y=-36` anchored),
  - compact mini-player container: `h=11` (`y=-11` anchored),
  - mini-player art: `30x30` at `x=8, y=-33`,
  - title baseline lane: `x=46, y=-28, h=16` (8px gap after `30px` art at `x=8`),
  - meta baseline lane: `x=46, y=-14, h=14`,
  - state indicator lane: `x=284, y=-26, w=20, h=16`.
- Loading-state shell behavior (locked):
  - splash/frame spacing token: `RECT_SPACING=8`,
  - loading/progress rail thickness: `2px`,
  - centered wait label + centered neutral rail under label.
- Typography precision (locked per surface):
  - library header: `16px` (`16-SFProText-Medium.fnt`),
  - list title: `16px` (`16-SFProText-Medium.fnt`),
  - list secondary: `13px` (`13-SFCompactText-Regular.fnt`),
  - mini-player title: `16px` (`16-SFProText-Medium.fnt` where lane allows, else `15px`),
  - mini-player meta: `13px` (`13-SFCompactText-Regular.fnt`),
  - track title: `16px` (`16-SFProText-Medium.fnt`),
  - track/meta secondary: `13px` (`13-SFCompactText-Regular.fnt`).

#### 33.2.1 Wave 3 micro-polish (optical refinement; does not change row-class targets)
- **WPS horizontal inset:** primary text/stack and scrubber use **16px** left/right inset (§10 gutter), not ad-hoc 18/20px.
- **Root large-title row (SBS):** `%Vl(large_title,…,-16,…)` right inset **16px** (match §10; avoid asymmetric `-32` clipping long titles early).
- **Tertiary/meta hex:** unify muted labels to **`#6E6E73`** on light shell (avoid mixed `6F6F73` / `6E6E73`).
- **Thin rails (progress / volume):** track fill **`#E5E5EA`** for calmer contrast vs **`#DADADD`** on **`#F8F8F8` / `#EDEDED`** surfaces.
- **WPS / mini-player rail thickness (Wave 3 rebuild):** progress scrubber **4px** track with **5px** active fill; volume scrubber **3px** — reads closer to Apple Music control weight than 2px Rockbox defaults.
- **Mini-player:** title/meta lanes at **`x=46`** so **8px** clear gap after **30px** art (**§18** icon-to-text rhythm).
- **WPS art render path:** draw album art in the main render layer (no `%VB` on art viewport) so first-frame cover art is reliably visible.
- **Progress/volume visual parity:** both controls use a flat neutral rail language (`#E5E5EA` base, darker fill) to avoid mixed bitmap-vs-flat slider styles.
- **Menu selector tone:** default selector gray is lightened to a softer neutral (`#DADAE0` family), not heavy dark gray.
- **Menu separators:** Apple2026 main list defaults to separator-off during this polish pass (including header-under-title separator removal).
- **Main menu emphasis scale:** default list/body font on iPod 5/71 is bumped to the 20px class with row-height safety and increased icon-padding to preserve spacing rhythm.

### 33.3 Pre-Wave 3 lock checklist (resolved)
The following required lock items are now explicitly resolved by section 33.2:
1. Header numeric spec (resolved).
2. Chevron numeric spec (resolved).
3. Scrollbar numeric spec (resolved).
4. Battery spec (resolved).
5. Mini-player spec (resolved).
6. Loading-state spec (resolved).
7. Surface-specific final font mapping (resolved).

### 33.4 Wave 3 implementation surfaces (exact file/asset map)

#### 33.4.1 Runtime theme registration and config
- `wps/WPSLIST` (register Apple2026 theme so build output writes `.rockbox/themes/*.cfg`).
- Generated/deployed runtime path to validate in simulator:
  - `build-sim/simdisk/.rockbox/themes/`
  - `build-sim/simdisk/.rockbox/wps/`
  - `build-sim/simdisk/.rockbox/icons/`
  - `build-sim/simdisk/.rockbox/fonts/`

#### 33.4.2 Theme shell files (primary Wave 3 edit targets)
- New Apple2026 config + shell files (to be added and wired via `WPSLIST`):
  - `.cfg` (theme-level color/selector/scroll/status/font/icon bindings)
  - `.sbs` (header/list chrome + mini-player shell behavior)
  - `.wps` (now playing and track/album composition)
- Baseline donor files for controlled extraction (read-only references):
  - `Imported Reference Themes/Interpod/.rockbox/themes/Interpod.cfg`
  - `Imported Reference Themes/Interpod/.rockbox/wps/Interpod.sbs`
  - `Imported Reference Themes/Interpod/.rockbox/wps/Interpod.wps`
  - `Imported Reference Themes/Interpod 2/.rockbox/themes/Interpod 2.cfg`
  - `Imported Reference Themes/Interpod 2/.rockbox/wps/Interpod 2.sbs`
  - `Imported Reference Themes/Interpod 2/.rockbox/wps/Interpod 2.wps`

#### 33.4.3 Icon assets
- Primary target iconsets to create/replace for Apple2026:
  - `icons/*` (main list/tab/menu icon strips)
  - optional status/helper strips used by `.sbs/.wps` image tags.
- Donor/reference icon assets:
  - `Imported Reference Themes/Interpod/.rockbox/icons/InterNightPod.bmp`
  - `Imported Reference Themes/amusicpodds/.rockbox/icons/amusicpod.bmp`
  - `Sourced Icons/sf-symbols-master/*`

#### 33.4.4 Font assets and mapping
- Final `.fnt` outputs must exist under runtime fonts path before list geometry sign-off.
- Current baseline source family references:
  - `Imported Reference Themes/.../.rockbox/fonts/*Inter*.fnt`
  - `Imported Reference Themes/.../.rockbox/fonts/*SF*.fnt`
  - generated outputs from `tools/convttf` workflow.

#### 33.4.5 Optional secondary surfaces (only if shell parity requires)
- `.fms` is optional in initial Wave 3 unless FM shell parity is explicitly included.
- Core C rendering files are out of scope unless a hard visual requirement is impossible via theme assets alone.

### 33.5 Wave 3 screen/shell implementation order (stability-first)
1. **Theme scaffolding + token wiring**
   - register theme in `WPSLIST`, establish `.cfg`, bind locked colors/fonts/icons/selectors/scrollbar.
2. **Header system (SBS)**
   - lock top strip behavior, title hierarchy, battery/lock/activity placements.
3. **List geometry + text inset rhythm**
   - enforce row heights and insets (`52/56/48`, `16/76/50`) across target list surfaces.
4. **Chevron/divider/icon integration**
   - enforce tertiary chevron behavior, `0.5px` inset separators, icon reserve alignment.
5. **Selector + scrollbar behavior**
   - apply flat selector token and subtle right scrollbar token with no gradient regressions.
6. **Mini-player continuity**
   - integrate persistent lower shell and tab bar rhythm above list surfaces.
7. **WPS parity alignment**
   - align now-playing composition with Apple2026 lock while preserving Interpod DNA.
8. **Loading/empty state shelling**
   - remove generic boxed feel; apply native shell typography/rhythm.
9. **Whole-shell consistency review**
   - cross-screen state/color/spacing audit before declaring Wave 3 visual pass complete.

### 33.6 Wave 3 validation plan (simulator + screenshots)

#### 33.6.1 Build cadence
- Rebuild simulator after each major step in section 33.5.
- If simulator build is not green, implementation progress is blocked from visual sign-off.

#### 33.6.2 Required screenshot set per major step
- Header pass:
  - library root top area (title + status indicators), compact list header variant.
- List geometry pass:
  - library list, album list, track list with visible row rhythm and separators.
- Icon/chevron/divider pass:
  - list with disclosure indicators + icon-bearing rows.
- Selector/scrollbar pass:
  - active selected row + right scrollbar in long list.
- Mini-player pass:
  - list + persistent mini-player + tab bar in one frame.
- WPS pass:
  - now playing (play, pause, seek/volume visible states).
- Loading pass:
  - loading state and at least one empty/error-like shell state.

#### 33.6.3 Comparison sources for every screenshot
1. Figma nodes `1:4008`, `1:475`, `1:5998`
2. Apple references listed in `MASTER.md`
3. Interpod lineage baseline

#### 33.6.4 Pass/fail criteria
- **Pass**: numeric geometry/token compliance, source hierarchy compliance, no rejected tokens.
- **Fail**: gradient selector reintroduced, dark-shell inversion, missing subtle scrollbar,
  chevrons/icons visually dominant, or typography hierarchy drift from locked mapping.

### 33.7 Drift prevention rules (Wave 3 execution guardrails)
- No Wave 3 visual edit is allowed unless it maps to a rule in this document.
- If a required value is missing from this document, implementation pauses and the value is
  first added as a lock (not guessed in code/theme files).
- For each changed surface, `WORK_LOG.md` must record:
  - touched files,
  - screenshot evidence,
  - pass/fail against Figma/Apple/Interpod hierarchy,
  - unresolved mismatches and explicit next action.
- Any mismatch that cannot be justified by source hierarchy blocks "done" state for that step.
- Cover Flow/performance/caching changes remain forbidden in this branch.

#### 33.7.1 Figma / iOS reference adaptation (iPod form factor)
- Figma nodes and iOS-oriented references define the **visual language**: hierarchy, separator
  opacity family (`#3C3C43` @ ~38%), typography roles, inset-divider discipline, icon/symbol
  logic, and calm “Apple-native” polish.
- Apple2026 on **320×240** implements **section 54** geometry and color tokens. Values are
  **not** a literal copy of iPhone point geometry; they are chosen so the shell **feels like
  the same design ecosystem** while respecting click-wheel density, Rockbox list/font metrics,
  and hardware constraints.
- When Figma pt numbers and §54 tokens disagree, **§54 wins** for shipped firmware; Figma remains
  the compass for proportion and hierarchy, not for pixel-perfect phone cloning.

### 33.8 Go / no-go decision for Wave 3
- **Go** for Wave 3 completion work:
  - section 33.3 numeric lock checklist is now resolved in-document,
  - implementation must stay within these tokens and source hierarchy.
- **No-go** only when a newly discovered surface requirement has no numeric/token lock.

## 34) Wave 2 full-product coverage lock (end-to-end surfaces)

Wave 2 now covers all major interface surfaces and transition states, not only core list shells.

### 34.1 Included surface families
- Boot/startup presentation.
- Theme/core loading and wait states.
- Home/root shell and all primary music lists.
- Album list and album page composition targets.
- WPS/Now Playing and mini-player continuity.
- Cover Flow UI surfaces and Cover Flow tracklist surfaces (UI only).
- Settings and Files/filesystem screens.
- Empty/fallback/error-like content states.
- End-to-end user flow continuity and return behavior.

### 34.2 Scope boundary (non-negotiable)
- This section defines visual/UX behavior only.
- No performance optimization, no deep Cover Flow architecture, no cache strategy redesign,
  and no Cover Flow internals tuning are permitted in this Wave 2 lock.

## 35) Boot / startup experience lock

### 35.1 Source asset lock
- Intended source image: `Sourced Icons/iPhone-Rebooting.png`.
- Verified source dimensions: `640x1136`.
- Visual intent: black field + centered Apple mark, no decorative UI chrome.

### 35.2 iPod target adaptation lock
- Target boot canvas: `320x240` (iPod Classic runtime orientation).
- Composition rule:
  - build a pure-black `320x240` canvas,
  - extract/scale Apple mark from source,
  - center logo on both axes optically and mathematically.
- Logo sizing rule:
  - logo height target band `34px` to `46px` on `240px` height,
  - default lock target: `40px` logo height unless panel test requires +/−2px.
- Text rule:
  - no extra text in flagship startup presentation,
  - no boot version text in the visual layer.

### 35.3 Crop/resize protocol
1. Detect non-black logo bounds from source image.
2. Export logo-only layer (white mark on transparent or black background).
3. Resize logo into locked target band with nearest clean anti-aliased result.
4. Composite onto black `320x240` canvas, centered.
5. Validate in simulator/hardware capture for logo centering and luminance balance.

### 35.4 Technical integration surfaces (implementation-facing)
- Generic boot path reference: `bootloader/show_logo.c` (draws logo + boot version text).
- iPod 6G startup path reference: `bootloader/ipod-s5l87xx.c` (text-first boot path currently).
- Bitmap source family reference: `apps/bitmaps/native/rockboxlogo.*.bmp`.

### 35.5 Boot fallback policy
- If full-screen boot replacement is blocked technically, use a centered Apple mark on black
  through the nearest available boot-logo path while suppressing non-essential text where possible.

## 36) Loading / wait-state system lock

### 36.1 Global loading behavior
- Loading states must read as shell-native, quiet, and Apple-like.
- Default loading palette:
  - black/near-black or shell-appropriate neutral background,
  - neutral primary text,
  - restrained progress indicators,
  - no harsh debug-box framing where theme/plugin surface allows custom draw.

### 36.2 Core splash/loading surfaces
- Core splash functions reference: `apps/gui/splash.c`.
- Existing rectangular border behavior is baseline fallback; Apple2026 surface styling should,
  where possible, reduce visual box harshness through controlled foreground/background tokens.
- Progress bars should appear as thin, calm, low-chroma indicators.

### 36.3 PictureFlow loading surfaces
- PictureFlow splash/progress references:
  - `draw_splashscreen()`
  - `draw_progressbar()`
  - `show_track_list_loading()`
  in `apps/plugins/pictureflow/pictureflow.c`.
- Required style direction:
  - consistent typography and neutral loading language,
  - no bright non-semantic green progress fill for flagship Apple2026,
  - loading label and bar spacing aligned to shell rhythm.

### 36.4 Wait-state content rules
- Approved wait copy tone:
  - concise, task-specific, non-technical where possible.
- Blocked tone:
  - noisy diagnostics and abrupt warning-only framing for normal waits.

## 37) Home / root menu shell lock

### 37.1 Geometry and hierarchy
- Preserve large-title hierarchy and light-shell baseline.
- Header zone must remain visually calm; battery/activity indicators tertiary.
- Row and inset lock remains:
  - `52px` row height,
  - `16px` horizontal inset,
  - `0.5px` inset separators.

### 37.2 Selection and state
- Default selected-row behavior: solid neutral gray bar (iPhone-like), non-gradient.
- Accent pink is reserved for music-emphasis state markers, not default list selection.

### 37.3 Scroll/disclosure
- Thin right-edge subtle gray scrollbar.
- Chevron as tertiary disclosure only; never dominant.

## 38) Music list screens lock (Artists/Albums/Songs/Playlists/DB/Files-future)

### 38.1 Common list rules
- Single visual family across all music lists.
- Stable icon reserve + text reserve + chevron reserve structure.
- Truncation policy:
  - single-line priority for title,
  - secondary line optional only where source hierarchy requires.

### 38.2 Density and spacing
- Artists/Songs/Playlists default to library rhythm unless album-art row model is required.
- Database and future filesystem-first music lists must keep same shell language and
  only differ by icon semantics/hierarchy cues.

## 39) Album list UI lock (Figma node `1:475`)

- Row height: `56px`.
- Cover size: `48px` square.
- Text/divider inset: `76px`.
- Metadata hierarchy:
  - title primary,
  - artist/secondary below,
  - concise two-line max.
- Disclosure placement:
  - right-aligned tertiary chevron, vertically centered to row.
- Divider behavior:
  - content-inset, hairline, quiet contrast.

## 40) Album page UI lock (Figma node `1:5998`)

- Hero art target: `270px` reference scale, proportionally adapted for iPod constraints.
- Centered metadata stack preserved.
- Action pills:
  - equal-weight pair,
  - soft-neutral fill,
  - restrained corner radius and spacing.
- Track rows:
  - `48px` rhythm,
  - `50px` inset divider model.
- Future-facing rule:
  - even if not fully implemented immediately, hero/metadata/action hierarchy must remain canonical
    for future completion and should not be replaced with legacy dense WPS-like stacks.

## 41) Now Playing / WPS lock

### 41.1 Composition
- Preserve Interpod DNA:
  - strong album art anchor,
  - clear title > artist > album readability,
  - stable progress and transport rhythm.
- Apply Apple principles:
  - less ornamental chrome,
  - calmer typographic hierarchy,
  - restrained accent usage.

### 41.2 Metadata/truncation
- Title must remain highest priority line.
- Artist/album are secondary and may scroll/truncate with controlled timing.
- Clipping must never cut baseline/stem integrity.

### 41.3 Missing-art fallback
- If art missing: use shell-consistent placeholder with same geometry,
  not layout collapse or abrupt text jump.

## 42) Mini-player / What’s Playing bar lock

- Persistent shell layer above tab bar in browsing surfaces.
- Height and rhythm must stay compact and stable across list contexts.
- Required content order:
  1) small art anchor,
  2) title line,
  3) restrained play/pause indicator.
- Hairline separator required between list and mini-player surfaces.
- Mini-player typography must follow body+secondary lock from section 27.

## 43) Cover Flow UI lock (UI-only)

### 43.1 Integration boundary
- Cover Flow remains a plugin surface (`apps/plugins/pictureflow/pictureflow.c`) but must
  visually read as part of the Apple2026 shell.
- No performance or architecture modifications are included in this lock.

### 43.2 Header/title and status treatment
- Persistent title should remain concise ("Cover Flow" allowed until renamed).
- Statusbar mode must be consistent with Apple2026 shell decision per surface, not arbitrary.
- If statusbar is hidden for a specific Cover Flow mode, typography and top spacing still follow
  Apple2026 top rhythm.

### 43.3 Label typography and placement
- Album/artist labels use same hierarchy logic as main shell.
- Text crossfade/scroll behavior must prioritize readability over effect intensity.

### 43.4 Cover Flow loading styling
- Splash and progress visuals should share Apple2026 loading grammar.
- Replace bright/non-semantic progress fills with neutral shell-consistent fills.

### 43.5 Placeholder styling
- Empty slide/placeholder (`pictureflow_emptyslide`) must remain neutral and unobtrusive,
  not high-contrast novelty artwork.

## 44) Cover Flow tracklist screen lock

- Tracklist header remains shell-consistent with Cover Flow context title.
- Row order visual hierarchy:
  - track title primary,
  - no noisy prefixes unless required for disambiguation.
- Selected-row treatment follows global selector lock:
  - solid neutral gray, non-gradient.
- Typography and spacing align with list-system rules; no plugin-only visual dialect.
- Loading-before-tracklist must use same loading grammar (centered wait text + restrained indicator).
- Scrollbar remains thin right-edge gray style when list exceeds viewport.
- Return flow must preserve album context and avoid abrupt visual mode-jumps.

## 45) Settings surface lock

- Settings stays in same shell family as music lists.
- Allowed differentiation:
  - slightly lower icon emphasis,
  - utility-first semantics.
- Development period requirement:
  - Theme Settings remain visible.
- EQ prominence requirement:
  - maintain elevated discoverability in top-level settings flow.
- Row/divider/selector/chevron behavior should remain structurally identical to main list system.

## 46) Files / filesystem screen lock

- Filesystem lists should not appear as a different product skin.
- Folder/file indicators use same icon grammar with clear semantic distinction.
- Chevron/disclosure rules remain identical to other hierarchical lists.
- Spacing and scrollbar behavior remain in Apple2026 list family.

## 47) Fallback / empty-state matrix lock

### 47.1 Required empty states
- No music library data.
- No playlists.
- No resume/last-track state.
- Missing album art.
- Cover Flow cache unavailable/not built.
- Tracklist unavailable for selected album.

### 47.2 Visual rules
- Keep shell-native spacing and typography.
- Use neutral language and simple guidance.
- Preserve return affordance and hierarchy context.
- Never drop into visually unrelated debug-style framing for ordinary fallback cases.

## 48) Scrollbar lock (iOS-like thin gray)

- Baseline style: thin neutral gray indicator similar to current iOS language.
- Placement: right edge.
- Width lock target for `320x240`: `2px` visual thickness (fallback `3px` only if panel rendering requires).
- Contrast: low-to-moderate; must be visible but near-background in idle view.
- Visibility rule:
  - show only when content exceeds viewport,
  - if platform surface cannot auto-hide, keep static low-contrast style.

## 49) Chevron / disclosure lock

- Role: hierarchical disclosure/navigation only.
- Tone: neutral gray, tertiary emphasis.
- Placement: right-aligned with consistent inset from row edge.
- Size expectation on `320x240` class:
  - compact, approximately `6x10` to `7x11` optical range.
- Weight expectation:
  - thin/medium stroke appearance; never bold or filled-dominant.

## 50) Icon color/state system lock (complete)

### 50.1 State palettes
- **Gray set**: passive, disclosure, structural list utility, default selected-row family context.
- **Black set**: primary symbols on light surfaces.
- **White set**: inverse-only contexts (dark overlays/special transient states).
- **Pink/Red set (`#FF2D55`)**: active music emphasis (playback-active, key action emphasis,
  selected top-level music semantics where appropriate).

### 50.2 State rules
- No arbitrary per-icon tinting.
- No mixing unrelated icon families in one surface.
- Default list selection bar is gray (iPhone-like), not pink.
- Pink accent should mark meaningful music emphasis, not generic focus navigation.

## 51) Complete user-flow continuity lock

### 51.1 End-to-end journey map
1. Boot/startup (black + centered Apple mark) ->
2. Home/root shell ->
3. Music browse (Artists/Albums/Songs/Playlists) ->
4. Album list ->
5. Album context / tracklist ->
6. Now Playing (WPS) + persistent mini-player continuity ->
7. Cover Flow browse (optional path) ->
8. Cover Flow tracklist ->
9. Settings/filesystem/fallback branches ->
10. predictable return to prior music context.

### 51.2 Continuity rules across transitions
- Header rhythm persists across surfaces (large-title vs compact-header model).
- Selector/scrollbar/chevron semantics remain stable across all hierarchical lists.
- Typography hierarchy remains consistent when moving between list, album, WPS, and Cover Flow text surfaces.
- Mini-player continuity must not visually detach from list shell during navigation transitions.
- Loading/fallback states must preserve the same shell identity and return affordance.

### 51.3 Return-path behavior requirements
- From Cover Flow tracklist -> return to same album/cover context.
- From WPS -> return to prior browse context without shell reset feel.
- From settings/filesystem -> re-enter music shell with unchanged visual grammar.
- From fallback states -> clear path back to actionable browse surfaces.

## 52) Wave 2 full-coverage completion gate

- Wave 2 may be considered full-coverage only when sections 35-51 are represented in
  implementation planning and screenshot validation.
- Wave 3 execution must block any surface whose numeric/value lock is still ambiguous.
- Any cross-surface inconsistency discovered during Wave 3 must be resolved by updating this
  design-system lock before continuing broad implementation.

## 53) Strict pre-implementation layer (Wave 2 exactness gate)

This section is a pre-code execution contract. If a value is not explicitly defined here,
Wave 3 implementation for that surface is blocked.

### 53.1 Rockbox theme construction model (practical)

#### 53.1.1 Source references used
- Rockbox CustomWPS model (construction semantics baseline):
  - `https://www.rockbox.org/wiki/CustomWPS.html`
- In-repo practical construction sources:
  - `Imported Reference Themes/Interpod/.rockbox/themes/Interpod.cfg`
  - `Imported Reference Themes/Interpod/.rockbox/wps/Interpod.sbs`
  - `Imported Reference Themes/Interpod/.rockbox/wps/Interpod.wps`
  - `Imported Reference Themes/Interpod 2/.rockbox/themes/Interpod 2.cfg`
  - `Imported Reference Themes/Interpod 2/.rockbox/wps/Interpod 2.sbs`
  - `Imported Reference Themes/Interpod 2/.rockbox/wps/Interpod 2.wps`
  - `Imported Reference Themes/amusicpodds/.rockbox/themes/amusicpodds.cfg`
  - `Imported Reference Themes/amusicpodds/.rockbox/wps/amusicpodds.sbs`
  - `Imported Reference Themes/amusicpodds/.rockbox/wps/amusicpodds.wps`

#### 53.1.2 Construction responsibility map
- `.cfg` controls:
  - theme linkage (`wps`, `sbs`, `fms`), font/icon bindings,
  - core list renderer tokens (selector, scrollbar, statusbar, colors).
- `.sbs` controls:
  - status/header shells, title bars, list viewport boundaries, mini-player shell logic.
- `.wps` controls:
  - now-playing composition (art, metadata stack, progress, playback states).
- Plugin UI surfaces (PictureFlow) control their own rendering in C:
  - `apps/plugins/pictureflow/pictureflow.c`.
- Core splash/wait fallback rendering is controlled by core UI code:
  - `apps/gui/splash.c`.
- Boot/startup visuals are target-dependent bootloader behavior:
  - iPod path reference: `bootloader/ipod-s5l87xx.c`
  - generic logo path reference: `bootloader/show_logo.c`.

### 53.2 Precision limits vs precision-available zones
- Precision-available (must be exact):
  - WPS/SBS viewport coordinates, bitmap boxes, font selections, color tokens, icon slots.
- Precision-limited (must be documented as bounded):
  - core list internal text baseline behavior,
  - splash box internals in `splash.c`,
  - plugin-only rendering paths unless explicitly edited in plugin code.

## 54) Exact geometry token table (Apple2026 implementation lock)

All values in this section are for the iPod `320x240` class and are Wave 3 implementation defaults.

### 54.1 Global shell tokens
- `screen_w = 320`
- `screen_h = 240`
- `header_y = 0`
- `header_h = 26`
- `header_hairline_y = 24` (`DCDCE0`); `header_hairline_soft_y = 25` (`F4F4F4`)
- `content_y = 27` (first list line below compact header when no large title)
- `content_y_large_title = 60` (first list line when root large-title band is active)
- `large_title_y = 4` (band start — aligns with `wps/Apple2026.sbs` `%Vl(large_title,16,4,-16,56,2)`)
- `large_title_h = 56` (band height; 35px SF Pro Display Bold + breathing room)
- `large_title_font_h = 35` (slot 2: `35-SFProDisplay-Bold.fnt`; regenerate with `tools/otf_to_rb12_fnt.py` or stock `tools/convttf` + OTF)
- `large_title_separator_y =` *none* (hairline under title band removed in current SBS pass)
- `list_viewport_x = 16` (Apple-like left inset)
- `list_viewport_w = 288` (320 - 16 - 16)
- `left_inset = 16`
- `right_inset = 16`

**Interpod adaptive viewport system** (Wave 3d, replaces fixed absolute heights):
Heights are defined as negative offsets from screen bottom, so they self-adjust.

Playing/paused (`mainlarge` — max content, thin 11px strip at bottom):
- `mainlarge_y = 27`, `mainlarge_neg_h = -12` → content h = `240-27-12 = 201`
- `mainlarge_lt_y = 60`, `mainlarge_lt_neg_h = -12` → content h = `240-60-12 = 168`

Stopped (`main` — smaller content, 36px bottom bar showing last track):
- `main_y = 27`, `main_neg_h = -37` → content h = `240-27-37 = 176`
- `main_lt_y = 60`, `main_lt_neg_h = -37` → content h = `240-60-37 = 143`

#### 54.1.1 Shell vertical stack and SBS routing (`wps/Apple2026.sbs`)
Rockbox draws the **statusbar skin (SBS)** as the chrome layer; the **list** is clipped to the
active `%Vi(...)` UI viewport. Apple2026 uses two independent switches.

**Key insight (Interpod pattern):** `%mp` TRUE = playing/paused; FALSE = stopped.
When playing → `mainlarge` (more content, thin 11px strip). When stopped → `main` (less content, 36px bottom bar with last-played track).

| Switch | Meaning | Viewport selected |
|--------|---------|-----------|
| `%?mp` TRUE | Playing/paused | `mainlarge_lt` or `mainlarge` — 201px/169px content |
| `%?mp` FALSE | Stopped | `main_lt` or `main` — 176px/144px content |
| `%?Lo` TRUE | At root | `_lt` variant — list starts at **y=60** (large title above) |
| `%?Lo` FALSE | Sub-menu | Standard variant — list starts at y=27 |

Routing: `%?mp<%?Lo<%VI(mainlarge_lt)|%VI(mainlarge)>|%?Lo<%VI(main_lt)|%VI(main)>>`

Vertical stack (playback **on**, large title **on** — the most content-constrained case):

```
y=0..23   header band (F8F8F8)
y=24      DCDCE0 hairline
y=25      F4F4F4 soft hairline
y=26      1px screen background (FFFFFF, transitions to title)
y=4..59   large title band "Library" (35px SF Pro Display Bold, FFFFFF bg, 56px viewport)
y=60..227 list content (mainlarge_lt: ~168px, FFFFFF)
y=228..239 11px thin strip (bottombarsmall: hairline only)
```

Vertical stack (playback **off**, large title **off** — full content view from sub-menu):

```
y=0..25   header band + hairlines
y=27..202 list content (main: h=176, FFFFFF)
y=203..239 36px bottom bar (bottombar: last-played art + title, F8F8F8)
```

**Architecture rule:** Do not change bottom bar heights without updating the paired `%Vi`
negative-height values. The negative offsets (`-12` and `-37`) must match the strip/bar heights
(`12 = 11px strip + 1px hairline` and `37 = 36px bar + 1px hairline`).

### 54.2 Header and indicator tokens
- `title_baseline_y = 17`
- `title_x_default = 74`
- `title_x_wide = 56` (battery-text-hidden mode)
- `battery_icon_box = (x:288, y:4, w:28, h:15)` (asset: `batteryStatus.bmp` frames 28×15)
- `battery_text_box = (x:250, y:5, w:38, h:15)`
- `lock_icon_box = (x:24, y:7, w:9, h:12)`
- `busy_indicator_box = (x:58, y:9, w:9, h:9)`

### 54.3 List geometry tokens
- `library_row_h = 52` (Figma `1:4008`; enforced as firmware minimum line height in `apps/gui/list.c` for `ROCKPOD_APPLE2026_IPOD`)
- `album_row_h = 56` (Figma reference)
- `track_row_h = 48` (Figma reference)
- `menu_list_font = 20-SFProText-Regular.fnt` (WPSLIST + `settings_list.c` + SBS slot 5)
- `icon_tile_w = 30` (`tools/apple2026_symbol_assets.py` → `icons/Apple2026Icons.bmp`)
- `icon_tile_h = 30`
- `row_h_firmware = 52` (`list_init_item_height` minimum in `apps/gui/list.c` for `ROCKPOD_APPLE2026_IPOD`)
- `icon_padding = 4` per side (`ICON_PADDING` in `apps/gui/bitmap/list.c`; **8px** total horizontal pad → **~8px** icon-to-label gap vs Figma **8px**)
- `icon_column_w = 30 + 4 + 4 = 38` (icon width + symmetric padding)
- `text_start_x_in_viewport = 38` (text starts after icon column)
- `text_start_x_from_screen_edge = 16 + 38 = 54` when list viewport uses **16px** horizontal inset (`%Vi`); divider inset in viewport coordinates matches text column (**38** from left of list VP)
- `divider_thickness = 1`
- `divider_implementation = inset` (separator drawn by `line.c` then icon-column portion covered in `_default_listdraw_fn` with viewport bg, creating Apple-style text-column-inset dividers)
- `divider_inset_x_in_viewport = 38` (divider visible from x=38 within the list viewport — icon column masked)
- `divider_inset_library = 38` (same; list VP is already inset **16px** from screen in `Apple2026.sbs`)
- `divider_inset_album = 76` (Figma: 48px art + 28px text margin)
- `divider_inset_track = 50` (Figma: 44px art + 6px gap)

**Visible row counts** (with **52px** rows and Interpod adaptive viewport heights — approximate):
- `visible_rows_playing_lt = floor(168/52) = 3` (root + playing: mainlarge_lt)
- `visible_rows_playing_no_lt = floor(201/52) = 3` (sub-menu + playing: mainlarge)
- `visible_rows_stopped_lt = floor(143/52) = 2` (root + stopped: main_lt — tight; verify on device)
- `visible_rows_stopped_no_lt = floor(176/52) = 3` (sub-menu + stopped: main)

### 54.4 Chevron/scrollbar/selector tokens
- `chevron_w = 5` (drawn via `drawline` in `apps/gui/bitmap/list.c`)
- `chevron_h = 10`
- `chevron_right_inset = 10` (from right edge of list text viewport)
- `chevron_color = C7C7CC` (Apple tertiary label — quiet gray, subdued on both white bg and selector)
- `chevron_implementation = drawline` (two `drawline` calls forming ">" after each row's `put_line`)
- `chevron_cy_formula = y + (line_h - 10) / 2` (vertically centered in row)
- `chevron_cx_formula = vp_w - 15` (5px chevron + 10px right inset from viewport right edge)
- `scrollbar_side = right`
- `scrollbar_w_default = 2`
- `scrollbar_w_fallback = 3`
- `scrollbar_right_inset = 2`
- `selector_style = flat_color`
- `selector_lss_color = E5E5EA` (WPSLIST `selector start color`)
- `selector_lse_color = E5E5EA` (WPSLIST `selector end color` — flat, no gradient; Picture Flow tracklist uses same fill in `pictureflow.c` `draw_gradient`)
- `selector_lst_color = 000000` (text color on selector)
- `selector_gradient = forbidden`

### 54.5 Mini-player / bottom bar tokens (Interpod adaptive)

The bottom bar height is **adaptive** — two states driven by `%?mp`:

**Stopped state** (`bottombar` — 36px, shows last-played track):
- `bottombar_h = 36` (viewport: `%Vl(bottombar,0,-36,-,-,-)`)
- `bottombar_hairline_y = 0` (DCDCE0 at top of bar)
- `bottombar_hairline_soft_y = 1` (F4F4F4 below)
- `bottombar_art = 30x30` at `(x:8, y:3)` within bar
- `bottombar_title_x = 48`
- `bottombar_title_h = 16` (slot 3: 16px Inter SemiBold, fits 36px bar)
- `bottombar_bg = F8F8F8`

**Playing state** (`bottombarsmall` — 11px, hairline only):
- `bottombarsmall_h = 11` (viewport: `%Vl(bottombarsmall,0,-11,-,-,-)`)
- `bottombarsmall_hairline_y = 0` (DCDCE0)
- `bottombarsmall_hairline_soft_y = 1` (F4F4F4)
- Content area **expands** to fill y=27..228 (`mainlarge`: h=201 vs stopped `main`: h=176)
- Volume overlay uses a 2px `noborder` `%pv` bar within the 11px strip

**Architecture constraint:** `neg_h` offsets in `%Vi` viewports = `-(bar_h + 1)`.
Playing: `-12` = `-(11+1)`. Stopped: `-37` = `-(36+1)`. Change together.

### 54.6 WPS geometry tokens (`wps/Apple2026.wps` lock) — REBUILT 2026-04-08

**Canonical locked geometry (do not drift from these without updating this section):**

- `wps_art_viewport = %V(85,8,150,150,-)%VB` — **%VB is mandatory** (Interpod pattern); removing %VB causes first-open blank art
- `wps_art_size = 150x150` at `(85,8)` — +15% from Interpod 130x130; centered horizontally ((320-150)/2=85)
- `wps_art_clip = %Cl(0,0,150,150,c,c)` — no rounded-corner BMP overlay; art clips to square
- `wps_art_bottom_y = 158` (8 + 150)
- `wps_placeholder = %?C<|%x(AlbumPlaceholder,albumPlaceholder.bmp,0,0)>` inside %VB viewport
- `wps_art_display = %Cd` inside %VB viewport (always after %Cl and placeholder logic)

**Font slots (verified against fonts/ directory):**
- Slot 3: `14-SFProText-Regular.fnt` — album text, time, playlist counter
- Slot 8: `20-SFProText-Regular.fnt` — song title (primary anchor)
- Slot 9: `16-SFProText-Medium.fnt` — artist (deliberate Medium for emphasis)

**Metadata stack (bottom-relative, screen height=240, art_bottom=158):**
- Title:   `%V(18,-82,-18,20,8)` -> y=158..177
- Artist:  `%V(18,-61,-20,16,9)` -> y=179..194, color `FF2D55` (Apple red)
- Album:   `%V(18,-44,-20,14,3)` -> y=196..209, color `6E6E73`
- pb bar:  `%Vl(pb,20,-29,-20,3,-)` -> inactive (3px)
- pb_act:  `%Vl(pb_active,20,-29,-20,5,-)` -> active (5px)
- pl_counter:  `%Vl(pl_counter,107,-20,106,14,3)` -> centered playlist "N of M"
- elapsed_time: `%Vl(elapsed_time,18,-20,87,-,3)` -> elapsed left
- lossless_ind: `%Vl(lossless_ind,200,-17,33,11,-)` -> lossless badge right of center
- remain_time:  `%Vl(remain_time,-87,-20,-20,-,3)` -> remaining right
- volbar:  `%Vl(volumebar,0,-28,-,18,-)` -> shown only during volume adjust

**Anti-regression rules (must not be changed without audit):**
1. `%VB` must stay on the art viewport -- it is the Rockbox-correct pattern for album art rendering
2. `%Cl` and `%Cd` must be inside the `%VB` viewport -- not in the main display layer
3. Font slots 3/8/9 only -- do not add a 4th font slot without checking parse overhead
4. No font reference to a `.fnt` file that does not exist in `fonts/` -- run audit script first
5. No duplicate image IDs -- `%xl` ID must not be repeated in another `%xl` or `%x`
6. No non-ASCII characters anywhere in the file -- comments included
7. Do not preload `albumShadow.bmp` without also drawing it via `%xd` (prior duplicate-ID crash)
8. `albumFramed.bmp` is 130x130 -- do not use it with 150x150 art (misrender)
9. Time/progress viewports use UNIQUE labels: `pl_counter`, `elapsed_time`, `lossless_ind`, `remain_time`. Do NOT reuse any label across multiple `%Vl` -- duplicate labels cause all but the first to silently never render.
10. Progress and volume bar are mutually exclusive via `%?mv(1.2)` logic
11. Preloaded images (`%xl`) must be drawn via `%xd` only -- never via `%x` with same ID

**Validation:** run `python tools/audit_apple2026_wps.py` before any future WPS edit is accepted.

### 54.7 Cover Flow UI tokens (policy-facing)
- `coverflow_header_h = 26` (when status bar enabled; default fullscreen omits theme chrome — `show_statusbar` default off in plugin cfg)
- `coverflow_label_lines_max = 2`
- `coverflow_label_zone_bottom_margin = 14`
- `coverflow_tracklist_row_h = font_ui_char_h` (plugin-dependent, bounded by font)
- `coverflow_tracklist_selected_style = flat_bar` (fill **E5E5EA**, `pictureflow.c` `draw_gradient` — matches shell selector)

### 54.8 Loading/fallback tokens
- `loading_text_center = true`
- `loading_bar_h = 2..4` (surface-dependent)
- `loading_bar_max_w = 240`
- `loading_box_padding = 8`
- `fallback_title_gap = 10`
- `fallback_action_gap = 14`

### 54.9 Boot image tokens (`Sourced Icons/iPhone-Rebooting.png`)
- Source: `640x1136`
- Output canvas: `320x240`
- `boot_bg = #000000`
- `boot_logo_center_x = 160`
- `boot_logo_center_y = 120`
- `boot_logo_h_default = 40`
- `boot_logo_h_min = 34`
- `boot_logo_h_max = 46`
- `boot_text = none`

## 55) Surface-by-surface exact prep rules

### 55.1 Home/root
- Must use section 54 header tokens and list geometry tokens exactly.
- Must reserve separate right lanes for chevron and scrollbar.

### 55.2 Artists/Albums/Songs/Playlists/Database
- Must share same row baseline family and disclosure rhythm.
- Icon/text reserve mapping may differ by list type only if explicitly documented.

### 55.3 Album list
- Enforce `56/48/76` model exactly before any visual polish pass.

### 55.4 Album page (future-facing lock)
- Preserve hero/metadata/action hierarchy from section 40.
- Track rows still obey `48/50` track rhythm.

### 55.5 Now Playing / WPS
- Use section 54.6 geometry defaults as start point.
- Missing-art fallback must keep art box and metadata lanes stable.

### 55.6 Mini-player
- Use section 54.5 tokens exactly.
- If text overflow occurs, truncate title before reducing geometry.

### 55.7 Cover Flow + Cover Flow tracklist
- Preserve plugin state machine behavior; only apply visual-token alignment in Wave 3.
- Tracklist selected row must migrate to neutral-gray non-gradient style.

### 55.8 Settings and Files
- Must remain in same shell family; no separate visual grammar.

### 55.9 Fallback/empty
- Must use shell-native typography and neutral spacing.
- No ad hoc debug-like framing for expected empty states.

## 56) Cropping / spacing / polish safeguards (pre-code risk matrix)

### 56.1 Text clipping safeguards
- Lock minimum text lane widths before theme edits.
- Enforce truncation rules before any font downscaling.

### 56.2 Icon cropping safeguards
- Every icon slot requires a safe box and padding contract.
- Reject symbols failing safe-box tests at target size.

### 56.3 Art cropping safeguards
- WPS and album list art must use centered square-safe crop rules.
- Avoid edge-biased auto-crops for portrait assets.

### 56.4 Divider/chevron/scrollbar collision safeguards
- Keep right-lane reservation explicit:
  - chevron lane,
  - scrollbar lane,
  - no overlap under narrow text cases.

### 56.5 Mini-player compression safeguards
- `mini_player_h` cannot drop below `34`.
- Art cannot drop below `28x28` without explicit lock update.

### 56.6 Loading box proportion safeguards
- Keep loading bar thin and centered.
- No heavy border-box visual in flagship surfaces.

### 56.7 Boot crop safeguards
- Do not scale full 640x1136 frame to 320x240 directly.
- Always extract logo and composite to black canvas per section 35.3 and 54.9.

## 57) Exact Wave 3 implementation prep sequence (no broad implementation yet)

### 57.1 File order
1. `wps/WPSLIST` registration scaffolding for Apple2026.
2. Apple2026 `.cfg` token binding shell.
3. Apple2026 `.sbs` header/list/footer structure.
4. Apple2026 `.wps` now-playing composition.
5. Optional `.fms` only if explicitly in wave scope.

### 57.2 Asset readiness order
1. Final `.fnt` set for locked typography roles.
2. Core icon strips and status glyph variants.
3. Boot image output asset (`320x240` centered Apple mark).
4. WPS art placeholders/fallback bitmaps.

### 57.3 Surface rollout order
1. Header + indicators
2. List geometry + dividers
3. Chevron/scrollbar/selector lanes
4. Mini-player
5. WPS
6. Cover Flow UI policy alignment
7. Loading/fallback polishing

### 57.4 Validation order
- Rebuild simulator at each rollout step.
- Capture screenshots at each step for all relevant surfaces.
- Compare in order: Figma -> Apple refs -> Interpod lineage.
- Record pass/fail and deltas in `WORK_LOG.md` immediately.

### 57.5 Drift prevention hard rule
- If any coordinate, lane, font slot, icon slot, or fallback alignment is undefined,
  implementation for that surface is blocked until this document is updated.

## 58) Implementation grid expansion (true execution grid)

### 58.1 Global shell grid
- Canvas: `320x240`.
- Horizontal grid columns:
  - `L0`: left safe edge (`x=0`)
  - `L1`: shell content start (`x=16`)
  - `L2`: library text start (`x=53`)
  - `R1`: chevron lane origin (`x=303`)
  - `R2`: scrollbar lane origin (`x=316` when `w=2`, `x=315` when `w=3`)
  - `R0`: right safe edge (`x=319`)
- Vertical grid bands:
  - `H0`: header (`y=0..25`)
  - `C0`: main content (`y=27..203`)
  - `F0`: mini-player (`y=204..239` when `h=36`)

### 58.2 Header grid
- Title baseline: `y=17`.
- Title text lanes:
  - default lane `x=74..246`
  - wide lane `x=56..246` (battery text hidden mode).
- Indicator anchors:
  - lock `24,7,9,12`
  - battery icon `288,4,27,16`
  - battery text `250,5,38,15`
  - busy indicator `58,9,9,9`

### 58.3 List row grid
- Row baselines:
  - library `52`
  - album list `56`
  - track list `48`
- Divider rails:
  - library from `x=16`
  - album list from `x=76`
  - track list from `x=50`
  - thickness `0.5`.

### 58.4 Icon/text/chevron/scrollbar lane grid
- Icon reserve lane (library): `x=16..44` (`29px` reserve).
- Text lane starts:
  - library `x=53`
  - album list `x=76`
  - track list `x=50`.
- Chevron lane:
  - `x=303..309`, center-on-row.
- Scrollbar lane:
  - right edge, `w=2` default, `w=3` fallback.
- Collision rule:
  - text must truncate before entering chevron lane.

### 58.5 Mini-player grid
- Container: `y=204..239`, `h=36`.
- Top hairline: `y=204`, `h=1`.
- Art box: `x=8,y=207,w=30,h=30`.
- Title lane: `x=48,y=212`.
- Meta lane: `x=48,y=226`.
- Play/pause lane: `x=284,y=214,w=20,h=16`.

### 58.6 WPS grid
- Art box default: `x=95,y=8,w=130,h=130`.
- Metadata stack:
  - title `y=158`
  - artist `y=180`
  - progress block `y=210`
  - time row `y=224`.

### 58.7 Cover Flow label/loading grid
- Header band: `y=0..25`.
- Cover field: plugin-rendered center zone beneath header.
- Label zone:
  - bottom-centered,
  - two-line max,
  - bottom margin `14`.
- Loading overlay:
  - centered wait label,
  - restrained bar below label,
  - no saturated accent fills.

### 58.8 Boot/loading grid
- Boot canvas: `320x240` black.
- Apple mark center: `160,120`.
- Logo target height: `40` (`34..46` allowed).
- Boot text: none.
- Loading dialog center alignment required for all shell-native loading surfaces.

## 59) Screen-by-screen token application map

### 59.1 Top-level menu surfaces
- **Home / Music / Artists / Albums / Songs / Playlists / Settings / Files**:
  - Use grids: `58.1`, `58.2`, `58.3`, `58.4`, `58.5`.
  - Use tokens: rows (`52` unless album-list specialization), selector gray, thin right scrollbar, tertiary chevron.

### 59.2 Album list
- Uses: `58.1`, `58.2`, `58.3(album)`, `58.4(album text lane + chevron/scrollbar)`, `58.5`.
- Mandatory: `56/48/76` rhythm and trailing disclosure.

### 59.3 Album page
- Uses: `58.1`, `58.2`, tracklist portion of `58.3` and `58.4(track)`.
- Future-facing hero/actions from section 40 remain canonical for staged implementation.

### 59.4 Now Playing / WPS
- Uses: `58.1` (header if shown), `58.6`, and mini-player continuity rules where shell overlap applies.

### 59.5 Mini-player
- Uses: `58.5` only; cannot be re-laid out ad hoc per screen.

### 59.6 Cover Flow browse
- Uses: `58.7` + section 43 rules.
- Plugin render core remains intact; apply visual-token alignment only.

### 59.7 Cover Flow loading
- Uses: `58.7` loading overlay + section 36 loading palette rules.

### 59.8 Cover Flow tracklist
- Uses: `58.7` header/label context + tracklist row styling rules from section 44.

### 59.9 Loading / fallback states
- Uses: `58.8` (boot/loading center rules) + section 47 fallback matrix.

### 59.10 Boot image
- Uses: `58.8` boot tokens + section 35 crop/resize protocol.

## 60) File-by-file Wave 3 execution order (exact)

### 60.1 Asset preflight (must complete first)
1. Boot output asset pipeline (from `Sourced Icons/iPhone-Rebooting.png`) finalized.
2. Font outputs finalized for locked hierarchy roles.
3. Icon strips/status glyph sets finalized and normalized.

### 60.2 Theme registration and cfg wiring
1. Edit `wps/WPSLIST` first:
   - add Apple2026 theme entry, target mappings, and asset references.
2. Validate generated runtime cfg after build:
   - `build-sim/simdisk/.rockbox/themes/apple2026.cfg` (generated result).

### 60.3 SBS execution sequence (file + section order)
1. Create/edit Apple2026 SBS source file (under `wps/` theme path).
2. Implement in this order:
   - `A` font loads and static assets,
   - `B` header strip + indicator anchors,
   - `C` main list viewport boundaries,
   - `D` divider/chevron/scrollbar lane compatibility,
   - `E` mini-player band + separators,
   - `F` loading/fallback shell viewports (where SBS-surface applicable).

### 60.4 WPS execution sequence
1. Create/edit Apple2026 WPS source file (under `wps/` theme path).
2. Implement in this order:
   - `A` art box and fallback art policy,
   - `B` metadata stack lanes,
   - `C` progress/time geometry,
   - `D` state overlays (pause/seek/volume),
   - `E` truncation/scroll behavior validation.

### 60.5 Cover Flow file-touch constraints
- Primary source file: `apps/plugins/pictureflow/pictureflow.c`.
- Do not touch performance/caching internals in this wave.
- Allowed sequence:
  1) loading palette/text style adjustments,
  2) tracklist selected-row visual alignment,
  3) header/label typography alignment,
  4) placeholder neutrality improvements.

### 60.6 Files explicitly deferred until prior validation passes
- Defer FM (`.fms`) styling until root/list/WPS/CoverFlow primary surfaces pass validation.
- Defer any nonessential plugin/internal refactors until all geometry checkpoints are green.

### 60.7 Stubbing policy
- Allowed stubs:
  - Apple2026 theme wiring with placeholder assets.
- Not allowed stubs:
  - undefined geometry placeholders in production lanes.

## 61) Wave 3 validation checklist (step-bound)

### 61.1 Step 0 — asset preflight
- Capture: boot mock, icon strip preview, font readability snapshot.
- Reference: Figma + Apple symbol/typography references.
- Pass: no clipping/cropping/muddy raster.
- Fail: cropped glyphs, unreadable stems, off-center boot mark.

### 61.2 Step 1 — cfg + header shell
- Capture: home header + indicators.
- Reference: Figma `1:4008` header hierarchy.
- Pass: anchors match token table; calm header density.
- Fail: battery overlap, title clipping, top-band crowding.

### 61.3 Step 2 — list geometry/lanes
- Capture: Home, Artists, Songs, Settings, Files lists.
- Reference: Figma list rhythm + Apple list/disclosure behavior.
- Pass: row heights/insets/dividers/lanes match tokens.
- Fail: divider mis-insets, chevron-lane collisions, uneven density.

### 61.4 Step 3 — album list specialization
- Capture: album list rows with art + metadata + chevrons.
- Reference: Figma `1:475`.
- Pass: `56/48/76` model preserved.
- Fail: art crop errors, metadata stack drift, wrong disclosure alignment.

### 61.5 Step 4 — selector + scrollbar
- Capture: long list with active row and visible scrollbar.
- Reference: iOS-like gray selection and thin gray scroll guidance.
- Pass: solid gray selector, subtle right scrollbar.
- Fail: gradient selector, pink default selection, heavy scrollbar.

### 61.6 Step 5 — mini-player
- Capture: list + mini-player + separator in one frame.
- Reference: Figma lower-shell continuity.
- Pass: stable `36h` band, art/text/control anchors correct.
- Fail: compressed text, missing separator, mode-jump feel.

### 61.7 Step 6 — WPS
- Capture: play/pause/seek/volume + no-art fallback.
- Reference: section 41 + Interpod DNA + Apple hierarchy.
- Pass: art/metadata/progress lanes stable.
- Fail: clipping, stack collapse, fallback layout jumps.

### 61.8 Step 7 — Cover Flow browse/loading/tracklist
- Capture: browse frame, loading frame, tracklist frame.
- Reference: section 43/44 rules + existing CF behavior constraints.
- Pass: integrated shell feel, neutral loading style, row selection aligned.
- Fail: detached plugin look, saturated progress style, inconsistent tracklist selection.

### 61.9 Step 8 — fallback/empty states
- Capture: no music/no art/no tracklist/no playlist states.
- Reference: section 47 matrix.
- Pass: shell-native fallback visuals with clear return paths.
- Fail: debug-like visual artifacts or undocumented fallback variants.

## 62) Boot / loading implementation plan (exact)

### 62.1 Boot asset preparation workflow
1. Read `Sourced Icons/iPhone-Rebooting.png`.
2. Detect logo bounds (non-black region extraction).
3. Export logo-only layer.
4. Resize logo to locked band (`34..46`, default `40`).
5. Composite on black `320x240` canvas centered at `160,120`.
6. Validate centering and luminance against panel/simulator captures.

### 62.2 Boot integration rules
- Preferred: dedicated boot image replacement path for iPod6G startup flow.
- Fallback: centered logo via nearest boot-logo path if full-screen replacement is limited.
- No boot text unless technical path forces unavoidable fallback.

### 62.3 Loading-state update rules
- Theme-driven first where possible (SBS/WPS/plugin loading overlays).
- Core-side polish required for generic splash behavior (`apps/gui/splash.c`) when theme control is insufficient.
- Keep one loading visual grammar across list/WPS/Cover Flow waits.

### 62.4 Theme-driven vs code-driven boundary
- Theme-driven:
  - SBS/WPS viewport-managed loading and fallback shells.
- Code-driven:
  - bootloader startup drawing behavior,
  - generic splash/dialog primitives,
  - Cover Flow plugin-specific loading and tracklist rendering.

## 63) Full user-flow coherence rules (transition continuity)

### 63.1 Journey chain
- Boot -> Home -> Music browse -> Album list/page context -> Now Playing/WPS -> mini-player continuity -> Settings/Files/Cover Flow branches -> predictable return.

### 63.2 Hierarchy persistence rules
- Header rhythm must persist through all branches.
- Lane system (icon/text/chevron/scrollbar) must persist across all list-like surfaces.
- Typography rank order must remain stable across transitions.

### 63.3 Transition behavior rules
- No abrupt shell dialect switches between surfaces.
- Cover Flow and tracklist must preserve shell identity markers.
- Loading/fallback overlays must not reset visual grammar.

### 63.4 Return-path rules
- Return from WPS/CF/Settings/Files must preserve prior context and shell continuity.
- Any transition that loses context requires explicit documentation and mitigation.

## 64) Wave 3 drift-prevention rules (hard)

1. No ad hoc spacing edits outside token table sections 54/58.
2. No icon swaps without icon-map/semantic check against section 30 + section 50.
3. No font size changes without hierarchy revalidation against section 27.
4. No selector/scrollbar style changes that violate gray-flat + thin-right lock.
5. No loading-state redesign outside unified loading grammar (section 36 + 62).
6. No undocumented fallback UI variants.
7. No silent deviation from Figma geometry anchors.
8. Any unresolved mismatch must be logged in `WORK_LOG.md` before proceeding.
9. If a surface lacks explicit token mapping, implementation halts for that surface.
10. Cover Flow optimization/performance edits remain blocked in this wave.

## 65) UI/UX best-practice safety lock (readability + overlap prevention)

This section is implementation-facing and mandatory for Wave 3 execution quality.
It defines practical readability floors, spacing safety, collision prevention, and
review behavior to keep Apple2026 clean and legible on iPod-class hardware.

### 65.1 Readability rules (minimum practical floors)
- Header dominant title:
  - target `22px`, hard floor `20px`.
- List primary/title text:
  - target `15px`, hard floor `14px`.
- Secondary metadata text:
  - target `13px`, hard floor `12px`.
- Micro/tab/utility labels:
  - target `10-11px`, hard floor `10px`.
- Battery/utility micro text:
  - `>=10px` equivalent with strong contrast.

#### 65.1.1 Scale direction rule
- If readability is borderline, scale text up before shrinking below floor.
- Do not use font downscaling as first response to tight lanes.

#### 65.1.2 Contrast and quiet hierarchy rule
- Primary text must keep strong near-black contrast on light backgrounds.
- Secondary metadata remains legible but quieter (reduced emphasis, not reduced clarity).
- Headers must feel dominant through hierarchy/placement, not decorative heaviness.

#### 65.1.3 Device legibility bias
- If text is only barely readable in simulator captures, it is considered too small for hardware.
- In uncertain cases, choose one step larger and reduce decorative density instead.

### 65.2 Overlap prevention rules (hard fail if violated)
- No icon/text overlap.
- No text/chevron overlap.
- No text/scrollbar overlap.
- No art/text overlap (list, mini-player, WPS, album contexts).
- No mini-player compression causing title/meta/control collisions.
- No header collisions between title, battery, lock, and busy indicators.
- No loading-box collisions between label/progress/margins.
- Any overlap in any state (normal/selected/loading/long-string) is a validation fail.

### 65.3 Cropping / truncation rules
- Truncate before shrinking below readability floors.
- Use marquee only for high-priority fields (focused row title / now-playing title).
- Space-pressure content priority order:
  1) primary title legibility,
  2) navigation affordances (chevron/selection),
  3) secondary metadata,
  4) decorative/tertiary content.
- Never hard-clip glyph stems; use clean ellipsis or controlled marquee.
- Long labels must degrade gracefully:
  - ellipsis at text-lane boundary,
  - preserve chevron and scrollbar lanes,
  - preserve row rhythm.

### 65.4 Spacing safety rules (minimums)
- Icon internal safe padding: `>=2px` per side.
- Icon-to-text gap: `>=8px`.
- Text-to-divider vertical breathing: `>=6px` equivalent.
- Text-to-chevron clearance: `>=8px`.
- Text-to-scrollbar lane separation: `>=10px`.
- Mini-player internal spacing:
  - art-to-title horizontal separation `>=10px`,
  - title-to-meta vertical separation `>=10px`,
  - control lane separation must remain intact.
- Boot/loading margins:
  - boot logo to nearest edge `>=34px`,
  - loading label/progress to viewport edge `>=12px`.

### 65.5 Hierarchy safety rules (Apple-like on small screen)
- Preserve semantic rank:
  - header > primary title > secondary metadata > micro utility.
- Allowed slight shrink:
  - secondary metadata and utility labels only (within floor limits).
- Not allowed below practical threshold:
  - header dominant title,
  - list primary titles,
  - now-playing primary title.
- Keep relative Apple proportion intent while prioritizing iPod readability.

### 65.6 Simulator validation best practices
- Review at 1:1 pixel view before sign-off; additionally inspect at zoomed view for edge artifacts.
- After each major pass, explicitly check:
  - right-lane collisions,
  - header density/crowding,
  - row text clipping,
  - mini-player compression,
  - loading-state centering and spacing.
- Highest-risk clipping screens (always mandatory review):
  - album list with long album/artist names,
  - WPS with long titles and no-art fallback,
  - settings/files with long labels,
  - Cover Flow tracklist with long track names.

### 65.7 Device-realism safety rules
- Desktop screenshots are optimistic; hardware rendering is harsher.
- Bias toward larger/cleaner text where ambiguity exists.
- Remove decorative density before reducing readability.
- Prefer simple icon silhouettes over detailed micro-icons in tight lanes.
- If simulator readability and expected hardware readability diverge,
  hardware legibility wins.

### 65.8 Enforcement rule
- These rules are part of Wave 3 acceptance gates.
- Any violation must be logged in `WORK_LOG.md` with screenshot evidence and corrected
  before marking a surface pass-complete.

## 66) High-risk string stress matrix (pre-implementation lock)

This section defines mandatory long-string and edge-label validation inputs so Wave 3 can
verify truncation, marquee, lane safety, and hierarchy behavior without ad hoc guessing.

### 66.1 Stress-string set (canonical)
- `S1`: Very long song title:
  - `The Night We Drove Through Every City Light and Forgot to Turn Back (Live at Shoreline 2004)`
- `S2`: Very long album title:
  - `Collected Works of Midnight Radios, Lost B-Sides, Alternate Masters and Unreleased Sessions`
- `S3`: Very long artist name:
  - `The International Orchestra for Symphonic Post-Analog Experiments and Signal Processing`
- `S4`: Mixed punctuation/title edge case:
  - `Vol. 7: Echoes, Fragments & "Unfinished" Cuts — Remaster / Deluxe Edition`
- `S5`: File/folder long label:
  - `2026-Archive_of_Live_Recordings_and_Annotated_Session_Notes_Final-FINAL_v3`
- `S6`: Playlist long label:
  - `Road Trip / Night Drive / Rain Mix / Favorites / Offline / Imported / Curated`
- `S7`: Missing metadata fallback labels:
  - title = `Unknown Title`, artist = `Unknown Artist`, album = `Unknown Album`.

### 66.2 Surface-by-surface stress application
- **Home / root lists**:
  - apply `S5`, `S6`; validate lane clipping and chevron preservation.
- **Artists list**:
  - apply `S3`; validate title truncation before chevron lane.
- **Albums list**:
  - apply `S2` + `S3`; validate two-line hierarchy and `56/48/76` integrity.
- **Songs list**:
  - apply `S1` + `S4`; validate single-line default behavior and selector stability.
- **Playlists**:
  - apply `S6`; validate long-label graceful degradation.
- **Settings / Files**:
  - apply `S5`; validate utility-list lane safety and icon/text spacing.
- **Album page track list**:
  - apply `S1` + `S4`; validate track row clipping behavior and divider rhythm.
- **Now Playing / WPS**:
  - apply `S1`, `S2`, `S3`, and `S7`; validate priority order and fallback stability.
- **Mini-player**:
  - apply `S1` + `S3`; validate compact lane behavior without control overlap.
- **Cover Flow tracklist**:
  - apply `S1` + `S4`; validate row readability and selected-state integrity.
- **Loading/fallback surfaces**:
  - apply concise status copy + `S7`; ensure no box/label/progress collisions.

### 66.3 Required behavior under stress
- Titles truncate before entering chevron/scrollbar lanes.
- Marquee is reserved for high-priority now-playing/focused-title contexts only.
- Metadata yields before primary title when space is constrained.
- No downscaling below section 65 floors to make text fit.
- No baseline clipping (stem/counter damage) under any stress string.

### 66.4 Pass/fail gates for stress matrix
- **Pass** when all are true:
  - no overlap (icon/text/chevron/scrollbar/art),
  - no illegible micro text,
  - truncation/marquee follows section 65/66 priorities,
  - hierarchy remains clear at first glance.
- **Fail** on any:
  - hard clipping,
  - lane invasion,
  - aggressive downscaling,
  - ambiguous title/metadata rank,
  - unstable row height/spacing caused by long strings.

### 66.5 Screenshot evidence requirement
- For each major Wave 3 step, capture at least one high-risk string frame for:
  - Home/Artists/Albums/Songs,
  - WPS + mini-player,
  - Cover Flow tracklist,
  - Settings/Files.
- Label captures with stress IDs (`S1..S7`) in `WORK_LOG.md` notes.

### 66.6 Drift block rule
- If any surface fails stress matrix checks, that surface cannot progress to next Wave 3 step
  until corrected and revalidated.

## 67) Full user-facing runtime audit lock (Wave 2 whole-product pass)

This section is the mandatory whole-product inventory/classification pass for everything user-facing
while Rockbox is running on the Apple2026 target path. It is intentionally broader than theme files
and includes core C-rendered/plugin/boot/dialog surfaces.

### 67.1 Full user-facing surface inventory

#### 67.1.1 Startup / boot / system-transition surfaces
- Bootloader startup and text path (`bootloader/ipod-s5l87xx.c`, `bootloader/show_logo.c`).
- Startup scanning/loading strings and shutdown strings (`apps/lang/english.lang`, splash usage).
- USB connected runtime takeover screen and HID-mode banner (`apps/gui/usb_screen.c`).

#### 67.1.2 Core shell navigation surfaces
- Root menu/top-level navigation (`apps/root_menu.c`).
- Main settings/system menu tree (`apps/menus/main_menu.c`, `apps/menus/settings_menu.c`).
- File browser / tree browser surfaces (`apps/tree.c`).
- Database/tag browser and dynamic menu/search flows (`apps/tagtree.c`).

#### 67.1.3 Music/runtime playback surfaces
- Now Playing / WPS runtime interactions (`apps/gui/wps.c`).
- On-Play context actions (queue, search, open-with/plugin actions) (`apps/onplay.c`).
- Current playlist viewer and queue states (`apps/playlist_viewer.c`).
- Playlist catalog create/add/view flows (`apps/playlist_catalog.c`).

#### 67.1.4 Radio/plugin/specialized surfaces
- FM radio runtime + skin-driven radio surface (`apps/radio/radio.c`, `apps/radio/radio_skin.c`).
- PictureFlow browse/loading/tracklist plugin surfaces (`apps/plugins/pictureflow/pictureflow.c`).
- Shortcuts menu and shortcut action surfaces (`apps/shortcuts.c`).

#### 67.1.5 Modal / dialog / utility surfaces
- Generic splash/progress overlays (`apps/gui/splash.c`).
- Yes/No confirm/timeout modal system (`apps/gui/yesno.c`).
- Keyboard/search-entry-dependent flows (playlist search and other text-entry callers).
- Language-string surfaces and wording tone source (`apps/lang/english.lang`).

### 67.2 Primary flagship surfaces (Wave 3 first-class)
- Boot/startup visual + loading handoff.
- Root/Home list shell and top-level navigation rhythm.
- Core browse lists: **Music** (`/Music`), Database (indexed), Playlists, Settings entry surfaces (no separate root **Storage** row on 5 / 71).
- Album/artist/song browsing path (tagtree + list rendering behavior).
- WPS/Now Playing primary playback surface.
- Persistent mini-player + lower-shell continuity where applicable.
- Album list and track list readability behavior (including long-string stress paths).

### 67.3 Secondary but important surfaces
- Playlist viewer and queue/search-in-playlist behavior.
- Playlist catalog management screens.
- On-Play context menus and quick action surfaces.
- FM radio and radio skin surfaces.
- Shortcuts menu and shortcut execution feedback surfaces.
- USB takeover screen (including HID mode text behavior).
- Deeper settings/system/voice/bookmark/autoresume menus.

### 67.4 Fallback / dialog / empty-state surfaces
- Generic loading, progress, and wait states.
- Yes/No confirm, cancel, timeout prompts.
- Missing/no files states (`LANG_NO_FILES` paths).
- Installation/folder fallback states (e.g., incomplete `.rockbox` / missing content warnings in tree paths).
- Bookmark empty/invalid/create-fail states.
- Missing metadata/unknown title/artist/album states.
- Missing album art / PictureFlow empty slide and index/cache load failures.
- Tagcache-busy / database-not-ready prompts.

### 67.5 Biggest current user-facing inconsistencies
1. **Theme vs plugin/core visual dialect drift**:
  - list-shell tokens are defined, but PictureFlow/loading/dialog paths still contain non-Apple2026 visual language.
2. **Loading/progress inconsistency**:
  - core splash, plugin progress, and boot transitions do not yet share one unified visual grammar.
3. **Fallback wording and tone inconsistency**:
  - user-facing copy includes abrupt technical phrasing mixed with consumer-facing labels.
4. **Secondary-surface parity gap**:
  - playlist/queue/search/radio/shortcuts are functionally connected but not yet fully locked to the same shell rhythm rules.
5. **Long-string stress risk outside primary lists**:
  - stress matrix exists, but secondary and modal surfaces still need explicit enforcement in Wave 3 execution.

### 67.6 Wave 3 must-fix surfaces (non-negotiable)
- Root/list shell parity across all top-level browse surfaces.
- WPS + mini-player continuity and typography/overflow safety.
- Loading/progress/dialog visual unification (core + plugin-visible waits).
- Playlist/queue/search surfaces readability and lane-safety parity.
- Cover Flow UI/tracklist visual alignment (UI-only; no performance architecture edits).
- Fallback/empty-state shell consistency and plain-language clarity.
- Boot/startup to runtime transition coherence.

### 67.7 Later-wave / deferred surfaces (allowed deferral)
- Cover Flow performance, caching, prefetch, and RAM architecture work (explicitly out of this branch).
- Deep plugin-by-plugin visual restyling beyond music-critical paths.
- Broad non-music utility polish not directly impacting flagship Apple2026 journeys.
- Rare debug/developer-facing diagnostics that are not normal-user runtime flows.

### 67.8 Documentation update plan (execution contract)
- Use this section (`67`) as the whole-product audit anchor for Wave 3 checkpoints.
- During Wave 3, each major validation step must explicitly mark:
  - covered surfaces,
  - pass/fail by primary/secondary/fallback class,
  - unresolved inconsistencies and block reason.
- `WORK_LOG.md` entries must reference this section when logging progress to prevent
  partial-surface sign-off.
- Any newly discovered user-facing surface must be added here before implementation is
  considered complete for that wave.

## 68) Wave 2 font-asset preparation lock (font-system readiness)

This section locks the prepared Apple2026 font library generated before broad Wave 3 shell work.
Purpose: prevent implementation stalls caused by missing sizes/weights and avoid ad hoc
font regeneration during layout polishing.

### 68.1 Generated library location and tooling
- Generated root:
  - `Apple Fonts/Generated FNT/Apple2026/`
- Generator script:
  - `tools/apple2026_font_prep.py`
- Converter path used:
  - `tools/convttf.exe`
- Conversion command policy:
  - `convttf -s 32 -l 255 -p <size> -L`
  - `-x` trim is intentionally not used in this pass to avoid glyph clipping artifacts observed
    during trial conversion.

### 68.2 Coverage produced (curated broad set)
- Total generated candidates: `144`.
- Status split:
  - `140` primary
  - `3` fallback
  - `1` reject
- Families/weights prepared:
  - `SF Pro Display`: Regular, Medium, Semibold, Bold (`19-25`)
  - `SF Compact Display`: Regular, Medium, Semibold, Bold (`19-25`)
  - `SF Pro Text`: Regular, Medium, Semibold, Bold (`10-19`)
  - `SF Compact Text`: Regular, Medium, Semibold, Bold (`8-19`)

### 68.3 Role readiness mapping
- Role recommendation tables and preview sheets are generated for:
  1) Large title/header
  2) Section/list title
  3) Body primary
  4) Body secondary
  5) Compact metadata
  6) Mini-player title
  7) Mini-player metadata
  8) Tracklist primary
  9) Tracklist secondary
  10) Loading text
  11) Micro/tab/tiny labels
- Inventory/report files:
  - `Apple Fonts/Generated FNT/Apple2026/APPLE2026_FONT_INVENTORY.md`
  - `Apple Fonts/Generated FNT/Apple2026/apple2026_font_inventory.csv`
  - `Apple Fonts/Generated FNT/Apple2026/apple2026_font_inventory.json`
  - `Apple Fonts/Generated FNT/Apple2026/previews/*.png`

### 68.4 Quality-filter outcome lock
- Candidate filtering evaluates: density balance, punctuation energy, digit width floors,
  and small-size weight risk.
- Explicit reject in this pass:
  - `08-SFCompactText-Bold.fnt` (`micro_bold_muddy_risk`)
- Fallback compatibility fonts retained (not regenerated) include Inter/Ubuntu legacy files from:
  - `Imported Reference Themes/Interpod/.rockbox/fonts/`
  - `Imported Reference Themes/Interpod 2/.rockbox/fonts/`
  - `Imported Reference Themes/iRB_Modern/.rockbox/fonts/`

### 68.5 Wave 3 usage rule
- Wave 3 must select from this prepared set first.
- Do not pause shell implementation for one-off font generation unless a newly discovered
  hard requirement is outside this prepared range.

## 69) Wave 2 full-glyph audit lock (completed)

This section locks the full glyph-review outcome for the prepared Apple2026 font library.

### 69.1 Audit scope and outputs
- Full scan range executed per font: `U+0020` to `U+00FF`.
- Font count scanned: `144` generated Apple2026 candidates.
- Per-font full-grid glyph sheets exported to:
  - `Apple Fonts/Generated FNT/Apple2026/glyph_sheets/*.png`
- Audit report output:
  - `Apple Fonts/Generated FNT/Apple2026/APPLE2026_GLYPH_AUDIT.md`

### 69.2 Printable glyph integrity set (ink-required set)
- Integrity checks for blank/missing/duplicate risk apply to:
  - `U+0021..U+007E`
  - `U+00A1..U+00FF`
- Explicit non-ink exceptions (allowed blank behavior):
  - `U+0020` (space)
  - `U+00A0` (non-breaking space)
  - `U+00AD` (soft hyphen)
  - C0/C1 control bands (`U+007F..U+009F`)

### 69.3 Final audit outcome
- Glyph integrity classification after criteria correction:
  - `Primary: 144`
  - `Fallback: 0`
  - `Reject: 0`
- No missing printable nonspace glyphs detected.
- No suspicious duplicate-cluster behavior detected.

### 69.4 Hard-fail criteria (locked)
- Reject if any printable nonspace glyph is missing.
- Reject if blank printable nonspace glyph count exceeds tolerance.
- Reject if duplicate-cluster signature indicates probable conversion collapse.
- Keep `convttf` generation policy from section 68 (`-L`, no `-x` in this branch pass).

### 69.5 Wave 3 usage rule
- Wave 3 shell work may treat Apple2026 prepared fonts as glyph-complete for the locked
  Latin-1 coverage band used by current UI surfaces.
- Any new locale/system requiring coverage beyond this band must trigger a new explicit
  glyph audit section update before adoption.


## 70) Current iOS Now Playing ingestion lock (Figma node `35:9972` via SVG reference)

This section adds the current Apple Music Now Playing composition language to Apple2026 as
an adaptation lock. It is reference-driven, not literal phone-copy behavior.

### 70.1 New Now Playing findings (reference geometry)
- Reference canvas: `390x844` (tall iPhone portrait).
- Hero art block:
  - `x=16, y=79, w=358, h=356, radius=6`
  - visual behavior: near-full-width framed card with light depth.
- Metadata stack begins below art:
  - title band around `y=477`
  - artist/secondary band around `y=499`
  - hierarchy: title strong black, artist/support tertiary gray.
- Primary progress slider:
  - rail around `y=530`, width `358` (`x=16..374`), visual thickness ~`3px`
  - active portion + thumb (`~7px` diameter) with tight elapsed/remaining labels.
- Playback controls row:
  - previous / play-pause / next arranged as triad with center control strongest.
  - optical centers approximately `x=89, 195, 301`.
- Secondary volume slider:
  - rail around `y=728`, width `298` (`x=44..342`), thickness ~`3px`
  - larger touch thumb (`~27px`) with soft shadow and speaker endpoints.
- Lower action row:
  - three action symbols around `y=779..804` (left black, center/right pink in this comp)
  - optional overflow/more circular control near lower-right.

### 70.2 What must be preserved from current iOS Now Playing
- Preserve **large-art-first** emotional anchor.
- Preserve clear **title > artist/metadata** hierarchy with generous breathing room.
- Preserve triad control semantics:
  - side controls visually lighter,
  - center play/pause optically dominant.
- Preserve modern slider language:
  - thin rail,
  - restrained active segment,
  - clear but not bulky thumb.
- Preserve SF-symbol-style icon weight consistency for playback and utility actions.

### 70.3 What must be adapted for iPod hardware (not copied literally)
- Do not use full-height phone stacking; iPod `320x240` requires compressed vertical bands.
- Do not keep persistent touch-target sizing from phone UI (thumbs/buttons are too large).
- Do not reserve permanent full-width lower action tray in default WPS.
- Keep click-wheel-first interaction model:
  - on-screen controls are visual language cues,
  - not a touch-first layout contract.

### 70.4 Interpod lineage comparison and inheritance

#### 70.4.1 Interpod (original) strengths to retain
- Strong centered album-art + metadata composition.
- Stable elapsed/remaining + progress readability.
- Robust volume-overlay behavior (`%?mv(...)`) that avoids persistent clutter.
- Clear status and playback-state communication under constrained space.

#### 70.4.2 Interpod 2 strengths to retain
- Cleaner art framing (`156x156`) and safer text fitting behavior.
- Better paused/active state separation.
- Cleaner bottom-band handling under limited vertical space.

#### 70.4.3 amusicpodds strengths to selectively borrow
- SF Compact playback typography character.
- Modern symbol tone and lighter visual rails.
- Keep dark-shell/global behavior rejected for Apple2026 flagship.

### 70.5 Apple2026 playback control and slider adaptation rules

#### 70.5.1 Overall composition (WPS)
- Primary WPS keeps Interpod centered-art DNA.
- Art target band: `148..156` square, default `156` (`Interpod 2` baseline).
- Metadata stack remains directly art-coupled; avoid large phone-like inter-block gaps.

#### 70.5.2 Album art scale/placement
- Preserve "large art" feeling by priority and framing, not by phone-like near-full width.
- Lock default art box: `156x156` centered horizontally.
- Allow fallback compact art only in constrained variants (`130..150`) when required by overlays.

#### 70.5.3 Title/artist/metadata stack
- Title remains dominant lane (single-line + marquee policy from stress rules).
- Artist/secondary metadata remain quieter and can yield first under compression.
- Vertical rhythm must keep minimum readable breathing:
  - title-to-artist baseline gap target `10..14px` equivalent,
  - never collapse below readability floors from section 65.

#### 70.5.4 Playback controls (prev/play-next)
- Triad visual language is approved for Apple2026, adapted for non-touch iPod context.
- Optical weight ratio lock:
  - center play/pause icon mass = `1.30..1.45x` each side icon.
- Horizontal spacing lock when shown:
  - center-to-side distance target `80..92px` (320-wide context).
- Controls should be visually clean SF-like symbols, not oversized tappable circles.
- Default behavior:
  - keep click-wheel interaction primary,
  - use on-screen triad as compositional/state language where space permits.

#### 70.5.5 Progress slider
- Track thickness:
  - default `2px`,
  - seeking-active `3px`.
- Thumb style:
  - default compact round thumb `6..8px` visual diameter,
  - avoid phone-sized touch thumb.
- Labels:
  - elapsed/remaining remain adjacent with clear separation from rail (`>=6px` gap).
- Visual tone:
  - neutral rail + darker active fill; avoid heavy glow/overly saturated fills.

#### 70.5.6 Volume slider
- Keep Interpod model: volume slider is **contextual/ephemeral**, not always-on persistent row.
- Apple-like language to borrow:
  - thin neutral rail,
  - subtle active segment,
  - clear endpoint speaker semantics.
- Reject literal phone behavior:
  - no large always-visible touch thumb (`~27px`) in default iPod WPS.

#### 70.5.7 Lower action row
- Treat iPhone lower action row as reference language, not required default structure.
- Apple2026 immediate rule:
  - keep default WPS uncluttered,
  - map only high-value actions into existing iPod paradigms (queue/list/context).
- Future-use influence allowed for:
  - symbol weight/state style,
  - optional extended playback overlays.

### 70.6 Explicit inherit/reject matrix for this reference

#### Inherit
- Large-art-first emphasis.
- Title/artist spacing discipline and hierarchy clarity.
- Center-dominant transport triad language.
- Modern thin-slider visual grammar.
- SF symbol optical consistency.

#### Reject
- Literal tall-phone vertical stacking.
- Persistent full-width touch-oriented volume row and oversized thumb.
- Mandatory always-visible bottom action dock.
- Phone-specific chrome elements (home indicator, floating utility bubbles) as structural requirements.

### 70.7 Wave 3 mapping note (pre-implementation)
- This section refines sections 41/54/58 for playback language only.
- Implementation remains blocked to Wave 3 steps; no broad shell coding is implied by this lock.






