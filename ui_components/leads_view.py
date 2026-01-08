"""
Leads View - CRM Pipeline Management (Sprint 2).

Displays leads in Kanban-style pipeline with status columns.
"""

import streamlit as st
import logging
from datetime import datetime

from services.crm_store import CRMStore
from services.inbox_store import get_inbox_store
from ui_components import ui_kit
from ui_components.router import go_to

logger = logging.getLogger(__name__)

def _format_date(date_str: str) -> str:
    """Format ISO date as readable string."""
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime("%b %d, %Y")
    except:
        return date_str


def render_lead_card(lead: dict, crm: CRMStore):
    """Render a single lead card."""
    lead_id = lead['id']
    
    with ui_kit.card(title=f"Lead #{lead_id}", icon="👤"):
        # Lead name
        name = lead.get('name') or 'Unnamed Lead'
        st.markdown(f"### {name}")
        
        # Metadata
        col1, col2 = st.columns(2)
        with col1:
            platform_emoji = {'instagram': '📷', 'facebook': '👥', 'whatsapp': '💬'}.get(
                lead.get('source_platform', '').lower(), '📱'
            )
            st.caption(f"{platform_emoji} {lead.get('source_platform', 'Unknown')}")
        
        with col2:
            st.caption(f"📅 {_format_date(lead['updated_at'])}")
        
        # Tags
        if lead.get('tags'):
            tags_text = " ".join([f"`{tag}`" for tag in lead['tags']])
            st.markdown(tags_text)
        
        # Notes preview
        if lead.get('notes'):
            notes_preview = lead['notes'].split('\n')[-1][:50]
            with st.expander("📝 Notes"):
                st.text(lead['notes'])
        
        st.divider()
        
        # Actions
        col1, col2 = st.columns(2)
        
        with col1:
            # Status change
            statuses = ['new', 'qualified', 'followup', 'won', 'lost']
            current_status = lead['status']
            
            new_status = st.selectbox(
                "Status",
                options=statuses,
                index=statuses.index(current_status),
                key=f"status_{lead_id}",
                label_visibility="collapsed"
            )
            
            if new_status != current_status:
                if st.button("💾 Update", key=f"update_status_{lead_id}"):
                    crm.update_lead_status(lead_id, new_status)
                    st.success("Status updated!")
                    st.rerun()
        
        with col2:
            # Open related thread
            if lead.get('thread_id'):
                if st.button("💬 Open Thread", key=f"open_thread_{lead_id}", use_container_width=True):
                    st.session_state.selected_thread_id = lead['thread_id']
                    go_to('inbox')
                    st.rerun()


def render_tasks_section(crm: CRMStore):
    """Render tasks section."""
    with ui_kit.card(title="Upcoming Tasks", icon="✅"):
        tasks = crm.list_tasks(include_completed=False)
        
        if not tasks:
            st.info("No pending tasks")
            return
        
        now = datetime.utcnow()
        
        for task in tasks[:10]:  # Show max 10 tasks
            due_dt = datetime.fromisoformat(task['due_at'].replace('Z', '+00:00'))
            is_overdue = due_dt.replace(tzinfo=None) < now
            
            col1, col2, col3 = st.columns([1, 4, 2])
            
            with col1:
                if st.checkbox("", key=f"task_{task['id']}", value=False):
                    crm.complete_task(task['id'])
                    st.rerun()
            
            with col2:
                status_emoji = "🔴" if is_overdue else "🟢"
                st.markdown(f"{status_emoji} **{task['title']}**")
                st.caption(f"Due: {_format_date(task['due_at'])} · Type: {task['type']}")
            
            with col3:
                if task.get('related_lead_id'):
                    if st.button("👤", key=f"task_lead_{task['id']}"):
                        st.session_state.selected_lead_id = task['related_lead_id']
                        st.rerun()


def leads_view():
    """Main leads view entry point."""
    try:
        ui_kit.inject_ui_kit_css()
        
        # Header
        st.title("📊 Leads Pipeline")
        st.caption("Manage your leads through the sales pipeline")
        
        st.divider()
        
        # Initialize CRM
        crm = CRMStore()
        
        # Tasks section at top
        render_tasks_section(crm)
        
        st.divider()
        
        # Pipeline tabs
        tab_new, tab_qual, tab_follow, tab_won, tab_lost = st.tabs([
            "🆕 New",
            "✅ Qualified",
            "⏰ Follow-up",
            "🎉 Won",
            "❌ Lost"
        ])
        
        with tab_new:
            leads = crm.list_leads(status='new')
            if not leads:
                st.info("No new leads")
            else:
                st.caption(f"{len(leads)} lead(s)")
                for lead in leads:
                    render_lead_card(lead, crm)
        
        with tab_qual:
            leads = crm.list_leads(status='qualified')
            if not leads:
                st.info("No qualified leads")
            else:
                st.caption(f"{len(leads)} lead(s)")
                for lead in leads:
                    render_lead_card(lead, crm)
        
        with tab_follow:
            leads = crm.list_leads(status='followup')
            if not leads:
                st.info("No leads needing follow-up")
            else:
                st.caption(f"{len(leads)} lead(s)")
                for lead in leads:
                    render_lead_card(lead, crm)
        
        with tab_won:
            leads = crm.list_leads(status='won')
            if not leads:
                st.info("No won deals yet")
            else:
                st.caption(f"{len(leads)} lead(s)")
                for lead in leads:
                    render_lead_card(lead, crm)
        
        with tab_lost:
            leads = crm.list_leads(status='lost')
            if not leads:
                st.info("No lost leads")
            else:
                st.caption(f"{len(leads)} lead(s)")
                for lead in leads:
                    render_lead_card(lead, crm)
    
    except Exception as e:
        logger.error(f"Leads view error: {e}", exc_info=True)
        st.error(f"Error loading leads: {str(e)}")
