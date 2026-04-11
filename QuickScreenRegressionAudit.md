# QuickScreenRegressionAudit.md

## Symptom

Apple2026 Quick Screen regressed to a white, effectively unreadable surface:

- white body
- no dependable visible text
- unstable redraw behavior tied to shell state

## Exact failure mode

The current Apple2026 quickscreen body was rendered by core code in
`apps/gui/quickscreen.c`, but its parent viewport still depended on SBS info
viewport routing.

That routing was too late and too stateful for quickscreen entry:

1. `gui_syncquickscreen_run()` asked `viewportmanager_theme_enable()` for the
   themed parent viewport.
2. Only after that did it run `skin_update()` for the SBS.
3. The SBS quickscreen branch then switched the info viewport to
   `qs_content`.
4. The native quickscreen body kept drawing into the stale viewport captured
   before the SBS switch.

At the same time, the SBS still owned a white quickscreen shell lane. When the
native body draw missed or used stale geometry, the visible result was a clean
white panel with no reliable text content.

## Why the text became invisible

This was not primarily a black-on-white token bug inside the native Apple2026
renderer. The renderer already sets readable colors in code.

The real problem was that the body draw was coupled to a mutable SBS-selected
viewport. If that viewport was stale, hidden, or simply not the quickscreen
lane yet, the SBS white shell remained visible while the body text landed in
the wrong place or got cleared by the later shell refresh.

## Broken layer / system

Broken contract:

- SBS shell viewport routing
- native quickscreen body geometry

Stable contract after fix:

- SBS owns shell chrome only:
  - header title
  - header indicators
  - bottom-bar suppression
- core quickscreen owns body layout directly

## What was simplified

The Apple2026 quickscreen body no longer relies on SBS info viewport selection
for its visible content area.

Instead it now uses a deterministic Apple2026 body frame in code:

- fullscreen base
- fixed `y = 30`
- fixed body height below the compact header
- explicit Apple2026 font and color setup

This keeps the shell/header behavior while removing the brittle viewport
handoff that caused the blank white failure.

## 2026-04-11 fallback rebase

The first Apple2026 quickscreen rewrite still left too much custom behavior in
`apps/gui/quickscreen.c` and `wps/Apple2026.sbs`:

- custom Apple2026 quickscreen-only body layout code stayed active
- the SBS still owned a dedicated quickscreen body viewport (`qs_content`)
- the resulting path was still harder to trust than the original Interpod
  baseline

This pass intentionally rebased Apple2026 quickscreen onto the more stable
Interpod-style contract:

- Apple2026 keeps a fixed light parent viewport below the header in core code
- body layout/drawing falls back to Rockbox native quickscreen behavior
- the SBS no longer routes quickscreen into a dedicated body viewport
- the SBS only suppresses shell chrome that should stay out of the way

That means the active quickscreen baseline is now deliberately conservative:
readable native body first, Apple2026 restyling later.

## Anti-regression rules

1. Do not make Apple2026 quickscreen body visibility depend on `%VI(...)`
   selection timing.
2. SBS may style quickscreen shell chrome, but body geometry must remain
   deterministic in core code.
3. If quickscreen becomes white again, inspect the quickscreen parent viewport
   path before touching text colors.
4. Do not reintroduce `%Q*` body overlays, `qs_content`, or hidden-viewport
   suppression for Apple2026 quickscreen.
5. If Apple2026 gets a richer quickscreen later, build it on top of the native
   quickscreen draw path instead of replacing the body renderer again.
