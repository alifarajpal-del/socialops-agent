"""
Search View - Unified search UI across threads, leads, and replies.

Provides search box with tabbed results and navigation to target pages.
"""

import streamlit as st
import logging

from services.search_service import search_all, search_threads, search_leads, search_replies
from ui_components.ui_kit import inject_ui_kit_css, ui_page, ui_card, ui_badge, card
from ui_components.router import go_to
from utils.i18n import get_lang
from utils.translations import get_text

logger = logging.getLogger(__name__)


def search_view():
    """Main search view with tabs for different result types."""
    try:
        inject_ui_kit_css()
        
        lang = get_lang()
        
        # Header
        st.title(f"🔍 {get_text('search_title', lang)}")
        st.caption(get_text('search_caption', lang))
        
        st.divider()
        
        # Search box
        query = st.text_input(
            get_text('search_box', lang),
            placeholder="Search threads, leads, replies...",
            key="search_query"
        )
        
        if not query or not query.strip():
            st.info(f"💡 {get_text('search_hint', lang)}")
            return
        
        # Tabs for result types
        tab_all, tab_inbox, tab_leads, tab_replies = st.tabs([
            f"📦 {get_text('search_tab_all', lang)}",
            f"📬 {get_text('search_tab_inbox', lang)}",
            f"👥 {get_text('search_tab_leads', lang)}",
            f"💬 {get_text('search_tab_replies', lang)}"
        ])
        
        with tab_all:
            results = search_all(query)
            _render_results(results, lang)
        
        with tab_inbox:
            results = search_threads(query)
            _render_results(results, lang)
        
        with tab_leads:
            results = search_leads(query)
            _render_results(results, lang)
        
        with tab_replies:
            results = search_replies(query)
            _render_results(results, lang)
    
    except Exception as e:
        logger.error(f"Search view error: {e}", exc_info=True)
        st.error(f"Error: {str(e)}")


def _render_results(results: list, lang: str):
    """Render search results with Open button."""
    if not results:
        st.info(f"🔍 {get_text('search_no_results', lang)}")
        return
    
    st.caption(f"Found {len(results)} result(s)")
    
    for result in results:
        with card(title=_get_result_title(result), icon=_get_result_icon(result)):
            st.caption(f"Type: {result['type'].capitalize()}")
            st.text(result['preview'])
            
            col1, col2 = st.columns([3, 1])
            
            with col2:
                if st.button(f"Open", key=f"open_{result['type']}_{result['id']}", use_container_width=True):
                    # Navigate to target page and select item
                    route_target = result['route_target']
                    
                    if route_target == 'inbox':
                        st.session_state.selected_thread_id = result['id']
                        go_to('inbox')
                    elif route_target == 'leads':
                        st.session_state.selected_lead_id = result['id']
                        go_to('leads')
                    elif route_target == 'replies':
                        st.session_state.selected_reply_id = result['id']
                        go_to('replies')
                    
                    st.rerun()


def _get_result_title(result: dict) -> str:
    """Get display title for result."""
    if result['type'] == 'thread':
        return f"{result['title']} ({result['platform']})"
    elif result['type'] == 'lead':
        return f"{result['name']} - {result['status']}"
    elif result['type'] == 'reply':
        return result['title']
    return "Unknown"


def _get_result_icon(result: dict) -> str:
    """Get icon for result type."""
    icons = {
        'thread': '📬',
        'lead': '👤',
        'reply': '💬'
    }
    return icons.get(result['type'], '📄')
