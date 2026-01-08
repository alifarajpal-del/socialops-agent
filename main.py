"""
SocialOps Agent - Social Media Operations Platform
Modular UI with bottom navigation, theme wheel, and operations dashboard.
"""

import os
import logging

import streamlit as st
from PIL import Image

logger = logging.getLogger(__name__)

# Configure Streamlit early


def _get_page_icon():
    """Load app icon from branding assets if available."""
    logo_path = os.path.join("ui_components", "assets", "logo.png")
    if os.path.exists(logo_path):
        try:
            return Image.open(logo_path)
        except Exception:
            return "💬"
    return "💬"


st.set_page_config(
    page_title="SocialOps Agent",
    page_icon=_get_page_icon(),
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Build marker for deployment verification
st.sidebar.caption("🔄 BUILD: SocialOps Agent v2.0 | Commit: 960b832")

# Theme toggle in sidebar
st.sidebar.divider()
from utils.translations import get_text
from utils.i18n import get_lang

lang = get_lang()
current_theme = st.session_state.get("theme", "light")

theme_choice = st.sidebar.radio(
    get_text("theme", lang),
    options=["light", "dark"],
    index=0 if current_theme == "light" else 1,
    format_func=lambda x: get_text(f"theme_{x}", lang),
    key="theme_toggle"
)

if theme_choice != current_theme:
    st.session_state["theme"] = theme_choice
    # Reset CSS injection to apply new theme
    if "_css_injected" in st.session_state:
        del st.session_state["_css_injected"]
    st.rerun()

# Imports
from app_config.settings import MOBILE_VIEWPORT
from ui_components.theme_wheel import render_theme_wheel
from ui_components.navigation import render_bottom_navigation, get_active_page
from ui_components.dashboard_view import render_dashboard
from ui_components.vault_view import render_vault
from ui_components.oauth_login import render_oauth_login, handle_oauth_callback
from ui_components.global_styles import inject_global_css
from ui_components.branding import render_brand_header
from ui_components.onboarding import render_onboarding
from ui_components.router import ensure_nav_state, go_to, go_back, next_page, prev_page
from ui_components.error_ui import safe_render
from services.auth import create_or_login_user, logout
from utils.i18n import get_lang, set_lang, t

# Camera view - choose version
try:
    from ui_components.camera_view_refactored import render_camera_view as render_camera_new
    REFACTORED_CAMERA_AVAILABLE = True
except ImportError:
    REFACTORED_CAMERA_AVAILABLE = False
    render_camera_new = None

from ui_components.camera_view import render_camera_view as render_camera_legacy
from ui_components.inbox_view import inbox_view
from ui_components.leads_view import leads_view
from ui_components.replies_view import replies_view
from ui_components.settings_channels_view import settings_channels_view
from ui_components.workspace_view import workspace_view
from ui_components.search_view import search_view
from ui_components.ops_view import ops_view

PAGE_SUBTITLES = {
    "dashboard": "Health Dashboard",
    "inbox": "Unified Inbox",
    "vault": "Medical Vault",
    "settings": "Settings & Theme",
    "channels": "Channel Integrations",
    "workspace": "Business Profile",
    "search": "Search",
    "ops": "Daily Operations",
}


# ============== Session State Initialization ==============

def init_session_state() -> None:
    """Initialize session state variables."""
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user_profile" not in st.session_state:
        st.session_state.user_profile = None
    if "active_theme" not in st.session_state:
        st.session_state.active_theme = "dark"
    if "analysis_history" not in st.session_state:
        st.session_state.analysis_history = []
    if "ai_provider" not in st.session_state:
        st.session_state.ai_provider = "gemini"
    if "use_refactored_camera" not in st.session_state:
        st.session_state.use_refactored_camera = REFACTORED_CAMERA_AVAILABLE
    # Initialize language with default English
    get_lang()  # This will set to "en" if not already set
    ensure_nav_state()
    if "onboarding_done" not in st.session_state:
        st.session_state.onboarding_done = False
    
    # Register plugins (Sprint A)
    if "plugins_registered" not in st.session_state:
        _register_plugins()
        st.session_state.plugins_registered = True


def _register_plugins() -> None:
    """Register available plugins with the plugin registry."""
    try:
        from services.plugins_registry import register_plugin
        from plugins.salons.plugin import SalonsPlugin
        
        # Register salons plugin
        salons = SalonsPlugin()
        register_plugin(salons)
        logger.info("Plugins registered successfully")
    except Exception as e:
        logger.error(f"Failed to register plugins: {e}")


# ============== Authentication UI ==============

def render_auth_screen() -> None:
    """Render login/register authentication screen."""
    from ui_components.auth_ui import render_login_register
    render_login_register()


# ============== Settings Page ==============

def render_settings_page() -> None:
    """Render settings page with safe error handling."""
    safe_render(_render_settings_inner, context="settings")


def _render_settings_inner() -> None:
    # Back button
    if st.button(f"⬅️ {t('go_home')}", key="settings_back_home"):
        go_back()
    
    st.markdown(f"## ⚙️ {t('settings_title')}")
    
    # Language selector
    st.markdown("### 🌍 Language / اللغة")
    current_lang = get_lang()
    lang_choice = st.selectbox(
        "Choose your language",
        options=["English", "العربية"],
        index=0 if current_lang == "en" else 1,
        key="language_selector"
    )
    new_lang = "en" if lang_choice == "English" else "ar"
    if new_lang != current_lang:
        set_lang(new_lang)
        st.rerun()
    st.divider()
    
    render_theme_wheel()
    st.divider()

    st.markdown("### 🤖 AI Provider")
    st.session_state.ai_provider = st.selectbox(
        "Choose AI engine",
        options=["gemini", "openai", "mock"],
        index=["gemini", "openai", "mock"].index(st.session_state.ai_provider or "gemini"),
        format_func=lambda x: {
            "gemini": "Gemini Vision",
            "openai": "OpenAI Vision",
            "mock": "Mock (offline)",
        }.get(x, x),
    )
    st.caption("Will use preferred engine, then fallback to others or mock mode if failed.")
    st.divider()
    
    # Camera view selector
    if REFACTORED_CAMERA_AVAILABLE:
        st.markdown("### 📸 Camera Version")
        use_new = st.checkbox(
            "Use Refactored Camera (Recommended)",
            value=st.session_state.use_refactored_camera,
            help="New modular camera with better performance and cleaner UI"
        )
        st.session_state.use_refactored_camera = use_new
        st.divider()

    st.markdown("### 👤 Profile")
    user = st.session_state.user_profile or {}
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Name", value=user.get("name", ""), key="profile_name")
        st.number_input("Age", value=user.get("age", 30), key="profile_age")
    with col2:
        st.number_input("Weight (kg)", value=user.get("weight", 70.0), key="profile_weight")
        st.number_input("Height (cm)", value=user.get("height", 170), key="profile_height")
    if st.button("💾 Save", width="stretch"):
        st.success("Profile saved locally")

    st.divider()
    
    # Link to channel settings
    st.markdown("### 🔌 Channel Integrations")
    if st.button("⚙️ Configure Instagram, Facebook, WhatsApp", use_container_width=True):
        go_to("channels")
    
    st.divider()
    
    # Workspace Profile
    st.markdown("### 🏢 Workspace Profile")
    if st.button("✏️ Edit Business Profile", use_container_width=True):
        go_to("workspace")
    
    st.divider()
    
    # Plan & Limits (Sprint 4)
    st.markdown("### 📊 Plan & Limits")
    from services.settings_flags import get_plan, get_plan_limits, enable_billing
    
    plan = get_plan()
    limits = get_plan_limits()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Current Plan", plan.capitalize())
        st.caption("Local mode (no billing)")
    
    with col2:
        if limits['max_threads'] == -1:
            st.metric("Max Threads", "Unlimited")
        else:
            st.metric("Max Threads", limits['max_threads'])
        
        if limits['max_replies'] == -1:
            st.metric("Max Replies", "Unlimited")
        else:
            st.metric("Max Replies", limits['max_replies'])
    
    if enable_billing():
        st.info("💰 Billing enabled - Upgrade available")
    else:
        st.info("💡 Tip: All features work locally without payment")
    
    # Export Data (Sprint 5)
    st.markdown(f"#### 📥 {t('export_title')}")
    from services.export_service import export_leads_csv, export_tasks_csv, export_threads_csv, export_all_data_zip
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        leads_csv = export_leads_csv()
        st.download_button(
            t('export_leads'),
            data=leads_csv,
            file_name="leads.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        tasks_csv = export_tasks_csv()
        st.download_button(
            t('export_tasks'),
            data=tasks_csv,
            file_name="tasks.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col3:
        threads_csv = export_threads_csv()
        st.download_button(
            t('export_threads'),
            data=threads_csv,
            file_name="threads.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col4:
        all_zip = export_all_data_zip()
        st.download_button(
            t('export_all'),
            data=all_zip,
            file_name="socialops_export.zip",
            mime="application/zip",
            use_container_width=True
        )
    
    st.divider()
    
    # Link to CRM/Leads (Sprint 2)
    st.markdown(f"### 📊 {t('crm_leads_title')}")
    if st.button(f"👥 {t('crm_leads_button')}", use_container_width=True):
        go_to("leads")
    st.caption(t('crm_leads_caption'))
    
    st.divider()
    
    # Link to Replies Library (Sprint 3)
    st.markdown(f"### 💬 {t('replies_title')}")
    if st.button(f"📝 {t('replies_button')}", use_container_width=True):
        go_to("replies")
    st.caption(t('replies_caption'))
    
    st.divider()
    
    st.markdown("### 🩺 Diagnostics")
    with st.expander("System Info", expanded=False):
        st.write({
            "current_page": st.session_state.get("current_page", "N/A"),
            "nav_stack_depth": len(st.session_state.get("nav_stack", [])),
            "authenticated": st.session_state.get("authenticated", False),
            "onboarding_done": st.session_state.get("onboarding_done", False),
            "ai_provider": st.session_state.get("ai_provider", "N/A"),
            "active_theme": st.session_state.get("active_theme", "N/A"),
        })
    
    st.divider()
    if st.button("🚪 Logout", width="stretch"):
        logout(st.session_state.user_id or "")
        st.session_state.authenticated = False
        st.session_state.user_id = None
        st.session_state.user_profile = None
        st.rerun()


# ============== Main Application ==============

def main() -> None:
    init_session_state()
    st.markdown(MOBILE_VIEWPORT, unsafe_allow_html=True)
    inject_global_css()

    if not st.session_state.authenticated:
        render_auth_screen()
        return

    if not st.session_state.onboarding_done:
        render_onboarding()
        return

    def _handle_swipe_navigation() -> None:
        """Update current_page based on swipe gestures."""
        if st.session_state.get("swipe_next"):
            st.session_state.swipe_next = False
            go_to(next_page())

        if st.session_state.get("swipe_prev"):
            st.session_state.swipe_prev = False
            go_to(prev_page())

    _handle_swipe_navigation()

    page = get_active_page()

    # Don't show header/back button for inbox (has its own header)
    if page not in ["inbox", "channels", "leads", "replies", "workspace", "search", "ops"]:
        render_brand_header(subtitle=PAGE_SUBTITLES.get(page, "BioGuard AI"))
        if page != "dashboard" and st.session_state.get("nav_stack"):
            if st.button("⬅️ رجوع", key="back_btn_top"):
                go_back()

    if page == "dashboard":
        render_dashboard()
    elif page == "inbox":
        inbox_view()
    elif page == "leads":
        leads_view()
    elif page == "replies":
        replies_view()
    elif page == "vault":
        render_vault()
    elif page == "settings":
        render_settings_page()
    elif page == "channels":
        settings_channels_view()
    elif page == "workspace":
        workspace_view()
    elif page == "search":
        search_view()
    elif page == "ops":
        ops_view()

    render_bottom_navigation()


if __name__ == "__main__":
    main()
