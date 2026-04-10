#!/usr/bin/env python3
"""
Comprehensive Apple2026 simulator screenshot capture.
Launches rockboxui.exe, navigates through key surfaces, captures PNGs.
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

pyautogui.PAUSE = 0.3
pyautogui.FAILSAFE = True

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD_DIR = os.path.join(REPO, "build-sim")
EXE = os.path.join(BUILD_DIR, "rockboxui.exe")
OUTDIR = os.path.join(BUILD_DIR, "runtime_captures")


def find_sim_window():
    """Find the Rockbox simulator window by title."""
    for w in pyautogui.getAllWindows():
        t = (w.title or "").strip()
        if t in ("iPod Video", "iPod 6G", "iPod Color", "Rockbox"):
            return w
    for w in pyautogui.getAllWindows():
        t = w.title or ""
        if "iPod" in t and "Cursor" not in t and "cursor" not in t:
            return w
    return None


def focus_and_click(w):
    """Focus the simulator window and click its LCD area."""
    try:
        w.activate()
    except Exception:
        pass
    time.sleep(0.5)
    x = w.left + max(8, w.width // 2)
    y = w.top + min(140, max(40, int(w.height * 0.22)))
    pyautogui.click(x, y)
    time.sleep(0.3)


def capture_full(name):
    """Capture the entire simulator window."""
    w = find_sim_window()
    if w is None:
        print(f"WARN: window not found for {name}")
        return None
    focus_and_click(w)
    time.sleep(0.3)
    region = (w.left, w.top, w.width, w.height)
    img = pyautogui.screenshot(region=region)
    path = os.path.join(OUTDIR, f"{name}_full.png")
    img.save(path)
    print(f"  captured: {path}")
    return path


def capture_lcd(name):
    """Capture just the LCD portion of the simulator window."""
    w = find_sim_window()
    if w is None:
        print(f"WARN: window not found for {name}")
        return None

    title_bar_h = 32
    lcd_x = w.left + 15
    lcd_y = w.top + title_bar_h + 6
    lcd_w = 320
    lcd_h = 240

    actual_w = min(lcd_w, w.width - 30)
    actual_h = min(lcd_h, w.height - title_bar_h - 30)

    region = (lcd_x, lcd_y, actual_w, actual_h)
    img = pyautogui.screenshot(region=region)
    path = os.path.join(OUTDIR, f"{name}_lcd.png")
    img.save(path)
    print(f"  captured: {path}")
    return path


def press_key(key, wait=0.4):
    """Press a key and wait."""
    pyautogui.press(key)
    time.sleep(wait)


def nav_down(count=1):
    for _ in range(count):
        press_key("down", 0.3)


def nav_up(count=1):
    for _ in range(count):
        press_key("up", 0.3)


def nav_select():
    press_key("enter", 0.8)


def nav_back():
    press_key("escape", 0.6)


def main():
    if not os.path.isfile(EXE):
        print(f"ERROR: {EXE} not found", file=sys.stderr)
        return 1

    os.makedirs(OUTDIR, exist_ok=True)

    existing = find_sim_window()
    if existing:
        print("Simulator already running, using existing window.")
        proc = None
    else:
        print(f"Launching: {EXE}")
        print(f"Working dir: {BUILD_DIR}")
        proc = subprocess.Popen([EXE], cwd=BUILD_DIR, close_fds=True)
        print("Waiting for simulator to initialize...")
        time.sleep(8.0)

    w = find_sim_window()
    if w is None:
        print("ERROR: Simulator window not found after launch!")
        if proc:
            proc.terminate()
        return 1

    print(f"Found simulator window: '{w.title}' at ({w.left},{w.top}) {w.width}x{w.height}")

    try:
        focus_and_click(w)
        time.sleep(1.0)

        print("\n=== 1. ROOT LIBRARY (top of menu) ===")
        nav_up(8)
        time.sleep(0.5)
        capture_full("01_root_top")
        capture_lcd("01_root_top")

        print("\n=== 2. ROOT LIBRARY (scroll to see more items) ===")
        nav_down(2)
        time.sleep(0.3)
        capture_full("02_root_scroll")
        capture_lcd("02_root_scroll")

        print("\n=== 3. ROOT LIBRARY (bottom items) ===")
        nav_down(3)
        time.sleep(0.3)
        capture_full("03_root_bottom")
        capture_lcd("03_root_bottom")

        print("\n=== 4. MUSIC BROWSER (enter Music) ===")
        nav_up(8)
        time.sleep(0.5)
        nav_select()
        time.sleep(2.0)
        capture_full("04_music_browser")
        capture_lcd("04_music_browser")

        print("\n=== 5. ARTIST FOLDER (first artist) ===")
        nav_select()
        time.sleep(1.5)
        capture_full("05_artist_folder")
        capture_lcd("05_artist_folder")

        print("\n=== 6. ALBUM FOLDER (first album) ===")
        nav_select()
        time.sleep(1.5)
        capture_full("06_album_folder")
        capture_lcd("06_album_folder")

        print("\n=== 7. TRACK LIST (inside album) ===")
        capture_full("07_tracklist")
        capture_lcd("07_tracklist")

        print("\n=== 8. Start playback (select first track) ===")
        nav_select()
        time.sleep(3.0)
        capture_full("08_wps")
        capture_lcd("08_wps")

        print("\n=== 9. WPS close-up (after settling) ===")
        time.sleep(2.0)
        capture_full("09_wps_settled")
        capture_lcd("09_wps_settled")

        print("\n=== 10. BACK to root from WPS ===")
        nav_back()
        time.sleep(1.0)
        nav_back()
        time.sleep(1.0)
        nav_back()
        time.sleep(1.0)
        nav_back()
        time.sleep(1.0)
        capture_full("10_back_to_root")
        capture_lcd("10_back_to_root")

        print("\n=== 11. SETTINGS (navigate down to Settings) ===")
        nav_up(8)
        time.sleep(0.5)
        nav_down(5)
        time.sleep(0.3)
        capture_full("11_settings_highlight")
        capture_lcd("11_settings_highlight")

        print("\n=== 12. SETTINGS MENU (enter) ===")
        nav_select()
        time.sleep(1.0)
        capture_full("12_settings_menu")
        capture_lcd("12_settings_menu")

        print("\n=== 13. BACK to root ===")
        nav_back()
        time.sleep(0.5)

        print("\n=== 14. COVER FLOW (navigate to it) ===")
        nav_up(8)
        time.sleep(0.5)
        nav_down(3)
        time.sleep(0.3)
        capture_full("14_coverflow_highlight")
        capture_lcd("14_coverflow_highlight")

        nav_select()
        time.sleep(6.0)
        capture_full("15_coverflow")
        capture_lcd("15_coverflow")

        print("\n=== 16. COVER FLOW TRACKLIST ===")
        press_key("right", 2.0)
        capture_full("16_coverflow_tracklist")
        capture_lcd("16_coverflow_tracklist")

        print("\n=== 17. BACK from Cover Flow ===")
        press_key("left", 1.0)
        nav_back()
        time.sleep(1.0)
        capture_full("17_back_from_cflow")
        capture_lcd("17_back_from_cflow")

        print("\nDone! All screenshots saved to:", OUTDIR)

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
