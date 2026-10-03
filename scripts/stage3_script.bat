@echo off
rem Stage 3: VFS variants with the startup script for stages 1-3.
rem Every call opens the emulator window; close it to continue.
cd /d "%~dp0.."

echo === minimal VFS
call run.bat --vfs examples/vfs/minimal --script ^
    examples/scripts/stage3_all.emu
echo === several files
call run.bat --vfs examples/vfs/files --script ^
    examples/scripts/stage3_all.emu
echo === 3+ levels of nesting
call run.bat --vfs examples/vfs/deep --script ^
    examples/scripts/stage3_all.emu
echo === default VFS
call run.bat --script examples/scripts/stage3_all.emu
echo === missing VFS
call run.bat --vfs examples/vfs/no_such_dir --script ^
    examples/scripts/stage3_all.emu
