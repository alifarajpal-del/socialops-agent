"""Copilot Chat View - Main conversational interface for SocialOps Agent.

User talks in natural language → Copilot returns suggested actions → User confirms via buttons.
NO automatic execution. ONLY suggestions + explicit confirmation.
"""

import streamlit as st
from typing import Optional, Dict, List
from datetime import datetime
from ui_components.ui_kit import inject_ui_kit_css, ui_page, ui_card, ui_badge
from services import copilot_router


def _init_copilot_state():
    """Initialize Copilot chat session state."""
    if "copilot_history" not in st.session_state:
        st.session_state.copilot_history = []
    
    if "copilot_context" not in st.session_state:
        st.session_state.copilot_context = {
            "language": st.session_state.get("language", "en"),
            "current_thread_id": None,
            "page": "copilot",
            "user_id": st.session_state.get("user_id", "demo_user")
        }
    
    if "pending_action" not in st.session_state:
        st.session_state.pending_action = None
    
    # Add welcome message on first load
    if len(st.session_state.copilot_history) == 0:
        welcome_msg = {
            "role": "assistant",
            "content": "Tell me what you want to do — I'll turn it into actions.",
            "timestamp": datetime.now().isoformat()
        }
        st.session_state.copilot_history.append(welcome_msg)


def _render_action_card(intent: Dict, index: int):
    """Render an action card with confirmation buttons.
    
    Args:
        intent: Intent JSON from copilot_router.parse_intent()
        index: Card index for unique button keys
    """
    intent_type = intent.get("intent", "UNKNOWN")
    confidence = intent.get("confidence", 0.0)
    steps = intent.get("steps", [])
    confirmation_text = intent.get("confirmation_text", "Proceed with this action?")
    entities = intent.get("entities", {})
    
    # Determine card title based on intent
    title_map = {
        "SUMMARIZE_THREAD": "📝 Summarize Conversation",
        "REPLY_DRAFTS": "✉️ Draft Replies",
        "CREATE_TASK": "✅ Create Task",
        "CREATE_LEAD": "👤 Create Lead",
        "GO_TO": "🔗 Navigate",
        "LOAD_DEMO": "🎬 Load Demo Data",
        "SEARCH": "🔍 Search",
    }
    title = title_map.get(intent_type, "💡 Suggested Action")
    
    # Confidence badge
    confidence_pct = int(confidence * 100)
    confidence_color = "success" if confidence >= 0.7 else "warning" if confidence >= 0.4 else "muted"
    
    with ui_card():
        # Header
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"### {title}")
        with col2:
            st.markdown(ui_badge(f"{confidence_pct}%", confidence_color), unsafe_allow_html=True)
        
        # Confirmation text
        st.markdown(f"**{confirmation_text}**")
        
        # Steps preview
        if steps:
            with st.expander("📋 Steps", expanded=False):
                for i, step in enumerate(steps, 1):
                    st.markdown(f"{i}. {step}")
        
        # Entities preview (if any)
        if any(v is not None for v in entities.values()):
            with st.expander("🔍 Details", expanded=False):
                for key, value in entities.items():
                    if value is not None:
                        st.markdown(f"**{key.replace('_', ' ').title()}:** `{value}`")
        
        st.divider()
        
        # Action buttons
        cols = st.columns([1, 1, 1, 1])
        
        # Primary action button (changes based on intent)
        with cols[0]:
            if intent_type == "GO_TO":
                action_label = "🔗 Go"
            elif intent_type in ["CREATE_TASK", "CREATE_LEAD"]:
                action_label = "✅ Create"
            elif intent_type == "LOAD_DEMO":
                action_label = "🎬 Load"
            elif intent_type == "REPLY_DRAFTS":
                action_label = "📝 Draft"
            else:
                action_label = "✓ Confirm"
            
            if st.button(action_label, key=f"confirm_{index}", type="primary", use_container_width=True):
                _execute_action(intent)
        
        # Cancel button
        with cols[1]:
            if st.button("✕ Cancel", key=f"cancel_{index}", use_container_width=True):
                st.session_state.pending_action = None
                st.rerun()
        
        # Optional: Edit button for certain intents
        if intent_type in ["CREATE_TASK", "CREATE_LEAD"]:
            with cols[2]:
                if st.button("✏️ Edit", key=f"edit_{index}", use_container_width=True):
                    # Store intent for editing (could open a form)
                    st.info("Edit functionality - open form with pre-filled values")


def _execute_action(intent: Dict):
    """Execute the confirmed action via copilot_router.
    
    Args:
        intent: Intent JSON to execute
    """
    with st.spinner("Executing..."):
        try:
            result = copilot_router.execute_intent(intent, st.session_state.copilot_context)
            
            # Add result to chat history
            response_msg = {
                "role": "assistant",
                "content": result.get("message", "Action completed."),
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
            st.session_state.copilot_history.append(response_msg)
            
            # Clear pending action
            st.session_state.pending_action = None
            
            # Navigate if needed
            if result.get("navigate_to"):
                st.session_state.page = result["navigate_to"]
            
            st.rerun()
            
        except Exception as e:
            st.error(f"Error executing action: {str(e)}")
            # Add error to history
            error_msg = {
                "role": "assistant",
                "content": f"❌ Error: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            st.session_state.copilot_history.append(error_msg)


def _render_chat_history():
    """Render the chat history with messages and action cards."""
    for i, msg in enumerate(st.session_state.copilot_history):
        role = msg.get("role", "assistant")
        content = msg.get("content", "")
        result = msg.get("result")
        
        with st.chat_message(role):
            st.markdown(content)
            
            # If message has a result, render it
            if result:
                _render_result_summary(result)
    
    # Render pending action card if exists
    if st.session_state.pending_action:
        with st.chat_message("assistant"):
            st.markdown("Here's what I can do:")
            _render_action_card(st.session_state.pending_action, index=999)


def _render_result_summary(result: Dict):
    """Render a summary of execution results.
    
    Args:
        result: Result dictionary from execute_intent()
    """
    result_type = result.get("type")
    data = result.get("data", {})
    
    if result_type == "REPLY_DRAFTS":
        drafts = data.get("drafts", [])
        if drafts:
            st.markdown("**📝 Draft Replies:**")
            for i, draft in enumerate(drafts, 1):
                with st.expander(f"Draft {i}", expanded=(i == 1)):
                    st.markdown(draft)
                    if st.button(f"Copy Draft {i}", key=f"copy_draft_{i}_{result.get('timestamp', '')}"):
                        st.code(draft)
    
    elif result_type == "SUMMARY":
        summary = data.get("summary", "")
        if summary:
            st.markdown("**📝 Summary:**")
            st.info(summary)
    
    elif result_type == "CREATED":
        item_type = data.get("item_type", "item")
        item_id = data.get("item_id")
        st.success(f"✅ {item_type.title()} created successfully! (ID: {item_id})")
    
    elif result_type == "NAVIGATION":
        target = data.get("target")
        st.info(f"🔗 Navigate to: {target}")


def _handle_user_input():
    """Handle user input from chat and trigger intent parsing."""
    if prompt := st.chat_input("Tell me what you want to do..."):
        # Add user message to history
        user_msg = {
            "role": "user",
            "content": prompt,
            "timestamp": datetime.now().isoformat()
        }
        st.session_state.copilot_history.append(user_msg)
        
        # Parse intent
        with st.spinner("Analyzing..."):
            try:
                intent = copilot_router.parse_intent(prompt, st.session_state.copilot_context)
                
                # If requires confirmation, store as pending action
                if intent.get("requires_confirmation", True):
                    st.session_state.pending_action = intent
                else:
                    # Auto-execute safe actions (like SEARCH, GO_TO)
                    _execute_action(intent)
                
            except Exception as e:
                # Add error message to history
                error_msg = {
                    "role": "assistant",
                    "content": f"Sorry, I couldn't understand that. Error: {str(e)}",
                    "timestamp": datetime.now().isoformat()
                }
                st.session_state.copilot_history.append(error_msg)
        
        st.rerun()


def copilot_chat_view():
    """Main Copilot Chat view - conversational interface for the app."""
    theme = st.session_state.get("theme", "dark")
    inject_ui_kit_css(theme)
    
    # Initialize state
    _init_copilot_state()
    
    # Page header
    ui_page(
        title="Social Copilot",
        subtitle="Tell me what you want to do — I'll turn it into actions.",
        icon="🤖"
    )
    
    # Context info bar
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        lang = st.session_state.copilot_context.get("language", "en")
        st.markdown(ui_badge(f"Language: {lang.upper()}", "info"), unsafe_allow_html=True)
    with col2:
        thread_id = st.session_state.copilot_context.get("current_thread_id")
        if thread_id:
            st.markdown(ui_badge(f"Thread: {thread_id[:8]}...", "primary"), unsafe_allow_html=True)
    with col3:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.copilot_history = []
            st.session_state.pending_action = None
            st.rerun()
    
    st.divider()
    
    # Chat history container
    chat_container = st.container(height=500)
    with chat_container:
        _render_chat_history()
    
    # Chat input (always at bottom)
    _handle_user_input()
    
    # Sidebar quick actions (optional)
    with st.sidebar:
        st.markdown("### 🎯 Quick Actions")
        
        if st.button("📊 Go to Dashboard", use_container_width=True):
            st.session_state.page = "dashboard"
            st.rerun()
        
        if st.button("📥 Go to Inbox", use_container_width=True):
            st.session_state.page = "inbox"
            st.rerun()
        
        if st.button("👥 Go to Leads", use_container_width=True):
            st.session_state.page = "leads"
            st.rerun()
        
        if st.button("🎬 Load Demo Data", use_container_width=True):
            demo_intent = {
                "intent": "LOAD_DEMO",
                "confidence": 1.0,
                "entities": {},
                "steps": ["Generate demo conversations", "Create sample leads", "Add demo tasks"],
                "requires_confirmation": True,
                "confirmation_text": "Load demo data to showcase the app?"
            }
            st.session_state.pending_action = demo_intent
            st.rerun()
        
        st.divider()
        
        st.markdown("### 💡 Example Prompts")
        examples = [
            "Summarize the last conversation",
            "Draft replies for this thread",
            "Create a task for follow-up",
            "Go to the dashboard",
            "Create a new lead for ACME Corp",
        ]
        for example in examples:
            st.caption(f"• {example}")
