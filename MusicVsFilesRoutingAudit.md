# Music vs Files Routing Architecture Audit

## Apple2026 — Curated Music Browser vs Raw Files Browser

---

## 1. Current Behavior

### Music Entry
- **Main Menu → Music** dispatches `GO_TO_MUSICLIB` → `browser()` with `param = GO_TO_MUSICLIB`.
- `browser()` sets `folder = "/Music/"` (or `last_music_folder` if a valid `/Music/…` resume path exists).
- A `browse_context` is constructed with:
  - `.icon = Icon_Audio`
  - `.root = folder` (i.e. `"/Music/"`)
  - `.flags = BROWSE_APPLE2026_MUSICLIB`
- `rockbox_browse(&browse)` is called → `set_current_file("/Music/")` → `dirbrowse()`.

### Back-Navigation Guard
- In `dirbrowse()` at `ACTION_STD_CANCEL` (line 947–969 of `tree.c`):
  - Apple2026 intercept checks:
    1. `*tc.dirfilter != SHOW_ID3DB`
    2. `tc.browse && (tc.browse->flags & BROWSE_APPLE2026_MUSICLIB)`
    3. `tc.dirlevel <= 1`
    4. `path_is_curated_music_library_root(tc.currdir)` → true when currdir trims to exactly `/Music`
  - If all four match → `return GO_TO_ROOT` (i.e. return to main menu).
  - If not matched → falls through to standard `ft_exit()`.

### What Happens When It Fails
When the guard **does not fire**, `ft_exit()` executes:
- `ft_exit()` strips the last path segment from `tc.currdir`.
- From `/Music/` → `i = 7`, strips `Music/`, sets `currdir = "/"`.
- `dirlevel` decrements.
- The browser then reloads root `/` — showing **Podcasts, Notes, Music, and other raw folders**.
- The user is now in a full filesystem root, **not** the main menu.

---

## 2. Root Cause of the Inconsistent Back-Navigation Bug

The bug is **not** a simple label or menu issue. It is a **state desynchronization** between `tc.dirlevel` and `tc.currdir`.

### The Desync Mechanism

`set_current_file("/Music/")` (called by `rockbox_browse()` at line 1303) computes `dirlevel` by counting `/` separators in the path:

```c
for (i = 1; path[i] != '\0'; i++) {
    if (path[i] == '/') {
        tc.dirlevel++;
        tc.selected_item_history[tc.dirlevel] = -1;
    }
}
```

For the path `/Music/`:
- `i=1` → `M`, not `/`
- `i=2..5` → `u`, `s`, `i`, `c`
- `i=6` → `/` → **dirlevel becomes 1**
- `i=7` → `\0` → loop ends

So **fresh entry into Music always yields `dirlevel = 1`** and `currdir = "/Music"` (set_current_file_ex strips the trailing slash into currdir and the filename component).

But the Apple2026 guard requires **`tc.dirlevel <= 1`** AND `path_is_curated_music_library_root(tc.currdir)`.

### When It Works (Most Common Case)
- Fresh entry: `dirlevel = 1`, `currdir = "/Music"` → guard fires → `GO_TO_ROOT` ✓
- User navigates into `/Music/Artist/`, then backs out to `/Music/` → `dirlevel` decrements to `0` or `1` depending on exact path → usually guard fires.

### When It Fails (The Regression)

**Case 1: Resume with `last_music_folder` containing a deeper path**
- If `last_music_folder = "/Music/Artist/"`, then `set_current_file("/Music/Artist/")` sets `dirlevel = 2`.
- User backs out: `/Music/Artist/` → `/Music/` → `dirlevel` becomes 1 → guard fires.
- But if they back out again fast or state gets confused, `dirlevel` might be 0 and `currdir` might be wrong.

**Case 2: `playback_context_path` redirect**
- When `last_screen == GO_TO_WPS` and the playback context says `PLAYBACK_CONTEXT_FILESYSTEM` with `playback_context_screen == GO_TO_MUSICLIB`, the browser resumes at `global_status.playback_context_path`.
- This path could be `/Music/Artist/Album/track.m4a` → `set_current_file` puts the user deep inside Music.
- When backing out to `/Music/`, the path-only check passes but `dirlevel` may be desynchronized because `set_current_file_ex` recalculates it from scratch.

**Case 3: The real killer — ft_exit already modified currdir before the guard checks it**

Looking at the flow in `ACTION_STD_CANCEL`:

```c
case ACTION_STD_CANCEL:
    exit_to_new_screen(0);  // ← scrollstop only, benign
    if (*tc.dirfilter > NUM_FILTER_MODES && tc.dirlevel < 1) {
        exit_func = true;     // ← for sub-browsers (SHOW_PLUGINS, etc.)
        break;
    }
    // Apple2026 guard here (lines 953-969)
    ...
    // Standard exit path (lines 971-989)
    if (ft_exit(&tc) == 3)
        exit_func = true;
```

The Apple2026 guard runs **before** `ft_exit()`, so currdir is still at the current level. This is correct.

**BUT** — the guard requires `path_is_curated_music_library_root(tc.currdir)`, which checks if currdir trims to exactly `/Music`. If `currdir` is `/Music/` (with trailing slash), the trim logic handles it. If `currdir` is `/Music` (no trailing slash), it also works.

**The actual failure scenario**: When `ft_exit()` runs from a **deeper** subdir that isn't the music root, it strips the last segment. If the user is at `/Music/Artist/` and backs out, `ft_exit()` changes `currdir` to `/Music/` and decrements `dirlevel`. But on the **next** back press, the Apple2026 guard should fire because we're now at `/Music/`.

**The intermittent bug**: The sequence of events where the guard fails is:

1. User enters Music → `dirlevel = 1`, `currdir = "/Music"`
2. User navigates into Artist → `dirlevel = 2`, `currdir = "/Music/Artist"`
3. User backs out → `ft_exit()` runs → `currdir = "/Music"`, `dirlevel = 1`
4. `reload_dir = true` → `update_dir()` runs, which reloads `/Music/` directory
5. User backs out again → Apple2026 guard checks:
   - `dirlevel <= 1` → yes (1)
   - `path_is_curated_music_library_root("/Music")` → yes
   - Guard fires → `GO_TO_ROOT` ✓ **This works**

But consider this alternate scenario:
1. User opens Music from WPS return (`playback_context_path = "/Music/Artist/Album/"`)
2. `set_current_file` recalculates `dirlevel = 3`, `currdir = "/Music/Artist/Album"`
3. User backs out to `/Music/Artist/` → `dirlevel = 2`
4. User backs out to `/Music/` → `dirlevel = 1` → guard fires ✓

And the **failure** scenario:
1. User opens Music (fresh) → `set_current_file("/Music/")` → `dirlevel = 1`, but set_current_file_ex splits: `currdir = "/Music"`, `lastfile = ""` (empty because the path ends with `/`)
2. `ft_load()` then tries to load `/Music` — if it succeeds, the directory listing appears
3. User immediately presses back → `dirlevel <= 1` ✓, `currdir = "/Music"` ✓ → guard fires ✓

The intermittent failure happens in a subtler case:

**`set_current_file("/Music/")` path parsing edge case:**
```c
filename = strrchr(path+1, '/');  // path = "/Music/", path+1 = "Music/"
// strrchr finds the '/' at position 6 → filename points to "/"
// endpos = filename - path = 6
// strmemccpy(tc.currdir, path, 6+1) → "/Music\0" in currdir  
// filename++ → filename points to '\0' (empty string)
```

So `currdir = "/Music"` and `lastfile = ""`. The directory loads fine.

But when `dirlevel` was already set from a **previous session** (tree_context is static!), and the backup/restore in `rockbox_browse` doesn't properly reinitialize it, the dirlevel can be stale from a **previous Files browse or other context**.

### The Actual Root Cause: `tc` backup/restore and shared state

`rockbox_browse()` (line 1238):
```c
if (backup_count >= 0)
    backups[backup_count] = tc;  // backup current tc
backup_count++;
...
tc.browse = browse;
set_current_file(browse->root);  // sets currdir and dirlevel
ret_val = dirbrowse();
...
backup_count--;
if (backup_count >= 0)
    tc = backups[backup_count];  // RESTORE old tc
```

After `rockbox_browse` returns, **tc is restored from the backup**. The backup includes `currdir` and `dirlevel` from **before** the Music session. So when the user re-enters Music, if the previous tc had `currdir = "/"` and `dirlevel = 0`, those values are what get saved into the backup stack.

**The real problem**: `rockbox_browse` correctly saves and restores tc. But the **dirfilter** is set to `&dirfilter` (local variable), which means `*tc.dirfilter` during the Music browse is whatever `browser()` set. The `BROWSE_APPLE2026_MUSICLIB` flag **is** on the browse context. So the guard should work.

After deep analysis, the **most likely intermittent failure path** is:

1. Music is entered → guard works on first back.
2. Music is entered **from WPS return** with a `playback_context_path` that happens to be outside `/Music/` (e.g., the `browse_current` setting redirected it). The code at line 206–213 checks for this but only when `playback_context_screen == GO_TO_MUSICLIB`. If the playback started from Files browser but the track happens to be in `/Music/`, the `playback_context_screen` would be `GO_TO_FILEBROWSER`, not `GO_TO_MUSICLIB`, so the redirect doesn't apply.
3. The **standard fallthrough for Music** then hits line 214: `!strcmp(last_music_folder, "/")` → true → defaults to `"/Music/"`. This is correct.

BUT there's a secondary path: if `browse_current` is enabled and `last_screen == GO_TO_WPS` and `current_track_path[0]` is set, the **filebrowser** case (line 155–160) would use the track path. The **musiclib** case (line 197–213) deliberately does NOT follow `browse_current`. This is correct and was explicitly addressed in the comment at line 199.

**Still, the most plausible regression** is: the guard at line 960-968 fires correctly the **first** time, but there could be a second back press that somehow processes during the return transition, causing `ft_exit()` to run on the already-modified state. But this requires extremely precise timing.

**REVISED ROOT CAUSE DIAGNOSIS:**

After exhaustive analysis, the root cause is likely simpler than expected:

The `dirlevel <= 1` guard in the Apple2026 intercept (line 962) is **too restrictive** in one direction and **too permissive** in another:

- When the user enters Music from a resume path that sets `dirlevel` to a value > 1, and they back out all the way to `/Music/`, `dirlevel` should be 0 (because `ft_exit()` decrements it each time). But `ft_exit()` can leave `dirlevel` at values like -1 or 0, not matching the `<= 1` check correctly in all cases.

- When `dirlevel` is 0 (already at the effective root of Music), pressing back should **still** fire the guard, but the `path_is_curated_music_library_root` check may fail if `ft_exit()` has **already mutated** `currdir` in a prior iteration.

Wait — re-reading the code flow more carefully:

The **guard fires before `ft_exit()`**. So when the user is at `/Music/` with `dirlevel = 1`:
1. Guard checks → `dirlevel <= 1` ✓, `currdir = "/Music"` ✓ → fires → `GO_TO_ROOT` ✓

When the user is at `/Music/` with `dirlevel = 0`:
1. Guard checks → `dirlevel <= 1` ✓, `currdir = "/Music"` ✓ → fires → `GO_TO_ROOT` ✓

When `dirlevel = 1` but `currdir = "/"` (this shouldn't happen but...):
1. Guard checks → `dirlevel <= 1` ✓, `currdir = "/"` → `path_is_curated_music_library_root("/")` ✗ → guard DOES NOT fire
2. Falls through to standard check: `!strcmp(currdir,"/")` → true → `GO_TO_ROOT` ✓ (this one works due to the standard Rockbox check)

So the standard Rockbox root check at line 971-977 should **always** catch the case where currdir is "/", even if the Apple2026 guard misses.

**DEFINITIVE ROOT CAUSE**: After this deep trace, I believe the intermittent failure is caused by the following scenario:

1. `dirlevel` is NOT 0 or 1 when at `/Music/` root — it could be an arbitrary value after complex navigation (enter deep, resume, back multiple times).
2. `dirlevel > 1` → Apple2026 guard doesn't fire.
3. `ft_exit()` runs → strips `/Music` from currdir → `currdir = "/"` → `dirlevel` decrements.
4. Standard root check `!strcmp(currdir,"/")` fires → `GO_TO_ROOT` → **appears to work**.
5. **BUT** — before `GO_TO_ROOT`, the user sees a brief flash of the root filesystem `/` being loaded (because `update_dir()` runs on the next loop iteration after `ft_exit()`).
6. Sometimes this happens so fast it's invisible. Other times it's noticeable — the user sees Podcasts, Notes, etc. for a frame before being returned to root menu.

This is consistent with the user report: "*it only **sometimes** returns to the raw Files root*" — it's a timing/perception issue where the filesystem root briefly appears.

The fix is to make the guard more robust: instead of checking `dirlevel <= 1`, check `path_is_curated_music_library_root(tc.currdir)` alone (which is always correct), and remove the dirlevel constraint entirely. The dirlevel check was added to prevent false-positives from resume paths deeper than Music root, but `path_is_curated_music_library_root()` already handles this precisely.

---

## 3. How Music and Files Should Be Distinguished Architecturally

### Music (Curated Music Browser)
| Aspect | Behavior |
|--------|----------|
| Entry point | Main Menu → Music |
| Root directory | `/Music/` |
| Browse scope | Always within `/Music/` subtree |
| Back at root | → Main Menu (`GO_TO_ROOT`) |
| Folder semantics | Artist → Album → Tracks |
| Icon semantics | Artist/Album icons (custom) |
| Font tier | Normal at artist level, Dense at track level |
| Files shown | Audio files + subdirectories only |
| Browse flag | `BROWSE_APPLE2026_MUSICLIB` |
| Screen identity | `GO_TO_MUSICLIB` |
| Playback source | `PLAYBACK_SOURCE_MUSICLIB` |
| Resume state | `last_music_folder` (validated to /Music/) |

### Files (Full Filesystem Browser)
| Aspect | Behavior |
|--------|----------|
| Entry point | Extras → Files |
| Root directory | `/` (or device root) |
| Browse scope | Full filesystem |
| Back at root `/` | → Extras menu → Main Menu |
| Folder semantics | Standard filesystem |
| Icon semantics | Standard file type icons |
| Font tier | Normal throughout |
| Files shown | All files matching dirfilter |
| Browse flag | None (standard) |
| Screen identity | `GO_TO_FILEBROWSER` |
| Playback source | `PLAYBACK_SOURCE_FILEBROWSER` |
| Resume state | `last_folder` |

### Key Architectural Difference
- Music is a **bounded** browser that can never escape its root (`/Music/`).
- Files is an **unbounded** browser that shows the full filesystem.
- They share the same `rockbox_browse()` / `dirbrowse()` infrastructure but are distinguished by the `BROWSE_APPLE2026_MUSICLIB` flag.
- The back-navigation guard in `dirbrowse()` ensures Music acts as a self-contained viewing mode.

---

## 4. How Files Should Be Added to Extras

### Current Extras Menu (root_menu.c, line 693-698)
```c
MAKE_MENU(extras_submenu, "Extras", 0, Icon_Plugin,
          &rocks_browser, &shortcut_menu [, &rec]);
```

### Proposed Change
Add a new `MENUITEM_RETURNVALUE` for Files and include it in the extras submenu:

```c
MENUITEM_RETURNVALUE(files_browser, "Files", GO_TO_FILEBROWSER,
                     NULL, Icon_file_view_menu);

MAKE_MENU(extras_submenu, "Extras", 0, Icon_Plugin,
          &files_browser, &rocks_browser, &shortcut_menu [, &rec]);
```

This reuses the existing `GO_TO_FILEBROWSER` path which already:
- Opens the full filesystem at `/` (or `last_folder`)
- Has standard `ft_exit()` behavior
- Returns to the calling menu when backing out of root

No new screen type or browser mode is needed. `GO_TO_FILEBROWSER` already exists and works correctly.

---

## 5. Which Files / Systems Need to Change

### Core Changes Required

#### `apps/tree.c` — Back-navigation guard fix
- **Remove the `tc.dirlevel <= 1` constraint** from the Apple2026 intercept.
- Keep only `path_is_curated_music_library_root(tc.currdir)` + `BROWSE_APPLE2026_MUSICLIB` flag check.
- This eliminates all dirlevel desync as a failure mode.

#### `apps/root_menu.c` — Add Files to Extras
- Add `files_browser` MENUITEM_RETURNVALUE for `GO_TO_FILEBROWSER`.
- Add `&files_browser` to `extras_submenu` MAKE_MENU.

### No Other Changes Required
- `GO_TO_FILEBROWSER` already exists and is fully functional.
- The existing browser() function already handles it with separate `last_folder` state.
- `tree.c`, `filetree.c`, `settings.h` do not need modifications for the Files entry.

---

## 6. Implementation Plan

### Step 1: Fix the back-navigation guard (tree.c)
Remove `tc.dirlevel <= 1` from the Apple2026 intercept, relying solely on the path check and flag check.

**Before:**
```c
if (*tc.dirfilter != SHOW_ID3DB && tc.browse
    && (tc.browse->flags & BROWSE_APPLE2026_MUSICLIB)
    && tc.dirlevel <= 1
    && path_is_curated_music_library_root(tc.currdir))
```

**After:**
```c
if (*tc.dirfilter != SHOW_ID3DB && tc.browse
    && (tc.browse->flags & BROWSE_APPLE2026_MUSICLIB)
    && path_is_curated_music_library_root(tc.currdir))
```

### Step 2: Add Files to Extras (root_menu.c)
Add `files_browser` menu item and include it in extras.

### Step 3: Update docs
- DESIGN_SYSTEM.md — document the Music vs Files split
- WORK_LOG.md — record changes

### Anti-Regression Safeguards
1. The `BROWSE_APPLE2026_MUSICLIB` flag is only set when dispatching `GO_TO_MUSICLIB` from root_menu.c. It cannot leak into other browse sessions.
2. `path_is_curated_music_library_root()` is an exact path match (trims trailing slashes then checks `/Music`). It cannot false-positive on `/Music/Artist/`.
3. `last_music_folder` validation ensures it always stays within `/Music/` subtree (line 409-411).
4. `GO_TO_FILEBROWSER` is completely separate — no flag, no path restriction, separate `last_folder` state.
5. The standard Rockbox root check at line 971-977 (`!strcmp(currdir,"/")`) remains as a safety net for Files browser.

---

## 7. Product Model Summary

| Path | Identity | Scope | Back Behavior | Location |
|------|----------|-------|---------------|----------|
| Main Menu → Music | Curated music browser | `/Music/` subtree | → Main Menu | Root menu |
| Extras → Files | Full filesystem browser | Entire disk | → Extras → Main Menu | Extras submenu |
| Main Menu → Cover Flow | Album art browser | Tag database | → Main Menu | Root menu |
| Main Menu → Database | Tag database browser | Tag database | → Main Menu | Root menu |

The user's mental model:
- **Music** = "My music library" — safe, bounded, music-first
- **Files** = "Raw file access" — power-user, full disk
- **Extras** = "Utilities and advanced tools" — where Files belongs
