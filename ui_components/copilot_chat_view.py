"""Copilot Chat View - premium conversational surface for SocialOps Agent.

Users speak in natural language, Copilot proposes structured actions, users confirm.
Copilot never executes without explicit confirmation.
"""

from datetime import datetime
from typing import Dict

import streamlit as st

from services import copilot_router
from ui_components.ui_kit import inject_ui_kit_css

ICON_BLACKLIST = [
    "✅",
    "📝",
    "✉️",
    "👤",
    "🔗",
    "🎬",
    "💡",
    "📋",
    "🔍",
    "✕",
    "✓",
    "❌",
]


def _init_copilot_state() -> None:
    """Initialize chat history, context, and action buffers."""
    if "copilot_history" not in st.session_state:
        st.session_state.copilot_history = []

    if "copilot_context" not in st.session_state:
        st.session_state.copilot_context = {
            "language": st.session_state.get("language", "en"),
            "current_thread_id": None,
            "page": "copilot",
            "user_id": st.session_state.get("user_id", "demo_user"),
        }

    if "pending_action" not in st.session_state:
        st.session_state.pending_action = None

    if len(st.session_state.copilot_history) == 0:
        st.session_state.copilot_history.append(
            {
                "role": "assistant",
                "content": "Tell me what you want to do — I'll turn it into actions.",
                "timestamp": datetime.now().isoformat(),
            }
        )


def _sanitize_text(text: str) -> str:
    """Strip decorative icons and whitespace for calmer copy."""
    cleaned = text or ""
    for icon in ICON_BLACKLIST:
        cleaned = cleaned.replace(icon, "")
    return cleaned.strip()


def _primary_label(intent_type: str) -> str:
    mapping = {
        "SUMMARIZE_THREAD": "Summarize",
        "REPLY_DRAFTS": "Generate drafts",
        "CREATE_TASK": "Create task",
        "CREATE_LEAD": "Create lead",
        "GO_TO": "Go now",
        "LOAD_DEMO": "Load demo",
        "SEARCH": "Search",
    }
    return mapping.get(intent_type, "Confirm")


def _inject_copilot_css() -> None:
    css = """
    <style>
        .block-container {
            padding: 24px 6% 140px;
        }
        .copilot-shell {
            background-color: #050608;
            min-height: 100vh;
        }
        .copilot-header {
            margin-bottom: 12px;
        }
        .copilot-title {
            font-family: 'Playfair Display', serif;
            font-size: 1.8rem;
            letter-spacing: -0.02em;
            color: #f5f5f5;
            margin: 0;
        }
        .copilot-subtitle {
            color: #9b9b9b;
            font-size: 0.95rem;
            margin-top: 6px;
        }
        .copilot-meta {
            display: flex;
            gap: 16px;
            margin-top: 14px;
            font-size: 0.8rem;
            letter-spacing: 0.15em;
            text-transform: uppercase;
            color: #8a8a8a;
        }
        .copilot-meta span {
            opacity: 0.8;
        }
        div[data-testid="stChatMessageUser"],
        div[data-testid="stChatMessageAssistant"] {
            border-radius: 18px;
            padding: 16px 20px;
            margin-bottom: 12px;
        }
        div[data-testid="stChatMessageUser"] {
            background: #11151a;
            border: 1px solid rgba(255, 255, 255, 0.05);
            color: #f5f5f5;
        }
        div[data-testid="stChatMessageAssistant"] {
            background: #0b0f12;
            border: 1px solid rgba(255, 255, 255, 0.04);
            color: #d8d8d8;
        }
        .action-panel {
            background: #0d1114;
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 18px;
            padding: 20px;
            margin-top: 8px;
        }
        .action-panel h4 {
            color: #f5f5f5;
            margin-bottom: 12px;
            font-size: 1.05rem;
        }
        .action-panel p,
        .action-panel li {
            color: #b9b9b9;
        }
        .action-panel ul {
            padding-left: 18px;
            margin-bottom: 18px;
        }
        .action-primary button {
            background: #d4af37 !important;
            color: #050608 !important;
            border: none !important;
            font-weight: 600;
        }
        .action-secondary button {
            background: transparent !important;
            color: #b9b9b9 !important;
            border: 1px solid rgba(255, 255, 255, 0.15) !important;
        }
        div[data-testid="stChatInput"] {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            background: rgba(5, 6, 8, 0.96);
            padding: 18px 24px 22px;
            border-top: 1px solid rgba(255, 255, 255, 0.04);
        }
        div[data-testid="stChatInput"] textarea {
            background: #11151a !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            color: #f5f5f5 !important;
        }
        @media (max-width: 768px) {
            .block-container {
                padding: 18px 16px 150px;
            }
            .action-panel {
                padding: 16px;
            }
            .action-panel button {
                width: 100%;
            }
        }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def _render_header() -> None:
    header_html = """
    <div class="copilot-header">
        <p class="copilot-title">Social Copilot</p>
        <p class="copilot-subtitle">One calm command surface for every operational move.</p>
    </div>
    """

    col_header, col_button = st.columns([5, 1])
    with col_header:
        st.markdown(header_html, unsafe_allow_html=True)
    with col_button:
        if st.button("Reset", use_container_width=True):
            st.session_state.copilot_history = []
            st.session_state.pending_action = None
            _init_copilot_state()
            st.rerun()


def _render_action_panel(intent: Dict) -> None:
    intent_type = intent.get("intent", "UNKNOWN")
    title_map = {
        "SUMMARIZE_THREAD": "Summarize conversation",
        "REPLY_DRAFTS": "Draft replies",
        "CREATE_TASK": "Create task",
        "CREATE_LEAD": "Create lead",
        "GO_TO": "Navigate",
        "LOAD_DEMO": "Load demo data",
        "SEARCH": "Search",
    }
    title = title_map.get(intent_type, "Suggested action")
    steps = intent.get("steps", [])[:2]
    confirmation_text = intent.get("confirmation_text", "Proceed with this action?")
    block_key = f"{intent_type}_{intent.get('confirmation_text', '')}"

    st.markdown("<div class='action-panel'>", unsafe_allow_html=True)
    st.markdown(f"<h4>{title}</h4>", unsafe_allow_html=True)
    st.markdown(f"<p>{_sanitize_text(confirmation_text)}</p>", unsafe_allow_html=True)
    if steps:
        st.markdown("<ul>", unsafe_allow_html=True)
        for step in steps:
            st.markdown(f"<li>{_sanitize_text(step)}</li>", unsafe_allow_html=True)
        st.markdown("</ul>", unsafe_allow_html=True)

    primary_label = _primary_label(intent_type)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='action-primary'>", unsafe_allow_html=True)
        if st.button(primary_label, key=f"primary_{block_key}", use_container_width=True):
            _execute_action(intent)
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='action-secondary'>", unsafe_allow_html=True)
        if st.button("Cancel", key=f"cancel_{block_key}", use_container_width=True):
            st.session_state.pending_action = None
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)


def _render_result_summary(result: Dict) -> None:
    result_type = result.get("type")
    data = result.get("data", {})

    if result_type == "REPLY_DRAFTS":
        drafts = data.get("drafts", [])
        for i, draft in enumerate(drafts, start=1):
            st.markdown(f"**Draft {i}**")
            st.markdown(_sanitize_text(draft))
    elif result_type == "SUMMARY":
        summary = _sanitize_text(data.get("summary", ""))
        if summary:
            st.markdown("**Summary**")
            st.markdown(summary)
    elif result_type == "CREATED":
        label = _sanitize_text(data.get("item_type", "Item")).title()
        item_id = data.get("item_id")
        message = f"{label} created successfully"
        if item_id:
            message += f" (ID: {item_id})"
        st.markdown(message)
    elif result_type == "NAVIGATION":
        target = _sanitize_text(data.get("target", ""))
        if target:
            st.markdown(f"Navigate to: {target}")
    elif result_type == "DEMO_LOADED":
        st.markdown("Demo data loaded.")
    elif result_type == "SEARCH":
        query = _sanitize_text(data.get("query", ""))
        if query:
            st.markdown(f"Search results for {query}")


def _render_chat_history() -> None:
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.copilot_history:
            role = message.get("role", "assistant")
            content = _sanitize_text(message.get("content", ""))
            result = message.get("result")
            error = message.get("error")

            with st.chat_message(role):
                if content:
                    st.markdown(content)
                if error:
                    st.markdown(f"<div style='padding:8px 12px;background:#1a0f0f;border-left:3px solid #800020;color:#c99;font-size:0.85rem;border-radius:6px;margin-top:8px;'>{error}</div>", unsafe_allow_html=True)
                if result:
                    _render_result_summary(result)

        if st.session_state.pending_action:
            with st.chat_message("assistant"):
                st.markdown("Here is the action I'm ready to run.")
                _render_action_panel(st.session_state.pending_action)


def _execute_action(intent: Dict) -> None:
    with st.spinner("Working..."):
        try:
            result = copilot_router.execute_intent(intent, st.session_state.copilot_context)
            st.session_state.copilot_history.append(
                {
                    "role": "assistant",
                    "content": _sanitize_text(result.get("message", "Action completed.")),
                    "result": result,
                    "timestamp": datetime.now().isoformat(),
                }
            )
            st.session_state.pending_action = None
            if result.get("navigate_to"):
                st.session_state.page = result["navigate_to"]
            st.rerun()
        except Exception as exc:
            error_msg = str(exc)[:100] if len(str(exc)) > 100 else str(exc)
            st.session_state.copilot_history.append(
                {
                    "role": "assistant",
                    "content": "Unable to complete that action.",
                    "error": error_msg,
                    "timestamp": datetime.now().isoformat(),
                }
            )
            st.session_state.pending_action = None
            st.rerun()


def _handle_user_input() -> None:
    prompt = st.chat_input("Ask Social Copilot to do something…")
    if not prompt:
        return

    st.session_state.copilot_history.append(
        {
            "role": "user",
            "content": prompt,
            "timestamp": datetime.now().isoformat(),
        }
    )

    with st.spinner("Thinking..."):
        try:
            intent = copilot_router.parse_intent(prompt, st.session_state.copilot_context)
        except Exception as exc:
            error_msg = str(exc)[:80] if len(str(exc)) > 80 else str(exc)
            st.session_state.copilot_history.append(
                {
                    "role": "assistant",
                    "content": "I could not understand that yet.",
                    "error": error_msg,
                    "timestamp": datetime.now().isoformat(),
                }
            )
            st.rerun()
            return

        if not intent:
            st.session_state.copilot_history.append(
                {
                    "role": "assistant",
                    "content": "I need a bit more detail to help.",
                    "timestamp": datetime.now().isoformat(),
                }
            )
        elif intent.get("requires_confirmation", True):
            st.session_state.pending_action = intent
        else:
            _execute_action(intent)

    st.rerun()


def copilot_chat_view() -> None:
    """Render the premium Copilot conversational experience."""
    theme = st.session_state.get("theme", "dark")
    inject_ui_kit_css(theme)
    _inject_copilot_css()
    _init_copilot_state()

    st.markdown("<div class='copilot-shell'>", unsafe_allow_html=True)
    _render_header()
    _render_chat_history()
    st.markdown("</div>", unsafe_allow_html=True)

    _handle_user_input()
