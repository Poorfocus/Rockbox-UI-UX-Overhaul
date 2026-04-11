#!/bin/bash
export PATH="/ucrt64/bin:/mingw64/bin:/usr/bin:$PATH"
LOG="/tmp/rockpod-hw-build.log"
echo "Starting iPod 6G build at $(date)" | tee "$LOG"
cd /c/Users/Jason/Documents/Rockpod/rockpod/build-hw-ipod6g
echo "Running make in: $PWD" | tee -a "$LOG"
make -j4 2>&1 | tee -a "$LOG"
echo "MAKE_EXIT:$?" | tee -a "$LOG"
echo "Running make install..." | tee -a "$LOG"
make install 2>&1 | tee -a "$LOG"
echo "INSTALL_EXIT:$?" | tee -a "$LOG"
