# RockPod build guide

**This file is the single place for build instructions** (commands, artifacts, env vars, troubleshooting, release packaging, and non-Windows notes). Other docs (`CLAUDE.md`, `AGENTS.md`, `MASTER.md` §8) only point here or repeat charter-level requirements.

This repository is upstream Rockbox with an out-of-tree build: `tools/configure` generates `Makefile`, then GNU `make` compiles firmware, codecs, plugins, and the UI simulator.

---

## Prerequisites

1. **MSYS2** installed (default path `C:\msys64`; override with `-MsysRoot` or `ROCKPOD_MSYS_ROOT`).
2. **UCRT64** environment packages: `make`, `gcc`, `perl` (with `IPC::Open2` for `wpsbuild.pl`), `python3`, SDL2 dev (`sdl2-config`, `pkg-config`), and **`arm-none-eabi-gcc`** for hardware builds.
3. Run a toolchain audit before chasing PATH issues:

```powershell
.\rockpod.ps1 check
# or
.\rockpod-check-env.ps1
```

**Charter-level requirement list** (what “installed” means for this project): `MASTER.md` §8.

**Cross-compiler:** If you need to build the ARM toolchain from source, use `tools/rockboxdev.sh` (upstream Rockbox helper).

---

## Quick start (copy-paste)

**Simulator** — full UI stack on the host (SDL):

```powershell
cd <repo-root>
.\build-sim.ps1 -Incremental
```

Run: `build-sim\rockboxui.exe` (working directory can stay `build-sim`; virtual disk is `build-sim\simdisk\`).

**iPod Classic 6G / 7G**:

```powershell
.\build-hw.ps1 -Target ipod6g -Incremental
```

Artifact: `build-hw-ipod6g\rockbox.zip`.

**iPod Video 5G / 5.5G**:

```powershell
.\build-hw.ps1 -Target ipodvideo -Incremental
```

Artifact: `build-hw-ipodvideo\rockbox.zip`.

**Unified CLI** (dispatches to the scripts above):

```powershell
.\rockpod.ps1 sim  -Incremental
.\rockpod.ps1 sim  -Incremental -SkipDep
.\rockpod.ps1 hw   -Target ipod6g -Incremental
.\rockpod.ps1 check -Scope SimOnly
.\rockpod.ps1 help
```

`rockpod.ps1` uses **explicit** `-Target`, `-Incremental`, `-SkipDep`, `-StrictInstall`, `-Scope`, and `-MsysRoot` parameters so **Windows PowerShell 5.1** binds switches correctly (splatting `ValueFromRemainingArguments` into child scripts is unreliable). Unsupported extra tokens produce a warning.

**Post-install sanity check (simulator):** after a successful build, from the repo root:

```powershell
.\tools\verify-sim-install.ps1
```

This checks that `make install` produced `rockboxui.exe`, `themes/Apple2026.cfg`, and the Apple2026 font/icon paths under `build-sim/simdisk/.rockbox/`.

---

## End-to-end flow (what the scripts do)

1. **Configure** (once per clean build dir): `Makefile`, `autoconf.h`, target selection.
2. **`make dep`**: dependency scan → `make.dep` (large; rerun after big header moves or if links look stale).
3. **`make`**: parallel compile — `rockboxui.exe` (sim) or firmware + codecs + plugins (hw).
4. **`make install` (sim)** / **`make zip` (hw)**: `tools/buildzip.pl` packages resources; themes go through `wps/wpsbuild.pl` and `wps/WPSLIST` (fonts, WPS/SBS, icons copied into the output tree).

Apple2026 assets (`fonts/`, `icons/`, `wps/Apple2026/`) are **copied** at install/zip time. Optional Python generators (below) are **not** run automatically.

---

## Scripts: clean vs incremental

| Script | Default (no flag) | Fast iteration |
|--------|---------------------|----------------|
| `build-sim.ps1` / `build-sim.sh` | Removes `build-sim/`, configure, `make dep`, full build | `-Incremental` / `-i` — keep dir; reconfigure only if missing or stamp mismatch |
| `build-hw.ps1` / `build-hw.sh` | Removes `build-hw-<target>/`, same pattern | Same |

- **Stamp**: `build-*/.rockpod_configure_stamp` records target. Switching target (`ipod6g` ↔ `ipodvideo`) needs a **clean** build or use separate directories (`build-hw-ipod6g` vs `build-hw-ipodvideo`).
- **`ROCKPOD_SKIP_DEP=1`**: skip `make dep` when `make.dep` exists — faster; run `make dep` manually after large include changes.

```powershell
$env:ROCKPOD_SKIP_DEP = "1"
.\build-hw.ps1 -Target ipod6g -Incremental
```

---

## Incremental compile inside an existing build directory

After the tree is configured, you can rebuild from the build folder without re-running the wrapper (Linux/macOS or MSYS UCRT64):

```bash
cd build-hw-ipod6g
make -j"$(getconf _NPROCESSORS_ONLN 2>/dev/null || nproc 2>/dev/null || echo 4)"
make zip
```

macOS often uses `make -j$(sysctl -n hw.ncpu)`. Windows: use the wrapper or open **UCRT64** and `cd` to the build dir the same way.

---

## Manual `configure` (reference)

From inside a build directory (or before first `make`):

```bash
../tools/configure --target=ipod6g --type=n      # 6G hardware
../tools/configure --target=ipodvideo --type=n   # 5G hardware
../tools/configure --target=ipod6g --type=s      # simulator
```

**Configure build types** (upstream Rockbox): (N)ormal firmware, (S)imulator, (B)ootloader, (A)dvanced, (C)heckWPS, (D)atabase tool, (W)arble codec tool, (T)est plugins, etc.

**Sanitizers** (simulator / advanced configs): `--with-address-sanitizer`, `--with-ubsan` passed to `configure` when supported.

**Default CFLAGS** (typical native): `-W -Wall -Wextra -Wundef -Os -nostdlib -ffreestanding -Wstrict-prototypes -pipe -std=gnu99` (exact flags come from generated makefiles).

---

## Common `make` targets (inside `build-sim` or `build-hw-*`)

| Target | Purpose |
|--------|---------|
| `(default)` | Full firmware / sim binary + libs |
| `make rocks` | Plugins only |
| `make codecs` | Codecs only |
| `make bin` | Main binary only |
| `make zip` | Package `rockbox.zip` (hardware) |
| `make install` | Install simulator tree (sim) |
| `make reconf` | Re-run configure after `tools/configure` changes |
| `make clean` / `make veryclean` | Clean build products |

---

## Outputs

| Build | Artifact | Notes |
|--------|-----------|--------|
| Simulator | `build-sim\rockboxui.exe` | Themes/fonts under `build-sim\simdisk\.rockbox\` after `make install` |
| Hardware | `build-hw-<target>\rockbox.zip` | Use zip for install; other binaries live in the same dir |

Theme iteration: from `build-sim`, `make symlinkinstall` can symlink theme files (see `tools/root.make`) when editing `wps/` frequently.

---

## PowerShell: parameter binding

Use **named** `-Target` when calling `build-hw.ps1` or `rockpod.ps1 hw`:

```powershell
.\build-hw.ps1 -Target ipod6g -Incremental   # good
```

Avoid passing the target as a **bare positional** before switches; a malformed invocation can bind `-Incremental` to the wrong parameter (e.g. `-Jobs`).

---

## Wrappers and stderr

`tools\rockpod-msys.ps1` runs `usr\bin\env.exe` and **bash -lc** with **stdout/stderr redirected to a temp file**, then replays the log (so `$LASTEXITCODE` stays the real build exit code and PowerShell pipelines do not steal it). Git or other tools may print CRLF warnings to stderr; the wrapper sets `$ErrorActionPreference = 'Continue'` around that invocation so benign stderr does not abort the script in strict mode.

**Strict install (CI / release):** set **`ROCKPOD_STRICT_INSTALL=1`** so a failed `make install` fails the simulator script.

---

## Environment variables (summary)

| Variable | Effect |
|----------|--------|
| `ROCKPOD_INCREMENTAL=1` | Same as `-Incremental` on `build-*.ps1` / `-i` on `build-*.sh` |
| `ROCKPOD_SKIP_DEP=1` | Skip `make dep` if `make.dep` exists |
| `ROCKPOD_INSTALL_ONLY=1` | Simulator: skip configure/dep/compile; run `make install` + font sync only (same as `-InstallOnly`) |
| `ROCKPOD_STRICT_INSTALL=1` | Simulator: fail script if `make install` fails |
| `ROCKPOD_MSYS_ROOT` | MSYS2 root if not `C:\msys64` |

PowerShell wrappers also accept **`-SkipDep`** (sets `ROCKPOD_SKIP_DEP=1`), **`-InstallOnly`** (sets `ROCKPOD_INSTALL_ONLY=1`), and, for the simulator only, **`-StrictInstall`** (sets `ROCKPOD_STRICT_INSTALL=1`).

---

## Fast simulator iteration (typical dev loop)

1. First build or after large header moves: `.\build-sim.ps1 -Incremental` (or clean default when switching branches).
2. Day-to-day C source edits: keep `build-sim/` and run `.\build-sim.ps1 -Incremental -SkipDep` to skip `make dep` when `make.dep` already exists.
3. **After font/WPS/icon-only changes (no C changes):** `.\build-sim.ps1 -InstallOnly` — skips configure/dep/compile entirely; ~30-40 sec instead of 2+ min.
4. If links or includes behave oddly, run `make dep` once inside `build-sim/` (or drop `-SkipDep`).
4. Confirm the install tree: `.\tools\verify-sim-install.ps1`.

**Wrappers and buffered output:** `tools/rockpod-msys.ps1` captures MSYS log output and prints it when the step finishes, so long `make` runs may appear quiet until the end. Re-run the same command inside **UCRT64** if you need a live TTY.

---

## Validation workflow (agents / humans)

Use this order after material UI or shell changes:

1. Clean or incremental configure/build (see above).
2. Run simulator — `build-sim\rockboxui.exe`.
3. Screenshots after major UI passes; compare to Figma / refs.
4. Log gaps in `WORK_LOG.md`.

Do **not** validate from plain `MSYS_NT` shells; use PowerShell wrappers or **UCRT64** so PATH matches.

---

## WSL Ubuntu / Linux fallback

If native Windows/MSYS2 is unstable, use **WSL Ubuntu** (or another Linux environment) for toolchain reliability: run `build-sim.sh` / `build-hw.sh` there, or bootstrap the cross-compiler with `tools/rockboxdev.sh`. Use Windows for running `rockboxui.exe`, Explorer access to artifacts, and optional checks.

If `wsl --status` reports `WSL_E_WSL_OPTIONAL_COMPONENT_REQUIRED`, reboot before continuing WSL setup.

---

## Non-Windows (macOS / Linux)

Use `build-sim.sh` / `build-hw.sh` from a suitable shell. **`build-hw.sh` refuses plain `MSYS_NT*`** — use MinGW UCRT64 or the same pattern as the PowerShell wrappers.

Hardware build examples:

```bash
./build-hw.sh                # iPod Classic 6G (default)
./build-hw.sh 5g             # iPod Video 5G
./build-hw.sh ipod6g
./build-hw.sh ipodvideo
./build-hw.sh -i ipod6g      # incremental
```

Simulator:

```bash
./build-sim.sh
./build-sim.sh -i
```

---

## Release packaging (GitHub)

After hardware zips exist:

```bash
# 1. Build hardware release zips
./build-hw.sh          # 6G
./build-hw.sh 5g       # 5G

# 2. Commit, tag, push
git add <files>
git commit -m "vX.Y: description"
git tag vX.Y
git push origin master
git push origin vX.Y

# 3. Create GitHub release with both zips
gh release create vX.Y \
    build-hw-ipod6g/rockbox.zip#rockbox-ipod6g.zip \
    build-hw-ipodvideo/rockbox.zip#rockbox-ipodvideo-5g.zip \
    --repo nuxcodes/rockbox -t "vX.Y" \
    -F release-notes.md
# Add -p for prerelease/alpha/beta tags
```

Releases: `https://github.com/nuxcodes/rockpod/releases`.

On Windows you can produce the same `rockbox.zip` files via `.\build-hw.ps1` then attach artifacts manually if `gh` is not used.

---

## Optional asset generators (not part of default `make`)

Run when changing sources; commit generated outputs.

| Script | Purpose |
|--------|---------|
| `tools/apple2026_symbol_assets.py` | `icons/Apple2026Icons.bmp`, `wps/Apple2026/*.bmp` |
| `tools/apple2026_boot_asset.py` | Boot logo bitmap |
| `tools/apple2026_font_prep.py` | Font prep under `Apple Fonts/Generated FNT/` |
| `tools/apple2026_rebuild_fonts_from_otf.py` | Rebuild all `fonts/*.fnt` from OTF sources |

---

## Fast install-only (after font or WPS changes)

After adding/changing a `.fnt` file under `fonts/` or editing `wps/Apple2026.*`, you can resync the simulator runtime without recompiling C code:

```powershell
# Fastest: skip configure + dep + compile; only run make install + font sync:
.\build-sim.ps1 -InstallOnly

# Same via unified CLI:
.\rockpod.ps1 sim -InstallOnly

# Alternative: incremental C build + install (use when C source also changed):
.\build-sim.ps1 -Incremental -SkipDep
```

Or from inside the already-built `build-sim/` directory (UCRT64 or WSL):

```bash
cd build-sim
make install
```

`make install` reruns `buildzip.pl` / `wpsbuild.pl` and re-copies all fonts, icons, WPS, and theme cfg into `simdisk/.rockbox/`. `build-sim.sh` also runs `sync_all_fonts()` after `make install` to copy any `.fnt` files in `fonts/` that `wpsbuild.pl` skipped (it only copies `%Fl`-referenced fonts). This is the correct remedy when:
- A new `.fnt` was added to `fonts/` but the sim was not rebuilt.
- `wps/Apple2026.sbs` was edited but `build-sim/simdisk/.rockbox/wps/Apple2026.sbs` is stale.
- The `build-sim.sh` staleness check (`[STALE]` / `[MISS]` lines) fires.
- `tools/apple2026_rebuild_fonts_from_otf.py` was run and fonts in `fonts/` were updated.

**Font regeneration workflow:**

```powershell
# 1. Regenerate fonts from OTF sources
python tools/apple2026_rebuild_fonts_from_otf.py

# 2. Sync to simulator runtime immediately (fastest)
.\build-sim.ps1 -InstallOnly

# 3. Verify
.\tools\verify-sim-install.ps1
```

**After `make install`, always verify:** `.\tools\verify-sim-install.ps1`

**Install stamp:** `build-sim/.rockpod_install_stamp` is touched after every successful `make install`. `verify-sim-install.ps1` uses this for its staleness reference instead of the binary mtime (the binary is built before install, so fonts newer than the binary but installed by the same run were falsely reported stale).

---

## Apple2026 simulator runtime asset contract

The simulator runtime must contain these Apple2026 assets after `make install`. Run `.\tools\verify-sim-install.ps1` to check all at once.

| Asset | Path in runtime | Source | Why critical |
|-------|----------------|--------|--------------|
| Large title font | `fonts/28-SFProDisplay-Bold.fnt` | `fonts/` via `wpsbuild.pl` `%Fl` | SBS slot 2 — Library / album title |
| Header font | `fonts/16-SFProText-Semibold.fnt` | `fonts/` via `wpsbuild.pl` `%Fl` | SBS slot 3 — compact header + mini-player |
| List font | `fonts/20-SFProText-Regular.fnt` | `fonts/` via `wpsbuild.pl` `%Fl` | SBS slot 5 + WPSLIST default |
| Icon strip | `icons/Apple2026Icons.bmp` | `icons/` via `wpsbuild.pl` | 32-tile menu icon strip |
| Theme cfg | `themes/Apple2026.cfg` | generated by `wpsbuild.pl` | theme load entry |
| SBS skin | `wps/Apple2026.sbs` | `wps/` copied by `wpsbuild.pl` | shell layout |
| WPS skin | `wps/Apple2026.wps` | `wps/` copied by `wpsbuild.pl` | Now Playing layout |
| WPS bitmaps | `wps/Apple2026/*.bmp` | `wps/Apple2026/` | battery, bars, player state, etc. |

**Font packaging path:** `wpsbuild.pl` scans all `%Fl(slot, name.fnt)` directives from
`Apple2026.sbs` and `Apple2026.wps`, then copies each matching `fonts/name.fnt` into the
install tree. If a `.bdf` counterpart exists it converts via `convbdf`; if only `.fnt`
exists it copies directly. A silent failure here leaves the runtime without a font.

**config.cfg vs Apple2026.cfg:** `build-sim/simdisk/.rockbox/config.cfg` is the
*live user state* file written by the running simulator. It may have a stale font entry
if you loaded a different theme at some point. `themes/Apple2026.cfg` is the canonical
Apple2026 theme spec (generated by `wpsbuild.pl`). When in doubt, delete `config.cfg`
and let the simulator recreate it when you load Apple2026 from the theme browser.

---

## Common issues

| Symptom | What to try |
|---------|-------------|
| `build-*.sh` says do not run from MSYS | Use **`build-*.ps1`** or **MinGW UCRT64**, not plain MSYS. |
| SDL / cross-compiler not found | `.\rockpod.ps1 check` — fix PATH inside UCRT64. |
| Slow every time | Default clean delete — use **`-Incremental`**. |
| Stale dependencies | `make dep` in the build dir, or unset `ROCKPOD_SKIP_DEP`. |
| Wrong theme / wrong font in sim | Delete `simdisk\.rockbox\config.cfg` and re-select theme from browser. |
| `make install` failed but script exited 0 | **`ROCKPOD_STRICT_INSTALL=1`** for CI/release. |
| Font missing from runtime (`[MISS]` in verify) | Run `.\build-sim.ps1 -InstallOnly` or full sim build. |
| Stale font in runtime (`[STALE]` in verify) | Run `.\build-sim.ps1 -InstallOnly`. The build script `sync_all_fonts()` will copy it. |
| Ran font generator, sim shows wrong font | Run `.\build-sim.ps1 -InstallOnly` immediately after font generation. |
| SBS font not appearing in sim (wrong title) | Verify `28-SFProDisplay-Bold.fnt` is in `build-sim/simdisk/.rockbox/fonts/`. |
| Ambiguous wrapper output | Reproduce once in **UCRT64 bash** to capture the first real error. |
| Git CRLF warnings during build | Noise unless something else fails; caused by mixed line endings in tracked files. |

---

## Related documentation (non-build)

- `CLAUDE.md` — project overview, architecture, code style, key tools (not duplicate build steps).
- `MASTER.md` §8 — environment charter (what must exist before implementation).
- `AGENTS.md` — branch boundaries and autonomous workflow (build steps are **here only**).
