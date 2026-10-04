@echo off
rem Stage 3: VFS variants given in the config file.
rem Every call opens the emulator window; close it to continue.
cd /d "%~dp0.."

echo === minimal VFS
call run.bat --config examples/config/vfs_minimal.json
echo === several files
call run.bat --config examples/config/vfs_files.json
echo === 3+ levels of nesting
call run.bat --config examples/config/vfs_deep.json
echo === config points to a missing VFS
call run.bat --config examples/config/vfs_missing.json
echo === command line --vfs wins over the config
call run.bat --config examples/config/vfs_minimal.json --vfs ^
    examples/vfs/deep
