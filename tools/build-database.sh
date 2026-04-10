#!/bin/sh
# Build the Rockbox database tool for iPod Classic 6G (target 29, type D)
# and generate the tagcache database from build-sim/simdisk/
set -e

REPO="$(cd "$(dirname "$0")/.." && pwd)"
BDIR="$REPO/build-database"

mkdir -p "$BDIR"
cd "$BDIR"

if [ ! -f Makefile ]; then
    echo "--- Configuring database tool (target 29=iPod Classic/6G, type D) ---"
    printf "29\nD\n" | "$REPO/tools/configure"
    echo "--- configure done ---"
fi

echo "--- Building database tool ---"
make -j4
echo "--- Build done ---"

# Find the built binary
DB_BIN=$(ls "$BDIR"/database_ipod6g.exe "$BDIR"/database.ipod6g 2>/dev/null | head -1)
echo "Database binary: ${DB_BIN:-NOT FOUND}"

if [ -n "$DB_BIN" ]; then
    SIMDISK="$REPO/build-sim/simdisk"
    echo "--- Running database tool from simdisk: $SIMDISK ---"
    cd "$SIMDISK"
    "$DB_BIN"
    echo "--- Database generation done ---"
    ls -la "$SIMDISK/.rockbox"/database_*.tcd
fi
