"""
Reply engine: AI-powered reply suggestions with guardrails.
Human-in-the-loop: suggests replies, user approves before sending.
"""

from typing import Optional, Dict, Any, List
import logging
from plugins._base import BasePlugin
from services.inbox_engine import Thread, Message, MessageDirection, ChannelType

logger = logging.getLogger(__name__)


class ReplyGuardrails:
    """Content safety and policy guardrails for replies."""
    
    # Blocked patterns (basic content safety)
    BLOCKED_PATTERNS = [
        "password",
        "credit card",
        "ssn",
        "social security",
    ]
    
    # WhatsApp 24h window rules
    WHATSAPP_TEMPLATE_REQUIRED_AFTER_HOURS = 24
    
    @staticmethod
    def check_content_safety(text: str) -> tuple[bool, Optional[str]]:
        """
        Check if reply text is safe to send.
        
        Returns:
            (is_safe, error_message)
        """
        text_lower = text.lower()
        
        for pattern in ReplyGuardrails.BLOCKED_PATTERNS:
            if pattern in text_lower:
                return False, f"Reply contains sensitive information: {pattern}"
        
        # Check minimum length
        if len(text.strip()) < 5:
            return False, "Reply is too short"
        
        # Check maximum length (platform limits)
        if len(text) > 2000:
            return False, "Reply exceeds maximum length (2000 chars)"
        
        return True, None
    
    @staticmethod
    def check_whatsapp_window(thread: Thread) -> tuple[bool, Optional[str]]:
        """
        Check if WhatsApp 24h messaging window is still open.
        
        Returns:
            (can_send_freeform, error_message)
        """
        if thread.channel != ChannelType.WHATSAPP:
            return True, None
        
        if not thread.messages:
            return False, "No message history for WhatsApp thread"
        
        # Get last incoming message
        last_incoming = None
        for msg in reversed(thread.messages):
            if msg.direction == MessageDirection.INCOMING:
                last_incoming = msg
                break
        
        if not last_incoming:
            return False, "No incoming messages in thread"
        
        # Check if within 24h window
        from datetime import datetime, timedelta
        hours_since = (datetime.now() - last_incoming.timestamp).total_seconds() / 3600
        
        if hours_since > ReplyGuardrails.WHATSAPP_TEMPLATE_REQUIRED_AFTER_HOURS:
            return False, f"WhatsApp 24h window expired ({hours_since:.1f}h ago). Use template message."
        
        return True, None


class ReplyEngine:
    """
    Core reply engine for AI-powered suggestions with guardrails.
    
    Human-in-the-loop workflow:
    1. Analyze thread + plugin context
    2. Generate reply suggestion
    3. Apply guardrails
    4. Present to user for approval/edit
    5. User sends (outside this engine)
    """
    
    def __init__(self):
        """Initialize reply engine."""
        self.guardrails = ReplyGuardrails()
        logger.info("ReplyEngine initialized")
    
    def suggest_reply(
        self,
        thread: Thread,
        plugin: BasePlugin,
        lang: str = "en",
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate reply suggestion for thread using plugin.
        
        Args:
            thread: Conversation thread
            plugin: Plugin to generate reply
            lang: Language code (en, ar, etc.)
            context: Additional context (extracted data, user profile, etc.)
            
        Returns:
            {
                "reply_text": str,
                "safe": bool,
                "warnings": List[str],
                "can_send": bool,
                "metadata": dict
            }
        """
        warnings = []
        
        # Get last message
        if not thread.messages:
            return {
                "reply_text": "",
                "safe": False,
                "warnings": ["No messages in thread"],
                "can_send": False,
                "metadata": {}
            }
        
        last_msg = thread.messages[-1]
        
        # Extract intent and data if needed
        if context is None:
            context = {}
        
        if "intent" not in context and last_msg.direction == MessageDirection.INCOMING:
            intent_obj = plugin.classify(last_msg.text, {"thread": thread.dict()})
            if intent_obj:
                context["intent"] = intent_obj.name
                extracted = plugin.extract(last_msg.text, intent_obj.name, {"thread": thread.dict()})
                context["extracted_data"] = extracted.dict()
        
        # Generate reply via plugin
        try:
            reply_text = plugin.reply(
                intent=context.get("intent", "general"),
                lang=lang,
                context=context
            )
        except Exception as e:
            logger.error(f"Plugin reply generation failed: {e}")
            return {
                "reply_text": "",
                "safe": False,
                "warnings": [f"Reply generation failed: {str(e)}"],
                "can_send": False,
                "metadata": {}
            }
        
        # Apply content safety guardrails
        is_safe, safety_error = self.guardrails.check_content_safety(reply_text)
        if not is_safe:
            warnings.append(safety_error)
        
        # Apply WhatsApp-specific rules
        can_send_whatsapp = True
        if thread.channel == ChannelType.WHATSAPP:
            can_send_whatsapp, whatsapp_error = self.guardrails.check_whatsapp_window(thread)
            if not can_send_whatsapp:
                warnings.append(whatsapp_error)
        
        can_send = is_safe and can_send_whatsapp
        
        return {
            "reply_text": reply_text,
            "safe": is_safe,
            "warnings": warnings,
            "can_send": can_send,
            "metadata": {
                "plugin": plugin.name,
                "intent": context.get("intent"),
                "lang": lang,
                "channel": thread.channel.value
            }
        }
    
    def validate_manual_reply(self, thread: Thread, reply_text: str) -> Dict[str, Any]:
        """
        Validate manually edited reply before sending.
        
        Args:
            thread: Thread context
            reply_text: User-edited reply text
            
        Returns:
            {"safe": bool, "warnings": List[str], "can_send": bool}
        """
        warnings = []
        
        # Content safety
        is_safe, safety_error = self.guardrails.check_content_safety(reply_text)
        if not is_safe:
            warnings.append(safety_error)
        
        # WhatsApp rules
        can_send_whatsapp = True
        if thread.channel == ChannelType.WHATSAPP:
            can_send_whatsapp, whatsapp_error = self.guardrails.check_whatsapp_window(thread)
            if not can_send_whatsapp:
                warnings.append(whatsapp_error)
        
        return {
            "safe": is_safe,
            "warnings": warnings,
            "can_send": is_safe and can_send_whatsapp
        }


# Global singleton
_reply_engine = None


def get_reply_engine() -> ReplyEngine:
    """Get or create global reply engine instance."""
    global _reply_engine
    if _reply_engine is None:
        _reply_engine = ReplyEngine()
    return _reply_engine
