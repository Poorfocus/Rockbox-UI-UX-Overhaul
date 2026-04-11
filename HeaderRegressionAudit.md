# HeaderRegressionAudit.md

## Scope

Apple2026 header/WPS regression investigation on branch `update-1`.

This document records only evidence-backed findings from the current pass.

## Symptom

The user reported that Apple2026 headers and WPS were regressing to a
minimal stock Rockbox look instead of the intended custom shell.

The observed broken visual model was:

- thin default-like header chrome instead of the Apple2026 Library / compact
  title treatment
- list content appearing to use fallback viewport placement
- WPS perceived as falling back as well

## What Was Investigated

1. Theme binding and runtime install state
2. SBS/WPS parser failure and fallback behavior
3. Bitmap / font asset presence
4. Skin buffer / plugin buffer pressure
5. Statusbar viewport routing and runtime info viewport selection
6. Simulator-vs-hardware memory differences

## Evidence

### 1. Current simulator runtime is loading Apple2026, not fallback

A fresh `build-sim\\rockboxui.exe --debugwps` run on the current install
shows:

- `A26 skin_load skin=0 ... requested=/.rockbox/wps/Apple2026.sbs loaded=1 fallback=0 failsafe=0`
- `A26 skin_load skin=1 ... requested=/.rockbox/wps/Apple2026.wps loaded=1 fallback=0 failsafe=0`

This means the currently installed SBS and WPS both load successfully in
the simulator.

### 2. The active info viewport is Apple2026 geometry in the fresh sim run

Fresh trace lines show Apple2026 viewport coordinates, not generated
fallback coordinates:

- default info VP seen at `0,38 320x158`
- `main_full` seen at `0,30 320x210`
- `main_full_lt` seen at `0,38 320x202`

Earlier fallback traces used the generated viewport shape
`0,8 320x232 font=0`. That is not what the current simulator run shows.

### 3. Runtime install now matches source for both skins

Current source and runtime copies are identical for:

- `wps/Apple2026.sbs`
- `wps/Apple2026.wps`

File-hash comparison and `git diff --no-index` both came back clean.

### 4. Asset-missing theory is not supported by the current runtime

Referenced Apple2026 WPS/SBS assets are present in runtime, including the
newer lockscreen and quickscreen assets.

### 5. Sim-vs-hardware plugin buffer mismatch is not a good primary explanation

- SDL simulator: `PLUGIN_BUFFER_SIZE 0x80000`
- iPod Video: `PLUGIN_BUFFER_SIZE 0x80000`
- iPod 6G: `PLUGIN_BUFFER_SIZE 0x300000`

So the simulator is representative of iPod Video for plugin-buffer size,
and iPod 6G has more headroom, not less.

## Findings

### Finding 1. The earlier "global SBS/WPS fallback" state was real, but it is not the current simulator state

Earlier traces showed parse failure followed by fallback. The current
freshly installed simulator run does not. This means the earlier broken
state cannot be treated as the live ground truth for the current runtime.

### Finding 2. Stale or mismatched runtime installs were a major confounder

Because the current simulator only behaved correctly after a fresh install
refresh, stale installed skins were a real risk during the investigation.

This does not prove stale install was the only root cause the user saw on
every test, but it does prove that "repo source looks correct" was not
sufficient validation on this branch.

### Finding 3. The current simulator investigation tree is now "loaded but wrong state/routing", not "failed to load"

Since both Apple2026 skins now load with `fallback=0`, any remaining header
problem in the current sim build has to come from:

- wrong runtime state
- wrong screen/context routing
- stale user config/runtime state
- a device-specific install or runtime divergence

and not from a universal SBS/WPS parser failure.

## Anti-Regression Safeguards Added

### verify-sim-install now checks WPS freshness as well as SBS freshness

`tools/verify-sim-install.ps1` previously warned only when
`wps/Apple2026.sbs` was newer than the installed copy.

It now also warns when:

- `wps/Apple2026.wps` in the repo is newer than the installed runtime copy

This closes a gap where the simulator could be tested against a stale WPS
even when the SBS freshness check passed.

## What To Check First In The Next Build

1. Run `.\tools\verify-sim-install.ps1`
2. Confirm it reports both:
   - `Apple2026.sbs runtime is current`
   - `Apple2026.wps runtime is current`
3. Run `build-sim\\rockboxui.exe --debugwps`
4. Confirm both loads show `fallback=0`
5. If the user still sees a broken header on device, compare device runtime
   install/config state against the simulator install before changing SBS/WPS
   geometry again
