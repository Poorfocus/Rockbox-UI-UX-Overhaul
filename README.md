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

> **Attribution:** This project is a UI/UX-focused fork of
> [Rockpod](https://github.com/nuxcodes/rockpod) by nuxcodes, which is itself
> a fork of [Rockbox](https://www.rockbox.org). Core platform features such as
> MFi digital audio, Cover Flow, dynamic colors, SSD-aware storage behavior,
> and power-management improvements originate with Rockpod. This repository
> focuses on interface, presentation, and user-experience changes built on top
> of that work. All upstream copyright notices are preserved. See [NOTICE](NOTICE)
> for licensing details.
>
> **Font notice:** Bitmap fonts derived from Apple SF Pro are included for
> **educational and research purposes only**. See [NOTICE](NOTICE).

---

## Overview

This repository is a personal UI/UX overhaul of Rockpod.

It began as a private build for my own daily-use iPod. I wanted Rockpod’s technical improvements, but with a cleaner and more deliberate interface: better visual consistency, less clutter, improved hierarchy, and a more cohesive overall presentation.

Development is iterative and experimental. Much of the project is effectively **vibe coded**: changes are made quickly, tested on real hardware, and refined over time based on direct use. As the project improves, I am publishing those changes for others who may find them useful.

This fork does **not** claim authorship of Rockpod’s core engineering work. Its purpose is to extend that foundation with UI and UX improvements.

---

## Scope of This Fork

This project is focused on the user-facing layer of the firmware, including:

- interface presentation
- visual consistency
- menu and navigation clarity
- typography and layout refinement
- metadata cleanup
- theme polish
- general usability improvements

The goal is not to replace Rockpod’s core identity, but to make the day-to-day experience of using it feel more cohesive and more considered.

---

## Upstream Rockpod Features

The following major features are inherited from **Rockpod** and remain fully credited to **nuxcodes** and upstream **Rockbox** contributors:

- **MFi digital audio output**
- **Reworked Cover Flow**
- **Dynamic album-art-based colors**
- **SSD-aware storage behavior**
- **Advanced power-management improvements**
- **Related rendering and playback-path improvements**

These features are a core part of this fork’s foundation. Their implementation and technical authorship belong upstream.

For full technical details, see the upstream [Rockpod repository](https://github.com/nuxcodes/rockpod).

---

## UI/UX Work in This Fork

This fork focuses on improving how Rockpod looks, reads, and feels in regular use.

Current areas of work include:

- cleaner visual hierarchy
- reduced menu and metadata clutter
- more consistent presentation across screens
- improved readability in browsing and playback views
- stronger theme cohesion
- tighter spacing, alignment, and layout decisions
- general refinement of the overall user experience

The emphasis is on polish, clarity, and consistency rather than new low-level platform features.

---

## Planned Work

Planned work remains UI/UX-focused and includes:

- further cleanup of menus and information density
- improved consistency across major screens
- additional theme and layout refinement
- better default presentation choices
- continued readability improvements
- more polished browsing and playback views
- small usability improvements identified through daily use

This roadmap is intentionally incremental. Changes are developed, tested, and refined in active use before being considered complete.

---

## Supported Models

This fork targets the same hardware base as the current Rockpod-derived builds:

- **iPod Classic (6G/7G)**
- **iPod Video (5G/5.5G)**

UI features are shared where supported by the underlying platform. Hardware-specific features remain dependent on upstream Rockpod support.

---

## Credits

This project depends on the work of upstream projects and contributors.

- **Rockbox** and its contributors
- **Rockpod** by [nuxcodes](https://github.com/nuxcodes), which provides the core platform features used by this fork
- Theme authors and other upstream contributors credited in their respective files and documentation

If you are here for the firmware-level features, the primary credit belongs to **Rockpod** and **Rockbox**. This repository’s contribution is the UI/UX layer built on top of that foundation.
