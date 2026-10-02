@echo off
rem Stage 2: config and startup script errors.
rem Every call opens the emulator window; close it to continue.
cd /d "%~dp0.."

echo === config file does not exist
call run.bat --config examples/config/missing.json
echo === config file is not valid JSON
call run.bat --config examples/config/broken.json
echo === config value has a wrong type
call run.bat --config examples/config/wrong_type.json
echo === startup script does not exist
call run.bat --script examples/scripts/missing.emu
echo === startup script with erroneous lines
call run.bat --script examples/scripts/stage2_errors.emu
echo === startup script with exit
call run.bat --script examples/scripts/stage2_exit.emu
echo === all parameters with a broken config and a script with errors
call run.bat --vfs examples/vfs/deep --script ^
    examples/scripts/stage2_errors.emu --config ^
    examples/config/broken.json
