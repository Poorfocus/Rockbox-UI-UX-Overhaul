<p align="center">
  <img src="WhatsOldisNewAgain.png" alt="Whats Old is New Again — Rockbox UI/UX Overhaul" width="720">
</p>

<p align="center">
  <a href="https://github.com/Poorfocus/Rockbox-UI-UX-Overhaul/releases/latest"><img src="https://img.shields.io/github/v/release/Poorfocus/Rockbox-UI-UX-Overhaul?style=flat-square&color=blue" alt="Latest Release"></a>
  <img src="https://img.shields.io/badge/license-GPLv2-green?style=flat-square" alt="GPLv2">
  <img src="https://img.shields.io/badge/educational%20use-font%20notice-orange?style=flat-square" alt="Educational Use">
  <br/><br/>
  <a href="https://ko-fi.com/poorfocus" target="_blank">
    <img height="36" style="border:0px;height:36px;" src="https://storage.ko-fi.com/cdn/kofi5.png?v=6" border="0" alt="Buy Me a Coffee at ko-fi.com" />
  </a>
</p>

> **Attribution:** This project is a UI/UX-focused research fork of
> [Rockpod](https://github.com/nuxcodes/rockpod) by nuxcodes, which is itself
> a fork of [Rockbox](https://www.rockbox.org). Core firmware features such as
> MFi digital audio, rewritten Cover Flow, dynamic colors, SSD-aware storage
> behavior, and low-level power-management improvements originate with Rockpod
> unless otherwise noted here. All upstream copyright notices are preserved.
> See [NOTICE](NOTICE) for licensing details.
>
> **Font notice:** Bitmap fonts derived from Apple SF Pro are included for
> **educational and research purposes only**. See [NOTICE](NOTICE).

---

## What This Fork Is

This repository is my personal UI/UX overhaul of Rockpod.

I started making it for my own daily-use iPod because I loved what Rockpod achieved technically, but wanted a version that felt more deliberate visually: cleaner presentation, more cohesive menus, better typography choices, less clutter, and a stronger sense of polish across the whole device.

A lot of this project is, honestly, **vibe coded**. It grows through fast iteration, testing on real hardware, noticing what feels off, refining it, and repeating. I am sharing it publicly because I think that process can still be useful to other people, and because I want the community to be able to follow along as the project improves.

This fork is **not** a claim over Rockpod’s core engineering work. It is a presentation, interface, and experience-focused fork built **on top of** that foundation.

---

## Why I’m Sharing It

This began as a personal build for my own iPod setup, but the more I refined it, the more it felt worth publishing.

My goal is to keep improving it in the open:
- refining the interface
- tightening visual consistency
- experimenting with new layout and interaction ideas
- making the overall Rockbox experience feel more intentional and more enjoyable to use every day

If other people enjoy it, test it, or build on it too, even better.

---

## What Comes From Rockpod

Rockpod is the technical foundation of this fork.

The major firmware features below are **Rockpod features by nuxcodes**, not original to this UI/UX fork:

- **MFi digital audio output** for supported iPod hardware
- **Rewritten Cover Flow**
- **Dynamic album-art-based colors**
- **SSD-aware storage behavior**
- **Advanced power-management improvements**
- **Rendering and playback-path improvements tied to those systems**

Those features remain one of the main reasons this project exists at all. This fork depends on that work and is meant to present it through a more curated visual and UX layer, not replace its authorship.

For full technical details on those systems, see the upstream [Rockpod repository](https://github.com/nuxcodes/rockpod).

---

## What This Fork Focuses On

This fork is centered on the experience of using Rockpod every day.

That includes work like:
- cleaning up visual hierarchy
- improving menu readability
- reducing clutter in navigation and track presentation
- refining theme behavior and consistency
- improving how screens feel as a connected whole rather than as isolated features
- making the device feel more cohesive, modern, and intentional while still respecting Rockbox’s strengths

Where Rockpod’s biggest contributions are low-level firmware capabilities, this fork’s goal is to improve the **surface layer**: how the device looks, feels, reads, and flows.

---

## Current UI/UX Direction

The current direction of this fork includes:

- **A stronger visual identity** built around a more cohesive, curated presentation
- **Cleaner navigation and menu behavior** with less unnecessary visual noise
- **Typography and layout refinement** for better readability and balance
- **Track and metadata cleanup** so content is presented more clearly
- **Theme polish** that makes the interface feel more unified across screens
- **A more intentional overall feel** for everyday browsing, playback, and library navigation

Some of these improvements are already implemented, and others are still evolving as I continue refining the fork.

---

## Planned Features

This project is still evolving, and the roadmap is intentionally UI/UX-first.

Planned work includes:
- continued menu and information-density cleanup
- more refined screen-to-screen consistency
- additional theme and visual presentation work
- better default styling and layout choices
- more polished playback and browsing screens
- ongoing readability improvements for text-heavy views
- more thoughtful icon, spacing, and hierarchy decisions
- further small usability improvements discovered through real-world use

As with the rest of the project, the plan is iterative: build, test, live with it, refine it, and share the results.

---

## Included Upstream Rockpod Features

This fork currently includes Rockpod’s core feature set for supported devices, including:

- **MFi digital audio output** on iPod Classic 6G/7G
- **Reworked Cover Flow**
- **Dynamic colors based on album art**
- **Support for both HDD and iFlash-modded units**
- **SSD-aware behavior and power improvements on supported hardware**
- **Rendering and playback-path improvements from upstream Rockpod**

Again, those features are credited to **Rockpod / nuxcodes** and upstream Rockbox contributors.

---

## Supported Models

This fork targets the same family of devices supported by the current Rockpod base:

- **iPod Classic (6G/7G)**
- **iPod Video (5G/5.5G)**

UI features are shared across both where supported by the underlying platform. Hardware-specific functionality such as some power/storage behavior and MFi audio support remains dependent on upstream Rockpod’s device support.

---

## Installation

> **Prerequisite:** Your iPod must already have the Rockbox bootloader installed. See the [Rockbox installation guide](https://www.rockbox.org/wiki/RockboxUtility) if needed.

1. Download the correct zip from [Releases](https://github.com/Poorfocus/Rockbox-UI-UX-Overhaul/releases/latest)
2. Connect your iPod in disk mode
3. Extract the zip to the root of the iPod so it creates or updates `.rockbox`
4. Eject and reboot

PictureFlow may rebuild its album-art cache on first launch after upgrade.

---

## Building from Source

See [`BUILD.md`](BUILD.md) for build instructions, platform-specific scripts, outputs, and toolchain notes.

For fonts and font regeneration details, see [`fonts/FONTS.md`](fonts/FONTS.md).

---

## Credits

This project stands on the work of several upstream projects and contributors.

- **Rockbox** and its contributors
- **Rockpod** by [nuxcodes](https://github.com/nuxcodes)  
  Core firmware features in this fork—including MFi digital audio, Cover Flow work, dynamic colors, SSD behavior, and related system-level improvements—originate from Rockpod
- **Themes and theme authors** included in or adapted from upstream sources
- Additional upstream references and implementation notes preserved in the source tree and documentation

If you are here because of the technical features, the credit belongs first to **Rockpod** and **Rockbox**. This repository’s contribution is the UI/UX direction layered on top of that work.

---

## License

[GNU General Public License v2.0](LICENSE)

This project is distributed under the GPLv2, the same license as upstream Rockbox and Rockpod. All existing copyright notices are preserved in their respective source files.

**Font notice:** Bitmap fonts derived from Apple SF Pro / SF Compact are included for educational and research purposes only and are not covered by the GPLv2. See [NOTICE](NOTICE) for details.
