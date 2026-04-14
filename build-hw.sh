#!/bin/sh
set -e
cd "$(dirname "$0")"
APPLE2026_THEME_VERSION="Update3"

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

stage_repo_fonts_for_zip() {
    local tempdir="$1"
    local repofonts="../fonts"
    local staged=0

    mkdir -p "$tempdir/.rockbox/fonts"
    for src in "$repofonts"/*.fnt; do
        [ -f "$src" ] || continue
        cp "$src" "$tempdir/.rockbox/fonts/"
        staged=$((staged + 1))
    done

    if [ "$staged" -gt 0 ]; then
        echo "RockPod: staged $staged repo font(s) for rockbox.zip."
    fi
}

stage_repo_theme_payload_for_zip() {
    local tempdir="$1"
    local repowps="../wps"

    mkdir -p "$tempdir/.rockbox/wps/Apple2026"
    cp "$repowps/Apple2026.sbs" "$tempdir/.rockbox/wps/"
    cp "$repowps/Apple2026.wps" "$tempdir/.rockbox/wps/"
    cp "$repowps/Apple2026"/*.bmp "$tempdir/.rockbox/wps/Apple2026/"
    echo "RockPod: staged Apple2026 theme payload for rockbox.zip."
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
rm -f rockbox.zip
make -j"$JOBS"
make zip

# Inject default config.cfg into the zip so Apple2026 theme loads on first boot.
# This is idempotent: re-running the build simply overwrites the entry.
echo "RockPod: injecting config.cfg into rockbox.zip..."
if [ -f rockbox.zip ]; then
    TMPDIR_CFG="$(mktemp -d)"
    mkdir -p "$TMPDIR_CFG/.rockbox"
    mkdir -p "$TMPDIR_CFG/.rockbox/themes"
    cat > "$TMPDIR_CFG/.rockbox/config.cfg" <<'ROCKPOD_CFG'
wps: /.rockbox/wps/Apple2026.wps
fms: -
sbs: /.rockbox/wps/Apple2026.sbs
selector type: bar (color)
foreground color: 000000
background color: ffffff
line selector start color: E5E5EA
line selector end color: E5E5EA
line selector text color: 000000
list separator height: 1
list separator color: C6C6C8
font: /.rockbox/fonts/18-SFProText-Regular.fnt
statusbar: top
iconset: /.rockbox/icons/Apple2026Icons.bmp
viewers iconset: -
show icons: on
ui viewport: -
scrollbar: right
scrollbar width: 2
disable main menu scrolling: on
dynamic colors: off
backlight on button hold: normal
qs top: brightness
qs left: shuffle
qs right: repeat
qs bottom: brightness
ROCKPOD_CFG
    cat > "$TMPDIR_CFG/.rockbox/themes/Apple2026.cfg" <<'ROCKPOD_THEME'
#
# Apple2026.cfg generated by build-hw.sh staging
#
fms: -
wps: /.rockbox/wps/Apple2026.wps
sbs: /.rockbox/wps/Apple2026.sbs
selector type: bar (color)
foreground color: 000000
background color: ffffff
line selector start color: E5E5EA
line selector end color: E5E5EA
line selector text color: 000000
list separator height: 1
list separator color: C6C6C8
font: /.rockbox/fonts/18-SFProText-Regular.fnt
statusbar: top
iconset: /.rockbox/icons/Apple2026Icons.bmp
viewers iconset: -
show icons: on
ui viewport: -
scrollbar: right
scrollbar width: 2
disable main menu scrolling: on
dynamic colors: off
backlight on button hold: normal
qs top: brightness
qs left: shuffle
qs right: repeat
qs bottom: brightness
ROCKPOD_THEME
    printf '%s\n' "$APPLE2026_THEME_VERSION" > "$TMPDIR_CFG/.rockbox/.apple2026_version"
    stage_repo_fonts_for_zip "$TMPDIR_CFG"
    stage_repo_theme_payload_for_zip "$TMPDIR_CFG"
    OLDPWD="$(pwd)"
    cd "$TMPDIR_CFG" || exit 1
    zip -q -u "$OLDPWD/rockbox.zip" ".rockbox/config.cfg"
    zip -q -u "$OLDPWD/rockbox.zip" ".rockbox/themes/Apple2026.cfg"
    zip -q -u "$OLDPWD/rockbox.zip" ".rockbox/.apple2026_version"
    zip -q -u -r "$OLDPWD/rockbox.zip" ".rockbox/fonts"
    zip -q -u "$OLDPWD/rockbox.zip" ".rockbox/wps/Apple2026.sbs"
    zip -q -u "$OLDPWD/rockbox.zip" ".rockbox/wps/Apple2026.wps"
    zip -q -u -r "$OLDPWD/rockbox.zip" ".rockbox/wps/Apple2026"
    cd "$OLDPWD" || exit 1
    rm -rf "$TMPDIR_CFG"
    echo "RockPod: config.cfg injected."
else
    echo "RockPod: WARNING — config.cfg injection skipped (rockbox.zip missing)."
fi
echo "RockPod: auditing Apple2026 source vs rockbox.zip..."
python3 ../tools/apple2026_skin_audit.py --zip-artifact rockbox.zip
echo "RockPod: auditing packaged hardware plugins..."
python3 ../tools/verify_plugin_package.py \
    --build-dir "$(pwd)" \
    --zip-artifact rockbox.zip
