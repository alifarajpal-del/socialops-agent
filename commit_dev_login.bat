@echo off
chcp 65001 > nul
cd /d "%~dp0"

git add services/auth.py ui_components/auth_ui.py

git commit -m "feat(auth): Add dev-only auto-login shortcut (admin/admin)" ^
-m "DEV ONLY: Quick login bypass for development/testing." ^
-m "" ^
-m "Changes:" ^
-m "  - services/auth.py: Auto-accept admin/admin credentials" ^
-m "  - ui_components/auth_ui.py: Show dev shortcut hint, set session keys" ^
-m "" ^
-m "Features:" ^
-m "  - Username: admin, Password: admin bypasses authentication" ^
-m "  - Sets session_state: authenticated=True, role=admin, user_id=999999" ^
-m "  - UI shows hint: Dev shortcut: admin / admin" ^
-m "  - Clearly marked as DEV ONLY in code comments" ^
-m "" ^
-m "Security: Remove or gate behind ENV flag in production"

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
