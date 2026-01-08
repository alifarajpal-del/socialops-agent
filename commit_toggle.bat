@echo off
chcp 65001 > nul
cd /d "%~dp0"

git add ui_components/inbox_view.py

git commit -m "feat(inbox): Add Append/Replace toggle for Insert Reply" ^
-m "- Added radio button with Append (default) and Replace options" ^
-m "- Positioned in 2-column layout with reply selector" ^
-m "- Minimal diff: +14 lines, cleaner UX"

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
