@echo off
cd /d "%USERPROFILE%\titanic-pipeline"
python scripts\run_pipeline.py > logs\pipeline_log.txt 2>&1
echo %date% %time% exit code %errorlevel% >> logs\history.txt
