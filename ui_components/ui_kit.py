"""UI Kit: Consistent cards, badges, metrics, and component system.
Enterprise-grade design system for SocialOps Agent with dark mode support.
"""

import streamlit as st
from typing import Optional, Literal
from contextlib import contextmanager


BadgeKind = Literal["info", "success", "warning", "danger", "muted", "primary"]


# Design Tokens - Digital Luxury
tokens = {
    "spacing": {"xs": "0.25rem", "sm": "0.5rem", "md": "1rem", "lg": "1.5rem", "xl": "2rem"},
    "radius": {"sm": "8px", "md": "14px", "lg": "18px"},
    "shadow": {
        "sm": "0 2px 8px rgba(0,0,0,0.15)",
        "md": "0 4px 16px rgba(0,0,0,0.25)",
        "deep": "0 8px 32px rgba(0,0,0,0.35)"
    },
    "blur": {"glass": "20px", "heavy": "30px"}
}

# Theme Colors - Cold Royal Obsidian (Digital Luxury)
colors = {
    "light": {
        "bg": "#020406",  # bg-void: OLED-safe base
        "card_bg": "#0B1015",  # bg-obsidian: Card surface with navy tint
        "glass_bg": "rgba(11, 16, 21, 0.70)",  # Glassmorphism overlay
        "text": "#E8DCCA",  # gold-champagne: Primary text (platinum/beige)
        "muted": "#8C7B50",  # gold-muted: Secondary text (oxidized)
        "border": "#D4AF37",  # gold-metallic: Active borders/icons
        "primary": "#D4AF37",  # gold-metallic: Primary accent
        "success": "#00A86B",  # success-emerald: Cold, desaturated
        "warning": "#D4AF37",  # Gold for warnings
        "danger": "#800020"  # error-crimson: Deep jewel tone
    },
    "dark": {
        "bg": "#020406",  # bg-void: OLED-safe base
        "card_bg": "#0B1015",  # bg-obsidian: Card surface
        "glass_bg": "rgba(11, 16, 21, 0.70)",  # Glassmorphism overlay
        "text": "#E8DCCA",  # gold-champagne: Primary text
        "muted": "#8C7B50",  # gold-muted: Secondary text
        "border": "#D4AF37",  # gold-metallic: Borders
        "primary": "#D4AF37",  # gold-metallic: Primary
        "success": "#00A86B",  # success-emerald
        "warning": "#D4AF37",  # Gold warnings
        "danger": "#800020"  # error-crimson
    }
}


def inject_ui_kit_css(theme: str = "light") -> None:
    """Inject UI Kit CSS with theme support (once per session).
    
    Args:
        theme: "light" or "dark" (default: "light")
    """
    # Guard: inject only once per theme change
    guard_key = f"_css_injected_{theme}"
    if st.session_state.get(guard_key, False):
        return
    
    theme = theme if theme in ["light", "dark"] else "light"
    c = colors[theme]
    t = tokens
    
    css = f"""
    <style>
        /* Import Luxury Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Manrope:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');
        
        /* CSS RESET - Remove any leaked backgrounds/pseudo-elements */
        * {{
            background-image: none !important;
        }}
        *::before, *::after {{
            content: none !important;
            display: none !important;
        }}
        
        /* Global Theme - Force background and text colors */
        .stApp {{
            background-color: {c['bg']} !important;
            color: {c['text']} !important;
            font-family: 'Manrope', -apple-system, sans-serif !important;
        }}        
        /* Typography Hierarchy */
        h1, h2, h3, .ui-heading {{
            font-family: 'Playfair Display', serif !important;
            font-weight: 600 !important;
            letter-spacing: -0.02em !important;
            line-height: 1.2 !important;
        }
        
        h1 { font-size: 2.5rem !important; }
        h2 { font-size: 2rem !important; }
        h3 { font-size: 1.5rem !important; }
        
        .ui-data, .ui-mono, .ui-kpi-value, .metric-value {{
            font-family: 'JetBrains Mono', monospace !important;
            font-variant-numeric: tabular-nums !important;
        }}
        
        section.main, .block-container {{
            background-color: {c['bg']} !important;
            color: {c['text']} !important;
        }}
        
        /* All text elements */
        .stMarkdown, .stText, .stCaption, p, div, span {{
            color: {c['text']} !important;
            background: transparent !important;
        }}
        
        /* Inputs and controls */
        input, select, textarea, button {{
            background-color: {c['card_bg']} !important;
            color: {c['text']} !important;
            border-color: {c['border']} !important;
        }}
        
        /* Tables */
        table, th, td {{
            background-color: {c['card_bg']} !important;
            color: {c['text']} !important;
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
            background-image: none !important;
        }}
        
        .badge-info {{
            background: {c['primary']}20 !important;
            color: {c['primary']} !important;
            border: 1px solid {c['primary']}40;
        }}
        
        .badge-success {{
            background: {c['success']}20 !important;
            color: {c['success']} !important;
            border: 1px solid {c['success']}40;
        }}
        
        .badge-warning {{
            background: {c['warning']}20 !important;
            color: {c['warning']} !important;
            border: 1px solid {c['warning']}40;
        }}
        
        .badge-danger {{
            background: {c['danger']}20 !important;
            color: {c['danger']} !important;
            border: 1px solid {c['danger']}40;
        }}
        
        .badge-muted {{
            background: {c['muted']}20 !important;
            color: {c['muted']} !important;
            border: 1px solid {c['muted']}40;
        }}
        
        .badge-primary {{
            background: {c['primary']}20 !important;
            color: {c['primary']} !important;
            border: 1px solid {c['primary']}40;
        }}
        
        /* UI Card - Gradient Border + Noise Texture + Deep Shadow */
        .ui-card {{
            background: {c['card_bg']} !important;
            border: 1px solid rgba(212, 175, 55, 0.15);
            border-radius: {t['radius']['md']};
            padding: {t['spacing']['md']};
            margin-bottom: {t['spacing']['md']};
            box-shadow: {t['shadow']['md']};
            opacity: 1 !important;
        }}
        
        .ui-card-title {{
            font-size: 1.1rem;
            font-weight: 600;
            color: {c['text']} !important;
            margin-bottom: {t['spacing']['sm']};
        }}
        
        /* KPI Metric - Luxury with gradient border */
        .ui-kpi {{
            background: {c['card_bg']} !important;
            border: 1px solid rgba(212, 175, 55, 0.15);
            border-radius: {t['radius']['md']};
            padding: {t['spacing']['lg']};
            text-align: center;
            box-shadow: {t['shadow']['md']};
            opacity: 1 !important;
        }}
        
        .ui-kpi-label {{
            font-size: 0.75rem;
            color: {c['muted']} !important;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-bottom: {t['spacing']['sm']};
        }}
        
        .ui-kpi-value {{
            font-family: 'JetBrains Mono', monospace !important;
            font-size: 2.2rem;
            font-weight: 600;
            color: {c['text']} !important;
            font-variant-numeric: tabular-nums;
        }}
        
        .ui-kpi-delta {{
            font-size: 0.8rem;
            margin-top: {t['spacing']['xs']};
        }}
        
        .ui-kpi-delta.positive {{ color: {c['success']} !important; }}
        .ui-kpi-delta.negative {{ color: {c['danger']} !important; }}
        
        /* Legacy metric-card */
        .metric-card {{
            background: {c['card_bg']} !important;
            border: 1px solid {c['border']};
            border-radius: {t['radius']['md']};
            padding: 16px;
            text-align: center;
            opacity: 1 !important;
        }}
        
        .metric-label {{
            font-size: 13px;
            color: {c['muted']} !important;
            margin-bottom: 4px;
        }}
        
        .metric-value {{
            font-size: 24px;
            font-weight: 700;
            color: {c['text']} !important;
            line-height: 1.2;
        }}
        
        .metric-unit {{
            font-size: 14px;
            color: {c['muted']} !important;
            margin-left: 4px;
        }}
        
        /* Section title */
        .section-title {{
            font-size: 18px;
            font-weight: 700;
            color: {c['text']} !important;
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
            background: {c['card_bg']} !important;
            color: {c['text']} !important;
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
            opacity: 1 !important;
        }}
        
        .info-card.info {{
            background: {c['primary']}10 !important;
            border-color: {c['primary']};
        }}
        
        .info-card.success {{
            background: {c['success']}10 !important;
            border-color: {c['success']};
        }}
        
        .info-card.warning {{
            background: {c['warning']}10 !important;
            border-color: {c['warning']};
        }}
        
        .info-card.danger {{
            background: {c['danger']}10 !important;
            border-color: {c['danger']};
        }}
        
        .info-card-title {{
            font-size: 14px;
            font-weight: 600;
            color: {c['text']} !important;
            margin-bottom: 8px;
        }}
        
        .info-card-body {{
            font-size: 13px;
            color: {c['text']} !important;
            line-height: 1.6;
        }}
        
        /* Glassmorphism Navigation/Header */
        .glass-nav {{
            background: {c['glass_bg']} !important;
            backdrop-filter: blur({t['blur']['glass']}) !important;
            -webkit-backdrop-filter: blur({t['blur']['glass']}) !important;
            border-bottom: 1px solid rgba(212, 175, 55, 0.2);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        }}
        
        /* Concierge Data Table - Professional Mobile Layout */
        .concierge-table {{
            width: 100%;
            border-collapse: collapse;
            background: {c['card_bg']} !important;
            border-radius: {t['radius']['md']};
            overflow: hidden;
            box-shadow: {t['shadow']['deep']};
        }}
        
        .concierge-table thead {{
            background: {c['bg']} !important;
            border-bottom: 2px solid {c['border']};
        }}
        
        .concierge-table th {{
            padding: 1rem;
            text-align: left;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: {c['border']} !important;
            font-family: 'Manrope', sans-serif !important;
        }}
        
        .concierge-table tbody tr {{
            border-bottom: 1px solid rgba(212, 175, 55, 0.1);
            transition: background 0.2s ease;
        }}
        
        .concierge-table tbody tr:nth-child(even) {{
            background: rgba(255, 255, 255, 0.03) !important;
        }}
        
        .concierge-table tbody tr:hover {{
            background: rgba(212, 175, 55, 0.08) !important;
        }}
        
        .concierge-table td {{
            padding: 1rem;
            color: {c['text']} !important;
            font-size: 0.9rem;
        }}
        
        .concierge-table td.numeric {{
            font-family: 'JetBrains Mono', monospace !important;
            font-variant-numeric: tabular-nums;
            text-align: right;
        }}
        
        /* Concierge Input - Underline Style with Float Label */
        .concierge-input-wrapper {{
            position: relative;
            margin: 1.5rem 0;
        }}
        
        .concierge-input {{
            width: 100%;
            padding: 0.75rem 0;
            background: transparent !important;
            border: none;
            border-bottom: 1px solid {c['muted']};
            color: {c['text']} !important;
            font-family: 'Manrope', sans-serif;
            font-size: 1rem;
            outline: none;
            transition: border-color 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .concierge-input:focus {{
            border-bottom-color: {c['border']};
            box-shadow: 0 1px 0 0 {c['border']}, 0 4px 12px rgba(212, 175, 55, 0.2);
        }}
        
        .concierge-label {{
            position: absolute;
            left: 0;
            top: 0.75rem;
            color: {c['muted']} !important;
            font-size: 1rem;
            pointer-events: none;
            transition: all 0.3s ease;
        }}
        
        .concierge-input:focus + .concierge-label,
        .concierge-input:not(:placeholder-shown) + .concierge-label {{
            top: -1.25rem;
            font-size: 0.75rem;
            color: {c['border']} !important;
            letter-spacing: 0.05em;
            text-transform: uppercase;
        }}
        
        /* Responsive - Mobile Full Support */
        @media only screen and (max-width: 768px) {{
            /* Force container padding smaller */
            .block-container {{
                padding: 1rem 0.5rem !important;
            }}
            
            /* Cards full width, reduced padding */
            .ui-card {{
                padding: {t['spacing']['sm']};
                margin-bottom: {t['spacing']['sm']};
                width: 100% !important;
            }}
            
            /* KPI stacked */
            .ui-kpi {{
                padding: {t['spacing']['sm']};
                margin-bottom: {t['spacing']['sm']};
                width: 100% !important;
            }}
            
            .ui-kpi-value {{
                font-size: 1.4rem;
            }}
            
            /* Buttons full width */
            .stButton button {{
                width: 100% !important;
            }}
            
            /* Inputs full width */
            input, textarea, select {{
                width: 100% !important;
            }}
            
            /* Tables scrollable */
            table, .concierge-table {{
                display: block;
                overflow-x: auto;
                white-space: nowrap;
            }}
            
            /* Concierge table mobile - stack layout */
            .concierge-table thead {{
                display: none;
            }}
            
            .concierge-table tbody tr {{
                display: block;
                margin-bottom: 1rem;
                border: 1px solid {c['border']};
                border-radius: {t['radius']['sm']};
                padding: 0.75rem;
            }}
            
            .concierge-table td {{
                display: block;
                text-align: right;
                padding: 0.5rem 0;
                border-bottom: 1px solid rgba(212, 175, 55, 0.1);
            }}
            
            .concierge-table td:last-child {{
                border-bottom: none;
            }}
            
            .concierge-table td::before {{
                content: attr(data-label);
                float: left;
                font-size: 0.75rem;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                color: {c['muted']} !important;
                font-weight: 600;
            }}
            
            /* Reduce font sizes slightly */
            .ui-kpi-label, .metric-label {{
                font-size: 0.75rem;
            }}
            
            .section-title {{
                font-size: 16px;
            }}
        }}
        
        @media only screen and (max-width: 480px) {{
            /* Extra small screens */
            .block-container {{
                padding: 0.5rem 0.25rem !important;
            }}
            
            .ui-card, .ui-kpi {{
                padding: 0.5rem;
                margin-bottom: 0.5rem;
            }}
            
            .ui-kpi-value {{
                font-size: 1.2rem;
            }}
            
            .section-title {{
                font-size: 14px;
            }}
        }}
    </style>
    """
    
    st.markdown(css, unsafe_allow_html=True)
    st.session_state[guard_key] = True


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


def concierge_input(label: str, key: str, input_type: str = "text", placeholder: str = " ") -> str:
    """Render a luxury underline input with floating label.
    
    Args:
        label: Input label (floats up on focus)
        key: Streamlit widget key
        input_type: HTML input type (text, email, tel, number)
        placeholder: Placeholder (use space for float effect)
    
    Returns:
        Input value from st.text_input
    """
    html = f"""
    <div class="concierge-input-wrapper">
        <input type="{input_type}" class="concierge-input" placeholder="{placeholder}" />
        <label class="concierge-label">{label}</label>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
    # Use native Streamlit input for actual data capture (hidden with custom CSS if needed)
    return st.text_input(label, key=key, label_visibility="collapsed")


def concierge_table(data: list[dict], columns: list[dict]) -> None:
    """Render a luxury data table with zebra striping and monospace numbers.
    
    Args:
        data: List of row dictionaries
        columns: List of column configs [{"key": "name", "label": "Name", "numeric": False}, ...]
    
    Example:
        concierge_table(
            data=[{"name": "Item 1", "price": "$1,250.00"}, ...],
            columns=[
                {"key": "name", "label": "Item", "numeric": False},
                {"key": "price", "label": "Price", "numeric": True}
            ]
        )
    """
    thead_html = "".join([f"<th>{col['label']}</th>" for col in columns])
    
    tbody_rows = []
    for row in data:
        cells = []
        for col in columns:
            value = row.get(col['key'], '')
            cell_class = 'numeric' if col.get('numeric', False) else ''
            data_label = col['label']  # For mobile responsive label
            cells.append(f'<td class="{cell_class}" data-label="{data_label}">{value}</td>')
        tbody_rows.append(f"<tr>{''.join(cells)}</tr>")
    
    tbody_html = "".join(tbody_rows)
    
    table_html = f"""
    <table class="concierge-table">
        <thead>
            <tr>{thead_html}</tr>
        </thead>
        <tbody>
            {tbody_html}
        </tbody>
    </table>
    """
    
    st.markdown(table_html, unsafe_allow_html=True)


def glass_header(content: str) -> None:
    """Render a glassmorphism header/navigation bar.
    
    Args:
        content: HTML content for the header
    """
    st.markdown(f'<div class="glass-nav">{content}</div>', unsafe_allow_html=True)


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
