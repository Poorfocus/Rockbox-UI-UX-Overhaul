# Apple2026 Deep Static Stability Audit

## 1. Audit Scope
This document provides a deep, static, source-level stability audit of the Apple2026 branch. The goal is to identify fragile, regression-prone, unmaintainable, or unsafe logic within the current architecture before further layering occurs.

## 2. Severity Classification
- **Critical:** Crash/panic/data-loss/fallback risk
- **High:** Major regression source / unstable core behavior
- **Medium:** Brittle/inconsistent, likely future regression
- **Low:** Cleanup/maintainability/polish stability

---

## 3. Subsystem-by-Subsystem Findings

### 3.1 Theme / Skin Load Stability
**Issue:** `Apple2026.sbs` and `.wps` parsing logic relies strictly on explicit viewport boundaries. If a calculated viewport exceeds the screen array by even one pixel (e.g., right-aligned lock sleep indicators), `apps/gui/skin_engine/skin_parser.c` will throw a parser error.
**Location:** `apps/gui/skin_engine/skin_parser.c`, `wps/Apple2026.sbs`
**Root Cause:** The parser handles coordinate overflows as fatal load failures rather than clipping them, causing the entire skin engine payload to eject.
**Severity:** Critical
**Current Impact:** Has already caused severe regressions (silent fallback to default Rockbox themes) that mimic routing bugs.
**Recommended Fix Type:** Branch-level architectural change (add safe viewport clipping or coordinate boundary checks before parser rejection).

### 3.2 Filesystem / Write / Config Safety
**Issue:** Config operations tied to UI elements exiting and `.cfg` generation can invoke `settings_save()` or partial state saves during volatile UI transitions.
**Location:** `apps/settings.c`, `apps/gui/quickscreen.c`, config generators
**Root Cause:** Saving settings on UI exit loops when the internal state hasn't fully synced or while memory banks are swapping (particularly into plugins) creates an unsafe configuration write state.
**Severity:** Medium
**Recommended Fix Type:** Subsystem cleanup (Defer non-critical writes to safe shutdown phases or debounced timers; strictly avoid write-on-exit in transient screens).

### 3.3 Navigation / State Stability
**Issue:** The branching logic separating the curated `/Music` browser from the raw `Files` browser relies heavily on `strncmp(browser_root, "/Music", 6)` and stack unwinding flags like `wps_entered_from_root` or `last_screen`.
**Location:** `apps/tree.c`, `apps/root_menu.c`, `apps/gui/wps.c`
**Root Cause:** Navigation is a state machine based on legacy return codes (`GO_TO_ROOT`, etc.) and variable patching, not explicit stack routing. Context dropouts (falling back to `/`) are structurally guaranteed when traversing complex nested menus.
**Severity:** High
**Current Impact:** Major regression source. Confirmed history of losing the curated Apple2026 state during unwinding.
**Recommended Fix Type:** Subsystem rewrite (Introduce an explicit typed shell router with parent pointers instead of string prefix checks).

### 3.4 Lockscreen Stability
**Issue:** Competing rendering loops for the hold switch (AOD/Status bar mode). The `Apple2026.sbs` overlay suppresses the usual status bar, but native Rockbox hold code attempts to assert hold status bounds simultaneously.
**Location:** `apps/gui/statusbar.c`, `apps/gui/statusbar-skinned.c`
**Root Cause:** Two surface owners attempting to paint to the same top chrome lane. Viewport misalignments cause duplicate icons and screen flickering.
**Severity:** Medium
**Recommended Fix Type:** Structural cleanup (Assure `apple2026_shell.h` logic explicitly governs when the lock overlay renders, muting redundant base system draws).

### 3.5 Quickscreen Stability
**Issue:** White-screen failures on quickscreen entry.
**Location:** `apps/gui/quickscreen.c`, `wps/Apple2026.sbs`
**Root Cause:** Viewport routing timing collisions. `gui_syncquickscreen_run()` queries the theme viewport before the SBS update has propagated the `qs_content` frame. The native C body renderer paints text to a stale invisible viewport while the theme draws a blank white container.
**Severity:** High
**Current Impact:** Confirmed past white-screen failure mode requiring an Interpod baseline rebase.
**Recommended Fix Type:** Source-fixable (Quickscreen must rely entirely on static determinable bounds mapped in C, with the SBS strictly relegated to styling the header chrome—never body coordinates).

### 3.6 Typography / List / Layout Stability
**Issue:** Height constraints and row layout are hardcoded strictly to `font_get(vp->font)->height`.
**Location:** `apps/gui/list.c`, `apps/gui/bitmap/list.c`, `firmware/export/font.h`
**Root Cause:** The list backend layout model relies on maximum font height. Apple2026 relies on hierarchy, dual-font rendering, and padded spacing, forcing the C side to inject minimum row boundaries on the fly. This fundamentally opposes the drawing engine assumptions.
**Severity:** High
**Recommended Fix Type:** Subsystem rewrite (Migrate away from the standard 1-string/1-icon callback path to a declarative semantic Row Descriptor model).

### 3.7 Cover Flow / Plugin Integration Stability
**Issue:** `pictureflow` operates as an entirely detached plugin that claims primary shell memory buffers and bypasses default navigation.
**Location:** `apps/plugins/pictureflow/pictureflow.c`, `apps/plugin.c`
**Root Cause:** Because PictureFlow hijacks `pluginbuf` and diverges from the internal router, returning from it or managing playback relies on patching hooks (`previous_music`), routinely failing if the cache is saturated.
**Severity:** High
**Recommended Fix Type:** Subsystem rewrite (Refactor Cover Flow into a first-class routed media surface inheriting the core `apple2026_shell` lifecycle hooks).

### 3.8 Build / Package / Install Stability
**Issue:** Output packages often harbor stale `.sbs` or `.wps` files extracted from previous hardware iterations, masquerading as correct code outputs.
**Location:** `packaging/`, `build-hw.sh`, `build-sim/`
**Root Cause:** Rockbox's traditional packaging allows overlapping assets if older `zip` folders aren't cleanly phased out.
**Severity:** Medium
**Recommended Fix Type:** Small patch (Ensure build pipelines cleanly wipe out destination `.rockbox/wps` data and heavily enforce `tools/apple2026_skin_audit.py`).

### 3.9 Donor-Theme / Import Stability
**Issue:** Residual dependencies on Adwaitapod/Interpod logic schemas left incomplete after porting.
**Location:** `Quickscreen` and `Apple2026.sbs` token maps.
**Root Cause:** Borrowing functional SBS hooks from established themes limits design agility because the underlying C implementations correspond directly to the donor theme's intent, not Apple2026's needs.
**Severity:** Low
**Recommended Fix Type:** Structural cleanup (Purge remaining legacy viewport tokens and formalize all core UI tags exclusively onto Apple2026 specifications).

### 3.10 Subsystem Ownership / Architecture
**Issue:** The skin engine is tasked with enforcing overarching product boundaries.
**Location:** Global framework
**Root Cause:** Depending on 2008-era custom layout scripting (WPS tags) to define a cohesive, multi-state music OS like Apple2026 is mathematically unsound. `sbs`/`wps` should decorate; C routing should construct.
**Severity:** Critical
**Recommended Fix Type:** Branch-level architectural change. Stop patching `apps/gui/list.c`. Establish a centralized routing kernel (`shell_router.c`) and comprehensive state object store (`shell_state.c`).

---

## 4. Recommended Order of Operations

**DO NOT BUILD ON THIS FURTHER UNTIL FIXED:**
1. **(Critical) Theme Parsing Safety:** Fortify `skin_parser.c` to gracefully clip pixel overshoots to safeguard against severe load failures dropping users back into legacy skins.
2. **(Critical) Core Routing and State:** Rip out `apps/tree.c` string prefix evaluations (`!strncmp(browser_root, "/Music", 6)`) and introduce a typed `apple2026_shell` session tracker.
3. **(High) Row Height Models:** Separate item rendering logic from core `font->height`. Push semantic rows so typography sizing errors don't trigger display assertions.
4. **(High) Quickscreen Decoupling:** Re-verify `qs_content` viewport decoupling. The SBS layer must only influence chrome elements with zero geometry reliance. 
5. **(Medium) CoverFlow Integration:** Prepare Coverflow memory logic to integrate tightly with the main tree router rather than bridging back upon unpredicted manual exit.

## 5. Anti-Regression Safe-guards
- Never approve coordinate or margin changes without first checking `debugwps.out` for underlying parser callbacks returning failures.
- Consistently validate *deep stack pop* navigation runs: _Cover Flow -> Target Album -> Drop back twice -> Music Main Menu_ to verify navigation stability strings.
