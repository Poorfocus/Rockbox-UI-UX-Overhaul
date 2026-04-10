# Contributing to Rockpod UI/UX Overhaul

Thank you for your interest in contributing! This project is a UI/UX research
and development fork of [Rockpod](https://github.com/nuxcodes/rockpod) (itself
a fork of [Rockbox](https://www.rockbox.org)), targeting iPod Classic 6G/7G
and iPod Video 5G/5.5G.

## Scope

This repository focuses on:
- UI/UX design and the Apple2026 WPS theme
- iPod firmware rendering improvements (list, splash, status bar, Cover Flow)
- MFi digital audio output on iPod Classic
- Dynamic album art colors
- iPod-specific build tooling and simulator tooling

If your contribution is a general Rockbox improvement not specific to this
project, please consider contributing upstream via
[gerrit.rockbox.org](https://gerrit.rockbox.org).

## Getting Started

See [BUILD.md](BUILD.md) for full build instructions on Windows (PowerShell /
MSYS2/UCRT64) and Linux/macOS. The UI simulator is the fastest way to test
changes without hardware.

## Font Setup

The Apple2026 theme requires SF Pro fonts that cannot be distributed here.
After cloning, generate them:

1. Download SF Pro and SF Compact from
   [developer.apple.com/fonts](https://developer.apple.com/fonts/) (free).
2. Place the .otf files in Apple Fonts/ at the repo root.
3. Run: python tools/apple2026_rebuild_fonts_from_otf.py

See [fonts/FONTS.md](fonts/FONTS.md) for details.

## Submitting Changes

- Fork the repo and create a feature branch from master.
- Keep commits focused; one logical change per commit.
- Follow the existing C code style: 4-space indent, C99, 80-column limit,
  /* C-style comments */ only. See [CLAUDE.md](CLAUDE.md) for full style
  notes.
- Open a pull request against master with a clear description of what
  changed and why.
- For WPS/theme changes, include simulator screenshots if possible.

## License

All contributions must be compatible with GPLv2. By submitting a pull request
you agree to license your contribution under GPLv2.

## Attribution

Please preserve all existing Copyright (C) notices in source files.
New files should include a standard GPLv2 header.
