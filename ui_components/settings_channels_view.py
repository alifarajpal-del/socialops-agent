"""
Channel Integration Settings View - Sprint A Implementation.

Shows connection status for Meta (Instagram/Facebook) and WhatsApp.
Works without secrets - displays missing keys and setup instructions.
"""

import streamlit as st
import logging
from typing import Dict, Any, List

from ui_components import ui_kit

logger = logging.getLogger(__name__)


def check_meta_credentials() -> Dict[str, Any]:
    """
    Check if Meta credentials are configured.
    
    Returns:
        {"configured": bool, "found": List[str], "missing": List[str]}
    """
    required = [
        "META_APP_ID",
        "META_APP_SECRET",
        "META_PAGE_ACCESS_TOKEN",
        "IG_BUSINESS_ACCOUNT_ID"
    ]
    
    found = []
    missing = []
    
    try:
        meta_secrets = st.secrets.get('meta', {})
        for key in required:
            if key in meta_secrets and meta_secrets[key]:
                found.append(key)
            else:
                missing.append(key)
    except:
        missing = required
    
    return {
        'configured': len(found) == len(required),
        'found': found,
        'missing': missing
    }


def check_whatsapp_credentials() -> Dict[str, Any]:
    """
    Check if WhatsApp credentials are configured.
    
    Returns:
        {"configured": bool, "found": List[str], "missing": List[str]}
    """
    required = [
        "WHATSAPP_ACCESS_TOKEN",
        "WHATSAPP_PHONE_NUMBER_ID"
    ]
    
    found = []
    missing = []
    
    try:
        wa_secrets = st.secrets.get('whatsapp', {})
        for key in required:
            if key in wa_secrets and wa_secrets[key]:
                found.append(key)
            else:
                missing.append(key)
    except:
        missing = required
    
    return {
        'configured': len(found) == len(required),
        'found': found,
        'missing': missing
    }


def render_meta_section():
    """Render Meta (Instagram/Facebook) integration status."""
    with ui_kit.card(title="Meta Platform (Instagram & Facebook)", icon="📷"):
        status = check_meta_credentials()
        
        if status['configured']:
            st.success("✅ Connected")
            st.caption(f"Keys configured: {', '.join(status['found'])}")
        else:
            st.error("❌ Not Connected")
            if status['found']:
                st.caption(f"✓ Found: {', '.join(status['found'])}")
            if status['missing']:
                st.caption(f"✗ Missing: {', '.join(status['missing'])}")
        
        st.divider()
        
        with st.expander("📚 Setup Instructions", expanded=not status['configured']):
            st.markdown("""
            ### Meta Integration Setup
            
            **1. Create Meta App:**
            - Go to [Meta Developers](https://developers.facebook.com/)
            - Create new app → Select "Business" type
            - Add Instagram and Facebook products
            
            **2. Get Credentials:**
            - **APP_ID**: App dashboard
            - **APP_SECRET**: Settings → Basic
            - **PAGE_ACCESS_TOKEN**: Graph API Explorer
            - **IG_BUSINESS_ACCOUNT_ID**: Instagram settings
            
            **3. Configure Secrets:**
            
            Add to Streamlit Cloud → App settings → Secrets:
            ```toml
            [meta]
            META_APP_ID = "your_app_id"
            META_APP_SECRET = "your_app_secret"
            META_PAGE_ACCESS_TOKEN = "your_token"
            IG_BUSINESS_ACCOUNT_ID = "your_ig_id"
            ```
            
            **4. Set Permissions:**
            - `instagram_basic`
            - `instagram_manage_messages`
            - `pages_messaging`
            - `pages_read_engagement`
            
            **Note:** App works without credentials using Manual Import.
            """)


def render_whatsapp_section():
    """Render WhatsApp Business API integration status."""
    with ui_kit.card(title="WhatsApp Business API", icon="💬"):
        status = check_whatsapp_credentials()
        
        if status['configured']:
            st.success("✅ Connected")
            st.caption(f"Keys configured: {', '.join(status['found'])}")
        else:
            st.error("❌ Not Connected")
            if status['found']:
                st.caption(f"✓ Found: {', '.join(status['found'])}")
            if status['missing']:
                st.caption(f"✗ Missing: {', '.join(status['missing'])}")
        
        st.divider()
        
        with st.expander("📚 Setup Instructions", expanded=not status['configured']):
            st.markdown("""
            ### WhatsApp Business API Setup
            
            **1. Get WhatsApp Business Account:**
            - Via [Meta Business Suite](https://business.facebook.com/)
            - Or WhatsApp provider (Twilio, MessageBird, etc.)
            
            **2. Get Credentials:**
            - **ACCESS_TOKEN**: From Meta Business or provider
            - **PHONE_NUMBER_ID**: Your WhatsApp number ID
            
            **3. Configure Secrets:**
            
            Add to Streamlit Cloud → App settings → Secrets:
            ```toml
            [whatsapp]
            WHATSAPP_ACCESS_TOKEN = "your_token"
            WHATSAPP_PHONE_NUMBER_ID = "your_phone_id"
            ```
            
            **4. Important:**
            - WhatsApp has 24-hour messaging window
            - Template messages required after 24h
            - No general-purpose chatbot - task-based only
            
            **Note:** App works without credentials using Manual Import.
            """)


def settings_channels_view():
    """Main entry point for channel settings view."""
    try:
        ui_kit.inject_ui_kit_css()
        
        st.title("🔌 Channel Integrations")
        st.caption("Configure Instagram, Facebook, and WhatsApp connections")
        
        # Info banner
        st.info("""
        **Sprint A Status:** This app is ready for integration but works without credentials.
        Use **Manual Import** in the Inbox to test workflows without real accounts.
        """)
        
        st.divider()
        
        # Meta section
        render_meta_section()
        
        st.divider()
        
        # WhatsApp section
        render_whatsapp_section()
        
    except Exception as e:
        logger.error(f"Settings channels view error: {e}", exc_info=True)
        st.error(f"Error loading settings: {str(e)}")
