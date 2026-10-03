@echo off
rem Stage 3: VFS variants given with --vfs, and loading errors.
rem Every call opens the emulator window; close it to continue.
cd /d "%~dp0.."

echo === default VFS (no path)
call run.bat
echo === minimal VFS
call run.bat --vfs examples/vfs/minimal
echo === several files
call run.bat --vfs examples/vfs/files
echo === 3+ levels of nesting
call run.bat --vfs examples/vfs/deep
echo === VFS path does not exist
call run.bat --vfs examples/vfs/no_such_dir
echo === VFS path is a file (invalid format)
call run.bat --vfs README.md
