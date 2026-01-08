"""
Dashboard view with modern card-based design.
Displays health metrics with rounded cards, soft shadows, and circular icons.
"""

import streamlit as st
import plotly.graph_objects as go
from plotly.colors import hex_to_rgb
import pandas as pd
from datetime import datetime, timedelta
from ui_components.theme_wheel import get_current_theme
from ui_components.error_ui import safe_render
from ui_components.micro_ux import skeleton_card, inject_skeleton_css
from ui_components.ui_kit import card, metric, badge, inject_ui_kit_css
from utils.logging_setup import get_logger, log_user_action
from utils.i18n import t, get_lang

logger = get_logger(__name__)


def render_dashboard() -> None:
    """Render modern dashboard with card-based design."""
    safe_render(_render_dashboard_inner, context="dashboard")


def _render_dashboard_inner() -> None:
    # Inject CSS
    inject_skeleton_css()
    inject_ui_kit_css()
    
    theme = get_current_theme()
    _inject_dashboard_css(theme)
    
    log_user_action(logger, 'dashboard_view', {})
    
    # Hero Header (Rebranding)
    st.markdown(f"""
    <div style="padding: 1.5rem 0; margin-bottom: 1.5rem; border-bottom: 1px solid {theme.get('background_secondary', '#e0e0e0')};">
        <h1 style="font-size: 2rem; font-weight: 700; color: {theme.get('text_primary', '#000')}; margin: 0 0 0.5rem 0; display: flex; align-items: center; gap: 0.5rem;">
            💬 {t('app_title')}
        </h1>
        <p style="font-size: 1rem; color: {theme.get('text_secondary', '#666')}; margin: 0;">
            {t('app_subtitle')}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick KPI Cards
    from database.db_manager import get_db_path
    import sqlite3
    
    col_k1, col_k2, col_k3 = st.columns(3)
    
    try:
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        
        with col_k1:
            cursor.execute("SELECT COUNT(*) FROM threads")
            thread_count = cursor.fetchone()[0]
            st.metric(t('app_hero_threads'), thread_count, delta=None)
        
        with col_k2:
            cursor.execute("SELECT COUNT(*) FROM leads")
            lead_count = cursor.fetchone()[0]
            st.metric(t('app_hero_leads'), lead_count, delta=None)
        
        with col_k3:
            cursor.execute("SELECT COUNT(*) FROM tasks WHERE status != 'completed'")
            task_count = cursor.fetchone()[0]
            st.metric(t('app_hero_tasks'), task_count, delta=None)
        
        conn.close()
    except Exception as e:
        logger.error(f"Failed to fetch KPI metrics: {e}")
    
    st.divider()
    
    st.markdown(f"## 🏠 {t('dashboard_title')}")
    
    # Demo Status Section (Sprint 5.4 & 5.6)
    from services.demo_seed import get_demo_stats, get_demo_event_summary
    
    st.markdown(f"### 📊 {t('demo_status_title')}")
    
    col_status, col_refresh = st.columns([4, 1])
    
    with col_status:
        stats = get_demo_stats()
        if not stats['exists']:
            st.info(t('demo_status_empty'))
        else:
            st.success(f"{t('demo_status_present')} {stats['threads']} threads, {stats['leads']} leads, {stats['tasks']} tasks, {stats['replies']} replies")
        
        # Show last action (Sprint 5.6)
        event_summary = get_demo_event_summary(limit=1)
        if event_summary['exists'] and event_summary['events']:
            last_event = event_summary['events'][0]
            event_type = last_event.get('event_type', '')
            ts = last_event.get('ts', '')
            
            # Format timestamp
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                time_ago = (datetime.utcnow() - dt.replace(tzinfo=None)).total_seconds()
                if time_ago < 60:
                    time_str = "just now"
                elif time_ago < 3600:
                    time_str = f"{int(time_ago / 60)}m ago"
                elif time_ago < 86400:
                    time_str = f"{int(time_ago / 3600)}h ago"
                else:
                    time_str = f"{int(time_ago / 86400)}d ago"
            except:
                time_str = ""
            
            # Get event type label
            event_labels = {
                'seed': t('demo_action_seed'),
                'clear': t('demo_action_clear'),
                'regenerate': t('demo_action_regenerate'),
                'integrity_check': t('demo_action_integrity')
            }
            event_label = event_labels.get(event_type, event_type)
            
            st.caption(f"{t('demo_last_action')}: {event_label} ({time_str})")
        else:
            st.caption(t('demo_last_action_none'))
    
    with col_refresh:
        if st.button(f"🔄 {t('refresh_demo_status')}", use_container_width=True, key="refresh_demo_stats"):
            st.rerun()
    
    st.divider()
    
    # Quick Actions (Sprint 5)
    col1, col2, col3 = st.columns([2, 2, 2])
    
    with col1:
        if st.button("🔍 Search", use_container_width=True):
            from ui_components.router import go_to
            go_to('search')
            st.rerun()
    
    with col2:
        if st.button("📊 Daily Ops", use_container_width=True):
            from ui_components.router import go_to
            go_to('ops')
            st.rerun()
    
    with col3:
        # Demo management buttons (Sprint 5.3/5.4)
        # Initialize demo_busy lock
        if 'demo_busy' not in st.session_state:
            st.session_state['demo_busy'] = False
        
        is_busy = st.session_state.get('demo_busy', False)
        
        col3a, col3b, col3c = st.columns(3)
        
        with col3a:
            if st.button(f"🧪 {t('load_demo')}", use_container_width=True, key="seed_demo", disabled=is_busy):
                from services.demo_seed import seed_demo_all
                from ui_components.router import go_to
                
                try:
                    st.session_state['demo_busy'] = True
                    result = seed_demo_all()
                    
                    if result.get('skipped'):
                        st.info(t('demo_exists'))
                    elif 'error' in result:
                        st.error(f"{t('demo_error')}: {result['error']}")
                    else:
                        st.success(f"✅ {t('demo_loaded')}: {result['threads']} threads, {result['leads']} leads, {result['tasks']} tasks, {result['replies']} replies")
                        go_to('ops')
                        st.rerun()
                finally:
                    st.session_state['demo_busy'] = False
        
        with col3b:
            # Regenerate with confirmation (Sprint 5.4)
            if 'confirm_regen_demo' not in st.session_state:
                st.session_state['confirm_regen_demo'] = False
            
            if not st.session_state['confirm_regen_demo']:
                if st.button(f"🔄 {t('regenerate_demo')}", use_container_width=True, key="regen_demo", disabled=is_busy):
                    st.session_state['confirm_regen_demo'] = True
                    st.rerun()
            else:
                # Show confirmation
                st.warning(t('confirm_regenerate_demo'))
                col_confirm, col_cancel = st.columns(2)
                
                with col_confirm:
                    if st.button(t('confirm'), use_container_width=True, key="confirm_regen"):
                        from services.demo_seed import seed_demo_regenerate
                        from ui_components.router import go_to
                        
                        try:
                            st.session_state['demo_busy'] = True
                            st.session_state['confirm_regen_demo'] = False
                            
                            result = seed_demo_regenerate()
                            
                            if 'error' in result.get('seeded', {}):
                                st.error(f"{t('demo_error')}: {result['seeded']['error']}")
                            elif 'error' in result.get('cleared', {}):
                                st.error(f"{t('demo_error')}: {result['cleared']['error']}")
                            else:
                                seeded = result['seeded']
                                st.success(f"✅ {t('demo_regenerated')}: {seeded['threads']} threads, {seeded['leads']} leads, {seeded['tasks']} tasks, {seeded['replies']} replies")
                                go_to('ops')
                                st.rerun()
                        finally:
                            st.session_state['demo_busy'] = False
                
                with col_cancel:
                    if st.button(t('cancel'), use_container_width=True, key="cancel_regen"):
                        st.session_state['confirm_regen_demo'] = False
                        st.rerun()
        
        with col3c:
            # Clear with confirmation (Sprint 5.4)
            if 'confirm_clear_demo' not in st.session_state:
                st.session_state['confirm_clear_demo'] = False
            
            if not st.session_state['confirm_clear_demo']:
                if st.button(f"🗑️ {t('clear_demo')}", use_container_width=True, key="clear_demo", disabled=is_busy):
                    st.session_state['confirm_clear_demo'] = True
                    st.rerun()
            else:
                # Show confirmation
                st.warning(t('confirm_clear_demo'))
                col_confirm, col_cancel = st.columns(2)
                
                with col_confirm:
                    if st.button(t('confirm'), use_container_width=True, key="confirm_clear"):
                        from services.demo_seed import clear_demo_all
                        
                        try:
                            st.session_state['demo_busy'] = True
                            st.session_state['confirm_clear_demo'] = False
                            
                            result = clear_demo_all()
                            
                            if 'error' in result:
                                st.error(f"{t('demo_error')}: {result['error']}")
                            else:
                                st.success(f"✅ {t('demo_cleared')}: {result['threads_deleted']} threads, {result['leads_deleted']} leads, {result['tasks_deleted']} tasks")
                                st.rerun()
                        finally:
                            st.session_state['demo_busy'] = False
                
                with col_cancel:
                    if st.button(t('cancel'), use_container_width=True, key="cancel_clear"):
                        st.session_state['confirm_clear_demo'] = False
                        st.rerun()
    
    st.divider()
    
    # Show skeleton while loading
    with st.spinner(""):
        _modern_stats_cards(theme)
    
    st.divider()

    col1, col2 = st.columns(2, gap="large")
    with col1:
        _health_score_trend(theme)
    with col2:
        _safety_breakdown(theme)

    st.divider()
    _activity_feed(theme)


def _inject_dashboard_css(theme: dict) -> None:
    """Inject modern card-based CSS for dashboard"""
    css = f"""
    <style>
        .stat-card {{
            background: var(--card-bg);
            border-radius: 20px;
            padding: 24px;
            box-shadow: 0 8px 24px var(--primary)15;
            border: 2px solid var(--secondary);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }}
        
        .stat-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, var(--card-color) 0%, var(--card-color-light) 100%);
        }}
        
        .stat-card:hover {{
            transform: translateY(-6px);
            box-shadow: 0 16px 40px var(--primary)25;
            border-color: var(--primary);
        }}
        
        .icon-circle {{
            width: 64px;
            height: 64px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 28px;
            margin-bottom: 16px;
            box-shadow: 0 8px 20px var(--card-color)30;
            background: linear-gradient(135deg, var(--card-color) 0%, var(--card-color-light) 100%);
        }}
        
        .stat-label {{
            color: var(--text);
            font-weight: 700;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 8px;
            opacity: 0.8;
        }}
        
        .stat-value {{
            color: var(--text);
            font-weight: 900;
            font-size: 36px;
            line-height: 1;
            margin-bottom: 8px;
        }}
        
        .stat-delta {{
            color: var(--text);
            font-size: 13px;
            font-weight: 600;
            opacity: 0.6;
        }}
        
        .activity-card {{
            background: var(--card-bg);
            border-radius: 16px;
            padding: 18px;
            margin-bottom: 12px;
            border: 2px solid var(--secondary);
            box-shadow: 0 4px 12px var(--primary)10;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 16px;
        }}
        
        .activity-card:hover {{
            transform: translateX(4px);
            box-shadow: 0 6px 20px var(--primary)20;
            border-color: var(--primary);
        }}
        
        .activity-icon {{
            width: 48px;
            height: 48px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            flex-shrink: 0;
        }}
        
        .chart-container {{
            background: var(--card-bg);
            border-radius: 20px;
            padding: 24px;
            border: 2px solid var(--secondary);
            box-shadow: 0 8px 24px var(--primary)15;
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def _modern_stats_cards(theme: dict) -> None:
    """Display modern statistics cards with circular icons."""
    cols = st.columns(4, gap="medium")
    
    # Get data (in real app, from database)
    history = st.session_state.get('analysis_history', [])
    total_scans = len(history)
    avg_score = sum([r.get('health_score', 0) for r in history]) / max(total_scans, 1) if history else 85
    safe_count = sum([1 for r in history if r.get('health_score', 0) > 70])
    warnings = sum([len(r.get('warnings', [])) for r in history])
    
    stats = [
        {
            "icon": "💚",
            "label": t('health_score'),
            "value": f"{int(avg_score)}",
            "delta": "+4 this week",
        },
        {
            "icon": "🔬",
            "label": t('total_scans'),
            "value": f"{total_scans}",
            "delta": "+12 today",
        },
        {
            "icon": "⚠️",
            "label": t('warnings'),
            "value": f"{warnings}",
            "delta": "Review needed",
        },
        {
            "icon": "✅",
            "label": t('safe_items'),
            "value": f"{safe_count}",
            "delta": f"{int(safe_count/max(total_scans, 1)*100)}% safe" if total_scans else "0%",
        },
    ]
    
    for col, stat in zip(cols, stats):
        with col:
            metric(
                label=stat['label'],
                value=stat['value'],
                delta=stat.get('delta'),
            )


def _health_score_trend(theme: dict) -> None:
    """Display health score trend chart with modern styling."""
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown(f"### 📈 {t('health_score')} Trend")
    
    dates = pd.date_range(end=datetime.now(), periods=14, freq="D")
    scores = [72 + i % 6 + (i * 0.6) for i in range(len(dates))]
    
    # Convert hex color to RGBA with transparency
    rgb = hex_to_rgb(theme['primary'])
    fillcolor = f"rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, 0.2)"
    
    fig = go.Figure()
    fig.add_scatter(
        x=dates, 
        y=scores, 
        mode="lines+markers",
        line=dict(color=theme['primary'], width=4, shape='spline'),
        marker=dict(size=8, color=theme['accent'], line=dict(width=2, color='white')),
        fill='tozeroy',
        fillcolor=fillcolor
    )
    fig.update_layout(
        height=300,
        margin=dict(l=0, r=0, t=10, b=0),
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False, color=theme['text']),
        yaxis=dict(showgrid=True, gridcolor=theme['secondary'], color=theme['text'])
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


def _safety_breakdown(theme: dict) -> None:
    """Display pie chart with modern styling."""
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown("### 🥧 توزيع الأمان")
    
    labels = ["آمن", "تحذير", "خطر"]
    values = [128, 11, 3]
    colors = ["#22c55e", "#f59e0b", "#ef4444"]
    
    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.6,
        marker=dict(colors=colors, line=dict(color='white', width=3)),
        textfont=dict(size=14, color='white', family='Arial Black'),
        hovertemplate='<b>%{label}</b><br>%{value} عنصر<br>%{percent}<extra></extra>'
    ))
    fig.update_layout(
        height=300,
        margin=dict(l=0, r=0, t=10, b=0),
        showlegend=True,
        legend=dict(orientation="v", x=1, y=0.5),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


def _activity_feed(theme: dict) -> None:
    """Display recent activity with modern card design."""
    st.markdown("### 📋 النشاط الأخير")
    
    items = [
        {
            "time": "منذ ساعتين",
            "item": "شوفان عضوي",
            "status": "آمن",
            "score": 92,
            "icon": "✅",
            "color": "#22c55e"
        },
        {
            "time": "منذ 5 ساعات",
            "item": "مشروب طاقة",
            "status": "تحذير",
            "score": 45,
            "icon": "⚠️",
            "color": "#f59e0b"
        },
        {
            "time": "منذ يوم",
            "item": "سمك السلمون الطازج",
            "status": "آمن",
            "score": 88,
            "icon": "✅",
            "color": "#22c55e"
        },
        {
            "time": "منذ يومين",
            "item": "شوكولاتة داكنة",
            "status": "آمن",
            "score": 78,
            "icon": "✅",
            "color": "#10b981"
        },
    ]
    
    for entry in items:
        st.markdown(
            f"""
            <div class="activity-card">
                <div class="activity-icon" style="background: {entry['color']}20; color: {entry['color']};">
                    {entry['icon']}
                </div>
                <div style="flex: 1;">
                    <div style="font-weight: 700; color: {theme['text']}; font-size: 16px; margin-bottom: 4px;">
                        {entry['item']}
                    </div>
                    <div style="font-size: 13px; color: {theme['text']}; opacity: 0.6;">
                        {entry['time']} • {entry['status']}
                    </div>
                </div>
                <div style="background: linear-gradient(135deg, {theme['primary']}, {theme['accent']});
                            color: white;
                            padding: 8px 16px;
                            border-radius: 12px;
                            font-weight: 800;
                            font-size: 18px;
                            box-shadow: 0 4px 12px {theme['primary']}30;">
                    {entry['score']}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
