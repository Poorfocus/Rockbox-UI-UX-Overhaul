# Apple2026 SBS Failure Audit

## Symptom Set

Observed runtime symptom:

- Apple2026 falls back to minimal/default Rockbox header and shell behavior.
- The custom SBS header chrome does not appear reliably.
- The WPS shell can also collapse back to Rockbox default behavior.
- This creates secondary symptoms that look like viewport routing issues because
  the custom info viewport is absent when SBS load fails.

The key fork for this investigation was:

- If `Apple2026.sbs` does not load, the first problem is a load failure.
- If `Apple2026.sbs` does load, the first problem is layout/routing/refresh.

## Load-State Determination

### Failing State

The failing runtime state was a true load failure, not a first-pass routing bug.

Evidence:

- `debugwps.out` reported parser failures before the skin could finish loading:
  - `Error on line 279.`
  - `%Vl(home_lock_sleep,-52,10,53,18,8)`
  - `Error on line 276.`
  - `%Vl(lock_sleep,-52,10,53,18,3)`
- Both failures were reported as `Parser callback returned error`.

### Fixed Verification State

After correcting the fatal viewport geometry, runtime logs showed both skins
loading successfully:

- `postfix_debugwps.err`
  - `Loading '/.rockbox/wps/Apple2026.sbs'`
  - `A26 skin_load skin=0 screen=0 isfile=1 requested=/.rockbox/wps/Apple2026.sbs loaded=1 fallback=0 failsafe=0`
  - `A26 sb_skin_get_info_vp ... found=1`
  - `Loading '/.rockbox/wps/Apple2026.wps'`
  - `A26 skin_load skin=1 screen=0 isfile=1 requested=/.rockbox/wps/Apple2026.wps loaded=1 fallback=0 failsafe=0`

Conclusion:

- `Apple2026.sbs` did not load in the failing state.
- The regression was first a load-failure question, not a routing-first question.

## Actual Root Cause

Primary current root cause:

- Parser-fatal viewport geometry in the Apple2026 lock sleep indicators.

Exact failing directives:

- `wps/Apple2026.sbs`
  - `%Vl(home_lock_sleep,-52,10,53,18,8)`
- `wps/Apple2026.wps`
  - `%Vl(lock_sleep,-52,10,53,18,3)`

Why they fail:

- In `apps/gui/skin_engine/skin_parser.c`, viewport parsing rejects any viewport
  whose final bounds exceed the display:
  - `skin_vp->vp.width + skin_vp->vp.x > display->lcdwidth`
- On a 320-pixel-wide display:
  - `x = -52` is resolved relative to the right edge
  - resulting `x = 268`
  - width `53`
  - `268 + 53 = 321`
- That is a one-pixel overflow, so `convert_viewport()` returns
  `CALLBACK_ERROR`, parse fails, and the skin load aborts.

This failure happens before bitmap-memory questions matter.

## Hypotheses Investigated

### Proven

- `Apple2026.sbs` and `Apple2026.wps` were failing to load because of parser
  rejection caused by the one-pixel viewport overflow above.

### Ruled Out As Primary Current Cause

- Skin buffer exhaustion
  - Investigated because the SBS preload budget is large.
  - `tools/apple2026_skin_audit.py` reports:
    - `Apple2026.sbs: percent-tokens=616 preload-decoded16=228200`
    - `Apple2026.wps: percent-tokens=341 preload-decoded16=69810`
  - This remains an architectural risk, but it was not the first failure in the
    current regression because the parser was already aborting beforehand.

- Token overflow
  - `apps/gui/skin_engine/wps_internals.h` defines `WPS_MAX_TOKENS 1150`.
  - Current Apple2026 token counts are well below that threshold:
    - SBS: `616`
    - WPS: `341`

- Wrong active `sbs:` / `wps:` paths
  - `build-sim/simdisk/.rockbox/config.cfg` points to:
    - `wps: /.rockbox/wps/Apple2026.wps`
    - `sbs: /.rockbox/wps/Apple2026.sbs`

- Missing current fonts in the simulator install
  - `tools/verify-sim-install.ps1` confirmed the expected runtime install state.
  - Font failure is a known global-skin failure mode, but it was not the cause
    of this specific regression.

- Duplicate viewport labels
  - Checked and not present in the current Apple2026 SBS/WPS files.

- CRLF line-ending corruption
  - `.gitattributes` and runtime files were checked; this was not the current
    failure mode.

### Secondary Contributor Identified

- Stale extracted hardware package directories created false signals during
  inspection.
  - `build-hw-ipodvideo/rockbox_5G_2026/.rockbox/...` was stale.
  - The real install artifacts are the rebuilt zip packages:
    - `build-hw-ipodvideo/rockbox.zip`
    - `build-hw-ipod6g/rockbox.zip`
  - Those zips now match source exactly for:
    - `.rockbox/wps/Apple2026.sbs`
    - `.rockbox/wps/Apple2026.wps`

## Why Prior Attempts Likely Missed It

- The visible symptom looked like header routing or shell chrome state failure.
- Apple2026 also carries real memory-pressure risk, which made `%xl()` preload
  exhaustion a plausible and distracting explanation.
- Once SBS is missing, viewport behavior downstream can look broken even though
  the real failure already occurred during parsing.
- Stale extracted package directories made it easy to inspect the wrong runtime
  payload and believe source changes were not propagating.
- Prior attempts appear to have modified symptoms around header placement and
  state logic without first proving whether SBS actually loaded.

## Files And Systems Involved

- `wps/Apple2026.sbs`
- `wps/Apple2026.wps`
- `apps/gui/skin_engine/skin_parser.c`
- `apps/gui/skin_engine/wps_internals.h`
- `build-sim/simdisk/.rockbox/config.cfg`
- `build-hw-ipodvideo/rockbox.zip`
- `build-hw-ipod6g/rockbox.zip`
- `debugwps.out`
- `postfix_debugwps.err`
- `tools/apple2026_skin_audit.py`

## Fix Applied

The fatal viewport widths were reduced by one pixel so the right-aligned
viewports stay within bounds:

- `wps/Apple2026.sbs`
  - `%Vl(home_lock_sleep,-52,10,53,18,8)` -> `%Vl(home_lock_sleep,-52,10,52,18,8)`
- `wps/Apple2026.wps`
  - `%Vl(lock_sleep,-52,10,53,18,3)` -> `%Vl(lock_sleep,-52,10,52,18,3)`

## Evidence That Proves The Fix

- Old failing parser log:
  - `debugwps.out` reports both viewport callback errors.
- New runtime load log:
  - `postfix_debugwps.err` shows:
    - SBS `loaded=1 fallback=0 failsafe=0`
    - WPS `loaded=1 fallback=0 failsafe=0`
    - `sb_skin_get_info_vp ... found=1`
- Audit script result:
  - `python tools/apple2026_skin_audit.py`
  - output: `OK`
- Rebuilt hardware package verification:
  - Source SHA1:
    - `Apple2026.sbs` -> `b9bb1f8f6f7e6f416323e5210b8f0e2cbf65a3fc`
    - `Apple2026.wps` -> `ec1120b86883ece48e95395a9cf6bc6f02ca6b11`
  - Matching hashes were confirmed inside:
    - `build-hw-ipodvideo/rockbox.zip`
    - `build-hw-ipod6g/rockbox.zip`

## Anti-Regression Safeguards

- Added `tools/apple2026_skin_audit.py` to check:
  - viewport bounds
  - duplicate viewport labels
  - approximate token counts
  - `%xl()` preload decode budgets
  - optional package drift against zip artifacts
- The audit specifically guards against repeating this class of parser-fatal
  right-edge overflow.
- Runtime validation now has a concrete first checkpoint:
  - confirm SBS/WPS load state before investigating layout symptoms.

## What To Check First Next Build

1. Run `python tools/apple2026_skin_audit.py`.
2. Confirm the active runtime config still points to Apple2026 SBS/WPS.
3. If the UI regresses again, check `debugwps.out` or equivalent logs before
   touching layout coordinates.
4. Confirm the actual install artifact is the rebuilt `rockbox.zip`, not a stale
   extracted convenience folder.
5. If SBS still loads cleanly, then move to viewport routing and state logic.
