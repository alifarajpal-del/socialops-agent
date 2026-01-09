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
from ui_components.ui_kit import inject_ui_kit_css, ui_page, ui_card, ui_kpi, ui_badge, card
from utils.logging_setup import get_logger, log_user_action
from utils.i18n import t, get_lang

logger = get_logger(__name__)


def render_dashboard() -> None:
    """Render modern dashboard with card-based design."""
    safe_render(_render_dashboard_inner, context="dashboard")


def _render_dashboard_inner() -> None:
    # Inject CSS with theme support
    theme = st.session_state.get("theme", "light")
    inject_skeleton_css()
    inject_ui_kit_css(theme)
    
    log_user_action(logger, 'dashboard_view', {})
    lang = get_lang()
    
    # 1) Hero Header with UI Kit
    ui_page(
        title="SocialOps Agent",
        subtitle="Social Media Operations Platform - Manage conversations, leads & tasks",
        icon="💬"
    )
    
    # 2) KPI Row
    col_k1, col_k2, col_k3 = st.columns(3)
    
    try:
        from database.db_manager import get_db_path
        import sqlite3
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        
        with col_k1:
            cursor.execute("SELECT COUNT(*) FROM threads")
            thread_count = cursor.fetchone()[0]
            ui_kpi("💬 Active Threads", str(thread_count))
        
        with col_k2:
            cursor.execute("SELECT COUNT(*) FROM leads")
            lead_count = cursor.fetchone()[0]
            ui_kpi("👥 Total Leads", str(lead_count))
        
        with col_k3:
            cursor.execute("SELECT COUNT(*) FROM tasks WHERE status != 'completed'")
            task_count = cursor.fetchone()[0]
            ui_kpi("📋 Open Tasks", str(task_count))
        
        conn.close()
    except Exception as e:
        logger.error(f"Failed to fetch KPI metrics: {e}")
    
    st.divider()
    
    # 3) Primary Action Row (Demo Management)
    with ui_card(title="Demo Data Management", icon="🧪"):
        demo_col1, demo_col2, demo_col3 = st.columns(3)
        
        if 'demo_busy' not in st.session_state:
            st.session_state['demo_busy'] = False
        
        is_busy = st.session_state.get('demo_busy', False)
        
        with demo_col1:
            if st.button("🧪 Load Demo Data", use_container_width=True, disabled=is_busy, type="primary"):
                st.session_state['demo_busy'] = True
                try:
                    from services.demo_seed import seed_demo_all
                    seed_demo_all()
                    st.success("✅ Demo data loaded!")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
                finally:
                    st.session_state['demo_busy'] = False
                    st.rerun()
        
        with demo_col2:
            if st.button("🔄 Regenerate", use_container_width=True, disabled=is_busy):
                st.session_state['demo_busy'] = True
                try:
                    from services.demo_seed import seed_demo_regenerate
                    seed_demo_regenerate()
                    st.success("✅ Regenerated!")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
                finally:
                    st.session_state['demo_busy'] = False
                    st.rerun()
        
        with demo_col3:
            if st.button("🗑️ Clear Demo", use_container_width=True, disabled=is_busy):
                st.session_state['demo_busy'] = True
                try:
                    from services.demo_seed import clear_demo_all
                    clear_demo_all()
                    st.success("✅ Cleared!")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
                finally:
                    st.session_state['demo_busy'] = False
                    st.rerun()
    
    st.divider()
    
    # 4) Status Area
    with ui_card(title="Demo Status", icon="📊"):
        from services.demo_seed import get_demo_stats
        
        col_status, col_refresh = st.columns([4, 1])
        
        with col_status:
            stats = get_demo_stats()
            if not stats['exists']:
                st.info("📭 No demo data loaded")
            else:
                st.success(f"✅ Demo active: {stats['threads']} threads, {stats['leads']} leads, {stats['tasks']} tasks")
        
        with col_refresh:
            if st.button("🔄", use_container_width=True, key="refresh_demo_status"):
                st.rerun()
    
    st.divider()
    
    # 5) Quick Navigation Cards
    st.markdown("### Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        with ui_card(title="Inbox", icon="📬"):
            st.markdown("Manage conversations from all platforms")
            if st.button("Open Inbox →", use_container_width=True, key="nav_inbox"):
                from ui_components.router import go_to
                go_to('inbox')
                st.rerun()
    
    with col2:
        with ui_card(title="Daily Operations", icon="🛠️"):
            st.markdown("SLA monitoring, tasks & lead pipeline")
            if st.button("Open Ops →", use_container_width=True, key="nav_ops"):
                from ui_components.router import go_to
                go_to('ops')
                st.rerun()
    
    with col3:
        with ui_card(title="Leads", icon="👥"):
            st.markdown("CRM pipeline & customer management")
            if st.button("Open Leads →", use_container_width=True, key="nav_leads"):
                from ui_components.router import go_to
                go_to('leads')
                st.rerun()
    
def _render_kpi_card(icon: str, title: str, value: int, variant: str = "primary") -> None:
    """Render modern KPI card with icon and styling."""
    color_map = {
        "primary": "#3B82F6",
        "success": "#10B981", 
        "warning": "#F59E0B",
        "danger": "#EF4444"
    }
    color = color_map.get(variant, "#3B82F6")
    
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-icon" style="color: {color};">{icon}</div>
        <div class="kpi-content">
            <div class="kpi-value">{value:,}</div>
            <div class="kpi-title">{title}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def _inject_modern_dashboard_css() -> None:
    """Inject modern SocialOps theme CSS for dashboard."""
    st.markdown("""
    <style>
    .hero-header {
        background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
        padding: 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
        text-align: center;
    }
    
    .hero-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0 0 0.5rem 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .hero-subtitle {
        font-size: 1.1rem;
        margin: 0;
        opacity: 0.9;
    }
    
    .kpi-section {
        margin-bottom: 2rem;
    }
    
    .kpi-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        border: 1px solid #E5E7EB;
        display: flex;
        align-items: center;
        gap: 1rem;
        transition: transform 0.2s, box-shadow 0.2s;
        margin-bottom: 1rem;
    }
    
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    }
    
    .kpi-icon {
        font-size: 2rem;
        width: 3rem;
        height: 3rem;
        border-radius: 50%;
        background: rgba(59, 130, 246, 0.1);
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .kpi-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1F2937;
        line-height: 1;
    }
    
    .kpi-title {
        font-size: 0.875rem;
        color: #6B7280;
        font-weight: 500;
        margin-top: 0.25rem;
    }
    
    .modern-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        border: 1px solid #E5E7EB;
        margin-bottom: 1.5rem;
    }
    
    .card-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 1rem;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid #F3F4F6;
    }
    
    .card-icon {
        font-size: 1.25rem;
        color: #3B82F6;
    }
    
    .card-title {
        font-size: 1.125rem;
        font-weight: 600;
        color: #1F2937;
        margin: 0;
    }
    
    .action-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 1.5rem 0;
    }
    
    .action-btn {
        background: #3B82F6;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        font-weight: 500;
        transition: background 0.2s;
        cursor: pointer;
        text-decoration: none;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        justify-content: center;
    }
    
    .action-btn:hover {
        background: #2563EB;
    }
    </style>
    """, unsafe_allow_html=True)
    
    
    # Demo Management Card
    st.markdown("""
    <div class="modern-card">
        <div class="card-header">
            <span class="card-icon">🧪</span>
            <h3 class="card-title">Demo Data Management</h3>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Demo Status Section
    from services.demo_seed import get_demo_stats, get_demo_event_summary
    
    col_status, col_refresh = st.columns([4, 1])
    
    with col_status:
        stats = get_demo_stats()
        if not stats['exists']:
            st.info("📭 No demo data loaded")
        else:
            st.success(f"✅ Demo active: {stats['threads']} threads, {stats['leads']} leads, {stats['tasks']} tasks")
        
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
    
    # Quick Actions
    st.markdown('<div class="modern-card"><div class="card-header"><span class="card-icon">⚡</span><h3 class="card-title">Quick Actions</h3></div></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔍 Search Conversations", use_container_width=True, type="primary"):
            from ui_components.router import go_to
            go_to('search')
            st.rerun()
    
    with col2:
        if st.button("📊 Daily Operations", use_container_width=True):
            from ui_components.router import go_to
            go_to('ops')
            st.rerun()
    
    with col3:
        if st.button("💬 Inbox", use_container_width=True):
            from ui_components.router import go_to
            go_to('inbox')
            st.rerun()
    
    st.divider()
    
    # Demo Management
    st.markdown('<div class="modern-card"><div class="card-header"><span class="card-icon">🧪</span><h3 class="card-title">Demo Data Management</h3></div></div>', unsafe_allow_html=True)
    
    # Demo Actions
    demo_col1, demo_col2, demo_col3 = st.columns(3)
    
    # Initialize demo_busy lock
    if 'demo_busy' not in st.session_state:
        st.session_state['demo_busy'] = False
    
    is_busy = st.session_state.get('demo_busy', False)
    
    with demo_col1:
        if st.button("🧪 Load Demo Data", use_container_width=True, disabled=is_busy):
            st.session_state['demo_busy'] = True
            try:
                from services.demo_seed import seed_demo_all
                seed_demo_all()
                st.success("✅ Demo data loaded successfully!")
            except Exception as e:
                st.error(f"❌ Error: {e}")
            finally:
                st.session_state['demo_busy'] = False
                st.rerun()
    
    with demo_col2:
        if st.button("🔄 Regenerate", use_container_width=True, disabled=is_busy):
            st.session_state['demo_busy'] = True
            try:
                from services.demo_seed import seed_demo_regenerate
                seed_demo_regenerate()
                st.success("✅ Demo regenerated!")
            except Exception as e:
                st.error(f"❌ Error: {e}")
            finally:
                st.session_state['demo_busy'] = False
                st.rerun()
    
    with demo_col3:
        if st.button("🗑️ Clear Demo", use_container_width=True, disabled=is_busy):
            st.session_state['demo_busy'] = True
            try:
                from services.demo_seed import clear_demo_all
                clear_demo_all()
                st.success("✅ Demo data cleared!")
            except Exception as e:
                st.error(f"❌ Error: {e}")
            finally:
                st.session_state['demo_busy'] = False
                st.rerun()


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
