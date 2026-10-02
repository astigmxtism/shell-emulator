#!/bin/sh
# Stage 2: config file values and their priority.
# Every call opens the emulator window; close it to continue.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT" || exit 1

emu() {
    echo
    echo "=== run.sh $*"
    ./run.sh "$@"
}

# config provides both values
emu --config examples/config/full.json
# config provides vfs_path, script comes from the command line
emu --config examples/config/vfs_only.json --script \
    examples/scripts/stage2_demo.emu
# command line --vfs overrides vfs_path from the config
emu --config examples/config/full.json --vfs examples/vfs/minimal
# all parameters
emu --vfs examples/vfs/deep --script examples/scripts/stage2_demo.emu \
    --config examples/config/full.json
