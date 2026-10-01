#!/bin/sh
ROOT="$(cd "$(dirname "$0")" && pwd)"
PYTHONPATH="$ROOT/src" exec python3 -m shell_emulator "$@"
