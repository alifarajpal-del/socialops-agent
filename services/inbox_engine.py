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


def compute_sla_status(last_message_time_iso: str) -> Dict[str, Any]:
    """
    Compute SLA status based on last message timestamp.
    
    Args:
        last_message_time_iso: ISO timestamp of last message
        
    Returns:
        Dict with:
        {
            'hours_since': float,
            'status': 'urgent' | 'warning' | 'ok',
            'color': str,
            'emoji': str
        }
    """
    try:
        last_time = datetime.fromisoformat(last_message_time_iso.replace('Z', '+00:00'))
        now = datetime.now()
        
        # Remove timezone info for comparison
        last_time = last_time.replace(tzinfo=None)
        
        delta = now - last_time
        hours_since = delta.total_seconds() / 3600
        
        # SLA thresholds
        if hours_since > 24:
            return {
                'hours_since': hours_since,
                'status': 'urgent',
                'color': '#ff4444',
                'emoji': '🔴'
            }
        elif hours_since > 4:
            return {
                'hours_since': hours_since,
                'status': 'warning',
                'color': '#ffaa00',
                'emoji': '🟡'
            }
        else:
            return {
                'hours_since': hours_since,
                'status': 'ok',
                'color': '#44ff44',
                'emoji': '🟢'
            }
    except Exception as e:
        logger.warning(f"SLA computation error: {e}")
        return {
            'hours_since': 0,
            'status': 'unknown',
            'color': '#888888',
            'emoji': '⚪'
        }


def suggest_followup_time(last_message_time_iso: str, priority: str = 'normal') -> str:
    """
    Suggest follow-up time based on last message and priority.
    
    Args:
        last_message_time_iso: ISO timestamp of last message
        priority: 'urgent', 'high', 'normal', 'low'
        
    Returns:
        Suggested follow-up time as ISO string
    """
    from datetime import timedelta
    
    try:
        last_time = datetime.fromisoformat(last_message_time_iso.replace('Z', '+00:00'))
        last_time = last_time.replace(tzinfo=None)
    except:
        last_time = datetime.now()
    
    # Follow-up delays by priority
    delays = {
        'urgent': timedelta(hours=1),
        'high': timedelta(hours=4),
        'normal': timedelta(hours=24),
        'low': timedelta(days=3)
    }
    
    delay = delays.get(priority, delays['normal'])
    followup_time = last_time + delay
    
    return followup_time.isoformat()

