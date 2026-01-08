"""Simple onboarding flow shown once per user session - 2 screens only."""

import streamlit as st
from utils.translations import get_text
from ui_components.ui_kit import inject_ui_kit_css


def get_screens(lang: str) -> list:
    """Get onboarding screens in the specified language (2 screens only)."""
    privacy_title = "Privacy & Data Control"
    privacy_body = """
            SocialOps Agent uses AI to help you manage conversations, leads, and operations across social platforms.

            • We only process data you explicitly connect
            • Messages are used to generate replies and insights
            • No data is shared with third parties
            • You remain in full control at all times
            """
    return [
        {
            "title": privacy_title,
            "body": privacy_body,
            "icon": "🔐",
        },
        {
            "title": privacy_title,
            "body": privacy_body,
            "icon": "🛡️",
        },
    ]


def render_onboarding() -> None:
    """Render 2-screen onboarding flow with consistent styling."""
    if st.session_state.get("onboarding_done"):
        return
    
    inject_ui_kit_css()
    
    # Get current language
    lang = st.session_state.get("language", "ar")
    screens = get_screens(lang)

    # Center all onboarding content
    st.markdown("""
    <style>
        .onboarding-container {
            max-width: 650px;
            margin: 0 auto;
            padding: 20px;
        }
        .onboarding-screen {
            background: #141414;
            border: 1px solid #2A2A2A;
            border-radius: 16px;
            padding: 32px 24px;
            margin: 16px 0;
            text-align: center;
            color: #F5F5F5;
        }
        .onboarding-icon {
            font-size: 64px;
            margin-bottom: 16px;
        }
        .onboarding-title {
            font-size: 24px;
            font-weight: 700;
            color: #F5F5F5;
            margin-bottom: 16px;
        }
        .onboarding-body {
            font-size: 15px;
            line-height: 1.8;
            color: #A1A1A1;
            text-align: left;
            direction: ltr;
        }
        .onboarding-body strong {
            color: #F5F5F5;
            font-weight: 600;
        }
        .welcome-title {
            text-align: center;
            font-size: 32px;
            font-weight: 800;
            color: #C9A24D;
            margin-bottom: 32px;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="onboarding-container">', unsafe_allow_html=True)
    
    st.markdown('<div class="welcome-title">مرحباً بك في SocialOps Agent 💬</div>', unsafe_allow_html=True)
    
    for screen in screens:
        st.markdown(f'''
        <div class="onboarding-screen">
            <div class="onboarding-icon">{screen["icon"]}</div>
            <div class="onboarding-title">{screen["title"]}</div>
            <div class="onboarding-body">{screen["body"]}</div>
        </div>
        ''', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("🚀 ابدأ الآن", type="primary", use_container_width=True):
        st.session_state.onboarding_done = True
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

