#!/usr/bin/env python3
"""
Diagnostic: find exact simulator window geometry and test button clicks.
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
    time.sleep(0.6)


def cap(name, w):
    img = pyautogui.screenshot(region=(w.left, w.top, w.width, w.height))
    path = os.path.join(OUTDIR, f"diag_{name}.png")
    img.save(path)
    print(f"  saved: {path}")


def main():
    os.makedirs(OUTDIR, exist_ok=True)

    proc = subprocess.Popen([EXE], cwd=BUILD_DIR, close_fds=True)
    print("Waiting for sim...")
    time.sleep(8.0)

    w = find_sim_window()
    if w is None:
        print("No window found")
        proc.terminate()
        return 1

    print(f"Window: '{w.title}'")
    print(f"  Position: ({w.left}, {w.top})")
    print(f"  Size: {w.width} x {w.height}")

    # The SDL window for iPod 6G simulator - the game/client area
    # Window has: title bar, border.
    # From screenshots we can see the LCD is inside a bordered frame.
    # Let's check: window is 547 wide. The iPod 6G skin is 349x618 px approx.
    # The LCD (320x240) starts within the skin at some offset.
    
    # Strategy: scan center of SDL clickwheel numerically.
    # The skin image centers the LCD and clickwheel within the window.
    # Estimate client area offset from window borders (usually ~8px sides, ~32px title bar on Windows)
    border = 8
    title_h = 32
    
    # Total skin width = window_width - 2*border
    skin_w = w.width - 2 * border
    skin_h = w.height - title_h - border
    print(f"  Estimated skin area: {skin_w} x {skin_h}")
    
    # For iPod 6G at SDL resolution, the game renders at the skin's native resolution
    # The SDL button map coords (bx, by) are within the SDL rendering surface
    # SDL surface = skin_w x skin_h (or the SDL window client dimensions)
    # So screen_x = w.left + border + bx, screen_y = w.top + title_h + by
    
    def click_sdl(bx, by, label=""):
        sx = w.left + border + bx
        sy = w.top + title_h + by
        print(f"  Clicking '{label}' at screen ({sx}, {sy}), sdl ({bx}, {by})")
        pyautogui.click(sx, sy)
        time.sleep(0.4)

    focus(w)
    time.sleep(0.5)

    print("\n--- Initial state ---")
    cap("00_init", w)

    # Scale factor: SDL button coords are for the native skin.
    # Native iPod 6G skin was 349x618. If our window client is skin_w x skin_h,
    # scale = skin_w / 349, scale_y = skin_h / 618
    native_w, native_h = 349, 618
    scale_x = skin_w / native_w
    scale_y = skin_h / native_h
    print(f"  Scale: {scale_x:.2f} x {scale_y:.2f}")
    
    # iPod 6G button map (native coords):
    # KP_5/SELECT: (175, 432) - center of wheel
    # KP_8/UP: (100, 375) - top of wheel
    # KP_2/DOWN: (245, 375) - bottom area
    # KP_6/RIGHT: (275, 432) - right of wheel
    # KP_4/LEFT: (75, 432) - left of wheel
    # KP_PERIOD/MENU: (175, 350) - above wheel
    
    def click_native(nx, ny, label=""):
        sx = w.left + border + int(nx * scale_x)
        sy = w.top + title_h + int(ny * scale_y)
        print(f"  Click '{label}' native ({nx},{ny}) -> screen ({sx},{sy})")
        pyautogui.click(sx, sy)
        time.sleep(0.5)

    # Test scroll down
    click_native(245, 375, "scroll_fwd")
    cap("01_after_scroll_down", w)

    click_native(245, 375, "scroll_fwd")
    cap("02_after_scroll_down2", w)
    
    # Test scroll up
    click_native(100, 375, "scroll_back")
    cap("03_after_scroll_up", w)

    # Test SELECT (center)
    click_native(175, 432, "select")
    time.sleep(1.5)
    cap("04_after_select", w)

    # Test RIGHT
    click_native(275, 432, "right")
    time.sleep(1.5)
    cap("05_after_right", w)

    proc.terminate()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
