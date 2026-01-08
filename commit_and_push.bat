@echo off
chcp 65001 > nul
cd /d "%~dp0"
git add -A
git commit -m "fix(sprint-a): Remove YAML dependency + fix translations - Remove pyyaml dependency from salons plugin - Embed all templates as Python dict (10 intents x 3 templates x 2 langs) - Add inbox translation key to French (kept scan for compatibility) - Create run_streamlit.bat for Windows UTF-8 encoding - All tests pass, no external dependencies, minimal diffs"
git push origin main
echo.
echo Git operations completed.
pause
