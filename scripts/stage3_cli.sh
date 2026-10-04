#!/bin/sh
# Stage 3: VFS variants given with --vfs, and loading errors.
# Every call opens the emulator window; close it to continue.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT" || exit 1

emu() {
    echo
    echo "=== run.sh $*"
    ./run.sh "$@"
}

# default VFS (no path)
emu
# minimal VFS
emu --vfs examples/vfs/minimal
# several files
emu --vfs examples/vfs/files
# 3+ levels of nesting
emu --vfs examples/vfs/deep
# VFS path does not exist
emu --vfs examples/vfs/no_such_dir
# VFS path is a file (invalid format)
emu --vfs README.md
