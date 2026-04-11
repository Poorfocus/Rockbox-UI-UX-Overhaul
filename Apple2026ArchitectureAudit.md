# Apple2026ArchitectureAudit.md

## 1. Problem statement

Apple2026 is no longer just a theming exercise. It is trying to turn Rockbox into a more coherent music product with:

- a native-feeling shell
- stronger typography and iconography
- cleaner browse/playback continuity
- less "toolbox firmware" feel
- less dependence on WPS/SBS tricks where source changes would be cleaner

The core question for this pass is not "how far can the theme layer be bent?"

It is:

- what in Rockbox's current UI architecture prevents Apple2026 from feeling native
- which limits are intrinsic to the current renderer and shell model
- which subsystems need patches, refactors, or rewrites
- what a dedicated Apple2026-focused Rockbox branch should stabilize first

This document is anchored to Apple2026 product goals from `MASTER.md`, `AGENTS.md`, `DESIGN_SYSTEM.md`, and `WORK_LOG.md`. It is not a general Rockbox review.

## 2. Audit lens and classification

### Apple2026 target qualities

- One coherent shell, not adjacent mini-apps.
- Music-first navigation and predictable return paths.
- Typography that can carry hierarchy cleanly.
- Iconography that feels semantic and system-owned.
- Lists, dialogs, playback, and utility screens that feel like one product.
- Cleaner extension points so future Apple2026 work is faster and less fragile.

### Classification used in this audit

- `Theme-impossible`: cannot be solved cleanly in WPS/SBS/theme assets alone.
- `Theme-awkward`: technically possible with theme or surface-specific hacks, but brittle.
- `Source-fixable`: a contained core change can remove the limitation.
- `Architecture-required`: needs a new abstraction or subsystem boundary.
- `Branch-justified`: important enough to define the Apple2026 branch identity.

### Rewrite scale used in this audit

- `Small patch`
- `Moderate refactor`
- `Deep rewrite`
- `Long-term branch foundation`

## 3. Executive summary

### Biggest Rockbox blockers

1. Rockbox does not have a unified shell model. Navigation is a mix of `GO_TO_*` return codes, activity globals, special-case playback routing, and per-screen control flow.
2. The list and menu system is still a single-line callback renderer, not a compositional row system. Apple2026 keeps pushing against this in almost every browse surface.
3. Typography is bitmap-font and font-height driven. There is no real text style system, no kerning/shaping, and almost no baseline/leading control.
4. The skin engine is powerful but it is still a token-and-viewport templating engine, not a general UI framework. It can decorate surfaces, but it cannot unify the shell.
5. Icons and assets are built around fixed sprite strips, BMPs, and hand-managed image preload rules. This is too rigid for a semantic Apple2026 asset system.
6. Dialogs, quickscreen, context menus, USB, and other utility screens are separate renderers with separate geometry rules. They do not inherit a shared Apple2026 surface model.
7. Plugins, especially PictureFlow, still behave like external applications that temporarily borrow the shell instead of first-class routed screens.
8. Playback-shell continuity relies on global flags and special cases such as `playback_source`, `last_screen`, `previous_music`, and activity stack coordination.

### What most directly blocks a native feel

- fragmented navigation and screen return behavior
- lack of a reusable row/cell rendering model
- limited typography and line layout control
- per-surface rendering silos for lists, dialogs, status chrome, WPS, plugins, and special screens
- plugin and PictureFlow isolation from the main shell lifecycle

### What theming can and cannot do

- Theming can still shape visual language on WPS/SBS-driven surfaces.
- Theming cannot create a unified navigation stack, a richer row model, real typography control, or first-class plugin integration.
- Many current Apple2026 improvements are effective only because they inject C-side exceptions into legacy systems, which confirms the branch needs deeper source work.

## 4. Subsystem findings

## 4.1 List, row, and menu framework

### 4.1.1 The core row contract is too narrow

- Current Rockbox behavior:
  - `apps/gui/list.h` defines `gui_synclist` around callbacks for one text string, one icon, optional color, and optional owner draw.
  - `struct list_putlineinfo_t` still assumes a line-centric draw with one display string and one icon slot.
  - `apps/menu.c` adapts menus into this same abstraction, so menus inherit list limits instead of expressing richer menu semantics.
- Why it limits Apple2026:
  - Modern Apple2026 surfaces want reusable row types: title + subtitle, artwork + metadata, trailing chevron/actions, badges, now-playing indicators, and different row densities without inventing a new renderer every time.
  - The current model forces either single-line compromises or surface-specific hacks.
- Classification:
  - `Theme-impossible`
  - `Architecture-required`
  - `Branch-justified`
- Recommended response:
  - `Deep rewrite`
- Likely source areas:
  - `apps/gui/list.h`
  - `apps/gui/list.c`
  - `apps/gui/bitmap/list.c`
  - `apps/menu.c`
- Implementation notes:
  - Replace the string/icon callback contract with a row descriptor contract.
  - A row descriptor should expose semantic slots: leading visual, primary text, secondary text, tertiary metadata, trailing accessory, background state, and interaction state.
  - Menus and file/database/playlist lists should all feed the same renderer with different row descriptors.
- Risks:
  - Broad surface impact across menus, lists, playlist viewer, and tree/database browsing.
  - Migration needs a compatibility layer so existing simple lists still work.
- Benefits unlocked:
  - consistent row rhythm
  - true metadata hierarchy
  - reusable trailing affordances
  - fewer Apple2026 one-off patches

### 4.1.2 Apple2026-specific list polish is currently injected into the renderer instead of supported by it

- Current Rockbox behavior:
  - `apps/gui/bitmap/list.c` now includes Apple2026-specific chevron drawing, inset separator masking, and font tier switching inside the default draw path.
  - `apps/gui/list.c` computes row height from font height and then patches Apple2026 minimums and viewport-filling behavior on top.
- Why it limits Apple2026:
  - This proves the existing list abstraction cannot express the needed visual model declaratively.
  - Every new Apple2026 requirement increases pressure on a renderer that still thinks in terms of old list primitives.
- Classification:
  - `Theme-awkward`
  - `Source-fixable`
- Recommended response:
  - `Moderate refactor`
- Likely source areas:
  - `apps/gui/list.c`
  - `apps/gui/bitmap/list.c`
- Implementation notes:
  - Move Apple2026-specific structural behavior into generic list renderer capabilities: divider inset lanes, accessory lanes, row density classes, typography roles, and disclosure rendering.
- Risks:
  - Existing themes may rely on old list assumptions.
- Benefits unlocked:
  - future Apple2026 changes become configuration, not renderer surgery

### 4.1.3 Skin-based list items are powerful but too constrained to become the universal row system

- Current Rockbox behavior:
  - `skinlist_draw()` exists, but it is still driven by `listitem_viewport_cfg`, per-row skin tree traversal, and viewport mutation.
  - It is limited enough that the normal list renderer still carries most real behavior.
- Why it limits Apple2026:
  - Skin-based rows cannot become the new shell foundation if they are expensive, specialized, and structurally tied to one selected row height model.
- Classification:
  - `Theme-awkward`
  - `Architecture-required`
- Recommended response:
  - `Moderate refactor`
- Likely source areas:
  - `apps/gui/bitmap/list-skinned.c`
  - `apps/gui/skin_engine/wps_internals.h`
- Implementation notes:
  - Keep skinlist compatibility, but introduce a real row renderer underneath it so skin data styles components instead of owning layout by itself.
- Risks:
  - hybrid system complexity during migration
- Benefits unlocked:
  - skinning stops fighting structure

## 4.2 Skin engine, WPS/SBS runtime, and viewport model

### 4.2.1 The skin engine is a templating engine, not a shell framework

- Current Rockbox behavior:
  - `apps/gui/skin_engine/wps_internals.h` centers the system around tokens, skin trees, viewports, images, progress bars, touch regions, and line alternators.
  - `WPS_MAX_TOKENS` is fixed at `1150`.
  - `skin_data_load()` in `skin_parser.c` builds these structures from a parse buffer, initially sourced from `plugin_get_buffer()`.
- Why it limits Apple2026:
  - WPS/SBS can decorate and orchestrate some surfaces, but they cannot own all shell behaviors cleanly.
  - Apple2026 wants shared components across playback, browse, dialogs, and plugins. The skin system is not designed to define a whole routed application shell.
- Classification:
  - `Theme-impossible`
  - `Architecture-required`
  - `Branch-justified`
- Recommended response:
  - `Long-term branch foundation`
- Likely source areas:
  - `apps/gui/skin_engine/skin_parser.c`
  - `apps/gui/skin_engine/skin_render.c`
  - `apps/gui/skin_engine/wps_internals.h`
- Implementation notes:
  - Do not throw the skin engine away immediately.
  - Reposition it as a presentation layer for declarative surfaces while a new shell framework owns navigation, shared state, and component contracts.
- Risks:
  - large surface area
  - compatibility concerns for legacy themes
- Benefits unlocked:
  - a stable base for Apple2026 shell components instead of endless WPS/SBS escalation

### 4.2.2 The viewport system is too low-level and stack-oriented for modern shell composition

- Current Rockbox behavior:
  - `viewportmanager_theme_enable()` and `viewportmanager_theme_undo()` in `apps/gui/viewport.c` push and pop a theme-enabled state on a fixed stack.
  - `viewport_get_nb_lines()` is simply `vp->height / font_get(vp->font)->height`.
  - Theme enable/disable is used opportunistically by many screens to temporarily escape or restore skinned UI ownership.
- Why it limits Apple2026:
  - This is a rendering toggle stack, not a layout or screen composition system.
  - A native shell needs parent/child surface ownership, shared chrome zones, and consistent lifecycle hooks, not ad hoc theme suspension.
- Classification:
  - `Source-fixable`
  - `Architecture-required`
- Recommended response:
  - `Deep rewrite`
- Likely source areas:
  - `apps/gui/viewport.c`
  - `apps/gui/statusbar-skinned.c`
  - `apps/gui/usb_screen.c`
  - `apps/screens.c`
- Implementation notes:
  - Introduce a surface framework with explicit composition zones: top chrome, content, overlay, bottom transport, transient modal.
  - Make viewports an internal implementation detail of surfaces rather than the main authoring model.
- Risks:
  - invasive cross-surface changes
- Benefits unlocked:
  - consistent layout ownership
  - fewer theme enable/disable bugs
  - cleaner special screens

### 4.2.3 WPS/SBS-specific parsing rules leak product complexity into theme authorship

- Current Rockbox behavior:
  - Images, viewports, album art, status bar integration, progress bars, and touch regions are all declared through specialized tags and label resolution rules.
  - Duplicate image IDs, missing assets, font-slot exhaustion, and label collisions remain easy failure modes.
- Why it limits Apple2026:
  - Too much product logic gets encoded into theme grammar rather than stable source abstractions.
- Classification:
  - `Theme-awkward`
  - `Source-fixable`
- Recommended response:
  - `Moderate refactor`
- Likely source areas:
  - `apps/gui/skin_engine/skin_parser.c`
  - `apps/gui/skin_engine/skin_display.c`
- Implementation notes:
  - Stabilize the existing skin engine with stricter diagnostics and clearer ownership.
  - Move shell-critical behaviors out of theme grammar and into source-level components.
- Risks:
  - short-term duality between old skin tags and new shell components
- Benefits unlocked:
  - less fragile Apple2026 authoring

## 4.3 Typography, font system, text layout, clipping, and baseline control

### 4.3.1 Rockbox typography is still a bitmap font system with hard slot limits

- Current Rockbox behavior:
  - `firmware/export/font.h` defines `MAXUSERFONTS 12`.
  - `.fnt` stores width, height, ascent, depth, offsets, widths, and bitmaps.
  - `struct font` exposes glyph widths and ascent, but there is no kerning, shaping, tracking, or style system.
- Why it limits Apple2026:
  - Apple2026 is explicitly typography-led. The current system can display fonts, but it cannot express a robust design system with real typographic behavior.
  - Font slot pressure also leaks upward into WPS/SBS and surface design.
- Classification:
  - `Theme-impossible`
  - `Architecture-required`
  - `Branch-justified`
- Recommended response:
  - `Long-term branch foundation`
- Likely source areas:
  - `firmware/export/font.h`
  - `firmware/font.c`
  - `firmware/font_cache.c`
- Implementation notes:
  - Introduce a text style layer above raw font IDs.
  - Expand or virtualize font slot management.
  - Long term, consider a richer glyph pipeline with optional kerning and better antialiasing control.
- Risks:
  - memory cost on constrained hardware
  - converter/tooling impact
- Benefits unlocked:
  - typography stops being the weakest part of Apple2026

### 4.3.2 Line layout is mostly derived from raw font height, which causes clipping pressure everywhere

- Current Rockbox behavior:
  - `screen_helper_getcharheight()`, `viewport_get_nb_lines()`, list row heights, and many text surfaces derive geometry directly from `font->height`.
  - WPS/SBS line placement uses line-number and line-height logic rather than baseline-safe text blocks.
- Why it limits Apple2026:
  - Apple-style layout needs consistent baseline relationships, not just "fit another font-height line in this box."
  - This is one root cause of frequent clipping and awkward vertical compromises.
- Classification:
  - `Source-fixable`
  - `Architecture-required`
- Recommended response:
  - `Deep rewrite`
- Likely source areas:
  - `apps/screen_access.c`
  - `apps/gui/viewport.c`
  - `apps/gui/list.c`
  - `apps/gui/skin_engine/skin_display.c`
- Implementation notes:
  - Introduce text metrics per style: cap/ascender/descender-safe line box, baseline offset, leading, truncation policy.
  - Stop using raw font height as the default layout unit for everything.
- Risks:
  - wide rendering fallout
- Benefits unlocked:
  - predictable hierarchy
  - fewer Apple2026 clipping corrections

### 4.3.3 Text alignment and clipping behavior is too primitive for modern shell surfaces

- Current Rockbox behavior:
  - The skin display pipeline merges aligned text segments and resolves overlap at the line level.
  - Truncation and marquee behavior are local, not part of a global text layout policy.
- Why it limits Apple2026:
  - Apple2026 needs consistent overflow rules across lists, WPS, mini-player, headers, and dialogs.
- Classification:
  - `Source-fixable`
- Recommended response:
  - `Moderate refactor`
- Likely source areas:
  - `apps/gui/skin_engine/skin_display.c`
  - `apps/gui/bitmap/list.c`
- Implementation notes:
  - Add shared truncation and marquee policies per text role.
  - Introduce column-aware text layout before final rasterization.
- Risks:
  - regression on existing skins
- Benefits unlocked:
  - stable overflow behavior across the product

## 4.4 Icons, bitmaps, image loading, and asset pipeline

### 4.4.1 Themeable icons are a fixed enum mapped to a vertical bitmap strip

- Current Rockbox behavior:
  - `apps/gui/icon.c` computes icon height as bitmap height divided by `Icon_Last_Themeable`.
  - Icon semantics are tied to enum positions, sprite strip order, and fixed raster tiles.
- Why it limits Apple2026:
  - Apple2026 wants a semantic icon system with clearer role ownership, variant management, and future growth.
  - Every new icon family change cascades through enums, sheets, and render assumptions.
- Classification:
  - `Theme-impossible`
  - `Architecture-required`
- Recommended response:
  - `Deep rewrite`
- Likely source areas:
  - `apps/gui/icon.c`
  - `apps/gui/icon.h`
  - icon asset generation tooling
- Implementation notes:
  - Introduce a semantic asset registry: named symbol roles, size classes, state variants, and per-surface resolution.
  - Preserve bitmap output for target hardware, but stop exposing sprite-strip order as the core contract.
- Risks:
  - tooling and compatibility work
- Benefits unlocked:
  - cleaner Apple2026 symbol family
  - easier expansion

### 4.4.2 Image handling remains BMP-centric and manually orchestrated

- Current Rockbox behavior:
  - Theme and plugin images are preloaded and drawn through manual label references and bitmap loaders.
  - Album art, progress assets, status assets, and plugin art all use slightly different pipelines.
- Why it limits Apple2026:
  - A product-level shell wants one asset story, not one pipeline for icons, another for WPS bitmaps, another for plugin art, and another for album art.
- Classification:
  - `Source-fixable`
  - `Architecture-required`
- Recommended response:
  - `Moderate refactor`
- Likely source areas:
  - `apps/gui/skin_engine/skin_parser.c`
  - `apps/gui/icon.c`
  - `apps/plugin.c`
  - album art and bitmap loaders
- Implementation notes:
  - Introduce shared asset APIs for static shell images, semantic icons, and media-derived art.
  - Centralize caching policy and size negotiation.
- Risks:
  - memory tuning required
- Benefits unlocked:
  - more predictable shell rendering

## 4.5 Dialogs, quickscreen, context menus, and utility surfaces

### 4.5.1 Utility surfaces are still separate renderers, not shell components

- Current Rockbox behavior:
  - `apps/gui/quickscreen.c`, `apps/gui/yesno.c`, `apps/gui/splash.c`, `apps/gui/usb_screen.c`, and calibration/info screens all compute their own geometry and draw their own content.
  - Theme enable/disable is often used as a bridge around them rather than true integration.
- Why it limits Apple2026:
  - These screens are highly visible product surfaces. If they do not inherit the same structural model as lists and playback, the shell never feels native.
- Classification:
  - `Theme-impossible`
  - `Architecture-required`
  - `Branch-justified`
- Recommended response:
  - `Deep rewrite`
- Likely source areas:
  - `apps/gui/quickscreen.c`
  - `apps/gui/yesno.c`
  - `apps/gui/splash.c`
  - `apps/gui/usb_screen.c`
  - `apps/screens.c`
- Implementation notes:
  - Build a reusable transient-surface framework: modal, sheet, overlay, utility page, system takeover.
  - Each should inherit shell chrome and typography roles instead of defining layout from scratch.
- Risks:
  - many screens touched
- Benefits unlocked:
  - whole-product coherence, not just browse/playback polish

### 4.5.2 Context menus are functionally central but structurally detached

- Current Rockbox behavior:
  - `apps/onplay.c` pushes `ACTIVITY_CONTEXTMENU`, runs a menu, and maps menu return codes back into shell actions.
- Why it limits Apple2026:
  - The context menu is a key UX surface, but it is still one more discrete lane rather than part of a shared surface model.
- Classification:
  - `Source-fixable`
- Recommended response:
  - `Moderate refactor`
- Likely source areas:
  - `apps/onplay.c`
  - `apps/menu.c`
- Implementation notes:
  - Move context menus onto the future transient-surface framework with shared row descriptors and shared action routing.
- Risks:
  - action regressions
- Benefits unlocked:
  - cleaner contextual UX

## 4.6 Navigation, actions, keymaps, activity stack, and screen return behavior

### 4.6.1 The shell is a return-code state machine, not a route stack

- Current Rockbox behavior:
  - `apps/root_menu.c` coordinates screens with `GO_TO_*`, `next_screen`, `last_screen`, and `previous_music`.
  - Many screens return integers that are interpreted differently by the root loop.
- Why it limits Apple2026:
  - Product-level continuity becomes a patchwork of special cases.
  - Back, home, resume, and "return to meaningful parent" behavior are difficult to reason about globally.
- Classification:
  - `Theme-impossible`
  - `Architecture-required`
  - `Branch-justified`
- Recommended response:
  - `Long-term branch foundation`
- Likely source areas:
  - `apps/root_menu.c`
  - `apps/tree.c`
  - `apps/gui/wps.c`
  - `apps/playlist_catalog.c`
- Implementation notes:
  - Introduce a typed shell router with explicit route objects, parent chain, and resume policy.
  - Separate "open screen," "replace stack," "return to parent," and "return to playback anchor" behaviors.
- Risks:
  - central control-flow rewrite
- Benefits unlocked:
  - predictable navigation and fewer regressions

### 4.6.2 Input behavior is context-map driven rather than intent driven

- Current Rockbox behavior:
  - `apps/action.c` resolves actions through context maps.
  - `apps/keymaps/keymap-ipod.c` gives the same hardware input different meanings depending on context.
- Why it limits Apple2026:
  - Apple2026 wants predictable mental models. Context-specific key behavior is necessary, but the current model makes consistency hard to prove across the product.
- Classification:
  - `Source-fixable`
  - `Architecture-required`
- Recommended response:
  - `Moderate refactor`
- Likely source areas:
  - `apps/action.c`
  - `apps/action.h`
  - `apps/keymaps/keymap-ipod.c`
- Implementation notes:
  - Keep low-level button mapping, but add a shell-intent layer above it: navigate, confirm, go-back, open-playback, open-context, open-utility.
  - Let each routed surface advertise which intents it supports.
- Risks:
  - button behavior regressions if migrated too fast
- Benefits unlocked:
  - clearer UX contracts

### 4.6.3 The activity stack is shallow and only loosely related to shell state

- Current Rockbox behavior:
  - `apps/misc.c` uses a fixed `MAX_ACTIVITY_DEPTH 12` stack.
  - Push/pop activity also resets skinlist config and refreshes the custom status bar.
- Why it limits Apple2026:
  - Activity is doing double duty as state annotation and refresh trigger, but it is not a true route history.
- Classification:
  - `Source-fixable`
- Recommended response:
  - `Moderate refactor`
- Likely source areas:
  - `apps/misc.c`
  - `apps/misc.h`
- Implementation notes:
  - Replace activity-as-navigation with a proper route/session model, then keep activity as analytics or coarse rendering context if still needed.
- Risks:
  - hidden dependencies
- Benefits unlocked:
  - less accidental coupling between state and redraw

## 4.7 Plugins, shell boundaries, and PictureFlow integration

### 4.7.1 Plugins are still separate applications with manual shell repair on exit

- Current Rockbox behavior:
  - `apps/plugin.c` loads plugins into `pluginbuf`, exposes a large API surface, and restores UI state manually after plugin execution.
  - Tree cache stability and buffer ownership are special concerns during plugin execution.
- Why it limits Apple2026:
  - A native-feeling shell cannot keep treating major features as foreign code that temporarily escapes the product.
- Classification:
  - `Theme-impossible`
  - `Architecture-required`
  - `Branch-justified`
- Recommended response:
  - `Deep rewrite`
- Likely source areas:
  - `apps/plugin.c`
  - `apps/open_plugin.c`
- Implementation notes:
  - Add a plugin-to-shell integration contract with lifecycle hooks:
    - enter as routed surface
    - declare chrome ownership
    - declare playback and browse return behavior
    - declare asset/theme participation
  - Long term, distinguish full external plugins from shell-integrated feature modules.
- Risks:
  - plugin compatibility
  - API breakage
- Benefits unlocked:
  - seamless major features

### 4.7.2 PictureFlow is integrated by return codes and plugin conventions, not by shell architecture

- Current Rockbox behavior:
  - `apps/plugins/pictureflow/pictureflow.c` defines its own contexts, state, caches, and rendering model.
  - Playback capability depends on buffer size (`PF_PLAYBACK_CAPABLE`).
  - WPS return into PictureFlow is coordinated externally through playback source and special-case routing.
- Why it limits Apple2026:
  - PictureFlow is a flagship music surface. If it remains plugin-shaped, it will always feel partially detached.
- Classification:
  - `Source-fixable`
  - `Architecture-required`
- Recommended response:
  - `Deep rewrite`
- Likely source areas:
  - `apps/plugins/pictureflow/pictureflow.c`
  - `apps/gui/wps.c`
  - `apps/root_menu.c`
- Implementation notes:
  - Treat PictureFlow as a routed media surface with shared shell services.
  - Keep its renderer specialized, but integrate navigation, playback bridge, and chrome ownership with the main shell.
- Risks:
  - nontrivial refactor of an old plugin
- Benefits unlocked:
  - Cover Flow can finally feel first-class without relying on hacks

## 4.8 Playback-shell coordination, browse/play continuity, and UI state management

### 4.8.1 Playback return behavior depends on global flags and special cases

- Current Rockbox behavior:
  - `global_status.playback_source`, `wps_entered_from_root`, `last_screen`, `previous_music`, and current track path all influence WPS exit behavior.
  - `wps_handle_browse_parent()` switches by playback source and falls back to settings-driven behavior.
- Why it limits Apple2026:
  - This works, but it is fragile. It encodes shell continuity as a collection of remembered exceptions instead of state ownership.
- Classification:
  - `Source-fixable`
  - `Architecture-required`
- Recommended response:
  - `Deep rewrite`
- Likely source areas:
  - `apps/gui/wps.c`
  - `apps/root_menu.c`
  - `apps/tree.c`
- Implementation notes:
  - Create a shared shell state store with:
    - current route
    - playback anchor route
    - current browse session
    - media context
    - return policy
  - Let WPS ask the shell where "back" should go instead of reconstructing it from globals.
- Risks:
  - wide behavior migration
- Benefits unlocked:
  - cleaner browse/playback continuity

### 4.8.2 Database, file browser, playlist browser, and playlist viewer are separate navigation worlds

- Current Rockbox behavior:
  - `apps/tagtree.c` keeps its own history stacks and custom parsed navigation definitions.
  - `apps/playlist_viewer.c` has fixed entry caps and plugin-buffer-backed loading behavior.
  - `apps/playlist_catalog.c` is another browse flow with separate return behavior.
- Why it limits Apple2026:
  - Apple2026 wants one music product. Today the music experience is split across several historically independent subsystems.
- Classification:
  - `Theme-impossible`
  - `Architecture-required`
- Recommended response:
  - `Long-term branch foundation`
- Likely source areas:
  - `apps/tagtree.c`
  - `apps/playlist_viewer.c`
  - `apps/playlist_catalog.c`
  - `apps/tree.c`
- Implementation notes:
  - Introduce a shared media-navigation domain model above file browser, database, playlists, and future PictureFlow.
  - Keep underlying engines initially, but route them through one shell service and one row renderer.
- Risks:
  - large conceptual migration
- Benefits unlocked:
  - coherent library UX and future filesystem-first experimentation

## 4.9 Redraw, buffering, responsiveness, and duplicated UI logic

### 4.9.1 Redraw ownership is fragmented across events, skins, lists, and special screens

- Current Rockbox behavior:
  - `GUI_EVENT_ACTIONUPDATE`, `skin_update()`, `skin_request_full_update()`, `sb_skin_force_next_update()`, list dirty ticks, and activity pushes all participate in redraw.
  - Multiple screens force refreshes by toggling theme state or pushing temporary activity changes.
- Why it limits Apple2026:
  - Responsiveness bugs and visual glitches become hard to reason about because no single layer owns "what changed and what should redraw."
- Classification:
  - `Source-fixable`
  - `Architecture-required`
- Recommended response:
  - `Moderate refactor`
- Likely source areas:
  - `apps/gui/viewport.c`
  - `apps/gui/skin_engine/skin_render.c`
  - `apps/gui/list.c`
  - `apps/misc.c`
- Implementation notes:
  - Introduce explicit invalidation scopes: route chrome, content region, overlay, media state, progress-only update.
- Risks:
  - redraw regressions
- Benefits unlocked:
  - smoother UI and easier debugging

### 4.9.2 Memory and buffer ownership is still too subsystem-specific

- Current Rockbox behavior:
  - Fonts, skins, plugins, playlist viewer, and tagtree all draw from different memory/buffer strategies such as buflib and `plugin_get_buffer()`.
- Why it limits Apple2026:
  - Product-level UI features compete for memory through legacy boundaries rather than explicit shell resource policy.
- Classification:
  - `Source-fixable`
- Recommended response:
  - `Moderate refactor`
- Likely source areas:
  - `firmware/font.c`
  - `apps/gui/skin_engine/skin_parser.c`
  - `apps/plugin.c`
  - `apps/playlist_viewer.c`
  - `apps/tagtree.c`
- Implementation notes:
  - Establish explicit resource classes for shell assets, playback UI, plugins, and transient media caches.
- Risks:
  - memory tuning work required per target
- Benefits unlocked:
  - more predictable UI feature development

### 4.9.3 UI logic is duplicated across multiple surfaces

- Current Rockbox behavior:
  - List item drawing, title handling, separators, utility screen layout, and shell enable/disable behavior are repeated in multiple files with slight variations.
- Why it limits Apple2026:
  - Duplication amplifies maintenance cost and causes inconsistent polish.
- Classification:
  - `Source-fixable`
- Recommended response:
  - `Moderate refactor`
- Likely source areas:
  - list, menu, splash, yes/no, quickscreen, USB, status bar, WPS-adjacent code
- Implementation notes:
  - The new shell foundation should aggressively centralize shared primitives rather than styling each screen class independently.
- Risks:
  - initial refactor overhead
- Benefits unlocked:
  - future Apple2026 work becomes faster and safer

## 5. Cross-cutting root causes

These limitations are not independent. The same historical assumptions keep recurring:

1. Rockbox UI was built as a collection of specialized screens rather than one coherent routed shell.
2. Rendering is line-oriented, bitmap-oriented, and viewport-oriented before it is component-oriented.
3. State is frequently represented by globals, return codes, and activity tags rather than explicit navigation/session objects.
4. The skin engine is asked to solve problems that should belong to shared UI infrastructure.
5. Plugins remain too separate from the main product model.

This is why Apple2026 improvements keep uncovering deeper structural limits. The theme is not failing. The platform contract is too old for the target product quality.

## 6. New branch architecture proposal

## 6.1 Branch identity

Recommended branch identity:

- `apple2026-ui-core`

Purpose:

- create a better Rockbox UI foundation for Apple2026
- preserve music playback strengths while modernizing shell structure
- avoid mixing this work with Cover Flow performance, cache, or storage tuning

## 6.2 Target architecture layers

### Layer 1: Shell router and session state

- explicit route stack
- route metadata for back/home/resume/playback anchor
- shell-wide current surface model
- shared browse/playback continuity

### Layer 2: Surface framework

- top chrome
- content surface
- bottom transport/miniplayer
- modal/sheet/overlay surfaces
- system takeover surfaces such as USB

### Layer 3: Reusable row/cell renderer

- semantic row descriptors
- density classes
- trailing accessories
- metadata lanes
- artwork lanes
- shared selection/divider behavior

### Layer 4: Text style/layout system

- named text roles
- baseline-aware line boxes
- truncation/marquee policy by role
- richer font asset management

### Layer 5: Asset registry

- semantic icon roles
- raster output variants
- shell images and component assets
- consistent loader/caching behavior

### Layer 6: Plugin and specialized-surface bridge

- routed plugin entry
- chrome ownership contract
- playback integration contract
- PictureFlow as a first-class media surface

## 6.3 Compatibility strategy

- Preserve existing WPS/SBS support during transition.
- Add compatibility shims so legacy lists and menus can still use the old callback path temporarily.
- Migrate Apple2026-critical surfaces first, then widen adoption.

## 6.4 Proposed module layout and ownership

The rewrite should not be dropped randomly into existing files. It should be introduced as a new UI core with explicit ownership.

### Proposed new source layout

- `apps/ui/shell_router.h`
- `apps/ui/shell_router.c`
- `apps/ui/shell_state.h`
- `apps/ui/shell_state.c`
- `apps/ui/surface.h`
- `apps/ui/surface.c`
- `apps/ui/nav_intent.h`
- `apps/ui/nav_intent.c`
- `apps/ui/row_model.h`
- `apps/ui/row_model.c`
- `apps/ui/row_renderer.h`
- `apps/ui/row_renderer.c`
- `apps/ui/text_style.h`
- `apps/ui/text_style.c`
- `apps/ui/text_layout.h`
- `apps/ui/text_layout.c`
- `apps/ui/asset_registry.h`
- `apps/ui/asset_registry.c`
- `apps/ui/transient_surface.h`
- `apps/ui/transient_surface.c`
- `apps/ui/plugin_bridge.h`
- `apps/ui/plugin_bridge.c`

### Ownership by module

- `shell_router`
  - owns route stack mutations
  - replaces most `GO_TO_*` coordination over time
  - decides open, replace, pop, and resume behavior
- `shell_state`
  - owns current route stack, playback anchor, browse anchor, modal stack, shell mode
  - replaces scattered globals such as `last_screen`, `previous_music`, and most ad hoc return memory
- `surface`
  - defines one standard lifecycle for pages, overlays, modals, and system takeovers
  - owns render/update/input hooks for all new Apple2026 shell surfaces
- `nav_intent`
  - maps current action-context results into product-level intents
  - sits above `action.c` and target keymaps
- `row_model` and `row_renderer`
  - define and render reusable list/menu/media rows
  - replace the single-line callback contract incrementally
- `text_style` and `text_layout`
  - own named text roles, line boxes, overflow policy, and baseline-aware layout
  - isolate typography decisions from raw font IDs
- `asset_registry`
  - owns semantic icons, shell bitmaps, and asset variant resolution
  - becomes the indirection layer above sprite strips and generated icon sheets
- `transient_surface`
  - standardizes dialogs, sheets, context menus, quickscreen, toasts, and progress overlays
- `plugin_bridge`
  - standardizes shell-integrated plugin lifecycle
  - first target is PictureFlow

### Existing files that should become adapters first, not rewrite targets first

- `apps/root_menu.c`
- `apps/tree.c`
- `apps/gui/wps.c`
- `apps/menu.c`
- `apps/gui/list.c`
- `apps/gui/bitmap/list.c`
- `apps/gui/quickscreen.c`
- `apps/gui/yesno.c`
- `apps/gui/splash.c`
- `apps/plugin.c`

These files should call into the new UI core as it becomes available. That keeps the migration staged instead of rewriting everything in-place.

## 6.5 Proposed data model and interfaces

### 6.5.1 Route model

The current `GO_TO_*` integer model should be replaced gradually by a typed route object.

Proposed shape:

```c
enum ui_route_kind {
    UI_ROUTE_HOME,
    UI_ROUTE_MUSIC_LIBRARY,
    UI_ROUTE_FILE_BROWSER,
    UI_ROUTE_DATABASE,
    UI_ROUTE_PLAYLIST_BROWSER,
    UI_ROUTE_PLAYLIST_VIEWER,
    UI_ROUTE_NOW_PLAYING,
    UI_ROUTE_PICTUREFLOW,
    UI_ROUTE_SETTINGS,
    UI_ROUTE_PLUGIN,
    UI_ROUTE_MODAL,
    UI_ROUTE_SYSTEM_USB,
};

enum ui_route_presentation {
    UI_PRESENT_PAGE,
    UI_PRESENT_MODAL,
    UI_PRESENT_OVERLAY,
    UI_PRESENT_SYSTEM_TAKEOVER,
};

struct ui_route {
    enum ui_route_kind kind;
    enum ui_route_presentation presentation;
    unsigned flags;
    union {
        struct ui_music_route_params music;
        struct ui_browser_route_params browser;
        struct ui_playlist_route_params playlist;
        struct ui_plugin_route_params plugin;
        struct ui_modal_route_params modal;
    } params;
};
```

Key decisions:

- a route is not just a screen ID
- route carries the minimum state needed to re-enter meaningfully
- modal and takeover surfaces use the same route system, but different presentation type

### 6.5.2 Shell session state

This should replace scattered globals and the weak activity stack.

Proposed shape:

```c
#define UI_ROUTE_STACK_MAX 16
#define UI_MODAL_STACK_MAX 4

struct ui_shell_state {
    struct ui_route route_stack[UI_ROUTE_STACK_MAX];
    int route_count;

    struct ui_route modal_stack[UI_MODAL_STACK_MAX];
    int modal_count;

    struct ui_route playback_anchor;
    bool has_playback_anchor;

    struct ui_route browse_anchor;
    bool has_browse_anchor;

    enum ui_shell_mode {
        UI_SHELL_MODE_STANDARD,
        UI_SHELL_MODE_LOCKED,
        UI_SHELL_MODE_USB,
        UI_SHELL_MODE_PLUGIN_TRANSITION,
    } mode;
};
```

What this replaces over time:

- `next_screen`
- `last_screen`
- `previous_music`
- `wps_entered_from_root`
- most use of `global_status.playback_source`
- most navigation use of `current_activity`

### 6.5.3 Navigation intents

Keep target keymaps and low-level actions. Add a translation layer above them.

Proposed intent model:

```c
enum ui_nav_intent {
    UI_INTENT_NONE,
    UI_INTENT_MOVE_PREV,
    UI_INTENT_MOVE_NEXT,
    UI_INTENT_CONFIRM,
    UI_INTENT_BACK,
    UI_INTENT_HOME,
    UI_INTENT_CONTEXT,
    UI_INTENT_OPEN_NOW_PLAYING,
    UI_INTENT_OPEN_QUICK_ACTIONS,
    UI_INTENT_ADJUST_UP,
    UI_INTENT_ADJUST_DOWN,
};
```

Why this matters:

- The shell should reason about intent, not target button combinations.
- `ACTION_WPS_BROWSE`, `ACTION_STD_CANCEL`, and similar actions can map to different intents per surface, but the router remains stable.

### 6.5.4 Surface contract

Every new Apple2026 shell surface should implement one lifecycle contract.

Proposed shape:

```c
struct ui_surface;

struct ui_surface_vtable {
    void (*on_enter)(struct ui_surface *surface, const struct ui_route *route);
    void (*on_exit)(struct ui_surface *surface);
    void (*on_suspend)(struct ui_surface *surface);
    void (*on_resume)(struct ui_surface *surface);
    void (*on_media_state_changed)(struct ui_surface *surface);
    void (*render)(struct ui_surface *surface, struct ui_render_ctx *ctx);
    bool (*handle_intent)(struct ui_surface *surface,
                          enum ui_nav_intent intent,
                          struct ui_route_command *out_cmd);
};
```

Important rule:

- surface code should not call root loop transitions directly
- it returns commands to the router

### 6.5.5 Router command contract

Surfaces should ask for transitions declaratively.

Proposed commands:

```c
enum ui_route_command_kind {
    UI_ROUTE_CMD_NONE,
    UI_ROUTE_CMD_PUSH,
    UI_ROUTE_CMD_REPLACE,
    UI_ROUTE_CMD_POP,
    UI_ROUTE_CMD_POP_TO_ROOT,
    UI_ROUTE_CMD_OPEN_NOW_PLAYING,
    UI_ROUTE_CMD_OPEN_MODAL,
    UI_ROUTE_CMD_CLOSE_MODAL,
};
```

This is the clean replacement for many direct `GO_TO_*` returns.

### 6.5.6 Reusable row model

The row system should be semantic, not string-only.

Proposed shape:

```c
enum ui_row_kind {
    UI_ROW_KIND_MENU,
    UI_ROW_KIND_LIBRARY,
    UI_ROW_KIND_ALBUM,
    UI_ROW_KIND_TRACK,
    UI_ROW_KIND_PLAYLIST,
    UI_ROW_KIND_SETTING,
    UI_ROW_KIND_CONTEXT_ACTION,
};

enum ui_row_accessory_kind {
    UI_ROW_ACCESSORY_NONE,
    UI_ROW_ACCESSORY_CHEVRON,
    UI_ROW_ACCESSORY_PLAYING,
    UI_ROW_ACCESSORY_CHECKMARK,
    UI_ROW_ACCESSORY_TOGGLE,
    UI_ROW_ACCESSORY_VALUE_TEXT,
};

struct ui_row_model {
    enum ui_row_kind kind;
    const char *title;
    const char *subtitle;
    const char *meta_left;
    const char *meta_right;
    enum ui_symbol_id leading_symbol;
    struct bitmap *leading_art;
    enum ui_row_accessory_kind accessory;
    const char *accessory_text;
    bool selected;
    bool dimmed;
    bool playing;
    bool destructive;
};
```

Rules:

- lists build arrays or callbacks returning `ui_row_model`
- row renderer owns geometry by row kind and density class
- separator, chevron, metadata clipping, and now-playing indicators become renderer responsibilities, not per-surface hacks

### 6.5.7 Text style and layout contract

The font system can stay bitmap-backed initially, but surfaces should stop using raw font IDs directly.

Proposed style roles:

```c
enum ui_text_role {
    UI_TEXT_ROLE_LARGE_TITLE,
    UI_TEXT_ROLE_NAV_TITLE,
    UI_TEXT_ROLE_ROW_TITLE,
    UI_TEXT_ROLE_ROW_SUBTITLE,
    UI_TEXT_ROLE_ROW_META,
    UI_TEXT_ROLE_WPS_TITLE,
    UI_TEXT_ROLE_WPS_META,
    UI_TEXT_ROLE_MODAL_TITLE,
    UI_TEXT_ROLE_MODAL_BODY,
    UI_TEXT_ROLE_UTILITY_LABEL,
};
```

Proposed layout box:

```c
struct ui_text_box {
    int x;
    int y;
    int width;
    int height;
    enum ui_text_role role;
    enum ui_text_overflow overflow;
    enum ui_text_align align;
};
```

Overflow policy should be standardized:

- headers: clip or marquee only when focused
- list titles: tail truncation
- WPS title: marquee allowed
- metadata: yield before primary titles

### 6.5.8 Asset registry contract

The icon pipeline needs semantic indirection.

Proposed shape:

```c
enum ui_symbol_id {
    UI_SYMBOL_NONE,
    UI_SYMBOL_MUSIC,
    UI_SYMBOL_ARTIST,
    UI_SYMBOL_ALBUM,
    UI_SYMBOL_SONG,
    UI_SYMBOL_PLAYLIST,
    UI_SYMBOL_SETTINGS,
    UI_SYMBOL_DISCLOSURE,
    UI_SYMBOL_PLAYING,
    UI_SYMBOL_BACK,
};

struct ui_symbol_variant {
    enum ui_text_role intended_role;
    int size_class;
    bool active;
    bool filled;
};
```

The registry resolves that into concrete bitmaps or icon-sheet indices for the current target.

### 6.5.9 Plugin bridge contract

PictureFlow should be the model for plugin-shell integration.

Proposed shape:

```c
struct ui_plugin_surface_desc {
    const char *plugin_name;
    bool owns_fullscreen;
    bool wants_shell_header;
    bool can_resume_playback_anchor;
    bool can_provide_row_surface;
    bool (*enter)(const struct ui_route *route);
    void (*exit)(void);
};
```

This allows the shell to know whether the plugin:

- is full takeover
- participates in playback continuity
- should restore to a known route on exit

## 6.6 Surface taxonomy for the rewrite

Not all screens should be treated equally. The rewrite should define stable surface classes.

### Page surfaces

- home
- library lists
- settings pages
- playlist browser/viewer
- now playing
- PictureFlow host page

### Transient surfaces

- context menu
- quickscreen
- yes/no
- progress sheet
- empty/error state overlays

### System takeover surfaces

- USB
- startup handoff
- shutdown/critical device states

### Embedded shell components

- top chrome/header
- bottom mini-player
- tab or root-nav region if introduced later
- scroll indicators
- inline badges and accessories

## 7. Implementation sequencing

## 7.1 Short-term changes

- Stabilize the audit conclusions in source-facing docs.
- Introduce a shell state module that centralizes:
  - current route
  - playback anchor
  - current browse session
  - current transient surface
- Stop adding new Apple2026 renderer hacks unless they are on the branch-foundation path.
- Improve diagnostics around skins, fonts, and asset loading to make later migration safer.

## 7.2 Medium-term changes

- Build the row descriptor and reusable list/menu renderer.
- Introduce shell surface types for:
  - standard list page
  - playback page
  - modal/sheet
  - system takeover page
- Move context menu, quickscreen, and yes/no onto the shared transient-surface model.
- Add semantic icon registry and text role abstractions.

## 7.3 Long-term changes

- Rebuild navigation around a typed route stack.
- Reposition WPS/SBS as presentation tools rather than shell owners.
- Integrate PictureFlow through the shell bridge.
- Consolidate database, filesystem, playlist viewer, and playlist catalog under a shared music-navigation domain.
- Explore richer font rendering and text layout if memory/performance permits.

## 7.4 Detailed migration plan

The migration should be staged so Apple2026 gains structure without requiring one destabilizing mega-merge.

### Stage 0: Freeze further ad hoc shell hacks

- Rule:
  - new Apple2026 logic should not introduce more one-off navigation globals or renderer-specific special cases unless it directly supports the new architecture
- Required prep:
  - document existing special cases in `root_menu.c`, `tree.c`, `wps.c`, `menu.c`, `plugin.c`
  - add TODO anchors pointing to the future replacement module where needed

### Stage 1: Introduce shell state beside the legacy root loop

- Add:
  - `apps/ui/shell_state.[ch]`
  - `apps/ui/shell_router.[ch]`
- Initial scope:
  - mirror current route transitions without changing visible behavior
  - record route stack for:
    - home
    - music library
    - file browser
    - database
    - playlist browser
    - playlist viewer
    - now playing
    - PictureFlow
- Legacy adapter points:
  - `root_menu.c`
  - `tree.c`
  - `wps.c`
- Success criteria:
  - current behavior preserved
  - route stack debug logging matches current user flow

### Stage 2: Replace playback return heuristics with explicit playback anchor state

- Move ownership away from:
  - `global_status.playback_source`
  - `wps_entered_from_root`
  - `previous_music`
- New model:
  - when playback is entered, router captures a `playback_anchor` route
  - WPS back asks router for the anchor instead of reconstructing it
- Files touched:
  - `apps/gui/wps.c`
  - `apps/root_menu.c`
  - `apps/tree.c`
  - `apps/settings.h` or a new UI-state header for migration glue
- Success criteria:
  - WPS back behavior matches current intended Apple2026 rules with less branching
  - no regressions on:
    - root -> now playing -> back
    - music library -> play -> WPS -> back
    - PictureFlow -> play -> WPS -> back
    - playlist viewer -> play -> WPS -> back

### Stage 3: Land the reusable row model without replacing all lists at once

- Add:
  - `apps/ui/row_model.[ch]`
  - `apps/ui/row_renderer.[ch]`
- First adopters:
  - root menu
  - Apple2026 music library list
  - settings top level
- Compatibility bridge:
  - old `gui_synclist` callbacks can be adapted into `ui_row_model`
  - new renderer can still be hosted by the old list selection engine initially
- Files touched:
  - `apps/gui/list.h`
  - `apps/gui/list.c`
  - `apps/gui/bitmap/list.c`
  - `apps/menu.c`
  - `apps/root_menu.c`
- Success criteria:
  - root and music library rows no longer need custom chevron or metadata hacks in per-surface code
  - row geometry is centralized by row kind

### Stage 4: Introduce text roles and layout boxes

- Add:
  - `apps/ui/text_style.[ch]`
  - `apps/ui/text_layout.[ch]`
- First adopters:
  - list row title/subtitle/meta
  - header titles
  - mini-player text
  - modal titles/body
- Do not change the underlying `.fnt` format yet.
- Files touched:
  - new UI text modules
  - `apps/gui/list.c`
  - `apps/gui/bitmap/list.c`
  - `apps/gui/wps.c` or Apple2026 WPS integration shim
- Success criteria:
  - row and header code stop hardcoding raw font IDs in most call sites
  - overflow behavior is standardized by role

### Stage 5: Build transient surface framework

- Add:
  - `apps/ui/transient_surface.[ch]`
- First migrated surfaces:
  - context menu
  - yes/no
  - quickscreen
  - splash/progress
- Files touched:
  - `apps/onplay.c`
  - `apps/gui/yesno.c`
  - `apps/gui/quickscreen.c`
  - `apps/gui/splash.c`
- Migration rule:
  - preserve existing behaviors first
  - unify geometry and shell chrome second
- Success criteria:
  - these surfaces share one lifecycle and one layout vocabulary
  - theme enable/disable toggling is reduced

### Stage 6: Add asset registry and migrate icon consumers

- Add:
  - `apps/ui/asset_registry.[ch]`
- First adopters:
  - list/menu leading symbols
  - disclosure chevrons
  - now-playing/accessory indicators
- Files touched:
  - `apps/gui/icon.c`
  - `apps/gui/icon.h`
  - icon generation tooling
- Success criteria:
  - Apple2026 code references semantic symbols, not enum-strip assumptions

### Stage 7: Build plugin bridge and move PictureFlow onto it

- Add:
  - `apps/ui/plugin_bridge.[ch]`
- First integrated plugin:
  - PictureFlow
- Files touched:
  - `apps/plugin.c`
  - `apps/open_plugin.c`
  - `apps/plugins/pictureflow/pictureflow.c`
  - `apps/gui/wps.c`
  - `apps/root_menu.c`
- Goals:
  - explicit route in/out
  - explicit chrome ownership
  - explicit playback anchor behavior
- Success criteria:
  - PictureFlow exit/return is router-owned rather than held together by special cases

### Stage 8: Consolidate music browsing domains

- Target:
  - file browser, music library, database, playlist browser, playlist viewer share one media navigation vocabulary
- This does not require deleting old engines immediately.
- It does require:
  - one route model
  - one row renderer
  - one playback-anchor system
- Success criteria:
  - Apple2026 music surfaces read as one product line

## 7.5 File-by-file rewrite strategy

### `apps/root_menu.c`

- Short term:
  - keep as dispatcher
  - add router integration points
- Mid term:
  - move most route branching into `shell_router`
- Long term:
  - root loop becomes thin orchestration instead of business logic owner

### `apps/tree.c`

- Short term:
  - keep browse engine
  - delegate route transitions and playback-anchor writes to UI core
- Mid term:
  - return `ui_route_command`-compatible actions at boundaries
- Long term:
  - split generic file browsing from Apple2026 media-surface behavior

### `apps/gui/wps.c`

- Short term:
  - stop growing special-case back-routing logic
- Mid term:
  - ask router for back/home/playlist/context transitions
- Long term:
  - WPS becomes a playback page surface integrated with shell state

### `apps/gui/list.c` and `apps/gui/bitmap/list.c`

- Short term:
  - add row model adapter layer
- Mid term:
  - centralize density, accessory, divider, and text-lane rules
- Long term:
  - list selection engine and row renderer become separable

### `apps/menu.c`

- Short term:
  - adapt menu items into row models
- Mid term:
  - migrate menu presentation to the same list/page surface class
- Long term:
  - menu becomes data provider, not renderer owner

### `apps/plugin.c`

- Short term:
  - expose plugin lifecycle notifications to shell router
- Mid term:
  - classify plugins by shell integration level
- Long term:
  - first-class plugin surfaces participate in routing and chrome ownership

## 7.6 Non-goals during the first rewrite wave

Do not mix these into the first foundation wave:

- Cover Flow performance optimization
- new caching/preload architecture for album art or storage
- deep changes to codec/playback engine internals
- broad international text shaping support before shell/state/row structure exists
- total removal of WPS/SBS

These would dilute the branch and make failures harder to isolate.

## 7.7 Testing and acceptance gates for the rewrite

Every stage needs explicit pass criteria. Architecture work without gates will drift.

### Router and shell-state gates

- Must preserve all current Apple2026 priority flows:
  - root -> now playing -> back -> root
  - music library -> album -> play -> WPS -> back -> album/list anchor
  - database -> play -> WPS -> back -> database
  - playlist viewer -> play -> WPS -> back -> playlist viewer
  - PictureFlow -> play -> WPS -> back -> PictureFlow
- Must log route stack transitions in debug builds.

### Row renderer gates

- Must support:
  - title-only rows
  - title + subtitle rows
  - art + title + subtitle rows
  - value-text accessory rows
  - chevron rows
  - now-playing indicator rows
- Must not regress scroll position, selection behavior, or wrap behavior.

### Typography/layout gates

- No baseline clipping on the Apple2026 stress strings already documented in `DESIGN_SYSTEM.md`.
- Metadata must yield before primary titles when constrained.
- No surface should directly use font height as a line box once migrated to text roles.

### Transient surface gates

- Context menu, quickscreen, yes/no, and splash must share:
  - common spacing tokens
  - common text roles
  - common entry/exit lifecycle
- No direct theme enable/disable workaround should remain in migrated surfaces unless explicitly documented.

### Plugin bridge gates

- Plugin exit must restore a known route rather than a guessed screen.
- PictureFlow must declare whether it owns fullscreen and whether it resumes a playback anchor.
- WPS and plugin transitions must no longer depend on multiple duplicated special cases.

## 7.8 Branch execution order after planning

The detailed rewrite plan implies this execution order:

1. Add router/state modules and debug route tracing.
2. Move WPS back behavior and playback anchor logic to router-owned state.
3. Build row model and migrate root + music library.
4. Land text roles/layout boxes in migrated list surfaces.
5. Migrate context menu and yes/no into transient surfaces.
6. Add asset registry and convert row accessories/leading symbols.
7. Integrate PictureFlow through plugin bridge.

This is the minimum sequence that changes the architecture without spreading the work too thin.

## 8. Recommended first branch wave

The most important first implementation wave for a new Apple2026 branch is:

1. `Shell state and routing foundation`
   - unify navigation decisions
   - remove dependence on scattered `GO_TO_*` special cases
2. `Reusable list/menu row renderer`
   - unlock browse-surface quality everywhere
3. `Transient surface framework`
   - unify dialogs, quickscreen, context menus, and utility surfaces
4. `Text role and layout abstraction`
   - reduce clipping churn and typography hacks
5. `Plugin and PictureFlow shell bridge`
   - make major media surfaces feel first-class

This order matters. If the branch starts with deeper cosmetic work first, it will keep paying tax to the old shell model.

## 9. Highest-value rewrites by impact

### Highest product impact

- unified shell router and session state
- row/cell list renderer
- transient-surface framework

### Highest Apple2026 visual impact

- text role/layout system
- semantic icon/asset registry

### Highest long-term leverage

- plugin shell bridge
- music-navigation domain consolidation

## 10. Final conclusion

Apple2026 is already proving that Rockbox can be pushed much farther than stock themes suggest. The deeper audit shows that the main blockers are no longer visual taste or asset quality. They are architectural:

- the shell is fragmented
- rendering primitives are too old and too narrow
- typography is too low-level
- plugins and special screens sit outside a unified product model

If Apple2026 wants to become a truly native-feeling product, the correct next move is not "more theme cleverness." It is a deliberate branch that modernizes the shell foundation while preserving Rockbox's playback core.

That branch should start by unifying navigation and reusable UI structure. Once those two are stable, typography, iconography, dialogs, and even PictureFlow become much cleaner to evolve.
