#!/bin/sh
# Stage 2: config and startup script errors.
# Every call opens the emulator window; close it to continue.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT" || exit 1

emu() {
    echo
    echo "=== run.sh $*"
    ./run.sh "$@"
}

# config file does not exist
emu --config examples/config/missing.json
# config file is not valid JSON
emu --config examples/config/broken.json
# config value has a wrong type
emu --config examples/config/wrong_type.json
# startup script does not exist
emu --script examples/scripts/missing.emu
# startup script with erroneous lines
emu --script examples/scripts/stage2_errors.emu
# startup script with exit
emu --script examples/scripts/stage2_exit.emu
# all parameters with a broken config and a script with errors
emu --vfs examples/vfs/deep --script \
    examples/scripts/stage2_errors.emu --config \
    examples/config/broken.json
