@echo off
chcp 65001 > nul
cd /d "%~dp0"

git add main.py ui_components/__init__.py ui_components/ui_kit.py ui_components/oauth_login.py ui_components/onboarding.py ui_components/camera_view.py ui_components/branding.py ui_components/dashboard_view.py utils/translations.py utils/i18n.py utils/__init__.py services/__init__.py services/auth_privacy.py tests/conftest.py

git commit -m "feat: Rebrand from BioGuard AI to SocialOps Agent" ^
-m "Complete rebrand with hero header and updated identity." ^
-m "" ^
-m "Changes:" ^
-m "- main.py: Page icon 💬, title SocialOps Agent" ^
-m "- ui_components/*: Updated all UI strings and docstrings" ^
-m "- utils/translations.py: Added hero i18n keys (app_title, app_subtitle, app_hero_*)" ^
-m "- utils/i18n.py: Updated app_name and login/register strings" ^
-m "- dashboard_view.py: Added hero header with KPI metrics" ^
-m "" ^
-m "Features:" ^
-m "- Hero header: App title, subtitle, 3 KPIs (threads/leads/tasks)" ^
-m "- Page icon: 💬 (chat bubble)" ^
-m "- All BioGuard to SocialOps Agent in UI" ^
-m "- i18n support: EN/AR/FR for hero" ^
-m "" ^
-m "Files: 14 modified, 93 translations added (31 keys × 3 langs)"

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
