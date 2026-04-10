#!/bin/sh
# Prerequisite audit for RockPod builds. Run from MSYS2 UCRT64 (or via rockpod-check-env.ps1).
# Exit 0 = all checked requirements present; 1 = one or more missing.

cd "$(dirname "$0")/.." || exit 1

MODE=all
while [ $# -gt 0 ]; do
    case "$1" in
        --sim-only) MODE=sim; shift ;;
        --hw-only)  MODE=hw; shift ;;
        -h|--help)
            echo "Usage: $0 [--sim-only | --hw-only]"
            echo "  Default: verify simulator + hardware toolchain requirements."
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            exit 1
            ;;
    esac
done

fail=0

echo "RockPod toolchain check (MODE=$MODE)"
if [ -n "${MSYSTEM:-}" ]; then
    echo "MSYSTEM=$MSYSTEM"
    if [ "$MSYSTEM" != "UCRT64" ]; then
        echo "  Warning: RockPod PowerShell wrappers use UCRT64; mixed PATH may hide SDL2 or gcc."
    fi
else
    echo "(MSYSTEM unset — if you are not using the repo wrappers, ensure UCRT64 tools are on PATH.)"
fi
echo ""

ok_line() {
    printf "  [ok]   %s\n" "$1"
}

miss_line() {
    printf "  [MISS] %s\n" "$1"
    fail=1
}

# Core (always)
for c in make gcc perl python3; do
    if command -v "$c" >/dev/null 2>&1; then
        case "$c" in
            make)    v=$(make --version 2>/dev/null | head -n 1 | tr -d '\r') ;;
            gcc)     v=$(gcc --version 2>/dev/null | head -n 1 | tr -d '\r') ;;
            perl)    v=$(perl -e 'printf "%s", $^V' 2>/dev/null | tr -d '\r') ;;
            python3) v=$(python3 --version 2>/dev/null | tr -d '\r') ;;
            *)       v="" ;;
        esac
        ok_line "$c ${v:-}"
    else
        miss_line "required tool not found: $c"
    fi
done

if command -v perl >/dev/null 2>&1; then
    if perl -MIPC::Open2 -e1 2>/dev/null; then
        ok_line "perl IPC::Open2 (wpsbuild.pl)"
    else
        miss_line "perl IPC::Open2 module"
    fi
else
    miss_line "perl IPC::Open2 (perl missing)"
fi

if [ "$MODE" = "all" ] || [ "$MODE" = "sim" ]; then
    echo ""
    echo "Simulator (SDL2):"
    for c in sdl2-config pkg-config; do
        if command -v "$c" >/dev/null 2>&1; then
            v=$("$c" --version 2>/dev/null | head -n 1 | tr -d '\r' || echo present)
            ok_line "$c ($v)"
        else
            miss_line "simulator prerequisite: $c"
        fi
    done
fi

if [ "$MODE" = "all" ] || [ "$MODE" = "hw" ]; then
    echo ""
    echo "Hardware (arm-none-eabi):"
    CC_PRE="${CROSS_COMPILE:-arm-none-eabi-}"
    for c in "${CC_PRE}gcc" "${CC_PRE}objcopy"; do
        if command -v "$c" >/dev/null 2>&1; then
            v=$("$c" --version 2>/dev/null | head -n 1 | tr -d '\r')
            ok_line "$c ($v)"
        else
            miss_line "cross tool not found: $c (set CROSS_COMPILE if using a different prefix)"
        fi
    done
fi

echo ""
echo "Optional:"
if command -v zip >/dev/null 2>&1; then
    ok_line "zip"
else
    echo "  [--]   zip (recommended for packaging)"
fi
if command -v ccache >/dev/null 2>&1; then
    v=$(ccache --version 2>/dev/null | head -n 1 | tr -d '\r')
    ok_line "ccache ($v) — optional; wire via CC= after configure if desired"
else
    echo "  [--]   ccache (not on PATH)"
fi

echo ""
if [ "$fail" -ne 0 ]; then
    echo "Result: FAILED (install missing pieces, then re-run)."
    echo "MSYS2 (UCRT64) examples: pacman -S mingw-w64-ucrt-x86_64-{SDL2,toolchain,gcc,make,perl,zip}"
    echo "ARM GCC: mingw-w64-ucrt-x86_64-arm-none-eabi-gcc (or your distro's arm-none-eabi-gcc)"
    exit 1
fi

echo "Result: OK"
exit 0
