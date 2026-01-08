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
from services.inbox_engine import compute_sla_status
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
        
        # Demo Status Banner (Sprint 5.4)
        from services.demo_seed import get_demo_stats
        
        col_demo, col_refresh_demo = st.columns([4, 1])
        
        with col_demo:
            stats = get_demo_stats()
            if not stats['exists']:
                st.info(get_text('demo_status_empty', lang))
            else:
                st.success(f"{get_text('demo_status_present', lang)} {stats['threads']} threads, {stats['leads']} leads, {stats['tasks']} tasks, {stats['replies']} replies")
        
        with col_refresh_demo:
            if st.button(f"🔄 {get_text('refresh_demo_status', lang)}", use_container_width=True, key="refresh_ops_demo"):
                st.rerun()
        
        st.divider()
        
        # Search & Filter Controls (Sprint 5.5)
        st.markdown(f"### 🔍 {get_text('ops_search', lang)}")
        
        col_search, col_sector, col_status, col_sort = st.columns([3, 2, 2, 2])
        
        with col_search:
            search_query = st.text_input(
                get_text('ops_search', lang),
                placeholder="Search threads/leads/messages",
                key="ops_search_input",
                label_visibility="collapsed"
            )
        
        with col_sector:
            sector_filter = st.selectbox(
                get_text('ops_filter_sector', lang),
                options=['all', 'salon', 'store', 'clinic'],
                format_func=lambda x: get_text(f'ops_{x}', lang),
                key="ops_sector_filter"
            )
        
        with col_status:
            status_filter = st.selectbox(
                get_text('ops_filter_status', lang),
                options=['all', 'overdue', 'today', 'tomorrow'],
                format_func=lambda x: get_text(f'ops_status_{x}' if x != 'all' else 'ops_all', lang),
                key="ops_status_filter"
            )
        
        with col_sort:
            sort_option = st.selectbox(
                get_text('ops_sort', lang),
                options=['newest', 'oldest', 'urgent'],
                format_func=lambda x: get_text(f'ops_sort_{x}', lang),
                key="ops_sort_option"
            )
        
        st.divider()
        
        # SLA Status Section
        st.markdown(f"### ⏱️ {get_text('ops_sla_title', lang)}")
        _render_sla_metrics(search_query, sector_filter, status_filter, sort_option)
        
        st.divider()
        
        # Tasks Section
        st.markdown(f"### ✅ {get_text('ops_tasks_title', lang)}")
        _render_tasks_metrics(search_query, sector_filter, status_filter, sort_option)
        
        st.divider()
        
        # Leads Section
        st.markdown(f"### 👥 {get_text('ops_leads_title', lang)}")
        _render_leads_metrics(search_query, sector_filter, status_filter, sort_option)
        
        st.divider()
        
        # Demo Activity Section (Sprint 5.6)
        st.markdown(f"### 📊 {get_text('demo_activity_title', lang)}")
        _render_demo_activity(lang)
    
    except Exception as e:
        logger.error(f"Ops view error: {e}", exc_info=True)
        st.error(f"Error: {str(e)}")


def _render_sla_metrics(search_query="", sector_filter="all", status_filter="all", sort_option="newest"):
    """Render SLA status metrics with optional filtering."""
    try:
        from services.demo_seed import infer_sector_from_thread_id
        
        store = get_inbox_store()
        threads = store.list_threads()
        
        # Apply filters
        filtered_threads = []
        for thread in threads:
            # Sector filter
            if sector_filter != 'all':
                thread_sector = infer_sector_from_thread_id(thread.get('id', ''))
                if thread_sector != sector_filter:
                    continue
            
            # Search filter
            if search_query:
                search_lower = search_query.lower()
                thread_subject = thread.get('subject', '').lower()
                if search_lower not in thread_subject:
                    # Also check messages
                    messages = store.list_messages(thread['id'])
                    message_match = any(search_lower in msg.get('text', '').lower() for msg in messages)
                    if not message_match:
                        continue
            
            filtered_threads.append(thread)
        
        sla_counts = {
            'urgent': 0,
            'warning': 0,
            'ok': 0
        }
        
        for thread in filtered_threads:
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


def _render_tasks_metrics(search_query="", sector_filter="all", status_filter="all", sort_option="newest"):
    """Render tasks due today and overdue with optional filtering."""
    try:
        from services.demo_seed import infer_sector_from_thread_id
        
        crm = CRMStore()
        tasks = crm.list_tasks()
        
        now = datetime.utcnow()
        today_end = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow_end = (now + timedelta(days=2)).replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Apply filters
        filtered_tasks = []
        for task in tasks:
            if task['completed']:
                continue
            
            # Sector filter
            if sector_filter != 'all':
                thread_id = task.get('related_thread_id', '')
                task_sector = infer_sector_from_thread_id(thread_id)
                if task_sector != sector_filter:
                    continue
            
            # Search filter
            if search_query:
                search_lower = search_query.lower()
                task_title = task.get('title', '').lower()
                task_desc = task.get('description', '').lower()
                if search_lower not in task_title and search_lower not in task_desc:
                    continue
            
            # Status filter
            due_at = datetime.fromisoformat(task['due_at'].replace('Z', '+00:00'))
            if status_filter == 'overdue' and due_at >= now:
                continue
            elif status_filter == 'today' and (due_at < now or due_at >= today_end):
                continue
            elif status_filter == 'tomorrow' and (due_at < today_end or due_at >= tomorrow_end):
                continue
            
            filtered_tasks.append(task)
        
        overdue_count = 0
        today_count = 0
        upcoming_count = 0
        
        for task in filtered_tasks:
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


def _render_leads_metrics(search_query="", sector_filter="all", status_filter="all", sort_option="newest"):
    """Render leads by status with optional filtering."""
    try:
        from services.demo_seed import infer_sector_from_thread_id
        
        crm = CRMStore()
        leads = crm.list_leads()
        
        # Apply filters
        filtered_leads = []
        for lead in leads:
            # Sector filter
            if sector_filter != 'all':
                thread_id = lead.get('thread_id', '')
                lead_sector = infer_sector_from_thread_id(thread_id)
                if lead_sector != sector_filter:
                    continue
            
            # Search filter
            if search_query:
                search_lower = search_query.lower()
                lead_name = lead.get('name', '').lower()
                lead_phone = lead.get('phone', '').lower()
                if search_lower not in lead_name and search_lower not in lead_phone:
                    continue
            
            filtered_leads.append(lead)
        
        status_counts = {
            'new': 0,
            'contacted': 0,
            'qualified': 0,
            'converted': 0,
            'lost': 0
        }
        
        for lead in filtered_leads:
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


def _render_demo_activity(lang: str):
    """Render demo activity panel with recent events and export buttons (Sprint 5.6)."""
    try:
        from services.demo_seed import get_demo_event_summary, get_demo_stats
        
        summary = get_demo_event_summary(limit=20)
        
        if not summary['exists']:
            st.info(get_text('demo_last_action_none', lang))
            return
        
        # Show recent events in expander
        with st.expander(f"📋 Recent Events ({len(summary['events'])})", expanded=False):
            if summary['events']:
                # Create simple table
                for event in summary['events'][:10]:  # Show top 10
                    ts = event.get('ts', '')
                    event_type = event.get('event_type', '')
                    payload = event.get('payload', {})
                    
                    # Format timestamp
                    try:
                        dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                        time_str = dt.strftime('%Y-%m-%d %H:%M')
                    except:
                        time_str = ts[:16] if len(ts) >= 16 else ts
                    
                    # Format summary
                    if event_type == 'seed':
                        summary_text = f"Seeded {payload.get('threads', 0)} threads"
                    elif event_type == 'clear':
                        summary_text = f"Cleared {payload.get('threads_deleted', 0)} threads"
                    elif event_type == 'regenerate':
                        seeded = payload.get('seeded', {})
                        summary_text = f"Regenerated {seeded.get('threads', 0)} threads"
                    elif event_type == 'integrity_check':
                        summary_text = f"Found {payload.get('orphans_found', 0)} orphans"
                    else:
                        summary_text = event_type
                    
                    st.text(f"{time_str} | {event_type:15} | {summary_text}")
        
        # Export buttons
        col_exp1, col_exp2 = st.columns(2)
        
        with col_exp1:
            # Export demo stats
            stats = get_demo_stats()
            stats_json = json.dumps(stats, indent=2)
            st.download_button(
                label=f"📥 {get_text('export_demo_stats', lang)}",
                data=stats_json.encode('utf-8'),
                file_name="demo_stats.json",
                mime="application/json",
                use_container_width=True
            )
        
        with col_exp2:
            # Export demo events
            events_json = json.dumps(summary['events'], indent=2)
            st.download_button(
                label=f"📥 {get_text('export_demo_events', lang)}",
                data=events_json.encode('utf-8'),
                file_name="demo_events.json",
                mime="application/json",
                use_container_width=True
            )
        
        # Show totals
        totals = summary['totals']
        st.caption(f"Total: {totals['seed_count']} seeds, {totals['clear_count']} clears, {totals['regen_count']} regens, {totals['integrity_count']} integrity checks")
    
    except Exception as e:
        logger.error(f"Demo activity error: {e}", exc_info=True)
        st.error("Error loading demo activity")
