#!/usr/bin/env python3
"""
Comprehensive Apple2026 simulator screenshot capture - v2.
Uses correct iPod simulator keymap: RIGHT=enter, LEFT=back, UP/DOWN=scroll.
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

pyautogui.PAUSE = 0.2
pyautogui.FAILSAFE = True

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD_DIR = os.path.join(REPO, "build-sim")
EXE = os.path.join(BUILD_DIR, "rockboxui.exe")
OUTDIR = os.path.join(BUILD_DIR, "runtime_captures")


def find_sim_window():
    for w in pyautogui.getAllWindows():
        t = (w.title or "").strip()
        if t in ("iPod Video", "iPod 6G", "iPod Color", "Rockbox"):
            return w
    for w in pyautogui.getAllWindows():
        t = w.title or ""
        if "iPod" in t and "Cursor" not in t and "cursor" not in t:
            return w
    return None


def focus_sim():
    w = find_sim_window()
    if w is None:
        raise RuntimeError("Simulator window not found")
    try:
        w.activate()
    except Exception:
        pass
    time.sleep(0.4)
    x = w.left + max(8, w.width // 2)
    y = w.top + min(160, max(40, int(w.height * 0.25)))
    pyautogui.click(x, y)
    time.sleep(0.3)


def capture(name):
    w = find_sim_window()
    if w is None:
        print(f"  WARN: no window for {name}")
        return

    focus_sim()
    time.sleep(0.3)

    img_full = pyautogui.screenshot(region=(w.left, w.top, w.width, w.height))
    img_full.save(os.path.join(OUTDIR, f"{name}_full.png"))

    lcd_x = w.left + 48
    lcd_y = w.top + 57
    lcd_w = 323
    lcd_h = 243
    if lcd_x + lcd_w > w.left + w.width:
        lcd_w = w.width - 48
    if lcd_y + lcd_h > w.top + w.height:
        lcd_h = w.height - 57

    img_lcd = pyautogui.screenshot(region=(lcd_x, lcd_y, lcd_w, lcd_h))
    img_lcd.save(os.path.join(OUTDIR, f"{name}_lcd.png"))

    print(f"  captured: {name}")


def scroll_up(n=1, delay=0.25):
    focus_sim()
    for _ in range(n):
        pyautogui.press("up")
        time.sleep(delay)


def scroll_down(n=1, delay=0.25):
    focus_sim()
    for _ in range(n):
        pyautogui.press("down")
        time.sleep(delay)


def select():
    """RIGHT key = ACTION_STD_OK on iPod."""
    focus_sim()
    pyautogui.press("right")
    time.sleep(0.8)


def back():
    """LEFT key = ACTION_STD_CANCEL on iPod."""
    focus_sim()
    pyautogui.press("left")
    time.sleep(0.6)


def menu():
    """ESCAPE = BUTTON_MENU on iPod."""
    focus_sim()
    pyautogui.press("escape")
    time.sleep(0.6)


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
        proc = subprocess.Popen([EXE], cwd=BUILD_DIR, close_fds=True)
        print("Waiting 8s for simulator init...")
        time.sleep(8.0)

    w = find_sim_window()
    if w is None:
        print("ERROR: no sim window!")
        if proc:
            proc.terminate()
        return 1

    print(f"Window: '{w.title}' at ({w.left},{w.top}) {w.width}x{w.height}")

    try:
        focus_sim()
        time.sleep(1.0)

        scroll_up(10, 0.15)
        time.sleep(0.5)

        print("\n=== 1. ROOT LIBRARY (Music highlighted) ===")
        capture("01_root_library")

        print("\n=== 2. Scroll root (Resume Playback) ===")
        scroll_down(1)
        capture("02_root_resume")

        print("\n=== 3. Scroll root (Equalizer) ===")
        scroll_down(1)
        capture("03_root_equalizer")

        print("\n=== 4. Continue scrolling ===")
        scroll_down(3)
        capture("04_root_bottom")

        print("\n=== 5. Back to top, ENTER MUSIC ===")
        scroll_up(10, 0.15)
        time.sleep(0.3)
        select()
        time.sleep(2.0)
        capture("05_music_browser")

        print("\n=== 6. ENTER first artist ===")
        select()
        time.sleep(1.5)
        capture("06_artist_albums")

        print("\n=== 7. ENTER first album ===")
        select()
        time.sleep(1.5)
        capture("07_album_tracks")

        print("\n=== 8. START PLAYBACK (select first track) ===")
        select()
        time.sleep(4.0)
        capture("08_wps")

        print("\n=== 9. WPS (settled) ===")
        time.sleep(3.0)
        capture("09_wps_settled")

        print("\n=== 10. BACK from WPS ===")
        back()
        time.sleep(1.5)
        capture("10_from_wps")

        print("\n=== 11. BACK to artist ===")
        back()
        time.sleep(1.0)
        capture("11_back_artist")

        print("\n=== 12. BACK to music root ===")
        back()
        time.sleep(1.0)
        capture("12_back_music_root")

        print("\n=== 13. BACK to main menu ===")
        back()
        time.sleep(1.0)
        capture("13_back_main_menu")

        print("\n=== 14. Root menu with mini-player ===")
        scroll_up(10, 0.15)
        time.sleep(0.5)
        capture("14_root_with_miniplayer")

        print("\n=== 15. Navigate to Settings ===")
        scroll_down(10, 0.15)
        time.sleep(0.3)
        scroll_up(2, 0.25)
        capture("15_near_settings")

        scroll_down(1)
        time.sleep(0.3)
        capture("15b_settings_highlight")

        print("\n=== 16. ENTER Settings ===")
        select()
        time.sleep(1.0)
        capture("16_settings_inside")

        print("\n=== 17. BACK from Settings ===")
        back()
        time.sleep(0.5)

        print("\n=== 18. Navigate to Cover Flow ===")
        scroll_up(10, 0.15)
        time.sleep(0.3)
        scroll_down(4, 0.25)
        capture("18_coverflow_highlight")

        select()
        time.sleep(8.0)
        capture("19_coverflow")

        print("\n=== 20. Cover Flow tracklist ===")
        focus_sim()
        pyautogui.press("right")
        time.sleep(3.0)
        capture("20_coverflow_tracklist")

        print("\n=== 21. BACK from Cover Flow ===")
        focus_sim()
        pyautogui.press("left")
        time.sleep(1.0)
        back()
        time.sleep(1.0)
        menu()
        time.sleep(1.0)
        capture("21_back_from_cflow")

        print("\nDone! Screenshots in:", OUTDIR)

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
