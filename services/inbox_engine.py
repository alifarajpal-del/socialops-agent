"""
Inbox Engine - Message normalization and thread management.

Provides utilities for processing imported messages and managing thread state.
"""

import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


def normalize_imported_message(msg: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize imported message to standard format.
    
    Args:
        msg: Raw message dict from JSON import
        
    Returns:
        Normalized message with keys:
        {
            'platform': str,
            'thread_id': str,
            'sender_id': str,
            'sender_name': str,
            'text': str,
            'timestamp_iso': str,
            'raw': dict
        }
    """
    platform = msg.get('platform', 'unknown').lower()
    sender_name = msg.get('sender_name', 'Unknown')
    sender_id = msg.get('sender_id', f"user_{sender_name.replace(' ', '_').lower()}")
    thread_id = msg.get('thread_id', f"{platform}_{sender_id}")
    
    # Parse or generate timestamp
    timestamp = msg.get('timestamp')
    if not timestamp:
        timestamp = datetime.now().isoformat()
    elif isinstance(timestamp, str) and not timestamp.endswith('Z') and '+' not in timestamp:
        # Ensure ISO format
        try:
            dt = datetime.fromisoformat(timestamp)
            timestamp = dt.isoformat()
        except:
            timestamp = datetime.now().isoformat()
    
    return {
        'platform': platform,
        'thread_id': thread_id,
        'sender_id': sender_id,
        'sender_name': sender_name,
        'text': msg.get('text', ''),
        'timestamp_iso': timestamp,
        'raw': msg
    }


def compute_thread_title(thread_id: str, platform: str, messages: list) -> str:
    """
    Compute thread title from messages.
    
    Args:
        thread_id: Thread ID
        platform: Platform name
        messages: List of message dicts
        
    Returns:
        Thread title (sender name or fallback)
    """
    if messages:
        # Use first message sender name
        first_msg = messages[0]
        sender_name = first_msg.get('sender_name')
        if sender_name:
            return sender_name
    
    # Fallback to thread ID
    return f"Thread {thread_id[:8]}..."


def get_lang() -> str:
    """
    Get current language from session state.
    
    Returns:
        Language code ('en' or 'ar'), defaults to 'en' if not set
    """
    try:
        import streamlit as st
        return st.session_state.get('language', 'en')
    except:
        return 'en'
