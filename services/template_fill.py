"""
Template Fill Service - Replace placeholders in text with profile data.

Supports: {business_name}, {city}, {phone}, {hours}, {booking_link}, {location_link}
"""

import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


def fill_placeholders(text: str, profile: Optional[Dict] = None) -> str:
    """
    Replace placeholders in text with profile data.
    
    Args:
        text: Text with placeholders like {business_name}
        profile: Workspace profile dict from WorkspaceStore.get_profile()
    
    Returns:
        Text with placeholders replaced (or left as-is if profile missing)
    """
    if not profile:
        return text
    
    try:
        # Define placeholder mappings
        placeholders = {
            'business_name': profile.get('business_name', ''),
            'city': profile.get('city', ''),
            'phone': profile.get('phone', ''),
            'hours': profile.get('hours', ''),
            'booking_link': profile.get('booking_link', ''),
            'location_link': profile.get('location_link', '')
        }
        
        # Replace each placeholder
        result = text
        for key, value in placeholders.items():
            placeholder = f"{{{key}}}"
            if placeholder in result:
                result = result.replace(placeholder, value)
        
        return result
    
    except Exception as e:
        logger.error(f"Template fill error: {e}", exc_info=True)
        return text
