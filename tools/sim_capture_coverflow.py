#!/usr/bin/env python3
"""
Cover Flow + key surfaces screenshot capture for Apple2026.
Launches the simulator, navigates to Cover Flow via the main menu,
then captures screenshots of all major surfaces.

Button coordinates (relative to window client area, for iPod 6G sim):
  SELECT: (175, 432)
  LEFT:   (75,  432)
  RIGHT:  (275, 432)
  MENU:   (175, 350)
  PLAY:   (175, 539)
  SCROLL_BACK (up):   (100, 375)
  SCROLL_FWD  (down): (245, 375)
"""
from __future__ import annotations
import os
import subprocess
import sys
import time

try:
    import pyautogui
    from PIL import Image
except ImportError:
    print("Install: pip install pyautogui pillow", file=sys.stderr)
    sys.exit(1)

pyautogui.PAUSE = 0.15
pyautogui.FAILSAFE = False  # Disabled to prevent corner-trigger during automated capture

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD_DIR = os.path.join(REPO, "build-sim")
EXE = os.path.join(BUILD_DIR, "rockboxui.exe")
OUTDIR = os.path.join(BUILD_DIR, "runtime_captures")

WIN_X = 0
WIN_Y = 0
TITLE_BAR = 32


def find_sim_window():
    """Find the Rockbox simulator window specifically (not browser tabs)."""
    for w in pyautogui.getAllWindows():
        t = (w.title or "").strip()
        # Only match exact titles of the actual simulator executable
        if t in ("iPod 6G", "iPod Video", "iPod Color", "iPod 6G"):
            # Ensure it's an actual visible window, not a minimized browser tab
            if w.left > -1000 and w.top > -1000 and w.width > 100:
                return w
    return None


def update_pos():
    global WIN_X, WIN_Y
    w = find_sim_window()
    if w:
        WIN_X = w.left
        WIN_Y = w.top


def click_btn(bx, by, wait=0.5):
    update_pos()
    x = WIN_X + 48 + int(bx)
    y = WIN_Y + TITLE_BAR + 24 + int(by)
    pyautogui.click(x, y)
    time.sleep(wait)


def scroll_up(n=1, delay=0.25):
    for _ in range(n):
        click_btn(100, 375, delay)


def scroll_down(n=1, delay=0.25):
    for _ in range(n):
        click_btn(245, 375, delay)


def select(wait=1.0):
    click_btn(175, 432, wait)


def go_right(wait=1.0):
    click_btn(275, 432, wait)


def go_left(wait=0.8):
    click_btn(75, 432, wait)


def menu_btn(wait=0.8):
    click_btn(175, 350, wait)


def focus_sim():
    w = find_sim_window()
    if w is None:
        return
    try:
        w.activate()
    except Exception:
        pass
    time.sleep(0.4)


def capture(name):
    w = find_sim_window()
    if w is None:
        print(f"  WARN: no window for {name}")
        return
    focus_sim()
    time.sleep(0.2)
    img_full = pyautogui.screenshot(region=(w.left, w.top, w.width, w.height))
    img_full.save(os.path.join(OUTDIR, f"cf_{name}_full.png"))
    client_x = w.left + 48
    client_y = w.top + TITLE_BAR + 24
    lcd_w = 325
    lcd_h = 245
    img_lcd = pyautogui.screenshot(region=(client_x, client_y, lcd_w, lcd_h))
    img_lcd.save(os.path.join(OUTDIR, f"cf_{name}_lcd.png"))
    print(f"  captured: {name}")


def main():
    if not os.path.isfile(EXE):
        print(f"ERROR: {EXE} not found", file=sys.stderr)
        return 1

    os.makedirs(OUTDIR, exist_ok=True)

    existing = find_sim_window()
    if existing:
        print("Simulator already running.")
        proc = None
    else:
        print(f"Launching: {EXE}")
        proc = subprocess.Popen([EXE], cwd=BUILD_DIR, close_fds=True)
        print("Waiting 10s for sim init + database load...")
        time.sleep(10.0)

    w = find_sim_window()
    if w is None:
        print("ERROR: no sim window!")
        if proc:
            proc.terminate()
        return 1

    print(f"Window: '{w.title}' at ({w.left},{w.top}) {w.width}x{w.height}")
    update_pos()

    try:
        focus_sim()
        time.sleep(1.0)

        # Reset to root menu top
        scroll_up(15, 0.12)
        time.sleep(0.5)

        print("\n=== 1. Root / Library (top) ===")
        capture("01_root_top")

        print("\n=== 2. Scroll down to see all root items ===")
        scroll_down(1)
        capture("02_root_scroll1")
        scroll_down(1)
        capture("03_root_scroll2")
        scroll_down(1)
        capture("04_root_scroll3")

        # Back to top
        scroll_up(15, 0.12)
        time.sleep(0.4)

        print("\n=== 5. Enter Music browser ===")
        capture("05_root_top_before_music")
        select(2.0)
        capture("06_music_entered")

        print("\n=== 7. Navigate to artist ===")
        select(2.0)
        capture("07_artist_level")

        print("\n=== 8. Navigate to album ===")
        select(2.0)
        capture("08_album_level")

        print("\n=== 9. Navigate to track ===")
        select(2.0)
        capture("09_track_level")

        print("\n=== 10. Start playback ===")
        select(6.0)
        capture("10_wps_playing")

        print("\n=== 11. WPS settled ===")
        time.sleep(3.0)
        capture("11_wps_settled")

        print("\n=== 12. Back to root ===")
        menu_btn(1.0)
        capture("12_back_to_root")

        # Navigate to Cover Flow
        # Cover Flow is in the main menu. Find it by scrolling.
        scroll_up(15, 0.12)
        time.sleep(0.4)
        print("\n=== 13. Scroll to Cover Flow item ===")
        # Cover Flow item position: depends on menu order, scroll down ~3 items
        scroll_down(3, 0.3)
        capture("13_near_coverflow")

        print("\n=== 14. Select Cover Flow (wait for database load) ===")
        select(12.0)  # Long wait: pictureflow scans + builds album index
        capture("14_coverflow_main")

        print("\n=== 15. Cover Flow loaded - capture ===")
        time.sleep(2.0)
        capture("15_coverflow_loaded")

        print("\n=== 16. Scroll Cover Flow right ===")
        scroll_down(2, 0.6)
        capture("16_coverflow_scroll1")

        scroll_down(2, 0.6)
        capture("17_coverflow_scroll2")

        scroll_down(2, 0.6)
        capture("18_coverflow_scroll3")

        print("\n=== 19. Enter tracklist (SELECT) ===")
        select(3.0)
        capture("19_tracklist")

        print("\n=== 20. Scroll tracklist ===")
        scroll_down(2, 0.4)
        capture("20_tracklist_scroll")

        print("\n=== 21. Back to Cover Flow ===")
        go_left(1.5)
        capture("21_coverflow_back")

        print("\n=== 22. Exit Cover Flow ===")
        menu_btn(2.0)
        capture("22_after_coverflow_exit")

        print("\nDone! Screenshots saved to:", OUTDIR)

    finally:
        if proc:
            print("Terminating simulator...")
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
