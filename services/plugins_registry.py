"""
Plugin Registry for SocialOps Agent Core.

Manages plugin registration, discovery, and routing of messages to appropriate
plugins based on platform and message content.
"""

import logging
from typing import List, Optional, Dict, Any
from plugins._base import Plugin

logger = logging.getLogger(__name__)

# Global plugin registry
_plugins: List[Plugin] = []


def register_plugin(plugin: Plugin) -> None:
    """
    Register a plugin with the system.
    
    Args:
        plugin: Plugin instance implementing the Plugin interface
    """
    global _plugins
    
    if not isinstance(plugin, Plugin):
        raise TypeError(f"Plugin must implement Plugin interface, got {type(plugin)}")
    
    # Check for duplicate names
    for existing in _plugins:
        if existing.name == plugin.name:
            logger.warning(f"Plugin '{plugin.name}' already registered, replacing")
            _plugins.remove(existing)
            break
    
    _plugins.append(plugin)
    logger.info(f"Registered plugin: {plugin.name} (platforms: {plugin.supported_platforms})")


def list_plugins() -> List[Plugin]:
    """
    Get all registered plugins.
    
    Returns:
        List of registered plugin instances
    """
    return _plugins.copy()


def get_plugin(name: str) -> Optional[Plugin]:
    """
    Get plugin by name.
    
    Args:
        name: Plugin name
        
    Returns:
        Plugin instance or None if not found
    """
    for plugin in _plugins:
        if plugin.name == name:
            return plugin
    return None


def route_to_plugin(platform: str, text: str, lang: str) -> Optional[Plugin]:
    """
    Route message to appropriate plugin based on platform and content.
    
    For Sprint 1: Returns first plugin that supports the platform.
    In future sprints, this can be enhanced with:
    - Multiple plugins per platform
    - Confidence-based routing using classify()
    - ML-based intent routing
    
    Args:
        platform: Message platform ('instagram', 'facebook', 'whatsapp')
        text: Message text
        lang: Language code
        
    Returns:
        Best matching plugin or None if no match
    """
    platform_lower = platform.lower()
    
    # Find plugins that support this platform
    candidates = [p for p in _plugins if platform_lower in p.supported_platforms]
    
    if not candidates:
        logger.warning(f"No plugin found for platform: {platform}")
        return None
    
    # For Sprint 1: return first candidate (salons plugin)
    # Future: evaluate confidence scores from classify()
    selected = candidates[0]
    logger.info(f"Routed {platform} message to plugin: {selected.name}")
    
    return selected


def clear_plugins() -> None:
    """Clear all registered plugins (useful for testing)."""
    global _plugins
    _plugins = []
    logger.info("Cleared all plugins")
