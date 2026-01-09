"""
Replies View - Manage reply templates library.

Provides UI for creating, editing, and deleting saved reply templates.
"""

import streamlit as st
import logging
from typing import Optional

from services.replies_store import RepliesStore
from ui_components.ui_kit import inject_ui_kit_css, ui_page, ui_card, ui_badge, card, pills_row
from utils.i18n import get_lang

logger = logging.getLogger(__name__)


def render_reply_form(reply_id: Optional[int] = None):
    """Render form to create or edit a reply."""
    replies_store = RepliesStore()
    
    # Get existing reply if editing
    existing_reply = None
    if reply_id:
        existing_reply = replies_store.get_reply(reply_id)
        if not existing_reply:
            st.error(f"Reply #{reply_id} not found")
            return
    
    form_title = "Edit Reply" if existing_reply else "New Reply"
    
    with st.form(key=f"reply_form_{reply_id or 'new'}"):
        st.markdown(f"### {form_title}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input(
                "Title",
                value=existing_reply['title'] if existing_reply else "",
                placeholder="E.g., Welcome Message"
            )
        
        with col2:
            lang = st.selectbox(
                "Language",
                options=["en", "ar", "fr"],
                index=["en", "ar", "fr"].index(existing_reply['lang']) if existing_reply else 0,
                format_func=lambda x: {"en": "English", "ar": "العربية", "fr": "Français"}[x]
            )
        
        body = st.text_area(
            "Reply Text",
            value=existing_reply['body'] if existing_reply else "",
            placeholder="Enter your reply template here...",
            height=150
        )
        
        tags_input = st.text_input(
            "Tags (comma-separated)",
            value=", ".join(existing_reply['tags']) if existing_reply and existing_reply['tags'] else "",
            placeholder="E.g., greeting, welcome, appointment"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            submitted = st.form_submit_button("💾 Save", use_container_width=True)
        
        with col2:
            cancelled = st.form_submit_button("❌ Cancel", use_container_width=True)
        
        if submitted:
            if not title or not body:
                st.error("Title and body are required")
                return
            
            tags = [t.strip() for t in tags_input.split(",") if t.strip()]
            
            if existing_reply:
                replies_store.update_reply(reply_id, title=title, body=body, tags=tags)
                st.success("✅ Reply updated!")
            else:
                replies_store.create_reply(title=title, body=body, lang=lang, tags=tags)
                st.success("✅ Reply created!")
            
            st.session_state.show_reply_form = False
            st.rerun()
        
        if cancelled:
            st.session_state.show_reply_form = False
            st.rerun()


def render_reply_card(reply: dict):
    """Render a single reply card."""
    with card():
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Title with language badge
            lang_badge = {"en": "🇬🇧 EN", "ar": "🇸🇦 AR", "fr": "🇫🇷 FR"}[reply['lang']]
            st.markdown(f"### {reply['title']} `{lang_badge}`")
            
            # Body preview
            body_preview = reply['body'][:100] + "..." if len(reply['body']) > 100 else reply['body']
            st.markdown(f"_{body_preview}_")
            
            # Tags
            if reply['tags']:
                pills_row(reply['tags'])
        
        with col2:
            # Actions
            if st.button("✏️ Edit", key=f"edit_{reply['id']}", use_container_width=True):
                st.session_state.editing_reply_id = reply['id']
                st.session_state.show_reply_form = True
                st.rerun()
            
            if st.button("🗑️ Delete", key=f"delete_{reply['id']}", use_container_width=True):
                replies_store = RepliesStore()
                replies_store.delete_reply(reply['id'])
                st.success("✅ Reply deleted!")
                st.rerun()


def replies_view():
    """Main replies management view."""
    try:
        inject_ui_kit_css()
        
        # Header
        st.title("💬 Replies Library")
        st.caption("Manage your saved reply templates for quick responses")
        
        st.divider()
        
        # Initialize store
        replies_store = RepliesStore()
        
        # Seed button (if table empty)
        replies_count = len(replies_store.list_replies())
        if replies_count == 0:
            with card(title="Get Started", icon="🌱"):
                st.info("Your replies library is empty. Seed with default templates to get started!")
                if st.button("🌱 Seed Default Replies (10 templates)", use_container_width=True, type="primary"):
                    count = replies_store.seed_defaults()
                    st.success(f"✅ Created {count} default replies!")
                    st.rerun()
            st.divider()
        
        # Filters and actions
        col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
        
        with col1:
            lang_filter = st.selectbox(
                "Language",
                options=["All", "en", "ar", "fr"],
                format_func=lambda x: {"All": "All Languages", "en": "🇬🇧 English", "ar": "🇸🇦 العربية", "fr": "🇫🇷 Français"}[x]
            )
        
        with col2:
            scope_filter = st.selectbox(
                "Scope",
                options=["All", "core", "plugin"],
                format_func=lambda x: {"All": "All", "core": "Core", "plugin": "Plugin"}[x]
            )
        
        with col3:
            st.write("")  # Spacing
        
        with col4:
            if st.button("➕ New", use_container_width=True, type="primary"):
                st.session_state.show_reply_form = True
                st.session_state.editing_reply_id = None
                st.rerun()
        
        st.divider()
        
        # Show form if triggered
        if st.session_state.get('show_reply_form'):
            render_reply_form(st.session_state.get('editing_reply_id'))
            st.divider()
        
        # Get filtered replies
        lang = None if lang_filter == "All" else lang_filter
        scope = None if scope_filter == "All" else scope_filter
        
        replies = replies_store.list_replies(scope=scope, lang=lang)
        
        if not replies:
            st.info("No replies found. Try adjusting filters or create a new reply.")
        else:
            st.markdown(f"### 📋 Replies ({len(replies)})")
            
            for reply in replies:
                render_reply_card(reply)
    
    except Exception as e:
        logger.error(f"Replies view error: {e}", exc_info=True)
        st.error(f"Error loading replies: {str(e)}")
