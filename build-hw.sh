#!/bin/sh
cd "$(dirname "$0")"

detect_jobs() {
    if [ -n "${JOBS:-}" ]; then
        echo "$JOBS"
    elif command -v getconf >/dev/null 2>&1; then
        getconf _NPROCESSORS_ONLN 2>/dev/null || echo 4
    elif command -v nproc >/dev/null 2>&1; then
        nproc 2>/dev/null || echo 4
    elif command -v sysctl >/dev/null 2>&1; then
        sysctl -n hw.ncpu 2>/dev/null || echo 4
    else
        echo 4
    fi
}

require_tools() {
    missing=0
    for tool in make gcc perl python3; do
        if ! command -v "$tool" >/dev/null 2>&1; then
            echo "Error: missing required tool '$tool' on PATH."
            missing=1
        fi
    done

    for tool in "${CROSS_COMPILE}gcc" "${CROSS_COMPILE}objcopy"; do
        if ! command -v "$tool" >/dev/null 2>&1; then
            echo "Error: missing cross-compiler tool '$tool' on PATH."
            missing=1
        fi
    done

    if [ "$missing" -ne 0 ]; then
        exit 2
    fi
}

prepare_core_generated_headers() {
    builddir_unix=$(pwd)

    make -j1 \
        "$builddir_unix/sysfont.h" \
        "$builddir_unix/lang/lang.h" \
        "$builddir_unix/lang_enum.h" \
        "$builddir_unix/lang/max_language_size.h" \
        "$builddir_unix/apps/core_asmdefs.h" \
        "$builddir_unix/rbversion.h" \
        "$builddir_unix/lib/rbcodec/codecs/ape-pre.map" \
        "$builddir_unix/lib/rbcodec/codecs/ape_free_iram.h" \
        "$builddir_unix/bitmaps/rockboxlogo.h" \
        "$builddir_unix/bitmaps/default_icons.h"
}

case "$(uname -s)" in
    MSYS_NT*)
        echo "Error: run this from a MinGW-family MSYS2 shell or use build-hw.ps1."
        exit 1
        ;;
esac

INCREMENTAL=0
case "${ROCKPOD_INCREMENTAL:-}" in
    1|yes|true|YES|TRUE) INCREMENTAL=1 ;;
esac
while [ $# -gt 0 ]; do
    case "$1" in
        -i|--incremental)
            INCREMENTAL=1
            shift
            ;;
        -h|--help)
            cat <<'EOF'
Usage: build-hw.sh [-i|--incremental] [ipod6g|6g|ipodvideo|5g]

  -i, --incremental   Reuse build-hw-<target>/ when already configured.

Environment:
  ROCKPOD_INCREMENTAL=1   same as -i
  ROCKPOD_SKIP_DEP=1      skip make dep when make.dep exists
  JOBS=N                  parallel job count
  CROSS_COMPILE=prefix-   default arm-none-eabi-

Default: remove build-hw-<target>/, full configure, make dep, build, make zip.
EOF
            exit 0
            ;;
        -*)
            echo "Unknown option: $1" >&2
            echo "Try: build-hw.sh --help" >&2
            exit 1
            ;;
        *)
            break
            ;;
    esac
done

TARGET="${1:-ipod6g}"
CROSS_COMPILE="${CROSS_COMPILE:-arm-none-eabi-}"
export CROSS_COMPILE

case "$TARGET" in
    ipod6g|6g)  TARGET=ipod6g ;;
    ipodvideo|5g) TARGET=ipodvideo ;;
    *)
        echo "Usage: $0 [-i|--incremental] [ipod6g|6g|ipodvideo|5g]"
        echo "  ipod6g / 6g      iPod Classic 6G/7G (default)"
        echo "  ipodvideo / 5g   iPod Video 5G/5.5G"
        exit 1
        ;;
esac

require_tools

BUILDDIR="build-hw-${TARGET}"
WANT_STAMP="hardware ${TARGET}"

run_configure() {
    ../tools/configure --target="$TARGET" --type=n
    printf '%s\n' "$WANT_STAMP" > .rockpod_configure_stamp
}

if [ "$INCREMENTAL" -eq 0 ]; then
    echo "RockPod: clean hardware build (removing ${BUILDDIR}/)..."
    rm -rf "$BUILDDIR"
    mkdir "$BUILDDIR"
    cd "$BUILDDIR" || exit 1
    run_configure
else
    echo "RockPod: incremental hardware build (${TARGET})..."
    mkdir -p "$BUILDDIR"
    cd "$BUILDDIR" || exit 1
    if [ ! -f Makefile ]; then
        echo "RockPod: configuring (no Makefile)..."
        run_configure
    elif [ ! -f .rockpod_configure_stamp ] || [ "$(cat .rockpod_configure_stamp)" != "$WANT_STAMP" ]; then
        echo "RockPod: re-configuring (stamp mismatch or missing)..."
        run_configure
    else
        echo "RockPod: using existing configure in $(pwd)"
    fi
fi

if [ -n "${ROCKPOD_SKIP_DEP:-}" ] && [ -f make.dep ]; then
    echo "RockPod: ROCKPOD_SKIP_DEP set; skipping make dep."
else
    make dep
fi

prepare_core_generated_headers
JOBS="$(detect_jobs)"
make -j"$JOBS"
make zip
