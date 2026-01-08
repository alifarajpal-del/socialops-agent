"""Global styles and CSS tokens for consistent theming.
WCAG 2.2 compliant color contrast ratios.
"""

import streamlit as st
from ui_components.theme_wheel import get_current_theme


def inject_global_css():
    """Inject global CSS with theme support and utility classes."""
    theme = get_current_theme()
    # Override to Cold Royal Obsidian palette
    palette = {
        "background": "#020406",  # bg-void: OLED-safe base
        "card_bg": "#0B1015",  # bg-obsidian: Card surface with navy tint
        "primary": "#D4AF37",  # gold-metallic: Active borders/icons
        "secondary": "#8C7B50",  # gold-muted: Secondary text/dividers
        "accent": "#E8DCCA",  # gold-champagne: Primary text/headings
        "text": "#E8DCCA",  # gold-champagne
        "text_secondary": "#8C7B50",  # gold-muted
    }
    theme = {**theme, **palette}
    st.markdown(f"""
    <style>
        /* Import Luxury Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Manrope:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');
        
        /* ============== CSS Tokens (Cold Royal Obsidian) ============== */
        :root {{
            /* Theme colors */
            --bg: {theme['background']};
            --card-bg: {theme['card_bg']};
            --primary: {theme['primary']};
            --secondary: {theme['secondary']};
            --accent: {theme['accent']};
            --text: {theme['text']};
            
            /* Extended palette - WCAG 2.2 compliant */
            --surface: #0B1015;
            --text-muted: #8C7B50;
            --border: #D4AF37;
            --primary-hover: #E3DAC9;
            --success: #00A86B;
            --warning: #D4AF37;
            --danger: #800020;
            --info: #D4AF37;
            
            /* Spacing */
            --spacing-xs: 4px;
            --spacing-sm: 8px;
            --spacing-md: 16px;
            --spacing-lg: 24px;
            --spacing-xl: 32px;
            
            /* Radius */
            --radius-sm: 6px;
            --radius-md: 12px;
            --radius-lg: 16px;
            --radius-full: 9999px;
            
            /* Shadows - Deep ambient occlusion */
            --shadow-sm: 0 4px 12px rgba(0, 0, 0, 0.3);
            --shadow-md: 0 8px 24px rgba(0, 0, 0, 0.4);
            --shadow-lg: 0 20px 40px rgba(0, 0, 0, 0.6);
            
            /* Typography */
            --font-serif: 'Playfair Display', serif;
            --font-sans: 'Manrope', -apple-system, sans-serif;
            --font-mono: 'JetBrains Mono', monospace;
            --font-size-xs: 12px;
            --font-size-sm: 13px;
            --font-size-base: 14px;
            --font-size-lg: 16px;
            --font-size-xl: 18px;
            --font-size-2xl: 24px;
        }}
        
        /* Dark theme adjustments (always dark for Royal Obsidian) */
        @media (prefers-color-scheme: dark) {{
            :root {{
                --surface: #0B1015;
                --text-muted: #8C7B50;
                --border: #D4AF37;
            }}
        }}
        
        /* Body styling - minimal changes */
        body, .stApp {{
            background-color: var(--bg) !important;
            color: var(--text) !important;
        }}
        
        /* ============== Utility Classes (scoped, no layout changes) ============== */
        
        /* Card components */
        .bg-card {{
            background: var(--card-bg, var(--surface));
            border: 1px solid var(--border);
            border-radius: var(--radius-md);
            padding: var(--spacing-md);
            box-shadow: var(--shadow-sm);
        }}
        
        .card-title {{
            font-size: var(--font-size-lg);
            font-weight: 600;
            color: var(--text);
            margin-bottom: var(--spacing-sm);
        }}
        
        .card-body {{
            font-size: var(--font-size-base);
            color: var(--text);
            line-height: 1.6;
        }}
        
        /* Spacing utilities */
        .mt-sm {{ margin-top: var(--spacing-sm); }}
        .mt-md {{ margin-top: var(--spacing-md); }}
        .mt-lg {{ margin-top: var(--spacing-lg); }}
        
        .mb-sm {{ margin-bottom: var(--spacing-sm); }}
        .mb-md {{ margin-bottom: var(--spacing-md); }}
        .mb-lg {{ margin-bottom: var(--spacing-lg); }}
        
        .p-sm {{ padding: var(--spacing-sm); }}
        .p-md {{ padding: var(--spacing-md); }}
        .p-lg {{ padding: var(--spacing-lg); }}
        
        /* Text utilities */
        .text-muted {{ color: var(--text-muted); }}
        .text-center {{ text-align: center; }}
        .text-sm {{ font-size: var(--font-size-sm); }}
        .text-lg {{ font-size: var(--font-size-lg); }}
        .font-semibold {{ font-weight: 600; }}
        .font-bold {{ font-weight: 700; }}
        
        /* Divider */
        .divider {{
            height: 1px;
            background: var(--border);
            margin: var(--spacing-md) 0;
        }}
        
        /* Focus styles for accessibility (WCAG 2.2) */
        button:focus-visible,
        input:focus-visible,
        select:focus-visible,
        textarea:focus-visible {{
            outline: 2px solid var(--primary);
            outline-offset: 2px;
        }}
        
        /* Ensure sufficient contrast for links */
        a {{
            color: var(--primary);
            text-decoration: underline;
        }}
        
        a:hover {{
            color: var(--primary-hover, var(--primary));
        }}
    </style>
    """, unsafe_allow_html=True)

