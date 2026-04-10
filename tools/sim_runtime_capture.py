#!/usr/bin/env python3
"""
Drive Rockbox UI simulator (Windows) and save PNG crops of the simulator window.
Requires: pyautogui, pillow (pip install pyautogui pillow).
"""
from __future__ import annotations

import os
import subprocess
import sys
import time

try:
    import pyautogui
except ImportError:
    print("Install: pip install pyautogui pillow", file=sys.stderr)
    sys.exit(1)

pyautogui.PAUSE = 0.35


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


def focus_sim():
    w = find_sim_window()
    if w is None:
        raise RuntimeError("Simulator window not found (expected title iPod 6G / iPod Video)")
    try:
        w.activate()
    except Exception:
        pass
    time.sleep(0.45)


def click_lcd_center():
    """Click main LCD (upper portion), not the on-screen click wheel."""
    w = find_sim_window()
    if w is None:
        return
    x = w.left + max(8, w.width // 2)
    y = w.top + min(140, max(40, int(w.height * 0.22)))
    pyautogui.click(x, y)
    time.sleep(0.25)


def capture(out_path: str) -> None:
    focus_sim()
    click_lcd_center()
    w = find_sim_window()
    if w is None:
        raise RuntimeError("lost window")
    region = (w.left, w.top, w.width, w.height)
    img = pyautogui.screenshot(region=region)
    img.save(out_path)
    print(out_path)


def main() -> int:
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    rbdir = os.path.join(repo, "build-sim")
    exe = os.path.join(rbdir, "rockboxui.exe")
    if not os.path.isfile(exe):
        print("Missing build-sim/rockboxui.exe — run build-sim.ps1 first.", file=sys.stderr)
        return 1

    outdir = os.path.join(repo, "build-sim", "runtime_captures")
    os.makedirs(outdir, exist_ok=True)

    proc = subprocess.Popen([exe], cwd=rbdir, close_fds=True)
    try:
        time.sleep(7.0)
        capture(os.path.join(outdir, "01_root_library.png"))

        # Second root item = WPS / Now Playing / Resume Playback
        focus_sim()
        click_lcd_center()
        pyautogui.press("down")
        time.sleep(0.3)
        pyautogui.press("enter")  # SDLK_RETURN -> SELECT
        time.sleep(2.0)
        capture(os.path.join(outdir, "02_wps_now_playing.png"))

        # Back to root, open Picture Flow (5th item: music, wps, eq, playlists, pf)
        focus_sim()
        click_lcd_center()
        pyautogui.press("escape")
        time.sleep(1.0)
        for _ in range(4):
            pyautogui.press("down")
            time.sleep(0.15)
        pyautogui.press("enter")
        time.sleep(6.0)
        focus_sim()
        click_lcd_center()
        pyautogui.press("right")  # PF_TRACKLIST
        time.sleep(1.5)
        capture(os.path.join(outdir, "03_coverflow_tracklist.png"))
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=4)
        except subprocess.TimeoutExpired:
            proc.kill()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
