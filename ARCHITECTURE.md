# Architecture Overview

This project is a UI/UX research fork of [Rockpod](https://github.com/nuxcodes/rockpod),
which is itself a fork of [Rockbox](https://www.rockbox.org). It targets two iPod models:

- **iPod Classic (6G/7G):** S5L8702 SoC, DesignWare USB OTG, CS42L55 codec. Config: ipod6g.
  Full feature set — MFi digital audio, SSD power management, Cover Flow, dynamic colors.
- **iPod Video (5G/5.5G):** PP5022 SoC, ARC USB OTG, WM8758 codec. Config: ipodvideo.
  UI features — Cover Flow, dynamic colors, themes. MFi audio ported but untested.

Both share the same 320x240 LCD and most app-layer code.

## Layer Structure

`
bootloader/    — Minimal boot code, loads main firmware
firmware/      — HAL, kernel, drivers, filesystem, low-level services
lib/           — Shared libraries (rbcodec, skin_parser, fixedpoint, tlsf)
apps/          — Application layer: UI, playback engine, codecs loader, plugins, i18n
`

## Target Tree

Hardware abstraction lives under irmware/target/:
`
firmware/target/<cpu_arch>/<soc>/<manufacturer>/<model>/
`
Each target has a config header at irmware/export/config/<modelname>.h.
The central irmware/export/config.h includes auto-generated utoconf.h
(produced by 	ools/configure) to select the right target header.

## Build System

Source file selection uses SOURCES files (not per-target Makefiles). These are
preprocessed with the C preprocessor using #ifdef conditionals keyed on target
config defines. This is how a single build system handles 80+ targets.

Key SOURCES files: irmware/SOURCES, pps/SOURCES, pps/plugins/SOURCES.

See [BUILD.md](BUILD.md) for all build commands.

## Plugin System

Plugins are dynamically loaded .rock files. The API is a large struct of function
pointers defined in pps/plugin.h, versioned so plugins must match the core binary.
Entry point: enum plugin_status plugin_start(const void *parameter).

## Codec System

Audio codecs live in lib/rbcodec/ and are loaded as .codec files. The codec
framework includes DSP processing (EQ, crossfeed, replaygain). Supports MP3, FLAC,
Vorbis, Opus, AAC, ALAC, WavPack, APE, WMA, and many more.

## Memory Management

- **buflib** — compacting, handle-based allocator (irmware/buflib*).
- **core_alloc** — core allocation interface built on buflib.
- **TLSF** — used for hosted/application builds (lib/tlsf/).

## Platform Types

1. **Native** (PLATFORM_NATIVE) — bare-metal firmware on real hardware
2. **Hosted** (PLATFORM_HOSTED) — runs atop Linux/Android
3. **Simulator** (SIMULATOR) — SDL-based desktop simulator (primary dev/test method)

## Testing

There is no unit test framework. The UI simulator is the primary testing method —
it builds with SDL2 and runs the full Rockbox stack on the host desktop.
Additional test tools: 	est_codec, 	est_fps, 	est_mem plugins;
	ools/checkwps/ for WPS theme validation.

## Code Style

- **C only** (gnu99). Assembly only when necessary for performance.
- **4-space indentation**, no tabs. 80-column line limit. Unix LF line endings. UTF-8.
- **Naming:** all lowercase for variables, functions, structs, enums.
  UPPER_CASE for preprocessor macros and enum constants. No typedefs for structs.
- **Comments:** /* C-style only */. Use #if 0 to disable blocks. No // comments.
- Function braces on a new line. Follow the existing style in any file you edit.

## Key Tools

| Tool | Purpose |
|---|---|
| 	ools/configure | Build configuration script |
| 	ools/rockboxdev.sh | Cross-compiler toolchain builder |
| 	ools/bmp2rb | Bitmap converter for Rockbox native format |
| 	ools/convbdf | BDF font converter |
| 	ools/scramble / 	ools/descramble | Firmware file format tools |
| 	ools/buildzip.pl | Creates deployment ZIP |
| 	ools/apple2026_rebuild_fonts_from_otf.py | Generates Apple2026 bitmap fonts from OTF |
| 	ools/otf_to_rb12_fnt.py | Low-level OTF-to-RB12 font conversion |
| 	ools/sim_capture_*.py | Simulator screenshot capture utilities |
