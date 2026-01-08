"""
Salons Plugin - Example implementation for SocialOps Agent Core.

Demonstrates how to implement the Plugin interface for a salon booking use case.
Supports 10 intent types with template-based replies in English and Arabic.
"""

from typing import Dict, Any, Set
import yaml
from pathlib import Path
import logging
import random

from plugins._base import Plugin
from plugins.salons.intents import classify_intent, extract_entities

logger = logging.getLogger(__name__)


class SalonsPlugin(Plugin):
    """
    Salons booking plugin - Example implementation.
    
    Handles 10 intent types:
    1. booking - Appointment booking requests
    2. prices - Pricing inquiries
    3. location - Location/address questions
    4. hours - Operating hours questions
    5. services - Service offerings questions
    6. reschedule - Appointment rescheduling
    7. cancellation - Cancellation policy questions
    8. complaint - Customer complaints
    9. confirmation - Booking confirmations
    10. upsell - Additional service offers
    """
    
    def __init__(self):
        """Initialize salons plugin with templates."""
        self._name = "salons"
        self._platforms = {"instagram", "facebook", "whatsapp"}
        self.templates = self._load_templates()
        logger.info("SalonsPlugin initialized")
    
    def _load_templates(self) -> Dict[str, Dict[str, list]]:
        """
        Load reply templates from YAML files.
        
        Returns:
            Dictionary with structure: {lang: {intent: [templates]}}
        """
        templates = {}
        plugin_dir = Path(__file__).parent
        
        for lang in ["en", "ar"]:
            yaml_path = plugin_dir / f"templates_{lang}.yaml"
            try:
                if yaml_path.exists():
                    with open(yaml_path, "r", encoding="utf-8") as f:
                        templates[lang] = yaml.safe_load(f) or {}
                    logger.info(f"Loaded {lang} templates: {list(templates[lang].keys())}")
                else:
                    logger.warning(f"Template file not found: {yaml_path}")
                    templates[lang] = {}
            except Exception as e:
                logger.error(f"Failed to load {lang} templates: {e}")
                templates[lang] = {}
        
        return templates
    
    @property
    def name(self) -> str:
        """Plugin identifier."""
        return self._name
    
    @property
    def supported_platforms(self) -> Set[str]:
        """Platforms this plugin supports."""
        return self._platforms
    
    def classify(self, text: str, lang: str) -> str:
        """
        Classify user message intent.
        
        Args:
            text: User message text
            lang: Language code ('en', 'ar')
            
        Returns:
            Intent string (booking, prices, etc.) or 'other'
        """
        intent = classify_intent(text, lang)
        logger.debug(f"Classified '{text[:30]}...' as '{intent}'")
        return intent
    
    def extract(self, text: str, lang: str) -> Dict[str, Any]:
        """
        Extract structured entities from message.
        
        Args:
            text: User message text
            lang: Language code
            
        Returns:
            Dictionary of extracted entities (date, time, service, name, etc.)
        """
        entities = extract_entities(text, lang)
        logger.debug(f"Extracted entities: {entities}")
        return entities
    
    def suggest_reply(self, intent: str, lang: str, context: Dict[str, Any]) -> str:
        """
        Generate reply suggestion using templates.
        
        Args:
            intent: Classified intent
            lang: Language code ('en', 'ar')
            context: Context including extracted entities, sender_name, etc.
            
        Returns:
            Suggested reply text
        """
        # Get templates for language
        lang_templates = self.templates.get(lang, {})
        
        if not lang_templates:
            # Fallback to English if language not found
            lang_templates = self.templates.get('en', {})
            logger.warning(f"No templates for lang '{lang}', using English")
        
        # Get templates for intent
        intent_templates = lang_templates.get(intent, [])
        
        if not intent_templates:
            # Fallback to generic response
            if lang == 'ar':
                return "شكراً على رسالتك! سنساعدك قريباً."
            else:
                return "Thank you for your message! We'll assist you shortly."
        
        # Select random template
        template = random.choice(intent_templates)
        
        # Fill in placeholders with context data
        reply = self._fill_template(template, context)
        
        logger.debug(f"Generated reply for intent '{intent}': {reply[:50]}...")
        return reply
    
    def _fill_template(self, template: str, context: Dict[str, Any]) -> str:
        """
        Fill template placeholders with context data.
        
        Args:
            template: Template string with placeholders like {name}, {date}
            context: Context dictionary
            
        Returns:
            Filled template
        """
        # Extract entities and other context
        extracted = context.get('extracted', {})
        sender_name = context.get('sender_name', '')
        
        # Build replacement dict
        replacements = {
            'name': sender_name,
            'date': extracted.get('day', 'your preferred date'),
            'time': extracted.get('time', 'your preferred time'),
            'service': extracted.get('service', 'the service'),
            'location': '123 Main Street, Dubai',  # Could be from config
            'phone': '+971-XX-XXX-XXXX',  # Could be from config
        }
        
        # Replace placeholders
        result = template
        for key, value in replacements.items():
            result = result.replace(f'{{{key}}}', str(value))
        
        return result
