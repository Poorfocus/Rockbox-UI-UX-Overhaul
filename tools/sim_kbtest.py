#!/usr/bin/env python3
"""
Find button positions by examining the screenshot image.
Also tries a direct keyboard approach (simpler but requires focus).
"""
import os
import subprocess
import sys
import time

try:
    import pyautogui
    from PIL import Image
except ImportError:
    print("Install: pip install pyautogui pillow")
    sys.exit(1)

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
        if "iPod" in t and "Cursor" not in t:
            return w
    return None


def focus(w):
    try:
        w.activate()
    except Exception:
        pass
    time.sleep(1.0)


def cap(name, w):
    img = pyautogui.screenshot(region=(w.left, w.top, w.width, w.height))
    path = os.path.join(OUTDIR, f"kbtest_{name}.png")
    img.save(path)
    print(f"  saved: {path}")
    return img


def main():
    os.makedirs(OUTDIR, exist_ok=True)

    proc = subprocess.Popen([EXE], cwd=BUILD_DIR, close_fds=True)
    print("Waiting for sim to initialize (10s)...")
    time.sleep(10.0)

    w = find_sim_window()
    if w is None:
        print("No window found")
        proc.terminate()
        return 1

    print(f"Window: '{w.title}' at ({w.left},{w.top}) {w.width}x{w.height}")

    # Focus the window first
    focus(w)
    time.sleep(1.0)
    cap("00_initial", w)

    # Move mouse to window center to ensure hover
    cx = w.left + w.width // 2
    cy = w.top + w.height // 2
    pyautogui.moveTo(cx, cy, duration=0.3)
    time.sleep(0.5)

    # Method 1: Keyboard keys (simplest, requires focus)
    # From keymap: SDLK_DOWN = BUTTON_SCROLL_FWD, SDLK_RETURN = BUTTON_SELECT
    print("\n--- Testing keyboard scroll down ---")
    pyautogui.press('down')
    time.sleep(0.5)
    cap("01_after_down_key", w)

    pyautogui.press('down')
    time.sleep(0.5)
    cap("02_after_down_key2", w)

    pyautogui.press('up')
    time.sleep(0.5)
    cap("03_after_up_key", w)

    print("\n--- Testing keyboard ENTER/Return for select ---")
    pyautogui.press('return')
    time.sleep(1.5)
    cap("04_after_return", w)

    pyautogui.press('return')
    time.sleep(1.5)
    cap("05_after_return2", w)

    # Navigate deeper
    pyautogui.press('return')
    time.sleep(1.5)
    cap("06_after_return3", w)

    # Back with escape/backspace
    print("\n--- Testing ESCAPE for back ---")
    pyautogui.press('escape')
    time.sleep(1.0)
    cap("07_after_escape", w)

    proc.terminate()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
