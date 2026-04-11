# Apple2026 Build-vs-Claims Verification Audit

Date: 2026-04-11
Branch: `update-1`
Flagship classification: `Apple2026`

## Scope

This audit was triggered by a credible user report that the published Apple2026
Update 1 build still showed the old versions of:

- battery text
- hold / sleep icons
- repeat icons
- mute icon

The goal was not to blindly tweak coordinates again. The goal was to verify
whether the claimed fixes were actually present in:

- committed source
- simulator install output
- packaged 6G release artifact
- packaged 5G release artifact

## Claims Audited

### User-reported items

1. Battery text sizing / formatting
2. Hold / sleep icon overlap / positioning
3. Repeat icon clarity / state display
4. Mute icon vertical alignment

### Issue / worklog mapping

- GitHub issue `#10` — `battery text size`
- GitHub issue `#7` — `hold icon and sleep timer on SBS`
- GitHub issue `#5` — `mute icon alignment in WPS`
- Repeat-mode simplification claim recorded in `Update1Worklog.md`
- Matching fix claims recorded in `WORK_LOG.md`

### Exact Update 1 claims that were audited

From `Update1Worklog.md`:

- SBS battery text changed from slot `3` to slot `6`
- battery `%` formatting no longer contains a space
- hold icon moved from `(24,6)` to `(-82,6)`
- sleep icon moved from `(42,6)` to `(-94,6)`
- repeat mode simplified so only one icon shows per mode
- `speaker_mute` moved from `y=8` to `y=5`

## Files And Artifacts Compared

### Source

- `wps/Apple2026.sbs`
- `wps/Apple2026.wps`
- `wps/WPSLIST`
- `Update1Worklog.md`
- `WORK_LOG.md`

### Runtime / generated outputs

- `build-sim/simdisk/.rockbox/wps/Apple2026.sbs`
- `build-sim/simdisk/.rockbox/wps/Apple2026.wps`
- `build-sim/simdisk/.rockbox/themes/Apple2026.cfg`

### Hardware artifacts audited

- stale 6G release zip: `build-hw-ipod6g/rockbox_2026_beta_update1_6G.zip`
- stale 5G Update 1 release zip: `build-hw-ipodvideo/rockbox_2026_beta_update1_5G.zip`
- stale older 5G release zip: `build-hw-ipodvideo/rockbox_5G_2026.zip`
- current rebuilt 6G artifact: `build-hw-ipod6g/rockbox.zip`
- current rebuilt 5G artifact: `build-hw-ipodvideo/rockbox.zip`

## What The Audit Found

### 1. The committed source did not match the published claims

Before this pass, the live Apple2026 skin source still contained the old
behavior:

- `wps/Apple2026.sbs`
  - battery text still used font slot `3`
  - battery text still used `%bl %%`
  - lock icon still used `(24,6)`
  - sleep icon still used `(42,6)`
- `wps/Apple2026.wps`
  - battery text still used `%bl %%`
  - repeat display still layered icons:
    `%?mm<|%xd(Ra)|%xd(Ra)%xd(X)|%xd(Ra)%xd(Y)|%xd(Ra)%xd(Z)>`
  - extra shuffle overlay still existed:
    `%?if(%ps, =, s)<%xd(S)|>`
  - mute icon still used `speaker_mute.bmp,39,8`

Conclusion:

- the Update 1 worklog claimed these fixes
- the committed Apple2026 source did not actually contain them

This is a **source-vs-claims mismatch**.

### 2. The simulator install matched the unfixed source exactly

Before the repair:

- `build-sim/simdisk/.rockbox/wps/Apple2026.sbs` matched repo SBS byte-for-byte
- `build-sim/simdisk/.rockbox/wps/Apple2026.wps` matched repo WPS byte-for-byte

Conclusion:

- this was not just a stale simulator install problem
- the simulator correctly reflected the unfixed source

This is **not** primarily a runtime-load-path bug.

### 3. The published release zips were also stale, and did not match source

The stale custom-named release zips contained Apple2026 skins that differed
from the live repo source and still lacked the four claimed fixes.

Important details:

- `rockbox_2026_beta_update1_6G.zip` shipped stale Apple2026 SBS/WPS files
- `rockbox_2026_beta_update1_5G.zip` shipped the same stale Apple2026 SBS/WPS
  pair as the 6G zip
- `rockbox_5G_2026.zip` shipped an even older Apple2026 variant

Hash evidence before cleanup:

- stale Update 1 SBS hash in both custom 6G and 5G zips:
  `62f5b57772b3705d8d83505faf013efeecdfb17d`
- stale Update 1 WPS hash in both custom 6G and 5G zips:
  `68a8b09cbf6ccb21b828a44bbb5e3faf5446cd0a`
- even older 5G SBS hash:
  `db83e3f995cc3f2e681274cd1ea16754de6195bc`
- even older 5G WPS hash:
  `85b181bdebd94bc2e5ebe1e9ba25d6acdc89e1b0`

Conclusion:

- the published custom-named zips were not trustworthy release proofs
- the release artifact layer had drifted from current working source

This is a **packaging / build-artifact mismatch**.

## Root Cause

This was not a single bug. It was two failures at once.

### Primary root cause

The Update 1 documentation claimed four Apple2026 fixes that were never
actually present in the committed skin source.

### Secondary root cause

The custom-named release zips were stale Apple2026 artifacts and did not
match the current repo source either.

### What this means in plain terms

The trust break came from:

1. a **source-vs-changelog mismatch**
2. a **release-artifact-vs-source mismatch**

The user report was correct.

## Fix Strategy Executed

### Source fixes

Updated `wps/Apple2026.sbs` to:

- use slot `6` for both battery text viewports
- remove the extra space before `%`
- move lock icon to `(-82,6)`
- move sleep icon to `(-94,6)`

Updated `wps/Apple2026.wps` to:

- remove the extra space before `%`
- simplify repeat-mode display to one icon per mode:
  `%?mm<|%xd(Ra)|%xd(X)|%xd(Y)|%xd(Z)>`
- remove the extra shuffle overlay
- move mute icon to `speaker_mute.bmp,39,5`

### Packaging fixes

- rebuilt simulator install
- rebuilt `build-hw-ipod6g/rockbox.zip`
- rebuilt `build-hw-ipodvideo/rockbox.zip`
- removed stale custom-named release zips

## Evidence That The Release Now Matches The Claims

### Static audit results

Source-only audit:

```text
python tools/apple2026_skin_audit.py --package-root .does-not-exist
-> OK
```

Source vs live artifacts:

```text
python tools/apple2026_skin_audit.py \
  --package-root build-sim/simdisk/.rockbox \
  --zip-artifact build-hw-ipod6g/rockbox.zip \
  --zip-artifact build-hw-ipodvideo/rockbox.zip
-> OK
```

### Current verified hardware artifact hashes

Both current hardware zips now contain the same corrected Apple2026 skin pair:

- `.rockbox/wps/Apple2026.sbs`
  - SHA-1: `421acf1c11e3a4b92b555a1bd9f2c7546102c8d3`
- `.rockbox/wps/Apple2026.wps`
  - SHA-1: `402d9fd0bdf72f358e733f6932337d6dd3362695`

### Current verified contract patterns in both hardware zips

- SBS contains:
  - `%Vl(batterytext,-70,5,38,20,6)`
  - `%?if(%bl, =, 100)<100%%|%bl%%>`
  - `%Vl(lock,-82,6,9,12,-)`
  - `%Vl(sleeptimericon,-94,6,9,12,-)`
- WPS contains:
  - `%?if(%bl, =, 100)<100%%|%bl%%>`
  - `%?mm<|%xd(Ra)|%xd(X)|%xd(Y)|%xd(Z)>`
  - `%x(M,speaker_mute.bmp,39,5)`

## Anti-Regression Safeguards Added

### 1. Claim-contract enforcement in `tools/apple2026_skin_audit.py`

The audit now fails if:

- SBS battery text falls back to slot `3`
- any Apple2026 battery text uses `%bl %%`
- hold/sleep icons return to the left-side coordinates
- layered repeat icon logic returns
- extra shuffle overlay returns
- mute icon returns to `y=8`

### 2. Build-time artifact verification

- `build-sim.sh` now runs the Apple2026 audit against the simulator install
- `build-hw.sh` now runs the Apple2026 audit against the generated `rockbox.zip`

This turns release verification into a build-time check instead of a manual
memory task.

### 3. Historical correction

- `Update1Worklog.md` now includes an explicit audit-correction note
- `WORK_LOG.md` now records the source-vs-claims and package-vs-source mismatch

## Release Verification Checklist

Before publishing the next Apple2026 build:

1. Confirm the repo source contains the claimed Apple2026 patterns.
2. Refresh the simulator install and ensure the Apple2026 audit passes.
3. Build `build-hw-ipod6g/rockbox.zip`.
4. Build `build-hw-ipodvideo/rockbox.zip`.
5. Run the Apple2026 audit against both zips.
6. Verify the final public artifact names come from those fresh `rockbox.zip`
   files, not from historical custom-named copies.
7. Only after artifact verification passes, update changelog / release notes.
8. If a note says "fixed", ensure the exact source line and packaged zip member
   both prove it.

## What To Check First In The Next Build

Check these first, in this order:

1. `python tools/apple2026_skin_audit.py --zip-artifact build-hw-ipod6g/rockbox.zip --zip-artifact build-hw-ipodvideo/rockbox.zip`
2. inspect the zip members:
   - `.rockbox/wps/Apple2026.sbs`
   - `.rockbox/wps/Apple2026.wps`
3. confirm the build being attached or published is the freshly built
   `rockbox.zip`, not an older renamed archive

## Final Assessment

The mismatch was primarily:

- **changelog / worklog ahead of source**, plus
- **stale packaged build artifacts**

It was not primarily:

- a theme cfg misload
- a 5G-vs-6G layout divergence in the Apple2026 skin logic itself
- a user misunderstanding

The release now matches the claim set for the four audited Apple2026 items in
the current simulator install and the rebuilt 5G/6G `rockbox.zip` artifacts.
