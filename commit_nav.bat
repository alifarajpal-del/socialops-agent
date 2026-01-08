@echo off
chcp 65001 > nul
cd /d "%~dp0"

git add -A
git commit -m "refactor(nav): Revert to 4-button navigation, move Leads to Settings" ^
-m "- Bottom nav: 4 buttons (dashboard, inbox, vault, settings)" ^
-m "- Leads accessible via Settings page" ^
-m "- Routing unchanged, minimal diff"

if %ERRORLEVEL% EQU 0 (
    echo ✅ Commit successful
    git push origin main
    if %ERRORLEVEL% EQU 0 (
        echo ✅ Push successful
    ) else (
        echo ❌ Push failed
        exit /b 1
    )
) else (
    echo ❌ Commit failed
    exit /b 1
)
