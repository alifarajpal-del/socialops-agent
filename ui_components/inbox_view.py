"""
Unified Inbox View - Sprint A Implementation.

Displays conversation threads from all platforms with:
- Thread list with platform badges
- Selected thread message timeline
- AI-powered reply suggestions via plugin system
- Manual JSON import for testing without integrations
- Send button disabled by default (human-in-the-loop)
"""

import streamlit as st
import json
import logging
from datetime import datetime, timedelta
from typing import Optional

from services.inbox_store import get_inbox_store
from services.crm_store import CRMStore
from services.inbox_engine import get_lang
from services.plugins_registry import route_to_plugin
from services.settings_flags import enable_send
from ui_components import ui_kit

logger = logging.getLogger(__name__)


def _get_platform_badge(platform: str) -> str:
    """Get emoji badge for platform."""
    badges = {
        'instagram': '📷 Instagram',
        'facebook': '👥 Facebook',
        'whatsapp': '💬 WhatsApp'
    }
    return badges.get(platform.lower(), f'📱 {platform}')


def _format_timestamp(timestamp_str: str) -> str:
    """Format ISO timestamp as readable string."""
    try:
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        now = datetime.now()
        diff = now - dt.replace(tzinfo=None)
        
        if diff.days > 0:
            return f"{diff.days}d ago"
        elif diff.seconds > 3600:
            return f"{diff.seconds // 3600}h ago"
        elif diff.seconds > 60:
            return f"{diff.seconds // 60}m ago"
        else:
            return "Just now"
    except:
        return timestamp_str


def render_json_import():
    """Render manual JSON import section."""
    with st.expander("📥 Manual Import (Testing)", expanded=False):
        st.markdown("""
        ### Import Messages from JSON
        
        Upload a JSON file to test inbox without connecting to Meta/WhatsApp.
        
        **Format:**
        ```json
        [
          {
            "platform": "instagram",
            "sender_name": "Lina",
            "text": "مرحبا، بدي أحجز ميك أب",
            "timestamp": "2026-01-08T10:05:00Z"
          }
        ]
        ```
        
        Fields:
        - `platform`: instagram, facebook, or whatsapp
        - `sender_name`: Display name (required)
        - `text`: Message content (required)
        - `timestamp`: ISO format (optional)
        """)
        
        uploaded_file = st.file_uploader("Upload JSON", type=['json'], key='inbox_json_upload')
        
        if uploaded_file:
            try:
                content = uploaded_file.read().decode('utf-8')
                messages = json.loads(content)
                
                if not isinstance(messages, list):
                    st.error("JSON must be an array of messages")
                    return
                
                st.info(f"📦 Found {len(messages)} messages")
                
                if st.button("Import Messages", type="primary", use_container_width=True):
                    with st.spinner("Importing..."):
                        store = get_inbox_store()
                        result = store.import_from_json(messages)
                        
                        if result['imported'] > 0:
                            st.success(f"✅ Imported {result['imported']} messages into {result['threads_created']} threads!")
                            
                            if result['errors']:
                                with st.expander("⚠️ Warnings"):
                                    for error in result['errors']:
                                        st.warning(error)
                            
                            st.rerun()
                        else:
                            st.error("❌ Import failed")
                            for error in result['errors']:
                                st.error(error)
                
            except json.JSONDecodeError as e:
                st.error(f"Invalid JSON: {e}")
            except Exception as e:
                st.error(f"Error: {e}")


def render_thread_list(store, platform_filter):
    """Render thread list in left column."""
    threads = store.list_threads(platform_filter=platform_filter)
    
    if not threads:
        st.info("No conversations yet. Use Manual Import to add test data.")
        return
    
    for thread in threads:
        is_selected = st.session_state.get('selected_thread_id') == thread['thread_id']
        
        button_label = f"{_get_platform_badge(thread['platform'])}: {thread['title'] or 'Untitled'}"
        
        if st.button(
            button_label,
            key=f"thread_{thread['thread_id']}",
            use_container_width=True,
            type="primary" if is_selected else "secondary"
        ):
            st.session_state.selected_thread_id = thread['thread_id']
            st.rerun()
        
        st.caption(f"Updated: {_format_timestamp(thread['updated_at'])}")
        st.divider()


def render_thread_detail(store, thread_id):
    """Render selected thread messages and reply interface."""
    messages = store.get_thread_messages(thread_id)
    
    if not messages:
        st.info("No messages in this thread")
        return
    
    # Get thread info
    threads = store.list_threads()
    thread_info = next((t for t in threads if t['thread_id'] == thread_id), None)
    
    if not thread_info:
        st.error("Thread not found")
        return
    
    # Thread header
    st.markdown(f"### {_get_platform_badge(thread_info['platform'])}: {thread_info['title']}")
    st.divider()
    
    # Messages timeline
    with ui_kit.card(title="Messages", icon="💬"):
        for msg in messages:
            st.markdown(f"**{msg['sender_name']}** · {_format_timestamp(msg['timestamp'])}")
            st.info(msg['text'])
    
    st.divider()
    
    # CRM Actions
    with ui_kit.card(title="CRM Actions", icon="📊"):
        crm = CRMStore()
        existing_lead = crm.get_lead_by_thread(thread_id)
        
        if existing_lead:
            st.success(f"✅ Lead #{existing_lead['id']}: {existing_lead['name'] or 'Unnamed'}")
            st.caption(f"Status: {existing_lead['status'].upper()}")
            
            # Quick tags
            current_tags = existing_lead.get('tags', [])
            tag_options = ["hot-lead", "follow-up", "vip", "new-customer", "returning"]
            updated_tags = st.multiselect(
                "Tags",
                options=tag_options,
                default=current_tags,
                key=f"tags_{thread_id}"
            )
            
            if updated_tags != current_tags:
                if st.button("💾 Save Tags", key=f"save_tags_{thread_id}"):
                    crm.set_lead_tags(existing_lead['id'], updated_tags)
                    st.success("Tags updated!")
                    st.rerun()
            
            # Add note
            new_note = st.text_area(
                "Add Note",
                placeholder="Enter note about this lead...",
                key=f"note_{thread_id}",
                height=80
            )
            
            if new_note and st.button("📝 Add Note", key=f"add_note_{thread_id}"):
                crm.add_lead_note(existing_lead['id'], new_note)
                st.success("Note added!")
                st.rerun()
            
            # Show existing notes
            if existing_lead.get('notes'):
                with st.expander("📋 View Notes"):
                    st.text(existing_lead['notes'])
            
            # Follow-up task
            col1, col2 = st.columns(2)
            with col1:
                if st.button("⏰ Follow-up in 24h", key=f"followup_{thread_id}", use_container_width=True):
                    due_at = (datetime.utcnow() + timedelta(hours=24)).isoformat()
                    crm.create_task(
                        title=f"Follow up with {last_msg['sender_name']}",
                        due_at_iso=due_at,
                        lead_id=existing_lead['id'],
                        thread_id=thread_id,
                        task_type="followup"
                    )
                    st.success("✅ Task created!")
            
            with col2:
                if st.button("📁 View in Leads", key=f"view_lead_{thread_id}", use_container_width=True):
                    from ui_components.router import go_to
                    st.session_state.selected_lead_id = existing_lead['id']
                    go_to('leads')
                    st.rerun()
        else:
            st.info("No lead created for this conversation yet")
            
            if st.button("➕ Create Lead", key=f"create_lead_{thread_id}", type="primary", use_container_width=True):
                lead_name = last_msg.get('sender_name', 'Unknown')
                lead_id = crm.create_lead_from_thread(thread_id, thread_info['platform'], lead_name)
                st.success(f"✅ Lead #{lead_id} created!")
                st.rerun()
    
    st.divider()
    
    # Reply section
    with ui_kit.card(title="AI Suggested Reply", icon="🤖"):
        # Get plugin and generate suggestion
        last_msg = messages[-1]
        lang = get_lang()
        
        plugin = route_to_plugin(thread_info['platform'], last_msg['text'], lang)
        
        if plugin:
            intent = plugin.classify(last_msg['text'], lang)
            extracted = plugin.extract(last_msg['text'], lang)
            
            context = {
                'extracted': extracted,
                'sender_name': last_msg['sender_name'],
                'platform': thread_info['platform']
            }
            
            suggested_reply = plugin.suggest_reply(intent, lang, context)
            
            st.caption(f"Plugin: {plugin.name} | Intent: {intent}")
        else:
            suggested_reply = "Thank you for your message! How can I assist you?"
            st.caption("No plugin matched (using default reply)")
        
        # Editable reply
        reply_text = st.text_area(
            "Edit reply before sending:",
            value=suggested_reply,
            height=100,
            key="reply_text"
        )
        
        # Action buttons
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Regenerate", use_container_width=True):
                st.rerun()
        
        with col2:
            send_enabled = enable_send()
            
            if st.button(
                "📤 Send" if send_enabled else "🚫 Send (Disabled)",
                disabled=not send_enabled,
                use_container_width=True,
                type="primary" if send_enabled else "secondary"
            ):
                if send_enabled:
                    st.success("Message sent! (Stub - no actual API call)")
                    # In real implementation: call platform API
                else:
                    st.error("Send is disabled by default")
        
        if not send_enabled:
            st.caption("⚠️ Sending disabled by default (ENABLE_SEND=false). Human-in-the-loop only.")


def inbox_view():
    """Main inbox view entry point."""
    try:
        ui_kit.inject_ui_kit_css()
        
        # Header
        st.title("📬 Unified Inbox")
        st.caption("AI-powered social media message management")
        
        # Manual import
        render_json_import()
        
        st.divider()
        
        # Filters
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            platform_filter = st.selectbox(
                "Platform",
                ["All", "Instagram", "Facebook", "WhatsApp"],
                key="platform_filter"
            )
            platform_filter = None if platform_filter == "All" else platform_filter.lower()
        
        with col2:
            st.write("")  # Spacing
        
        with col3:
            if st.button("🔄 Refresh", use_container_width=True):
                st.rerun()
        
        st.divider()
        
        # Get store
        store = get_inbox_store()
        
        # Two-column layout
        col_left, col_right = st.columns([1, 2])
        
        with col_left:
            st.markdown("### Conversations")
            render_thread_list(store, platform_filter)
        
        with col_right:
            selected_thread_id = st.session_state.get('selected_thread_id')
            
            if selected_thread_id:
                render_thread_detail(store, selected_thread_id)
            else:
                st.info("👈 Select a conversation to view details")
    
    except Exception as e:
        logger.error(f"Inbox view error: {e}", exc_info=True)
        st.error(f"Error loading inbox: {str(e)}")
