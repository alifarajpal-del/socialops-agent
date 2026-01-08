"""
Base Plugin Interface for SocialOps Agent Core.

Defines the contract that all plugins must implement to integrate with the
unified inbox system. This enables multi-platform (Instagram, Facebook, WhatsApp)
message routing, intent classification, entity extraction, and reply generation.
"""

from abc import ABC, abstractmethod
from typing import Set, Dict, Any


class Plugin(ABC):
    """
    Abstract base class for SocialOps plugins.
    
    All plugins must implement this interface to be registered with the
    plugins registry and participate in message routing.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """
        Unique plugin identifier.
        
        Returns:
            Plugin name (e.g., 'salons', 'restaurants', 'retail')
        """
        pass
    
    @property
    @abstractmethod
    def supported_platforms(self) -> Set[str]:
        """
        Platforms this plugin can handle.
        
        Returns:
            Set of platform names: {'instagram', 'facebook', 'whatsapp'}
        """
        pass
    
    @abstractmethod
    def classify(self, text: str, lang: str) -> str:
        """
        Classify user message intent.
        
        Args:
            text: User message text
            lang: Language code ('en', 'ar', etc.)
            
        Returns:
            Intent string (e.g., 'booking', 'prices', 'hours')
            Returns 'other' if no specific intent matched
        """
        pass
    
    @abstractmethod
    def extract(self, text: str, lang: str) -> Dict[str, Any]:
        """
        Extract structured entities from user message.
        
        Args:
            text: User message text
            lang: Language code ('en', 'ar', etc.)
            
        Returns:
            Dictionary of extracted entities:
            {
                'date': '2026-01-15',
                'time': '14:00',
                'service': 'makeup',
                'name': 'Sarah',
                ...
            }
        """
        pass
    
    @abstractmethod
    def suggest_reply(self, intent: str, lang: str, context: Dict[str, Any]) -> str:
        """
        Generate reply suggestion based on intent and context.
        
        Args:
            intent: Classified intent from classify()
            lang: Language code ('en', 'ar', etc.)
            context: Additional context including:
                - extracted: Extracted entities from extract()
                - sender_name: Sender's name
                - platform: Message platform
                - Any other contextual data
                
        Returns:
            Suggested reply text (human will review before sending)
        """
        pass
