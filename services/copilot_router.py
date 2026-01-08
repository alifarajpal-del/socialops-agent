"""Copilot Router - Intent parsing and execution for conversational commands.

Translates natural language → structured intents → confirmed actions.
NO automatic execution. ONLY returns intent JSON for UI confirmation.
"""

import re
from typing import Dict, List, Optional
from datetime import datetime, timedelta


def parse_intent(user_text: str, context: Dict) -> Dict:
    """Parse user text into structured intent JSON.
    
    Args:
        user_text: Raw user input (natural language)
        context: Current session context (language, thread_id, page, user_id)
    
    Returns:
        Intent JSON with schema:
        {
          "intent": "SUMMARIZE_THREAD | REPLY_DRAFTS | CREATE_TASK | CREATE_LEAD | GO_TO | LOAD_DEMO | SEARCH",
          "confidence": float (0.0-1.0),
          "entities": {
            "thread_id": str | None,
            "lead_name": str | None,
            "task_title": str | None,
            "due_date": str | None,
            "language": "ar" | "en",
            "target_page": str | None
          },
          "steps": [list of human-readable steps],
          "requires_confirmation": bool,
          "confirmation_text": str
        }
    """
    text_lower = user_text.lower().strip()
    language = context.get("language", "en")
    current_thread_id = context.get("current_thread_id")
    
    # Intent patterns (conservative matching)
    intent_patterns = {
        "SUMMARIZE_THREAD": [
            r"summarize|summary|recap|overview",
            r"what.*happen|what.*discuss",
            r"tldr|brief",
        ],
        "REPLY_DRAFTS": [
            r"draft.*repl|repl.*draft",
            r"suggest.*response|response.*suggest",
            r"what.*should.*say|how.*should.*respond",
            r"write.*response|write.*reply",
        ],
        "CREATE_TASK": [
            r"create.*task|add.*task|new.*task",
            r"remind.*me|follow.*up",
            r"todo|to.*do",
        ],
        "CREATE_LEAD": [
            r"create.*lead|add.*lead|new.*lead",
            r"add.*contact|new.*contact",
            r"create.*client|new.*client",
        ],
        "GO_TO": [
            r"go.*to|navigate.*to|open|show.*me",
            r"take.*me.*to|switch.*to",
        ],
        "LOAD_DEMO": [
            r"demo|example|sample",
            r"load.*data|populate|seed",
            r"test.*data",
        ],
    }
    
    # Try to match intent
    matched_intent = None
    max_confidence = 0.0
    
    for intent_name, patterns in intent_patterns.items():
        for pattern in patterns:
            if re.search(pattern, text_lower):
                # Calculate confidence based on pattern specificity
                confidence = 0.5 + (0.3 if len(pattern) > 15 else 0.1)
                if confidence > max_confidence:
                    matched_intent = intent_name
                    max_confidence = confidence
    
    # Default to SEARCH if no clear intent
    if not matched_intent or max_confidence < 0.4:
        return {
            "intent": "SEARCH",
            "confidence": 0.3,
            "entities": {
                "query": user_text,
                "language": language
            },
            "steps": [
                f"Search for: '{user_text}'",
                "Display relevant results"
            ],
            "requires_confirmation": False,
            "confirmation_text": f"Search for '{user_text}'?"
        }
    
    # Build intent-specific response
    if matched_intent == "SUMMARIZE_THREAD":
        return {
            "intent": "SUMMARIZE_THREAD",
            "confidence": max_confidence,
            "entities": {
                "thread_id": current_thread_id,
                "language": language
            },
            "steps": [
                "Analyze conversation history",
                "Extract key points and decisions",
                "Generate concise summary"
            ],
            "requires_confirmation": True,
            "confirmation_text": "Summarize the current conversation?"
        }
    
    elif matched_intent == "REPLY_DRAFTS":
        # Extract tone/style if mentioned
        tone = "professional"
        if re.search(r"casual|friendly", text_lower):
            tone = "casual"
        elif re.search(r"formal|professional", text_lower):
            tone = "formal"
        
        return {
            "intent": "REPLY_DRAFTS",
            "confidence": max_confidence,
            "entities": {
                "thread_id": current_thread_id,
                "language": language,
                "tone": tone,
                "count": 3
            },
            "steps": [
                "Analyze conversation context",
                f"Generate 3 {tone} reply drafts",
                f"Return drafts in {language.upper()}"
            ],
            "requires_confirmation": True,
            "confirmation_text": f"Draft 3 {tone} replies in {language.upper()}?"
        }
    
    elif matched_intent == "CREATE_TASK":
        # Extract task title from text
        task_title = _extract_quoted_text(user_text) or _extract_task_title(text_lower)
        
        # Extract due date if mentioned
        due_date = _extract_due_date(text_lower)
        
        return {
            "intent": "CREATE_TASK",
            "confidence": max_confidence,
            "entities": {
                "task_title": task_title,
                "due_date": due_date,
                "thread_id": current_thread_id,
                "language": language
            },
            "steps": [
                f"Create task: '{task_title}'",
                f"Due date: {due_date or 'Not specified'}",
                "Link to current conversation" if current_thread_id else "Create standalone task"
            ],
            "requires_confirmation": True,
            "confirmation_text": f"Create task '{task_title}'?"
        }
    
    elif matched_intent == "CREATE_LEAD":
        # Extract lead name
        lead_name = _extract_quoted_text(user_text) or _extract_lead_name(text_lower)
        
        return {
            "intent": "CREATE_LEAD",
            "confidence": max_confidence,
            "entities": {
                "lead_name": lead_name,
                "language": language
            },
            "steps": [
                f"Create new lead: '{lead_name}'",
                "Set status: New",
                "Open lead form for additional details"
            ],
            "requires_confirmation": True,
            "confirmation_text": f"Create lead for '{lead_name}'?"
        }
    
    elif matched_intent == "GO_TO":
        # Extract target page
        target_map = {
            "dashboard": ["dashboard", "home", "overview"],
            "inbox": ["inbox", "messages", "conversations"],
            "leads": ["leads", "pipeline", "crm"],
            "ops": ["ops", "operations", "workspace"],
            "settings": ["settings", "config", "preferences"],
        }
        
        target_page = None
        for page_id, keywords in target_map.items():
            for keyword in keywords:
                if keyword in text_lower:
                    target_page = page_id
                    break
            if target_page:
                break
        
        return {
            "intent": "GO_TO",
            "confidence": max_confidence if target_page else 0.5,
            "entities": {
                "target_page": target_page,
                "language": language
            },
            "steps": [
                f"Navigate to {target_page or 'unknown page'}"
            ],
            "requires_confirmation": False,  # Safe action
            "confirmation_text": f"Go to {target_page}?"
        }
    
    elif matched_intent == "LOAD_DEMO":
        return {
            "intent": "LOAD_DEMO",
            "confidence": max_confidence,
            "entities": {
                "language": language
            },
            "steps": [
                "Generate demo conversations (5 threads)",
                "Create sample leads (3 leads)",
                "Add demo tasks (4 tasks)",
                "Populate with realistic data"
            ],
            "requires_confirmation": True,  # Destructive
            "confirmation_text": "Load demo data? This will add sample content."
        }
    
    # Fallback
    return {
        "intent": "SEARCH",
        "confidence": 0.3,
        "entities": {
            "query": user_text,
            "language": language
        },
        "steps": [f"Search for: '{user_text}'"],
        "requires_confirmation": False,
        "confirmation_text": f"Search for '{user_text}'?"
    }


def execute_intent(intent_json: Dict, context: Dict) -> Dict:
    """Execute confirmed intent and return structured result.
    
    Args:
        intent_json: Intent JSON from parse_intent() (confirmed by user)
        context: Current session context
    
    Returns:
        Result dictionary:
        {
          "type": "REPLY_DRAFTS | SUMMARY | CREATED | NAVIGATION | DEMO_LOADED | ERROR",
          "message": str (human-readable message),
          "data": dict (intent-specific data),
          "navigate_to": str | None (page to navigate to),
          "timestamp": str (ISO format)
        }
    """
    intent = intent_json.get("intent")
    entities = intent_json.get("entities", {})
    language = entities.get("language", context.get("language", "en"))
    
    try:
        if intent == "SUMMARIZE_THREAD":
            return _execute_summarize(entities, context, language)
        
        elif intent == "REPLY_DRAFTS":
            return _execute_reply_drafts(entities, context, language)
        
        elif intent == "CREATE_TASK":
            return _execute_create_task(entities, context, language)
        
        elif intent == "CREATE_LEAD":
            return _execute_create_lead(entities, context, language)
        
        elif intent == "GO_TO":
            return _execute_navigation(entities, context, language)
        
        elif intent == "LOAD_DEMO":
            return _execute_load_demo(entities, context, language)
        
        elif intent == "SEARCH":
            return _execute_search(entities, context, language)
        
        else:
            return {
                "type": "ERROR",
                "message": f"Unknown intent: {intent}",
                "data": {},
                "navigate_to": None,
                "timestamp": datetime.now().isoformat()
            }
    
    except Exception as e:
        return {
            "type": "ERROR",
            "message": f"Execution failed: {str(e)}",
            "data": {"error": str(e)},
            "navigate_to": None,
            "timestamp": datetime.now().isoformat()
        }


# ============================================================================
# EXECUTION HELPERS (Map to existing services)
# ============================================================================

def _execute_summarize(entities: Dict, context: Dict, language: str) -> Dict:
    """Execute SUMMARIZE_THREAD intent."""
    thread_id = entities.get("thread_id")
    
    if not thread_id:
        return {
            "type": "ERROR",
            "message": "No conversation selected. Please open a thread first.",
            "data": {},
            "navigate_to": "inbox",
            "timestamp": datetime.now().isoformat()
        }
    
    # Mock summary (TODO: integrate with actual engine/summarization)
    summary = f"""**Conversation Summary (Thread: {thread_id[:8]}...)**

• **Main Topic:** Customer inquiry about pricing and features
• **Key Points:** 
  - Requested enterprise plan details
  - Asked about integration options
  - Needs demo scheduling
• **Action Items:**
  - Send pricing sheet
  - Schedule demo call
  - Follow up in 2 days
    
*Generated at {datetime.now().strftime('%Y-%m-%d %H:%M')}*"""
    
    return {
        "type": "SUMMARY",
        "message": "✅ Conversation summarized successfully",
        "data": {
            "summary": summary,
            "thread_id": thread_id
        },
        "navigate_to": None,
        "timestamp": datetime.now().isoformat()
    }


def _execute_reply_drafts(entities: Dict, context: Dict, language: str) -> Dict:
    """Execute REPLY_DRAFTS intent."""
    thread_id = entities.get("thread_id")
    tone = entities.get("tone", "professional")
    count = entities.get("count", 3)
    
    # Mock drafts (TODO: integrate with actual engine/LLM)
    if language == "ar":
        drafts = [
            "شكراً لتواصلك معنا. سنقوم بمراجعة طلبك والرد عليك خلال 24 ساعة.",
            "نقدر اهتمامك بخدماتنا. هل يمكنك تزويدنا بمزيد من التفاصيل لنتمكن من مساعدتك بشكل أفضل؟",
            "تم استلام رسالتك بنجاح. فريقنا سيتواصل معك قريباً للمتابعة."
        ]
    else:
        if tone == "casual":
            drafts = [
                "Hey! Thanks for reaching out. I'll look into this and get back to you soon.",
                "Appreciate you getting in touch! Can you share a bit more detail so I can help better?",
                "Got your message! Our team will follow up with you shortly."
            ]
        else:  # formal/professional
            drafts = [
                "Thank you for your inquiry. We will review your request and respond within 24 hours.",
                "We appreciate your interest. Could you provide additional details to better assist you?",
                "Your message has been received. Our team will contact you shortly to follow up."
            ]
    
    return {
        "type": "REPLY_DRAFTS",
        "message": f"✅ Generated {count} reply drafts in {language.upper()}",
        "data": {
            "drafts": drafts[:count],
            "tone": tone,
            "language": language,
            "thread_id": thread_id
        },
        "navigate_to": None,
        "timestamp": datetime.now().isoformat()
    }


def _execute_create_task(entities: Dict, context: Dict, language: str) -> Dict:
    """Execute CREATE_TASK intent."""
    task_title = entities.get("task_title", "Untitled Task")
    due_date = entities.get("due_date")
    thread_id = entities.get("thread_id")
    
    # Mock task creation (TODO: integrate with actual database)
    task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    return {
        "type": "CREATED",
        "message": f"✅ Task created: '{task_title}'",
        "data": {
            "item_type": "task",
            "item_id": task_id,
            "task_title": task_title,
            "due_date": due_date,
            "thread_id": thread_id,
            "status": "pending"
        },
        "navigate_to": "leads",  # Navigate to tasks view
        "timestamp": datetime.now().isoformat()
    }


def _execute_create_lead(entities: Dict, context: Dict, language: str) -> Dict:
    """Execute CREATE_LEAD intent."""
    lead_name = entities.get("lead_name", "Untitled Lead")
    
    # Mock lead creation (TODO: integrate with actual database)
    lead_id = f"lead_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    return {
        "type": "CREATED",
        "message": f"✅ Lead created: '{lead_name}'",
        "data": {
            "item_type": "lead",
            "item_id": lead_id,
            "lead_name": lead_name,
            "status": "new",
            "created_at": datetime.now().isoformat()
        },
        "navigate_to": "leads",
        "timestamp": datetime.now().isoformat()
    }


def _execute_navigation(entities: Dict, context: Dict, language: str) -> Dict:
    """Execute GO_TO intent."""
    target_page = entities.get("target_page", "dashboard")
    
    return {
        "type": "NAVIGATION",
        "message": f"🔗 Navigating to {target_page}...",
        "data": {
            "target": target_page
        },
        "navigate_to": target_page,
        "timestamp": datetime.now().isoformat()
    }


def _execute_load_demo(entities: Dict, context: Dict, language: str) -> Dict:
    """Execute LOAD_DEMO intent."""
    # Mock demo data loading (TODO: integrate with actual setup_livevision.py or similar)
    
    return {
        "type": "DEMO_LOADED",
        "message": "🎬 Demo data loaded successfully!",
        "data": {
            "threads_created": 5,
            "leads_created": 3,
            "tasks_created": 4,
            "language": language
        },
        "navigate_to": "inbox",
        "timestamp": datetime.now().isoformat()
    }


def _execute_search(entities: Dict, context: Dict, language: str) -> Dict:
    """Execute SEARCH intent."""
    query = entities.get("query", "")
    
    # Mock search results (TODO: integrate with actual search)
    results = [
        f"Result 1 for '{query}'",
        f"Result 2 for '{query}'",
        f"Result 3 for '{query}'"
    ]
    
    return {
        "type": "SEARCH",
        "message": f"🔍 Search results for '{query}'",
        "data": {
            "query": query,
            "results": results,
            "count": len(results)
        },
        "navigate_to": None,
        "timestamp": datetime.now().isoformat()
    }


# ============================================================================
# TEXT EXTRACTION UTILITIES
# ============================================================================

def _extract_quoted_text(text: str) -> Optional[str]:
    """Extract text within quotes."""
    match = re.search(r'["\'](.+?)["\']', text)
    return match.group(1) if match else None


def _extract_task_title(text_lower: str) -> str:
    """Extract task title from natural language."""
    # Remove intent keywords
    text_cleaned = re.sub(r'create|add|new|task|todo|to do', '', text_lower).strip()
    
    # Take first 50 chars as title
    return text_cleaned[:50] or "Follow-up task"


def _extract_lead_name(text_lower: str) -> str:
    """Extract lead name from natural language."""
    # Remove intent keywords
    text_cleaned = re.sub(r'create|add|new|lead|contact|client', '', text_lower).strip()
    
    # Take first 50 chars as name
    return text_cleaned[:50] or "New Lead"


def _extract_due_date(text_lower: str) -> Optional[str]:
    """Extract due date from natural language."""
    # Simple date extraction (TODO: use dateparser or similar)
    if "tomorrow" in text_lower:
        return (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    elif "next week" in text_lower:
        return (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    elif "today" in text_lower:
        return datetime.now().strftime("%Y-%m-%d")
    
    # Look for date patterns (YYYY-MM-DD or MM/DD/YYYY)
    date_match = re.search(r'(\d{4}-\d{2}-\d{2})|(\d{1,2}/\d{1,2}/\d{4})', text_lower)
    if date_match:
        return date_match.group(0)
    
    return None
