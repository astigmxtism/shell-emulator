#!/bin/sh
# Stage 2: every command-line parameter, alone and together.
# Every call opens the emulator window; close it to continue.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT" || exit 1

emu() {
    echo
    echo "=== run.sh $*"
    ./run.sh "$@"
}

# no parameters
emu
# --vfs only
emu --vfs examples/vfs/minimal
# --script only
emu --script examples/scripts/stage2_demo.emu
# --config only
emu --config examples/config/full.json
# all parameters (command line wins over the config file)
emu --vfs examples/vfs/deep --script examples/scripts/stage2_demo.emu \
    --config examples/config/full.json
