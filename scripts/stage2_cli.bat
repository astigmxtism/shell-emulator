@echo off
rem Stage 2: every command-line parameter, alone and together.
rem Every call opens the emulator window; close it to continue.
cd /d "%~dp0.."

echo === no parameters
call run.bat
echo === --vfs only
call run.bat --vfs examples/vfs/minimal
echo === --script only
call run.bat --script examples/scripts/stage2_demo.emu
echo === --config only
call run.bat --config examples/config/full.json
echo === all parameters (command line wins over the config file)
call run.bat --vfs examples/vfs/deep --script ^
    examples/scripts/stage2_demo.emu --config ^
    examples/config/full.json
