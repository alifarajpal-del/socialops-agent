"""UI Kit: Consistent cards, badges, metrics, and component system.
Enterprise-grade design system for SocialOps Agent with dark mode support.
"""

import streamlit as st
from typing import Optional, Literal
from contextlib import contextmanager


BadgeKind = Literal["info", "success", "warning", "danger", "muted", "primary"]


# Design Tokens
tokens = {
    "spacing": {"xs": "0.25rem", "sm": "0.5rem", "md": "1rem", "lg": "1.5rem", "xl": "2rem"},
    "radius": {"sm": "4px", "md": "8px", "lg": "12px"},
    "shadow": {"sm": "0 1px 3px rgba(0,0,0,0.12)", "md": "0 4px 6px rgba(0,0,0,0.16)"}
}

# Theme Colors
colors = {
    "light": {
        "bg": "#ffffff", "card_bg": "#f8f9fa", "text": "#1f2937", "muted": "#6b7280",
        "border": "#e5e7eb", "primary": "#3b82f6", "success": "#10b981",
        "warning": "#f59e0b", "danger": "#ef4444"
    },
    "dark": {
        "bg": "#0f172a", "card_bg": "#1e293b", "text": "#f1f5f9", "muted": "#94a3b8",
        "border": "#334155", "primary": "#60a5fa", "success": "#34d399",
        "warning": "#fbbf24", "danger": "#f87171"
    }
}


def inject_ui_kit_css(theme: str = "light") -> None:
    """Inject UI Kit CSS with theme support (once per session).
    
    Args:
        theme: "light" or "dark" (default: "light")
    """
    # Guard: inject only once per theme change
    current_theme = st.session_state.get("_css_theme", None)
    if st.session_state.get("_css_injected") and current_theme == theme:
        return
    
    theme = theme if theme in ["light", "dark"] else "light"
    c = colors[theme]
    t = tokens
    
    css = f"""
    <style>
        /* Global Theme */
        .stApp {{
            background-color: {c['bg']};
            color: {c['text']};
        }}
        
        /* Badge components */
        .badge {{
            display: inline-flex;
            align-items: center;
            gap: 4px;
            padding: 4px 12px;
            border-radius: {t['radius']['md']};
            font-size: 12px;
            font-weight: 600;
            line-height: 1.4;
        }}
        
        .badge-info {{
            background: {c['primary']}20;
            color: {c['primary']};
            border: 1px solid {c['primary']}40;
        }}
        
        .badge-success {{
            background: {c['success']}20;
            color: {c['success']};
            border: 1px solid {c['success']}40;
        }}
        
        .badge-warning {{
            background: {c['warning']}20;
            color: {c['warning']};
            border: 1px solid {c['warning']}40;
        }}
        
        .badge-danger {{
            background: {c['danger']}20;
            color: {c['danger']};
            border: 1px solid {c['danger']}40;
        }}
        
        .badge-muted {{
            background: {c['muted']}20;
            color: {c['muted']};
            border: 1px solid {c['muted']}40;
        }}
        
        .badge-primary {{
            background: {c['primary']}20;
            color: {c['primary']};
            border: 1px solid {c['primary']}40;
        }}
        
        /* UI Card */
        .ui-card {{
            background: {c['card_bg']};
            border: 1px solid {c['border']};
            border-radius: {t['radius']['md']};
            padding: {t['spacing']['md']};
            margin-bottom: {t['spacing']['md']};
            box-shadow: {t['shadow']['sm']};
        }}
        
        .ui-card-title {{
            font-size: 1.1rem;
            font-weight: 600;
            color: {c['text']};
            margin-bottom: {t['spacing']['sm']};
        }}
        
        /* KPI Metric */
        .ui-kpi {{
            background: {c['card_bg']};
            border: 1px solid {c['border']};
            border-radius: {t['radius']['md']};
            padding: {t['spacing']['md']};
            text-align: center;
            box-shadow: {t['shadow']['sm']};
        }}
        
        .ui-kpi-label {{
            font-size: 0.85rem;
            color: {c['muted']};
            margin-bottom: {t['spacing']['xs']};
        }}
        
        .ui-kpi-value {{
            font-size: 1.8rem;
            font-weight: 700;
            color: {c['text']};
        }}
        
        .ui-kpi-delta {{
            font-size: 0.8rem;
            margin-top: {t['spacing']['xs']};
        }}
        
        .ui-kpi-delta.positive {{ color: {c['success']}; }}
        .ui-kpi-delta.negative {{ color: {c['danger']}; }}
        
        /* Legacy metric-card */
        .metric-card {{
            background: {c['card_bg']};
            border: 1px solid {c['border']};
            border-radius: {t['radius']['md']};
            padding: 16px;
            text-align: center;
        }}
        
        .metric-label {{
            font-size: 13px;
            color: {c['muted']};
            margin-bottom: 4px;
        }}
        
        .metric-value {{
            font-size: 24px;
            font-weight: 700;
            color: {c['text']};
            line-height: 1.2;
        }}
        
        .metric-unit {{
            font-size: 14px;
            color: {c['muted']};
            margin-left: 4px;
        }}
        
        /* Section title */
        .section-title {{
            font-size: 18px;
            font-weight: 700;
            color: {c['text']};
            margin: 24px 0 12px 0;
            padding-bottom: 8px;
            border-bottom: 2px solid {c['border']};
        }}
        
        /* Pills row */
        .pills-row {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin: 12px 0;
        }}
        
        .pill {{
            padding: 6px 14px;
            background: {c['card_bg']};
            color: {c['text']};
            border-radius: 16px;
            font-size: 13px;
            font-weight: 500;
            border: 1px solid {c['border']};
        }}
        
        /* Info card */
        .info-card {{
            padding: 16px;
            border-radius: {t['radius']['md']};
            border-left: 4px solid;
            margin: 12px 0;
        }}
        
        .info-card.info {{
            background: {c['primary']}10;
            border-color: {c['primary']};
        }}
        
        .info-card.success {{
            background: {c['success']}10;
            border-color: {c['success']};
        }}
        
        .info-card.warning {{
            background: {c['warning']}10;
            border-color: {c['warning']};
        }}
        
        .info-card.danger {{
            background: {c['danger']}10;
            border-color: {c['danger']};
        }}
        
        .info-card-title {{
            font-size: 14px;
            font-weight: 600;
            color: {c['text']};
            margin-bottom: 8px;
        }}
        
        .info-card-body {{
            font-size: 13px;
            color: {c['text']};
            line-height: 1.6;
        }}
        
        /* Responsive */
        @media only screen and (max-width: 768px) {{
            .ui-card {{
                padding: {t['spacing']['sm']};
                margin-bottom: {t['spacing']['sm']};
            }}
            
            .ui-kpi {{
                padding: {t['spacing']['sm']};
                margin-bottom: {t['spacing']['sm']};
            }}
            
            .ui-kpi-value {{
                font-size: 1.4rem;
            }}
            
            .stButton button {{
                width: 100% !important;
            }}
        }}
    </style>
    """
    
    st.markdown(css, unsafe_allow_html=True)
    st.session_state["_css_injected"] = True
    st.session_state["_css_theme"] = theme


def ui_page(title: str, subtitle: Optional[str] = None, icon: str = "💬") -> None:
    """Render page header with title, subtitle, and icon.
    
    Args:
        title: Page title
        subtitle: Optional subtitle/description
        icon: Emoji icon (default: 💬)
    """
    st.title(f"{icon} {title}")
    if subtitle:
        st.caption(subtitle)
    st.divider()


@contextmanager
def ui_card(title: Optional[str] = None, icon: Optional[str] = None):
    """Context manager for card container.
    
    Args:
        title: Optional card title
        icon: Optional emoji icon
        
    Usage:
        with ui_card(title="My Card", icon="📊"):
            st.write("Content here")
    """
    if title:
        title_text = f"{icon} {title}" if icon else title
        st.markdown(f'<div class="ui-card"><div class="ui-card-title">{title_text}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="ui-card">', unsafe_allow_html=True)
    
    container = st.container()
    yield container
    
    st.markdown('</div>', unsafe_allow_html=True)


def ui_kpi(label: str, value: str, delta: Optional[str] = None) -> None:
    """Render KPI metric card.
    
    Args:
        label: Metric label
        value: Metric value (formatted string)
        delta: Optional delta/change indicator (e.g., "+12%", "-5")
    """
    delta_class = ""
    if delta:
        if delta.startswith("+") or (delta[0].isdigit() and float(delta.rstrip("%")) > 0):
            delta_class = "positive"
        elif delta.startswith("-"):
            delta_class = "negative"
    
    delta_html = f'<div class="ui-kpi-delta {delta_class}">{delta}</div>' if delta else ""
    
    html = f"""
    <div class="ui-kpi">
        <div class="ui-kpi-label">{label}</div>
        <div class="ui-kpi-value">{value}</div>
        {delta_html}
    </div>
    """
    
    st.markdown(html, unsafe_allow_html=True)


def ui_badge(text: str, kind: str = "info") -> str:
    """Generate badge HTML.
    
    Args:
        text: Badge text
        kind: Badge type (info|success|warning|danger)
        
    Returns:
        HTML string for badge
    """
    kind = kind if kind in ["info", "success", "warning", "danger", "muted", "primary"] else "info"
    return f'<span class="badge badge-{kind}">{text}</span>'


def badge(text: str, kind: BadgeKind = "info", icon: Optional[str] = None) -> str:
    """Generate a badge HTML (legacy compatibility).
    
    Args:
        text: Badge text
        kind: Badge style variant
        icon: Optional emoji/icon to show before text
    
    Returns:
        HTML string for the badge
    """
    icon_html = f'<span>{icon}</span>' if icon else ''
    return f'<span class="badge badge-{kind}">{icon_html}{text}</span>'


def metric(label: str, value: str, unit: str = "", delta: Optional[str] = None) -> None:
    """Display a metric card.
    
    Args:
        label: Metric label
        value: Metric value
        unit: Optional unit (e.g., "g", "%", "kcal")
        delta: Optional delta/change indicator
    """
    unit_html = f'<span class="metric-unit">{unit}</span>' if unit else ''
    delta_html = f'<div style="font-size: 12px; color: #10b981; margin-top: 4px;">{delta}</div>' if delta else ''
    
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}{unit_html}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def section_title(text: str, icon: Optional[str] = None) -> None:
    """Display a section title with optional icon.
    
    Args:
        text: Section title text
        icon: Optional emoji/icon
    """
    icon_html = f'{icon} ' if icon else ''
    st.markdown(f'<div class="section-title">{icon_html}{text}</div>', unsafe_allow_html=True)


def pills_row(items: list[str], interactive: bool = False) -> None:
    """Display a row of pill badges.
    
    Args:
        items: List of pill text items
        interactive: Whether pills should appear clickable (visual only)
    """
    style_extra = 'cursor: pointer;' if interactive else ''
    pills_html = ''.join([
        f'<span class="pill" style="{style_extra}">{item}</span>'
        for item in items
    ])
    
    st.markdown(f'<div class="pills-row">{pills_html}</div>', unsafe_allow_html=True)


@contextmanager
def card(title: Optional[str] = None, icon: Optional[str] = None):
    """Context manager for a consistent card layout (legacy compatibility).
    
    Args:
        title: Optional card title
        icon: Optional icon/emoji for title
    
    Usage:
        with card(title="نتائج التحليل", icon="🔬"):
            st.write("Card content here")
    """
    # Delegate to ui_card
    with ui_card(title=title, icon=icon) as container:
        yield container


def info_card(
    title: str,
    body: str,
    kind: Literal["info", "success", "warning", "danger"] = "info",
    icon: Optional[str] = None
) -> None:
    """Display an information card with colored border.
    
    Args:
        title: Card title
        body: Card body text
        kind: Card style variant
        icon: Optional icon/emoji
    """
    icon_html = f'{icon} ' if icon else ''
    
    st.markdown(f"""
    <div class="info-card {kind}">
        <div class="info-card-title">{icon_html}{title}</div>
        <div class="info-card-body">{body}</div>
    </div>
    """, unsafe_allow_html=True)


def confidence_badge(confidence: float, label: str = "الثقة") -> str:
    """Generate a confidence badge with appropriate styling.
    
    Args:
        confidence: Confidence score (0.0 to 1.0)
        label: Label text
    
    Returns:
        HTML string for the badge
    """
    if confidence >= 0.85:
        kind = "success"
        icon = "✓"
    elif confidence >= 0.65:
        kind = "warning"
        icon = "⚠"
    else:
        kind = "danger"
        icon = "⚠"
    
    percentage = int(confidence * 100)
    return badge(f"{label}: {percentage}%", kind=kind, icon=icon)


def source_badge(source: str, cached: bool = False) -> str:
    """Generate a source badge.
    
    Args:
        source: Data source name
        cached: Whether the data is from cache
    
    Returns:
        HTML string for the badge
    """
    source_names = {
        "fooddata": "USDA",
        "openfoodfacts": "Open Food Facts",
        "edamam": "Edamam",
        "nutritionix": "Nutritionix",
    }
    
    display_name = source_names.get(source, source)
    icon = "📦" if cached else "🌐"
    
    return badge(f"{icon} {display_name}", kind="info" if not cached else "muted")
