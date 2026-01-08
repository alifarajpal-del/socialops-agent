@echo off
chcp 65001 > nul
cd /d "%~dp0"

git add services/db.py services/inbox_store.py services/crm_store.py services/replies_store.py

git commit -m "refactor(db): Unify database path with shared get_db_path()" ^
-m "Single source of truth for DB path across all stores." ^
-m "" ^
-m "Changes:" ^
-m "- services/db.py: CREATED - Shared get_db_path() function" ^
-m "- services/inbox_store.py: MODIFIED - Use get_db_path()" ^
-m "- services/crm_store.py: MODIFIED - Use get_db_path()" ^
-m "- services/replies_store.py: MODIFIED - Use get_db_path()" ^
-m "" ^
-m "Benefits:" ^
-m "- Single source of truth for database path" ^
-m "- Environment variable override support (SOCIALOPS_DB_PATH)" ^
-m "- Consistent behavior across InboxStore, CRMStore, RepliesStore" ^
-m "" ^
-m "Tests: All smoke tests passing (manual_import, crm, sprint3)" ^
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
