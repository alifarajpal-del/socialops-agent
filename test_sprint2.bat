@echo off
chcp 65001 > nul
cd /d "%~dp0"

echo ====================================
echo Sprint 2: Compilation Check
echo ====================================
echo.

python -m py_compile main.py ui_components/leads_view.py ui_components/inbox_view.py services/crm_store.py tests/crm_smoke.py ui_components/navigation.py ui_components/router.py

if %ERRORLEVEL% EQU 0 (
    echo ✅ All files compiled successfully
    echo.
) else (
    echo ❌ Compilation failed
    exit /b 1
)

echo ====================================
echo Sprint 2: Running Tests
echo ====================================
echo.

python tests/crm_smoke.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ All tests passed
) else (
    echo.
    echo ❌ Tests failed
    exit /b 1
)

pause
