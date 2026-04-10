# MASTER.md
## RockPod Fresh-Restart Project Charter
### Apple2026 Program Master Document
### Version 4 — Fresh-Run Autonomous Project Skeleton

---

## 0. Purpose of this document

This file is the **primary source of truth** for the fresh restart of this RockPod-based iPod Classic project.

The goal is that future agents should need as little repeated prompting as possible.

The intended workflow is simple:

1. Read `MASTER.md`
2. Read any referenced companion documents
3. Read `AGENTS.md` if present
4. Continue the current wave of work
5. Build and validate after major passes
6. Use the simulator and screenshots to confirm UI/UX progress
7. Keep updating the project docs as the work evolves

This document is meant to make the project **autonomous, coherent, and stable**.

The user should be able to point an agent to this file and say:

> Continue.

And the agent should understand:
- the product vision
- the source-of-truth hierarchy
- the technical setup
- the design lineage
- the implementation order
- the branch boundaries
- the validation requirements
- the “do not break this again” rules

This project is intentionally ambitious.
It is both:
- a **UI/UX redesign**
- and a long-term **software architecture modernization**

But those efforts must happen in the correct order.

---

## 1. Project overview

This project exists to transform Rockbox on iPod Classic / iPod 7th generation hardware into something that feels:

- native
- premium
- Apple-like
- music-first
- polished
- coherent
- calm
- fast
- intentional
- visually beautiful
- structurally sound
- maintainable enough for long multi-agent work

The end goal is not “a good theme.”
The end goal is not “a fast plugin.”
The end goal is not “Rockbox but prettier.”

The end goal is:

> A fully revitalized iPod Classic operating experience that feels like Apple might have rebuilt the iPod in a modern era, while preserving the wheel, the object-like simplicity, and the music-first soul.

This new final shell / theme system is now classified as:

# **Apple2026**

That is the final classification name for the custom themeing direction in this fresh run.

Important:
- `Interpod V2` is already taken and should not be reused as the flagship identity
- `Apple2026` is the final classification for the custom flagship direction going forward

However:

`Apple2026` is **not** meant to abandon Interpod.
It is meant to emerge from the best of Interpod, the best of Apple Music reference material, the best of stock iPod clarity, and the strongest pieces of other theme references.

---

## 2. Critical reset philosophy

The previous run became unstable because too many things were changing at once.

The major failures of the previous run included:
- UI and performance changes being mixed together
- theme path confusion
- fallback UI being edited instead of the intended theme path
- Cover Flow architecture experimentation happening while the shell was still in flux
- design decisions drifting away from the true source references
- typography and icon systems not being locked early enough
- agents making real progress in one area while accidentally regressing another

This new run must not repeat those mistakes.

That means:

### Non-negotiable reset rules
- Build from a fresh copy of RockPod
- Build from fresh original copies of the base themes used for reference
- Lock design and shell intent before doing architectural performance work
- Treat Cover Flow optimization as a **late-stage branch**, not a first-branch task
- Validate major UI changes in the simulator using screenshots
- Keep docs concise but authoritative
- Separate “hard instructions” from “personal reminders”
- Always compare back to the true design sources
- Never assume memory is good enough when Figma and Apple documentation exist

---

## 3. Source of truth hierarchy

This project must have a very clear source-of-truth hierarchy.

## 3.1 Primary source of truth — user-created Figma files

The **largest and strongest source of truth** for the visual and layout direction is the user’s personally created Figma file(s).

These are the most important design references in the entire project.



### Apple Music Library UI Figma
User-designed personally by the project owner:
https://www.figma.com/design/JyDHVsT9bqCPjbGEfyUD8d/Apple-Music-UI?node-id=1-4008&t=ETI4SrIbOMkfYL3L-4

### Apple Music album list UI mockup
User-designed personally by the project owner:
https://www.figma.com/design/JyDHVsT9bqCPjbGEfyUD8d/Apple-Music-UI?node-id=1-475&t=GJ78MMn5On07GPYk-4

### Apple Music album page mockup
User-designed personally by the project owner:
https://www.figma.com/design/JyDHVsT9bqCPjbGEfyUD8d/Apple-Music-UI?node-id=1-5998&t=GJ78MMn5On07GPYk-4

These are not casual inspiration.
These are not optional references.
These are the **most important visual standards** for the project.

### Local Figma exports
In addition to the live Figma links, the 3 core Figma reference files are also exported locally for convenience and stored in:

`Imported Icons/Figma File as SVG.svg`

These local SVG exports are reference materials for implementation and comparison.

Important:
- the live Figma files remain the strongest visual source of truth, but if this is easier to pull from then use the SVG
- if there is any mismatch between local exported SVG references and the live Figma design, prefer the live Figma
- use the local exports for quick inspection, asset tracing, and implementation support
- use the live Figma for exact spacing, hierarchy, layout, and design comparisons

The agent must:
- repeatedly return to these Figma files
- use them to compare hierarchy, spacing, typography, row rhythm, icon placement, divider behavior, mini-player treatment, and overall shell composition
- use them throughout the project, not just at the beginning
- treat them as the strongest available visual truth

If there is ever a disagreement between memory and the Figma:
- trust the Figma

If there is ever drift away from the intended Apple-native design:
- go back to the Figma

The audit and design-principles phase must be incredibly detailed and must keep returning to these references.

## 3.2 Secondary source of truth — official Apple design documentation

These official references are the second major design source of truth.

### Apple Music symbols
https://support.apple.com/guide/music/symbols-used-in-music-mus131245dbe/mac

### iPhone Music player controls symbols
https://support.apple.com/guide/iphone/use-the-music-player-controls-iph676daac9b/ios

### Apple HIG — Icons
https://developer.apple.com/design/human-interface-guidelines/icons

### Apple HIG — Typography
https://developer.apple.com/design/human-interface-guidelines/typography

### Apple UI Kit reference
https://www.sketch.com/s/bb57439f-19da-4c7a-bfd2-a196cf51f766

### Apple fonts
https://developer.apple.com/fonts/

### iOS / iPadOS 26 community reference Figma
https://www.figma.com/design/z4Tlzt8ZuTZvyIbC8medFr/iOS-and-iPadOS-26--Community-?node-id=0-2194&p=f&t=3GVjsSq0YqqdDsGj-0

These should be used to establish:
- icon rules
- symbol weights
- font hierarchy
- title sizing
- row spacing
- disclosure/chevron behavior
- list rhythm
- typography alignment
- state color logic
- overall Apple-native restraint

Important:
Do not use these to turn the iPod into a fake iPhone.
Use them to understand:
- Apple’s visual discipline
- Apple’s hierarchy
- Apple’s minimalism
- Apple’s rhythm
- Apple’s system coherence

## 3.3 Tertiary source of truth — Imported Reference Themes

A folder named:

# `Imported Reference Themes`

will be added to the fresh codebase.

This folder will contain additional themes that the agent can study.
These themes each have some strengths:
- stock OS feel
- Apple Music-inspired spacing
- icon ideas
- font ideas
- interesting shell choices
- better menu density
- better headers
- better mini-player ideas
- existing SF Pro experiments in some cases
- stronger asset choices in some cases

However:
none of them are the final answer.

The agent must review **all imported reference themes** for strengths, but always remember:

> **Original Interpod is still the strongest overall base theme.**

That is non-negotiable.

The job is not to replace Interpod.
The job is to:
- audit every imported reference theme
- identify what each one gets right
- extract the strongest pieces
- combine those pieces carefully
- keep Interpod as the base DNA
- evolve it into Apple2026

The agent must not:
- randomly merge themes together without rules
- turn the design into a patchwork
- lose Interpod’s strengths
- drift into a generic “theme pack” look

It must always:
- pick and choose the best from each
- keep the system coherent
- compare everything back to the Figma and Apple docs

## 3.4 Additional source assets

The fresh codebase will also include:

### `SF Pro/`
A folder containing the full Apple SF Pro font library that the user wants available for evaluation and conversion.

### `Sourced Icons/`
A folder containing the user’s sourced icon library.

### `sf-symbols-master/`
A folder containing an open-source symbols library that should now be treated as a **primary icon source** for the project.

This is extremely important.

The agent should treat `sf-symbols-master/` as one of the main implementation asset sources for iconography work.

This means:
- when the shell needs a symbol, menu icon, playback icon, state glyph, chevron, utility icon, or navigation icon, the agent should first search `sf-symbols-master/`
- it should identify the closest matching symbol type
- then optimize, simplify, scale, normalize, and adapt that symbol into the runtime icon system
- it should create the cleanest rendering version practical for Rockbox
- it should generate coherent color/state variants where needed

The expectation is NOT to dump raw symbols directly into the theme.
The expectation is:
- search intelligently
- choose carefully
- normalize consistently
- render cleanly
- convert into the cleanest bitmap/vector-derived asset possible for the iPod display

This folder should be considered a major source for:
- menu icons
- playback icons
- state icons
- mini-player controls
- chevrons/disclosure arrows
- utility/settings symbols
- library/music symbols
- queue / playlist symbols
- other Apple-like glyph needs

The icon family still needs to remain coherent.
That means the agent must:
- audit symbol weights
- audit fill/stroke feel
- audit optical scale
- audit padding
- audit red/grey state behavior
- generate a unified runtime family from the best chosen symbols

Do not use random mixed symbols without cleanup.


These are meant to give the agent:
- better font options
- better icon options
- more direct visual ingredients

The agent is expected to:
- audit them
- normalize them
- scale them
- optimize them
- choose only the best
- build coherent runtime assets from them

But again:
selection must always be guided by:
1. Figma
2. Apple design docs
3. Interpod base
4. other reference themes
5. sourced icons/fonts

That is the order.

---

## 4. Personal, educational, and non-commercial note

This project is for:
- personal use
- personal learning
- personal design and software exploration
- personal educational experimentation

This project is **not** intended to:
- be sold
- be distributed as a commercial Apple imitation
- infringe on Apple trademarks in any commercial sense
- become a public trademark-confusing product

The intent is private, educational, and experimental.

Agents working on this project should treat Apple resources as:
- design references
- system-pattern references
- visual standard references
- educational references

not as assets to be redistributed carelessly.

Where possible:
- convert or derive implementation-safe equivalents
- keep the runtime shell owned by this project
- avoid shipping raw third-party design-resource exports unless clearly acceptable

---

## 5. What the fresh run is trying to achieve

The next run must be better in the following ways:

### 5.1 Stronger planning
Documentation first, but not markdown bloat.

The project should be guided by:
- clear steps
- clear waves
- strict branch boundaries
- few but highly important documents
- better project management discipline

### 5.2 Better source grounding
The agent should constantly compare:
- current implementation
- original Interpod
- imported reference themes
- Apple Figma
- Apple HIG
- stock iPod behavior

### 5.3 Perfect typography
Typography should feel as close as possible to Apple spec:
- hierarchy
- weights
- sizes
- spacing
- anti-aliasing
- title scale
- menu rhythm
- secondary text tone
- truncation behavior

“Not a pixel off” is the aspiration.

### 5.4 Better icon system
Use the best of:
- original Interpod
- imported reference themes
- sourced icons
- Apple symbols references

But always normalize and simplify them into one coherent family.

### 5.5 Stable UI/UX-first primary branch
Do **not** touch performance in the primary branch.
The first branch is for:
- shell
- theme
- typography
- icons
- spacing
- menu UX
- file-system-first music browsing experiments
- settings organization
- native-feeling loading states
- mini-player
- header behavior

### 5.6 Better UX flow
The project must feel faster and easier, not just look nicer.

That means:
- predictable button behavior
- good browse continuity
- clear Now Playing access
- easy return paths
- less user confusion
- less dead-end navigation

### 5.7 Architecture later, not first
Performance optimization, Cover Flow optimization, and hardware-specific deep tuning happen later in separate branches.

This is critical.

---

## 6. Three core docs only

To avoid documentation bloat, the fresh branch should begin with only these core docs:

## 6.1 `MASTER.md`
This document.
The long-term project charter and source-of-truth hierarchy.

## 6.2 `DESIGN_SYSTEM.md`
The concise visual system authority.

Should include only:
- source hierarchy
- typography rules
- header rules
- row geometry
- icon rules
- divider rules
- chevron rules
- color rules
- mini-player rules
- loading-state rules
- asset ingestion notes
- exact references used

## 6.3 `WORK_LOG.md`
A compact running execution log.

Should include only:
- date/session
- branch
- what changed
- why
- files touched
- build/sim status
- screenshot validation status
- next task

Additional docs may be created if needed, but only when clearly useful.
Avoid the prior run’s doc sprawl.

---

## 7. AGENTS.md policy

The fresh project is allowed and encouraged to maintain an `AGENTS.md`.

The agent may:
- create it
- update it
- refine it
- align it with `MASTER.md`

Its role is to turn the project charter into actionable local operating rules.

It should include:
- branch boundaries
- build/sim requirements
- screenshot validation rule
- source-of-truth hierarchy
- “do not optimize Cover Flow here” rule
- “always compare to Figma” rule
- “Interpod is base” rule
- doc update rules
- the “continue” workflow expectations

`AGENTS.md` should be short, strict, and operational.
`MASTER.md` remains the detailed charter.

---

## 8. Environment setup must happen first

The project must begin by installing and validating all build dependencies before any major implementation.

The next agent should treat environment setup as the first real implementation wave.

**Concrete commands, scripts, artifacts, incremental flags, and troubleshooting:** use **`BUILD.md`** (single source of truth for everything build-related). This section (§8) states *what* must exist at charter level; `BUILD.md` states *how* to install and verify it.

### 8.1 Windows requirements
- Windows 10/11
- PowerShell
- Git for Windows
- MSYS2 at `C:\msys64` or equivalent
- enough disk space

### 8.2 Required packages
As captured from the prior run, install:

Core packages:
- bash
- make / gmake
- gcc / g++
- patch
- zip / unzip
- perl
- gawk
- bison
- flex
- autoconf
- automake
- libtool
- texinfo
- curl
- gmp
- python

Simulator packages:
- SDL2 runtime/tooling
- pkg-config / pkgconf if needed

Cross compiler:
- `arm-elf-eabi-*` or `arm-none-eabi-*`
- plus wrapper/shim support where needed

Optional but useful:
- 7zip
- ccache

### 8.3 Setup order
1. Open the correct MSYS2 shell
2. Update package database
3. Install required packages
4. Verify base tools on PATH
5. Verify ARM toolchain
6. Build simulator first
7. Build hardware targets
8. Validate artifacts

### 8.4 Build-first rule
Do not begin UI implementation until:
- simulator builds
- simulator runs
- hardware build succeeds
- package output is known-good

This is mandatory.

---

## 9. Simulator-first workflow

The simulator is first-class in the next run.

It is not optional.
It is not a late convenience.
It is part of the main validation loop.

### 9.1 Why simulator matters
The previous run suffered because too many visual and shell changes were judged blindly or mainly on-device.

The simulator helps with:
- theme path validation
- WPS/SBS/header validation
- fallback-vs-intended shell detection
- typography iteration
- icon iteration
- spacing checks
- loading-state UI checks
- screenshot-based comparison to Figma

### 9.2 Simulator requirements
After major UI/UX passes, the agent must:
- rebuild simulator if needed
- run the simulator
- verify that the intended theme path loads
- capture screenshots of key surfaces
- compare screenshots directly to source references
- log what matched and what did not

### 9.3 Required screenshot checkpoints
At minimum, after major visual passes:
- Home/root menu
- Music list
- Settings list
- mini-player / shell footer
- Now Playing
- loading state
- any album list or Apple Music-inspired list screen
- any new key shell surface

These screenshots must be used for direct design comparison.

### 9.4 Simulator comparison rule
For all major visual changes:
- compare against the user Figma first
- compare against Apple docs second
- compare against original Interpod third
- record mismatches in `WORK_LOG.md`

---

## 10. Theme lineage and naming

This project keeps the following lineage:

### 10.1 Original Interpod
The strongest overall base theme.

This remains the primary DNA.

### 10.2 Imported reference themes
Used as supporting studies only.
Each may contribute useful parts.

### 10.3 Prior “Interpod V2” idea
This should not become the final classification.
That name is already taken and should not be reused for the flagship theme identity.

### 10.4 Final classification
The flagship theme and shell direction for this fresh run is:

# **Apple2026**

But Apple2026 must still feel like:
- Interpod evolved
- not Interpod erased

---

## 11. Detailed Interpod lineage reminder

The earlier intended changes relative to stock Interpod were always relatively selective, such as:
- album art size changes
- metadata size changes
- track number / song count positioning
- selector bar color changes
- icon simplification
- cleanup of ugly grey backgrounds in header areas
- stronger native shell polish

That means the project should **not** casually drift into:
- a fully unrelated shell
- generic fallback Rockbox
- a random modern mobile theme
- heavy visual experimentation without lineage

Apple2026 should feel like:
- original Interpod’s confidence
- plus Apple Music’s discipline
- plus your sourced icon and font improvements
- plus more native shell cohesion

---

## 12. Detailed design goals

## 12.1 Overall shell goals
- white-first, calm shell
- large clear headers
- cleaner battery indicator
- elegant list rhythm
- thin inset dividers
- small right-side chevrons
- subtle grey selection treatment
- integrated mini-player
- native-feeling loading states
- stronger typography

## 12.2 Menu/list goals
- more breathing room
- larger visual confidence
- less dense and computer-like
- exact spacing harmony with Apple Music references where practical
- coherent icon placement
- correct text offsets
- stronger shell rhythm

## 12.3 Typography goals
- evaluate the full SF Pro library from `SF Pro/`
- choose the sharpest realistic Rockbox-compatible font strategy
- define exact weights and sizes
- use anti-aliased conversions where possible
- make typography the heart of the design system
- no improvisation after the system is chosen

## 12.4 Icon goals
- use original Interpod strengths
- use the best imported reference theme icon ideas
- use the best of `Sourced Icons/`
- use `sf-symbols-master/` as a **primary icon source**
- normalize sizes, weights, fills, and spacing
- build red and grey state variants where needed
- support alternate color schemes where useful, especially:
  - Apple Music-style pink/red active states
  - neutral grey inactive/secondary states
- optimize every chosen symbol into the cleanest rendering version practical for Rockbox
- no cartoonish, emoji-like, or Windows-like icons
- no raw unoptimized symbol dumps

## 12.5 Loading-state goals
- loading states must feel native
- no ugly Rockbox box-and-border feeling
- calm typography
- consistent shell
- if animation is feasible and tasteful, consider it
- otherwise keep it simple and elegant

## 12.6 Mini-player / What’s Playing goals
- integrated into shell
- more Apple Music-like in composition
- stronger balance
- clear text hierarchy
- subtle play/pause state
- visually tied to the rest of the shell

---

## 13. Audit phase must be extremely detailed

The agent’s first real design-system wave must be a serious audit.

It must review:
- original Interpod
- all imported reference themes in `Imported Reference Themes/`
- all Apple documentation links
- all three user-created Figma references
- the `SF Pro/` folder
- the `Sourced Icons/` folder
- the `sf-symbols-master/` folder

It must then define:
- what to preserve from Interpod
- what to borrow from each imported reference theme
- what to reject from each imported reference theme
- what the Apple docs are demanding
- what the Figma defines as the most important layout truth
- how the Apple2026 system will be formed

This audit must take its time.
The agent should not rush to implementation.

---


## 13A. `sf-symbols-master/` icon-source protocol

This project now has an additional primary icon source:

# `sf-symbols-master/`

This library should be treated as one of the best starting points for Apple-like iconography work.

The agent must use it deliberately.

### 13A.1 Search behavior
When a symbol is needed, the agent should:
1. identify the semantic need
   - Music
   - Albums
   - Songs
   - Artists
   - Playlists
   - Cover Flow
   - Settings
   - System
   - Files
   - Queue
   - Search
   - Play
   - Pause
   - Next / Previous
   - Chevron / Disclosure
   - Battery or utility states
2. search `sf-symbols-master/` for the closest candidate symbols
3. compare multiple candidates rather than taking the first match
4. choose the symbol that best matches Apple-native tone and the intended shell hierarchy

### 13A.2 Optimization behavior
After selecting candidate symbols, the agent must:
- normalize optical scale
- normalize padding
- normalize visual weight
- simplify any shape that renders poorly at iPod scale
- test legibility in the simulator
- remove unnecessary detail that will muddy at low resolution
- convert them into the cleanest runtime-friendly form practical for Rockbox

### 13A.3 Color/state behavior
The agent should prepare icon/state families where needed, including:
- neutral grey variants for inactive/secondary/menu-depth states
- Apple Music-style pink/red variants for active/emphasized music states
- any additional subtle state variants only if truly useful and visually coherent

The color discipline should remain restrained:
- pink/red is an accent, not a blanket treatment
- grey is for passive/disclosure/secondary state
- black/dark can be used for primary symbol clarity where the shell calls for it

### 13A.4 Rendering rule
The goal is not just “use symbols.”
The goal is:
- make them render beautifully on Rockbox/iPod hardware
- make them feel like a single family
- make them look as crisp and native as possible
- avoid muddy, over-detailed, or mismatched symbol behavior

### 13A.5 Audit requirement
The icon audit phase must explicitly compare:
- original Interpod icons
- imported theme icons
- `Sourced Icons/`
- `sf-symbols-master/`
- Apple symbol references
- final Apple2026 runtime icons

And determine:
- which symbols are best for each use
- which ones scale well
- which ones need simplification
- which ones should get red/grey state variants
- which ones should be rejected

## 14. “Imported Reference Themes” protocol

The folder `Imported Reference Themes/` exists to make this next run smarter.

The agent must:
- inspect every theme inside it
- identify strengths
- identify weaknesses
- identify what feels Apple-like
- identify what feels stock-like
- identify where each theme has better icons, headers, spacing, or mini-player ideas
- note any included SF Pro or other premium font experiments
- note any icon system worth extracting

Then create a comparison section in `DESIGN_SYSTEM.md` summarizing:
- Theme A strengths
- Theme B strengths
- Theme C strengths
- etc.

But always conclude:
> Original Interpod is still the best overall base.

No imported theme is allowed to hijack the visual identity.

---

## 15. Apple design compliance rule

Every major design pass must compare directly back to:
1. the user’s Figma files
2. Apple docs
3. original Interpod
4. imported reference themes

The agent must never rely on vague memory.

It must compare:
- font hierarchy
- row height
- text inset
- icon inset
- icon weight
- divider inset
- header spacing
- mini-player spacing
- battery size
- chevron placement
- loading-state geometry

If it cannot prove a choice against those sources, it should not lock it in.

---

## 16. Primary branch boundaries

The primary branch is strictly:

# UI / UX / Design System / Navigation

It must not include:
- Cover Flow performance work
- deep caching work
- RAM work
- prefetch work
- deep database optimization
- architecture-level performance tuning

The primary branch is allowed to include:
- theme shell work
- WPS/SBS visual work
- loading UI work
- font system work
- icon system work
- menu structure
- file-browser UX experiments
- shell flow and button behavior
- settings reorganization
- user flow improvements
- database-reduction strategy planning (not Cover Flow internals)

This separation is mandatory.

---

## 17. UX flow goals

The project is not just a theme project.

It is also a UX project.

The agent must audit:
- stock iPod OS UX
- Rockbox UX
- intended target UX

Important known user preferences:
- pressing **down** should reliably get to What’s Playing / Now Playing
- pressing **up** should feel predictable and help the user get back to the right place
- browsing continuity matters
- getting lost in lists or menus is bad
- tracklist return paths matter
- queue and Now Playing context should be easy to recover

The product should feel:
- fast in button logic
- easy to mentally model
- easy to recover from mistakes
- music-first
- not technical

---

## 18. File-system-first music browsing vision

This is one of the most important long-term architecture ideas from the planning discussion.

The user’s library is already organized in a MusicBrainz Picard-style folder system:

`Music / Album Artist / Album / Songs`

The idea is to reduce reliance on Rockbox’s database for normal browsing and let the filesystem become the primary music browser.

Potential approach:
- Main menu → Artists → directly browse album artist folders
- Main menu → Albums → directly browse album folders at depth 2
- Main menu → Songs → browse songs at depth 3
- Database remains available separately
- Cover Flow can still use the database as needed
- Primary music finding experience becomes smoother and less HDD-spin-heavy

This could be a major future win.

Important:
This should be treated as a dedicated future architecture branch, not mixed into the first visual-shell wave.

But it should be planned from the start so the shell and menu structure support it.

The agent should document:
- feasibility
- likely implementation options
- where it belongs in the roadmap
- what parts of the UI should anticipate it

---

## 19. Settings strategy

Settings should be improved, but not over-pruned early.

The user wants:
- fewer unnecessary settings in the main path
- more user-friendly ordering
- important settings higher up
- theme settings available during active development
- EQ / Equalizer surfaced prominently at top level
- a future ranking/priority pass on all settings

The fresh run should therefore:
- keep settings flexible during development
- not over-lock them down too early
- plan a dedicated settings-curation wave later

---

## 20. Long-term features not for immediate implementation

These are important future goals, but not first-wave tasks.

### 20.1 Stock-OS-style album screen
A future screen inspired by stock iPod:
- album covers in boxes on the left side
- stronger album browsing view

This should be a later project, not an initial branch.

### 20.2 Full software rebuild for personal hardware
Long-term the user wants:
- a software rebuild optimized specifically for iPod 6.5/7th gen
- SSD/iFlash storage
- upgraded battery
- absolute best performance on personal hardware

This is a late-stage optimization wave.
Do not start here.

---

## 21. Wave structure for the fresh run

## Wave 0 — Clean reset and environment proof
- fresh RockPod
- fresh original Interpod
- imported reference themes placed in `Imported Reference Themes/`
- `SF Pro/` added
- `Sourced Icons/` added
- build dependencies installed
- simulator built and running
- hardware build proven
- docs initialized

## Wave 1 — Source audit
- audit all Figma references
- audit Apple docs
- audit original Interpod
- audit imported reference themes
- audit SF Pro fonts
- audit sourced icons
- write comparison notes

## Wave 2 — Design system lock
- choose typography
- choose icon family direction
- define row geometry
- define headers
- define mini-player
- define loading UI
- define selector/dividers/chevrons
- produce `DESIGN_SYSTEM.md`

## Wave 3 — Apple2026 shell implementation
- build Apple2026 as the flagship theme path
- preserve Interpod DNA
- implement header/list/footer/loading/icon system
- validate in simulator
- compare screenshots to Figma

## Wave 4 — UX flow pass
- down press / Now Playing behavior
- up press / return predictability
- navigation continuity
- playlist/queue access
- shell behavior consistency

## Wave 5 — Music Library IA / menu simplification
- Library-first main menu: **Music** (`/Music`) only at root (no separate Storage row); **Database** lower in the list
- No flat virtual Albums/Songs hubs; no indexing/caching work in this wave
- Picard folder hierarchy remains the real browse backbone; deeper IA in Wave 6 if needed

## Wave 6 — Settings reorganization
- surface EQ
- reorder settings
- keep development-useful controls available
- clean up top-level settings structure

## Wave 7 — Cover Flow restore baseline
- restore to known-good RockPod functional baseline
- no optimization yet

## Wave 8 — Cover Flow UI polish
- visual integration only

## Wave 9 — Cover Flow performance branch
- absolute last
- optimization only after shell is stable
- separate branch

## Wave 10 — hardware-specific optimization
- SSD/iFlash
- battery-aware behavior
- personal-device specialization

---

## 22. Cover Flow rule — absolutely last

This must be hammered in:

**Cover Flow optimization is absolutely last.**

Reason:
- it caused major regressions before
- it is too easy to destabilize the project while the shell is still evolving
- UI/UX branch must remain stable
- Cover Flow needs its own branch later

Allowed earlier:
- restoring baseline functionality
- visual integration
- ensuring shell consistency

Not allowed earlier:
- new optimization architecture
- caching experiments
- RAM experiments
- preload redesign
- selection-path performance redesign

---

## 23. Build and validation after major passes

This is mandatory.

After every major pass the agent must:
1. build
2. run simulator if UI-related
3. take screenshots if UI-related
4. check package output if build-related
5. log results in `WORK_LOG.md`

### 23.1 UI/UX pass validation
After major UI/UX work:
- simulator must run
- screenshots must be captured
- screenshots compared to Figma and Apple docs
- obvious mismatches documented

### 23.2 Navigation/UX pass validation
After navigation logic work:
- simulator or target run should confirm flow
- log expected routes and actual routes

### 23.3 Build artifacts
After build system changes:
- hardware artifact presence must be checked
- simulator artifact presence must be checked

---

## 24. Screenshot audit protocol

For UI/UX waves, screenshots are not optional.

The agent should maintain a stable screenshot checklist:
- Home
- Music list
- Settings
- mini-player
- Now Playing
- loading state
- any album list view
- any shell-chrome comparison surface

And compare them against:
- Figma Library UI
- Figma album list UI
- Figma album page UI
- Apple docs as needed

This should be explicitly logged.

---

## 25. Personal design reminders preserved from prior run

These are reminders, not hard rules, but they matter.

### 25.1 Original Interpod fit
You consistently liked original Interpod the most overall.

### 25.2 Big album art
You like:
- larger album art
- slightly smaller text around it
- strong balance
- more premium Now Playing composition

### 25.3 Native-feeling loading states
You want loading states to feel:
- native
- calm
- shell-consistent
- not like generic Rockbox dialog boxes

### 25.4 Better icons
You want:
- clean Apple-like symbols
- no Windows-like icons
- no emoji/cartoon style
- extracted best-of icon logic from references + sourced icons

### 25.5 Strong typography
You want perfect typography.
This must stay central.

---

## 26. What to avoid from previous run

The fresh run should avoid:
- editing fallback theme paths by accident
- touching performance in the UI branch
- broad speculative Cover Flow changes
- mixed documentation sprawl
- random icon substitutions
- font improvisation after lock
- making changes without simulator validation
- drifting away from the Figma
- layering fixes on a broken branch instead of resetting cleanly

---

## 27. Immediate instructions for a new autonomous agent

If a new agent starts with only this doc, it should do the following:

1. Read `MASTER.md`
2. Create or update `AGENTS.md` based on it
3. Create `DESIGN_SYSTEM.md`
4. Create `WORK_LOG.md`
5. Verify build environment
6. Build simulator
7. Build hardware
8. Confirm a clean baseline
9. Audit all source references:
   - 3 user Figma files
   - Apple docs
   - original Interpod
   - Imported Reference Themes
   - `SF Pro/`
   - `Sourced Icons/`
   - `sf-symbols-master/`
10. Produce a design-system comparison summary
11. Begin Wave 2 (design system lock)
12. Continue from there

---

## 28. Final autonomous project rule

The entire point of this file is to make future work autonomous.

That means future agents should be able to:
- read this
- inspect the referenced docs and assets
- infer the correct next wave
- continue without needing new prompts every time

The user should only need to say:
> Continue.

The project should still move forward coherently.

If a conflict arises, use this order:
1. Figma
2. Apple docs
3. MASTER.md
4. DESIGN_SYSTEM.md
5. AGENTS.md
6. original Interpod
7. imported theme studies
8. current implementation

---

## 29. Final summary

This project should now proceed as:

- a clean restart
- grounded in real design sources
- with strict branch separation
- with simulator-first validation
- with typography and icon systems locked early
- with Interpod preserved as the true base
- with Apple2026 as the final classification
- with Cover Flow optimization saved for last
- with a much stronger autonomous operating structure than before

That is the skeleton for the next run.

This file is meant to be good enough that the project can keep going for a long time with very little additional prompting.
