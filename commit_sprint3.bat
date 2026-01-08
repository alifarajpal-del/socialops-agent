@echo off
chcp 65001 > nul
cd /d "%~dp0"

git commit -m "feat(sprint-3): Replies Library + SLA + Follow-up + i18n fix" ^
-m "Sprint 3 deliverables:" ^
-m "- Replies Library with DB backend and UI" ^
-m "- SLA status computation (ok/warning/urgent)" ^
-m "- Follow-up time suggestions by priority" ^
-m "- Insert saved reply in inbox" ^
-m "- i18n fix for CRM/Leads in Settings" ^
-m "" ^
-m "Changes:" ^
-m "- services/replies_store.py: CREATED (360 lines)" ^
-m "- ui_components/replies_view.py: CREATED (160 lines)" ^
-m "- services/inbox_engine.py: MODIFIED (+92 lines SLA/followup)" ^
-m "- ui_components/inbox_view.py: MODIFIED (+32 lines insert)" ^
-m "- utils/translations.py: MODIFIED (+30 lines i18n keys)" ^
-m "- main.py: MODIFIED (replies routing + i18n fix)" ^
-m "- ui_components/router.py: MODIFIED (replies page)" ^
-m "- tests/sprint3_smoke.py: CREATED (4 tests)" ^
-m "" ^
-m "Features:" ^
-m "- Replies CRUD: create, list, update, delete" ^
-m "- Seed 10 default templates (5 EN + 5 AR)" ^
-m "- Filter by lang/scope/plugin" ^
-m "- SLA thresholds: 4h warning, 24h urgent" ^
-m "- Priority-based followup: 1h-72h" ^
-m "" ^
-m "Tests: 100%% pass rate (4/4)" ^
-m "Zero new dependencies. Minimal diffs."

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
