#!/bin/sh
# Stage 3: VFS variants given in the config file.
# Every call opens the emulator window; close it to continue.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT" || exit 1

emu() {
    echo
    echo "=== run.sh $*"
    ./run.sh "$@"
}

# minimal VFS
emu --config examples/config/vfs_minimal.json
# several files
emu --config examples/config/vfs_files.json
# 3+ levels of nesting
emu --config examples/config/vfs_deep.json
# config points to a missing VFS
emu --config examples/config/vfs_missing.json
# command line --vfs wins over the config
emu --config examples/config/vfs_minimal.json --vfs examples/vfs/deep
