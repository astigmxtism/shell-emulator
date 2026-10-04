#!/bin/sh
# Stage 3: VFS variants with the startup script for stages 1-3.
# Every call opens the emulator window; close it to continue.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT" || exit 1

emu() {
    echo
    echo "=== run.sh $*"
    ./run.sh "$@"
}

# minimal VFS
emu --vfs examples/vfs/minimal --script \
    examples/scripts/stage3_all.emu
# several files
emu --vfs examples/vfs/files --script examples/scripts/stage3_all.emu
# 3+ levels of nesting
emu --vfs examples/vfs/deep --script examples/scripts/stage3_all.emu
# default VFS
emu --script examples/scripts/stage3_all.emu
# missing VFS
emu --vfs examples/vfs/no_such_dir --script \
    examples/scripts/stage3_all.emu
