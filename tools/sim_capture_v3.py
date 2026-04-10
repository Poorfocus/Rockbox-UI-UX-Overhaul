#!/usr/bin/env python3
"""
Apple2026 sim capture v3 - uses clickwheel mouse clicks instead of keyboard.
The iPod 6G simulator button map coordinates (relative to window client area):
  SELECT: (175, 432) radius 45
  LEFT:   (75, 432)  radius 38
  RIGHT:  (275, 432) radius 39
  MENU:   (175, 350) radius 34
  PLAY:   (175, 539) radius 41
  SCROLL_BACK (up):    (100, 375) radius 35
  SCROLL_FWD  (down):  (245, 375) radius 35
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
pyautogui.FAILSAFE = True

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD_DIR = os.path.join(REPO, "build-sim")
EXE = os.path.join(BUILD_DIR, "rockboxui.exe")
OUTDIR = os.path.join(BUILD_DIR, "runtime_captures")

WIN_X = 0
WIN_Y = 0
TITLE_BAR = 32


def find_sim_window():
    for w in pyautogui.getAllWindows():
        t = (w.title or "").strip()
        if t in ("iPod Video", "iPod 6G", "iPod Color", "Rockbox"):
            return w
    for w in pyautogui.getAllWindows():
        t = w.title or ""
        if "iPod" in t and "Cursor" not in t:
            return w
    return None


def update_pos():
    global WIN_X, WIN_Y
    w = find_sim_window()
    if w:
        WIN_X = w.left
        WIN_Y = w.top


def click_btn(bx, by, wait=0.5):
    """Click a button at SDL coordinates relative to window client area."""
    update_pos()
    x = WIN_X + 48 + int(bx * 1.0)
    y = WIN_Y + TITLE_BAR + 24 + int(by * 1.0)
    pyautogui.click(x, y)
    time.sleep(wait)


def scroll_up(n=1, delay=0.3):
    for _ in range(n):
        click_btn(100, 375, delay)


def scroll_down(n=1, delay=0.3):
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
    img_full.save(os.path.join(OUTDIR, f"{name}_full.png"))

    client_x = w.left + 48
    client_y = w.top + TITLE_BAR + 24
    lcd_w = 325
    lcd_h = 245
    img_lcd = pyautogui.screenshot(region=(client_x, client_y, lcd_w, lcd_h))
    img_lcd.save(os.path.join(OUTDIR, f"{name}_lcd.png"))

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
        print("Waiting 8s for init...")
        time.sleep(8.0)

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

        scroll_up(12, 0.15)
        time.sleep(0.5)

        print("\n=== 1. ROOT LIBRARY TOP ===")
        capture("01_root_top")

        print("\n=== 2. Scroll root down ===")
        scroll_down(1)
        capture("02_root_item2")

        scroll_down(1)
        capture("03_root_item3")

        scroll_down(3)
        capture("04_root_bottom")

        print("\n=== 5. Back to top, SELECT Music ===")
        scroll_up(12, 0.15)
        time.sleep(0.5)
        capture("05a_before_select")

        select(2.0)
        capture("05b_after_select_music")

        print("\n=== 6. Try RIGHT instead (iPod enter) ===")
        go_right(2.0)
        capture("06_after_right")

        print("\n=== 7. Navigate deeper ===")
        go_right(1.5)
        capture("07_deeper")

        go_right(1.5)
        capture("08_deeper2")

        go_right(4.0)
        capture("09_maybe_wps")

        time.sleep(3.0)
        capture("10_wps_settled")

        print("\n=== 11. Back path ===")
        go_left(1.0)
        capture("11_back1")

        go_left(1.0)
        capture("12_back2")

        go_left(1.0)
        capture("13_back3")

        go_left(1.0)
        capture("14_back4")

        menu_btn(1.0)
        capture("15_menu")

        print("\n=== 16. Navigate to Settings ===")
        scroll_up(12, 0.15)
        scroll_down(6, 0.2)
        capture("16_settings_area")

        go_right(1.0)
        capture("17_settings_inside")

        go_left(1.0)
        capture("18_back_from_settings")

        print("\n=== 19. Navigate to Cover Flow ===")
        scroll_up(12, 0.15)
        scroll_down(4, 0.2)
        capture("19_coverflow_area")

        select(8.0)
        capture("20_coverflow")

        go_right(3.0)
        capture("21_coverflow_tracklist")

        go_left(1.0)
        menu_btn(1.0)
        capture("22_back_from_cf")

        print("\nDone!")

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
