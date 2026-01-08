"""
Daily Ops View - Operations dashboard for daily tasks and SLA monitoring.

Shows SLA status, tasks due today/overdue, and lead status breakdown.
"""

import streamlit as st
import logging
from datetime import datetime, timedelta
from typing import Dict

from services.crm_store import CRMStore
from services.inbox_store import get_inbox_store
from services.replies_store import compute_sla_status
from ui_components import ui_kit
from utils.i18n import get_lang
from utils.translations import get_text

logger = logging.getLogger(__name__)


def ops_view():
    """Main daily operations dashboard."""
    try:
        ui_kit.inject_ui_kit_css()
        
        lang = get_lang()
        
        # Header
        st.title(f"📊 {get_text('ops_title', lang)}")
        st.caption(get_text('ops_caption', lang))
        
        st.divider()
        
        # SLA Status Section
        st.markdown(f"### ⏱️ {get_text('ops_sla_title', lang)}")
        _render_sla_metrics()
        
        st.divider()
        
        # Tasks Section
        st.markdown(f"### ✅ {get_text('ops_tasks_title', lang)}")
        _render_tasks_metrics()
        
        st.divider()
        
        # Leads Section
        st.markdown(f"### 👥 {get_text('ops_leads_title', lang)}")
        _render_leads_metrics()
    
    except Exception as e:
        logger.error(f"Ops view error: {e}", exc_info=True)
        st.error(f"Error: {str(e)}")


def _render_sla_metrics():
    """Render SLA status metrics."""
    try:
        store = get_inbox_store()
        threads = store.list_threads()
        
        sla_counts = {
            'urgent': 0,
            'warning': 0,
            'ok': 0
        }
        
        for thread in threads:
            messages = store.list_messages(thread['id'])
            if messages:
                last_msg = messages[-1]
                sla_status = compute_sla_status(last_msg.get('timestamp', ''), thread.get('platform', 'instagram'))
                
                if sla_status == 'urgent':
                    sla_counts['urgent'] += 1
                elif sla_status == 'warning':
                    sla_counts['warning'] += 1
                else:
                    sla_counts['ok'] += 1
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "🔴 Urgent",
                sla_counts['urgent'],
                help="Messages requiring immediate response"
            )
        
        with col2:
            st.metric(
                "🟡 Warning",
                sla_counts['warning'],
                help="Messages nearing SLA deadline"
            )
        
        with col3:
            st.metric(
                "🟢 OK",
                sla_counts['ok'],
                help="Messages within SLA"
            )
    
    except Exception as e:
        logger.error(f"SLA metrics error: {e}", exc_info=True)
        st.error("Error loading SLA metrics")


def _render_tasks_metrics():
    """Render tasks due today and overdue."""
    try:
        crm = CRMStore()
        tasks = crm.list_tasks()
        
        now = datetime.utcnow()
        today_end = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        
        overdue_count = 0
        today_count = 0
        upcoming_count = 0
        
        for task in tasks:
            if task['completed']:
                continue
            
            due_at = datetime.fromisoformat(task['due_at'].replace('Z', '+00:00'))
            
            if due_at < now:
                overdue_count += 1
            elif due_at < today_end:
                today_count += 1
            else:
                upcoming_count += 1
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "⚠️ Overdue",
                overdue_count,
                delta=f"-{overdue_count}" if overdue_count > 0 else None,
                delta_color="inverse"
            )
        
        with col2:
            st.metric(
                "📅 Due Today",
                today_count,
                help="Tasks due by end of today"
            )
        
        with col3:
            st.metric(
                "📆 Upcoming",
                upcoming_count,
                help="Tasks due after today"
            )
        
        # Show overdue tasks list
        if overdue_count > 0:
            with st.expander(f"⚠️ View {overdue_count} Overdue Task(s)"):
                for task in tasks:
                    if task['completed']:
                        continue
                    
                    due_at = datetime.fromisoformat(task['due_at'].replace('Z', '+00:00'))
                    if due_at < now:
                        days_overdue = (now - due_at).days
                        st.warning(f"**{task['title']}** (Overdue by {days_overdue} day(s))")
    
    except Exception as e:
        logger.error(f"Tasks metrics error: {e}", exc_info=True)
        st.error("Error loading tasks metrics")


def _render_leads_metrics():
    """Render leads by status."""
    try:
        crm = CRMStore()
        leads = crm.list_leads()
        
        status_counts = {
            'new': 0,
            'contacted': 0,
            'qualified': 0,
            'converted': 0,
            'lost': 0
        }
        
        for lead in leads:
            status = lead.get('status', 'new')
            if status in status_counts:
                status_counts[status] += 1
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("🆕 New", status_counts['new'])
        
        with col2:
            st.metric("💬 Contacted", status_counts['contacted'])
        
        with col3:
            st.metric("⭐ Qualified", status_counts['qualified'])
        
        with col4:
            st.metric("✅ Converted", status_counts['converted'])
        
        with col5:
            st.metric("❌ Lost", status_counts['lost'])
    
    except Exception as e:
        logger.error(f"Leads metrics error: {e}", exc_info=True)
        st.error("Error loading leads metrics")
