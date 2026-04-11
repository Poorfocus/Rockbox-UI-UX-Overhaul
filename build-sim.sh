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

    for tool in sdl2-config pkg-config; do
        if ! command -v "$tool" >/dev/null 2>&1; then
            echo "Error: missing simulator prerequisite '$tool' on PATH."
            missing=1
        fi
    done

    if [ "$missing" -ne 0 ]; then
        exit 2
    fi
}

# Copy every .fnt in repo/fonts/ into the runtime fonts dir, skipping files that are
# already up-to-date.  make install (wpsbuild.pl) only copies %Fl-referenced fonts;
# this ensures PictureFlow, fallback skins, and future WPS can also find their fonts.
sync_all_fonts() {
    local builddir="$1"
    local simfonts="$builddir/simdisk/.rockbox/fonts"
    local repofonts="../fonts"
    local copied=0

    if [ ! -d "$simfonts" ]; then
        echo "RockPod: [SKIP] sync_all_fonts: $simfonts does not exist."
        return
    fi

    for src in "$repofonts"/*.fnt; do
        [ -f "$src" ] || continue
        fname=$(basename "$src")
        dst="$simfonts/$fname"
        if [ ! -f "$dst" ] || [ "$src" -nt "$dst" ]; then
            cp "$src" "$dst"
            copied=$((copied + 1))
        fi
    done

    if [ "$copied" -gt 0 ]; then
        echo "RockPod: [sync] Copied $copied font(s) from repo/fonts/ to runtime (wpsbuild.pl gap)."
    fi
}

check_asset_freshness() {
    local simfonts="$1/simdisk/.rockbox/fonts"
    local repofonts="../fonts"
    local stale=0

    # All Apple2026 fonts from apple2026_rebuild_fonts_from_otf.py JOBS list
    # plus 15-Adobe-Helvetica (upstream fallback used by default failsafe theme)
    for fname in \
        35-SFProDisplay-Bold.fnt \
        28-SFProDisplay-Bold.fnt \
        25-SFProDisplay-Bold.fnt \
        22-SFProText-Regular.fnt \
        22-SFProText-Medium.fnt \
        22-SFCompactDisplay-Semibold.fnt \
        20-SFProText-Regular.fnt \
        20-SFProText-Medium.fnt \
        19-SFProText-Medium.fnt \
        19-SFProText-Semibold.fnt \
        18-SFProText-Regular.fnt \
        17-SFProText-Bold.fnt \
        16-SFProText-Medium.fnt \
        16-SFProText-Semibold.fnt \
        15-SFProText-Medium.fnt \
        15-SFProText-Semibold.fnt \
        14-SFProText-Regular.fnt \
        13-SFCompactText-Regular.fnt; do
        repo="$repofonts/$fname"
        runtime="$simfonts/$fname"
        if [ -f "$repo" ] && [ -f "$runtime" ] && [ "$repo" -nt "$runtime" ]; then
            echo "RockPod: [STALE] fonts/$fname is newer than runtime — run 'make install' inside build-sim/."
            stale=1
        elif [ -f "$repo" ] && [ ! -f "$runtime" ]; then
            echo "RockPod: [MISS]  fonts/$fname exists in repo but not in runtime — run 'make install' inside build-sim/."
            stale=1
        fi
    done

    if [ "$stale" -eq 0 ]; then
        echo "RockPod: [ok] Apple2026 runtime fonts are current."
    else
        echo "RockPod: [NOTE] Font sync: cd build-sim && make install   (or .\build-sim.ps1 -Incremental -SkipDep)"
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
        echo "Error: run this from a MinGW-family MSYS2 shell or use build-sim.ps1."
        exit 1
        ;;
esac

INCREMENTAL=0
INSTALL_ONLY=0
case "${ROCKPOD_INCREMENTAL:-}" in
    1|yes|true|YES|TRUE) INCREMENTAL=1 ;;
esac
case "${ROCKPOD_INSTALL_ONLY:-}" in
    1|yes|true|YES|TRUE) INSTALL_ONLY=1 ;;
esac
while [ $# -gt 0 ]; do
    case "$1" in
        -i|--incremental)
            INCREMENTAL=1
            shift
            ;;
        --install-only)
            INSTALL_ONLY=1
            shift
            ;;
        -h|--help)
            cat <<'EOF'
Usage: build-sim.sh [-i|--incremental] [--install-only]

  -i, --incremental   Reuse build-sim/ when already configured (faster iteration).
  --install-only      Skip configure/dep/compile; run only make install + freshness check.
                      Use after font/WPS/icon changes when the binary is already current.
                      (Sets INCREMENTAL=1 implicitly.)

Environment:
  ROCKPOD_INCREMENTAL=1    same as -i
  ROCKPOD_SKIP_DEP=1       skip make dep when make.dep exists
  ROCKPOD_INSTALL_ONLY=1   same as --install-only
  JOBS=N                   parallel job count

Default: remove build-sim/, full configure, make dep, build, make install.
EOF
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            echo "Try: build-sim.sh --help" >&2
            exit 1
            ;;
    esac
done

require_tools

BUILDDIR="build-sim"
WANT_STAMP="simulator ipod6g"

run_configure() {
    ../tools/configure --target=ipod6g --type=s
    printf '%s\n' "$WANT_STAMP" > .rockpod_configure_stamp
}

# --install-only: skip configure/dep/compile; sync assets only
if [ "$INSTALL_ONLY" -eq 1 ]; then
    echo "RockPod: install-only mode (font/theme sync without recompile)..."
    mkdir -p "$BUILDDIR"
    cd "$BUILDDIR" || exit 1
    if [ ! -f Makefile ]; then
        echo "Error: $BUILDDIR/Makefile not found — run a full build first."
        exit 1
    fi
    if ! make install; then
        echo "Warning: make install failed; simdisk install may be incomplete."
        if [ -n "${ROCKPOD_STRICT_INSTALL:-}" ]; then
            echo "RockPod: ROCKPOD_STRICT_INSTALL is set; failing the script."
            exit 1
        fi
    else
        touch .rockpod_install_stamp
    fi
    sync_all_fonts "$(pwd)"
    check_asset_freshness "$(pwd)"
    exit 0
fi

if [ "$INCREMENTAL" -eq 0 ]; then
    echo "RockPod: clean simulator build (removing ${BUILDDIR}/)..."
    rm -rf "$BUILDDIR"
    mkdir "$BUILDDIR"
    cd "$BUILDDIR" || exit 1
    run_configure
else
    echo "RockPod: incremental simulator build..."
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

# Pre-build generated headers (serial; guards against parallel header-before-use races).
# Skipped when all targets are demonstrably current (stamp matches source hash).
HEADERS_STAMP=".rockpod_headers_stamp"
HEADERS_NEED_REBUILD=1
if [ -f "$HEADERS_STAMP" ]; then
    # Sources that drive header generation: lang files, configure outputs, rbversion
    STAMP_DEPS="../apps/lang/ ../firmware/export/ ../tools/configure"
    newest=$(find $STAMP_DEPS -maxdepth 1 -name '*.c' -o -name '*.h' -o -name '*.lang' \
             -o -name '*.make' -o -name 'configure' 2>/dev/null \
             | xargs ls -t 2>/dev/null | head -n 1)
    if [ -z "$newest" ] || [ "$HEADERS_STAMP" -nt "$newest" ]; then
        HEADERS_NEED_REBUILD=0
    fi
fi
if [ "$HEADERS_NEED_REBUILD" -eq 1 ]; then
    prepare_core_generated_headers
    touch "$HEADERS_STAMP"
else
    echo "RockPod: generated headers stamp current — skipping prepare_core_generated_headers."
fi

JOBS="$(detect_jobs)"
make -j"$JOBS"
if ! make install; then
    echo "Warning: make install failed; simulator binary was built, but simdisk install is incomplete."
    if [ -n "${ROCKPOD_STRICT_INSTALL:-}" ]; then
        echo "RockPod: ROCKPOD_STRICT_INSTALL is set; failing the script."
        exit 1
    fi
else
    touch .rockpod_install_stamp
fi
# Sync all repo fonts to runtime — make install (wpsbuild.pl) only copies %Fl-referenced
# fonts; any font used by PictureFlow, WPS fallback, or future skins must also be present.
sync_all_fonts "$(pwd)"
check_asset_freshness "$(pwd)"

# Write config.cfg so Apple2026 theme loads automatically on simulator start.
SIMDISK="$(pwd)/simdisk/.rockbox"
if [ -d "$SIMDISK" ]; then
    cat > "$SIMDISK/config.cfg" <<'ROCKPOD_CFG'
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
font: /.rockbox/fonts/20-SFProText-Regular.fnt
statusbar: top
iconset: /.rockbox/icons/Apple2026Icons.bmp
viewers iconset: -
show icons: on
ui viewport: -
scrollbar: right
scrollbar width: 2
disable main menu scrolling: on
qs top: brightness
qs left: shuffle
qs right: repeat
qs bottom: sleeptimer duration
ROCKPOD_CFG
    echo "RockPod: config.cfg written to simdisk."
fi

# Normalize line endings in all text theme files to LF.
# Rockbox skin parser is LF-only; CRLF (Windows default) causes silent parse failure.
if command -v sed >/dev/null 2>&1; then
    find "$SIMDISK" -name "*.wps" -o -name "*.sbs" -o -name "*.fms" -o -name "*.cfg" \
        -o -name "*.theme" | while read -r tf; do
        sed -i 's/\r//' "$tf"
    done
    echo "RockPod: theme files normalized to LF."
fi
