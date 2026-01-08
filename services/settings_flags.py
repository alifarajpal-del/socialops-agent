"""
Settings Flags - Feature flags for SocialOps Agent.

Manages feature toggles without requiring secrets to be configured.
All features default to disabled for safety (human-in-the-loop).
"""

import logging

logger = logging.getLogger(__name__)


def enable_send() -> bool:
    """
    Check if message sending is enabled.
    
    Default: False (human-in-the-loop only, no auto-send)
    
    Returns:
        True if sending enabled, False otherwise
    """
    try:
        import streamlit as st
        
        # Check session state first
        if 'enable_send' in st.session_state:
            return st.session_state.enable_send
        
        # Check secrets (safe access)
        try:
            return st.secrets.get('ENABLE_SEND', False)
        except:
            return False
            
    except:
        return False


def enable_polling() -> bool:
    """
    Check if message polling is enabled.
    
    Default: False (manual import only in Sprint A)
    
    Returns:
        True if polling enabled, False otherwise
    """
    try:
        import streamlit as st
        
        if 'enable_polling' in st.session_state:
            return st.session_state.enable_polling
        
        try:
            return st.secrets.get('ENABLE_POLLING', False)
        except:
            return False
            
    except:
        return False


def enable_webhook_relay() -> bool:
    """
    Check if webhook relay is enabled.
    
    Default: False (not implemented in Sprint A)
    
    Returns:
        True if webhook relay enabled, False otherwise
    """
    try:
        import streamlit as st
        
        if 'enable_webhook_relay' in st.session_state:
            return st.session_state.enable_webhook_relay
        
        try:
            return st.secrets.get('ENABLE_WEBHOOK_RELAY', False)
        except:
            return False
            
    except:
        return False
