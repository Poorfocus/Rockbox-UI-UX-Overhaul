# AGENTS.md

## Mission
- `MASTER.md` is the primary source of truth.
- Flagship classification: `Apple2026`.
- Visual/base DNA: original `Interpod`.
- Continue autonomously wave-by-wave unless a true blocker requires user input.

## Source-Of-Truth Order
1. User Figma file (`Apple-Music-UI` nodes: `1:4008`, `1:475`, `1:5998`)
2. Official Apple references listed in `MASTER.md` (Music symbols, iPhone controls, HIG icons/typography, fonts)
3. `Imported Reference Themes/`
4. Local assets:
   - `Apple Fonts/`
   - `Sourced Icons/`
   - `Sourced Icons/sf-symbols-master/`
   - `Sample Music Folder with Library Structure/`

## Branch Boundaries
- This branch is UI/UX/design-system/navigation only.
- Do **not** do Cover Flow optimization here.
- Do **not** do deep performance architecture/caching/prefetch RAM tuning here.
- Cover Flow optimization is last and belongs to a dedicated later branch.

## Build + Validation Workflow

**All build commands, env vars, PATH rules, WSL fallback, and troubleshooting are in `BUILD.md` only.** Do not duplicate them here.

Operational expectations:
- Use PowerShell wrappers / UCRT64 as described in `BUILD.md`; do not validate from plain `MSYS_NT` shells.
- Treat non-zero exit, `make: ***`, and explicit compiler/linker/package fatal errors as real blockers.
- Treat circular dependency warnings and CRLF/git warning flood as noise unless they are the terminating error.

**Validation order** (after major UI work):
1. Clean or incremental build (`BUILD.md`)
2. Simulator launch
3. Screenshots after major UI/UX pass
4. Direct comparison vs Figma + Apple refs
5. Log mismatches + next fixes in `WORK_LOG.md`

## Mandatory Documentation Maintenance
- Update `WORK_LOG.md` continuously (verified vs assumed must be explicit).
- Update `DESIGN_SYSTEM.md` whenever visual system decisions change.
- Update `AGENTS.md` when operating rules need clarification.

## Autonomous Continuation Rules
- Identify current wave from `MASTER.md` and complete it fully.
- Move directly to the next wave without waiting for prompts.
- Build/sim/screenshot checkpoints are mandatory after major UI/UX passes.
- Only pause for:
  - missing required sources/assets
  - build/toolchain failure not solvable from repo context
  - unresolved strategic conflict not answered by project docs
