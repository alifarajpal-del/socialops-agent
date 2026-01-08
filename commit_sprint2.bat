@echo off
chcp 65001 > nul
cd /d "%~dp0"

git commit -m "feat(sprint-2): Add CRM with leads pipeline and task management" ^
-m "Sprint 2 deliverables:" ^
-m "- CRM backend with leads/tasks tables" ^
-m "- Leads pipeline UI with 5 status tabs" ^
-m "- Inbox integration with CRM Actions section" ^
-m "- Task management with follow-up scheduling" ^
-m "- Navigation updated with Leads page" ^
-m "- Comprehensive smoke tests" ^
-m "" ^
-m "Changes:" ^
-m "- services/crm_store.py: CREATED (461 lines)" ^
-m "- ui_components/leads_view.py: REWRITTEN" ^
-m "- ui_components/inbox_view.py: MODIFIED" ^
-m "- ui_components/navigation.py: MODIFIED" ^
-m "- ui_components/router.py: MODIFIED" ^
-m "- main.py: MODIFIED" ^
-m "- tests/crm_smoke.py: CREATED" ^
-m "- test_sprint2.bat: CREATED" ^
-m "" ^
-m "Tables: leads (11 fields), tasks (9 fields)" ^
-m "Tests: 100%% pass rate" ^
-m "Zero new dependencies. SQLite only."

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Commit successful
    echo.
    echo Pushing to GitHub...
    git push origin main
    
    if %ERRORLEVEL% EQU 0 (
        echo.
        echo ✅ Push successful
    ) else (
        echo.
        echo ❌ Push failed
        exit /b 1
    )
) else (
    echo.
    echo ❌ Commit failed
    exit /b 1
)
