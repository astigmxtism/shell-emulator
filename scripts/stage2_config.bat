@echo off
rem Stage 2: config file values and their priority.
rem Every call opens the emulator window; close it to continue.
cd /d "%~dp0.."

echo === config provides both values
call run.bat --config examples/config/full.json
echo === config provides vfs_path, script comes from the command line
call run.bat --config examples/config/vfs_only.json --script ^
    examples/scripts/stage2_demo.emu
echo === command line --vfs overrides vfs_path from the config
call run.bat --config examples/config/full.json --vfs ^
    examples/vfs/minimal
echo === all parameters
call run.bat --vfs examples/vfs/deep --script ^
    examples/scripts/stage2_demo.emu --config ^
    examples/config/full.json
