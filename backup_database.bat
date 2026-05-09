@echo off
cd /d %~dp0
if not exist backups mkdir backups
for /f "tokens=1-4 delims=/ " %%a in ("%date%") do set mydate=%%d%%b%%c
for /f "tokens=1-2 delims=: " %%a in ("%time%") do set mytime=%%a%%b
copy data\task_tracker.db backups\task_tracker_backup_%mydate%_%mytime%.db
echo Backup completed.
pause
