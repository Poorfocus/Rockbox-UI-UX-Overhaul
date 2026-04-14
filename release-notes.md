## Rockpod Apple2026 — Beta Update 2

### Highlights

- Apple2026 Quick Settings has been rebuilt into a fixed Apple2026 control surface with a centered wheel, brightness on top and bottom, shuffle/repeat on the sides, and new horizontal brightness/volume bars.
- Now Playing and the mini-player have been polished with larger playback-state icons, clearer repeat/shuffle presentation, refreshed art framing, and a restored Interpod-style Lossless badge.
- WPS, menu, and packaging behavior have been tightened across the branch, including Lyrics/LRC routing on short `Select`, restored chevrons, cleaner `Extras -> Files` behavior, and more reliable Apple2026 staging in sim/hardware builds.

--
### Community Feedback Fixes

Thanks to everyone who kept reporting issues after the last release.

**Fixed**
- ✅ WPS short `Select` is now routed back through the WPS hotkey path on Apple2026 iPods, and Apple2026 now defaults that hotkey to Lyrics / LRC instead of Playlist Viewer.
- ✅ Menu chevrons are back on functional Apple2026 rows like `Music`, `Database`, and `Files`, not just nested submenu rows.
- ✅ Repeat, shuffle, and transport status on Now Playing now use larger dedicated glyphs and clearer labels instead of the older tiny mixed-state treatment.
- ✅ The WPS speaker row was cleaned up so mute/loud icons match properly and the old red warning-stripe overlay is gone.
- ✅ Exiting `Files` from `Extras` now returns cleanly to `Extras` instead of forcing a jump back out of the submenu.

### Also in this release
- Apple2026 Quick Settings now ships with a fixed Apple2026 runtime map: top/bottom brightness, left shuffle, right repeat, and wheel volume.
- The WPS/mini-player asset set was refreshed with rounded hero-art trim, a rebuilt mini-player background, larger transport strips, and new repeat/shuffle/status assets.
- PictureFlow tracklist return was reworked so returning from WPS can re-open on the current song once without pinning the selection there after you start scrolling.
- Build and packaging scripts now explicitly stage the live Apple2026 theme payload, `Apple2026.cfg`, version stamp, and plugin-package verification instead of relying on stale installed files.

---

**Not yet implemented and Known Issues**
- ❌ The new Quick Settings surface is in place, but it still needs more live simulator/hardware validation for redraw and interaction edge cases.
- ❌ The full WPS back-navigation matrix is improved in code, but it is not fully closed yet across Music, Files, Database, Playlists, and Cover Flow.
- ❌ The old custom Apple2026 notification-style lockscreen is not shipping; hold currently uses the simplified/native path and still needs more validation.
- ❌ Some of the newest WPS polish still needs runtime eyeballing, especially right-side status spacing, lossless badge placement, and mini-player shadow balance.

> ⚠️ **Experimental beta.** Back up your `.rockbox` folder before installing. For cleanest results, delete the existing folder and replace it from the release zip.
>

🔋 Modded iPods: If you're running an upgraded battery or iFlash/SSD mod, make sure to set your battery capacity and storage type in Settings → System → Battery and Settings → System → Disk so battery estimates and power management work correctly.

## Intentionally Left Out

- Anything from `Apple2026QuickSettingsPlan.md` beyond what is already backed by live source diffs.
- Scratch/tmp files and visual experiments (`scratch_*`, `tmp_*`, empty `backdrops/ReleaseNotes.MD`).
- Any claim that the full WPS return matrix, full lockscreen fix, or final Quick Settings stability is done.

## Still Too Incomplete

- Quick Settings live runtime validation.
- Hold/lock transition polish.
- End-to-end WPS return-path verification.
- Final live verification of the new WPS/LRC short-`Select` flow and the newest WPS visual spacing.
