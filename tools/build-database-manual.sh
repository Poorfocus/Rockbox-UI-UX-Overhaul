#!/bin/sh
# Direct compile of the Rockbox database tool without the Rockbox build system.
# Run this from the repo root under MSYS2/UCRT64.

set -e

REPO="$(cd "$(dirname "$0")/.." && pwd)"
BDIR="$REPO/build-database"
SIMDISK="$REPO/build-sim/simdisk"
OUT="$BDIR/database_ipod6g.exe"

AUTOCONF="$BDIR/autoconf.h"
if [ ! -f "$AUTOCONF" ]; then
    echo "ERROR: run tools/build-database.sh first to run configure"
    exit 1
fi

mkdir -p "$BDIR/obj-manual"

SRCS="
$REPO/tools/database/database.c
$REPO/apps/misc.c
$REPO/apps/tagcache.c
$REPO/firmware/common/itoa_buf.c
$REPO/firmware/common/crc32.c
$REPO/firmware/common/pathfuncs.c
$REPO/firmware/common/strmemccpy.c
$REPO/firmware/common/strlcpy.c
$REPO/firmware/common/strcasestr.c
$REPO/firmware/common/unicode.c
$REPO/firmware/target/hosted/debug-hosted.c
$REPO/tools/database/logf_stub.c
$REPO/firmware/target/hosted/filesystem-win32.c
$REPO/uisimulator/common/filesystem-sim.c
$REPO/lib/fixedpoint/fixedpoint.c
"

METADATAS=$(ls "$REPO/lib/rbcodec/metadata/"*.c 2>/dev/null)

CC=/mingw64/bin/gcc

CFLAGS="-W -Wall -Wundef -Os -Wstrict-prototypes -pipe -std=gnu99 \
-funit-at-a-time -fno-delete-null-pointer-checks -fno-strict-overflow -fno-common \
-g -DDEBUG -D__PCTOOL__ -DDBTOOL -DWIN32 -DROCKBOX \
-DMEMORYSIZE=64 -DTARGET_ID=71 -DIPOD_6G \
-Wno-unused-result -Wno-pointer-sign -Wno-override-init -Wimplicit-fallthrough=0 \
-Wno-implicit-function-declaration \
-include $AUTOCONF \
-include $BDIR/target_name.h \
-I$REPO/apps \
-I$REPO/apps/gui \
-I$REPO/apps/recorder \
-I$REPO/firmware/export \
-I$REPO/firmware/include \
-I$REPO/firmware/kernel/include \
-I$REPO/firmware/target/hosted \
-I$REPO/firmware/target/hosted/sdl \
-I$REPO/firmware/target/hosted/sdl/database \
-I$REPO/lib/rbcodec \
-I$REPO/lib/rbcodec/metadata \
-I$REPO/lib/rbcodec/dsp \
-I$REPO/lib/fixedpoint \
-I$BDIR \
-I$REPO/uisimulator/sdl"

echo "--- Compiling database tool sources ---"
OBJS=""
for src in $SRCS $METADATAS; do
    [ -f "$src" ] || continue
    base=$(basename "$src" .c)
    obj="$BDIR/obj-manual/${base}.o"
    echo "  CC $base.c"
    eval $CC $CFLAGS -c $src -o $obj 2>&1 || { echo "FAILED: $src"; exit 1; }
    OBJS="$OBJS $obj"
done

echo "--- Linking $OUT ---"
$CC -o "$OUT" $OBJS -lm 2>&1
echo "--- Done ---"

echo ""
echo "--- Running database tool from: $SIMDISK ---"
cd "$SIMDISK"
"$OUT"
echo "--- Database generation done. Results: ---"
ls -lh "$SIMDISK/.rockbox"/database_*.tcd
