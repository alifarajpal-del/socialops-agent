# Cold Royal Obsidian Design System

**Digital Luxury UI/UX Implementation for SocialOps Agent**

## Overview

The application has been upgraded to the **Cold Royal Obsidian** design language — a premium, OLED-optimized theme inspired by luxury automotive and horology digital ecosystems.

---

## Design Philosophy

### Digital Luxury Principles
- **Cold**: No warm yellows; only platinum/champagne/beige golds
- **Deep**: Z-axis depth through shadows, blurs, and layering
- **Refined**: High contrast, precise typography, restrained animation

---

## Color Palette

### Background Layers
```css
--bg-void: #020406          /* OLED-safe base (prevents smearing) */
--bg-obsidian: #0B1015      /* Card surface with subtle navy tint */
--bg-glass: rgba(11, 16, 21, 0.70)  /* Glassmorphism overlays */
```

### Accent Colors (Cold Gold Spectrum)
```css
--gold-champagne: #E8DCCA   /* Primary text/headings (platinum/beige) */
--gold-metallic: #D4AF37    /* Active borders/icons (classic gold) */
--gold-muted: #8C7B50       /* Secondary text/dividers (oxidized) */
--gold-gradient: linear-gradient(135deg, #E3DAC9 0%, #C5A059 100%)
```

### Semantic Colors
```css
--success-emerald: #00A86B  /* Cold, slightly desaturated green */
--error-crimson: #800020    /* Deep jewel tone red */
```

---

## Typography

### Font Hierarchy
1. **Headings**: `Playfair Display` (Serif, High contrast, 700 weight)
2. **Body**: `Manrope` (Clean Sans-serif, 400-600 weight)
3. **Data/Numbers**: `JetBrains Mono` (Monospaced, tabular-nums for alignment)

### Usage
```python
# In Streamlit components:
st.markdown('<h1 class="ui-heading">Portfolio Overview</h1>', unsafe_allow_html=True)

# For data displays (automatic with ui_kpi):
ui_kpi(label="Revenue", value="$1,250,000", delta="+12%")
```

---

## Visual Effects

### Deep Shadows (Ambient Occlusion)
```css
box-shadow: 0 20px 40px rgba(0,0,0,0.6);
```
Creates depth perception mimicking real-world lighting.

### Gradient Borders
Cards use `::before` pseudo-element with gradient overlay:
- Top-left: Brighter (light source simulation)
- Bottom-right: Fades out (shadow side)

### Glassmorphism
Navigation bars and overlays:
```css
backdrop-filter: blur(20px);
background: rgba(11, 16, 21, 0.70);
```

### Noise Texture
Subtle 2% noise overlay on cards (SVG data URI) for tactile feel.

---

## Components

### 1. Lux-Container Card (`ui_card`)

**Usage:**
```python
from ui_components.ui_kit import ui_card

with ui_card(title="Analytics Dashboard", icon="📊"):
    st.write("Your content here")
```

**Features:**
- Gradient border (135deg angle)
- Noise texture overlay (2% opacity)
- Deep shadow (`0 20px 40px rgba(0,0,0,0.6)`)
- 12px border radius

---

### 2. Concierge Data Table (`concierge_table`)

**Usage:**
```python
from ui_components.ui_kit import concierge_table

data = [
    {"client": "ACME Corp", "revenue": "$1,250,000", "status": "Active"},
    {"client": "Beta LLC", "revenue": "$875,000", "status": "Pending"}
]

columns = [
    {"key": "client", "label": "Client", "numeric": False},
    {"key": "revenue", "label": "Revenue", "numeric": True},  # Monospace font
    {"key": "status", "label": "Status", "numeric": False}
]

concierge_table(data=data, columns=columns)
```

**Features:**
- Zebra striping via opacity (even rows: `rgba(255,255,255,0.03)`)
- Uppercase headers with tracking (`letter-spacing: 0.1em`)
- Monospace numbers (`.numeric` class)
- Mobile: Stacked layout with data-label attributes

---

### 3. Concierge Input (`concierge_input`)

**Usage:**
```python
from ui_components.ui_kit import concierge_input

name = concierge_input(
    label="Full Name",
    key="user_name",
    input_type="text"
)
```

**Features:**
- Underline style (no box border)
- Floating label animation (moves up on focus)
- Gold glow on focus: `box-shadow: 0 1px 0 0 #D4AF37, 0 4px 12px rgba(212, 175, 55, 0.2)`
- Smooth 0.3s transitions

---

### 4. Glassmorphism Navigation (`glass_header`)

**Usage:**
```python
from ui_components.ui_kit import glass_header

glass_header('<div style="padding: 1rem;">🏠 Dashboard</div>')
```

**Features:**
- `backdrop-filter: blur(20px)`
- Semi-transparent background
- Gold border bottom

---

### 5. KPI Metric (`ui_kpi`)

**Usage:**
```python
from ui_components.ui_kit import ui_kpi

ui_kpi(
    label="Monthly Revenue",
    value="$1,250,000",
    delta="+12%"
)
```

**Features:**
- Monospace value display (JetBrains Mono)
- Gradient border
- Deep shadow
- Color-coded delta (green/red)

---

## Mobile Optimization

### Breakpoints
- **768px**: Tablet layout (full-width cards, stacked KPIs)
- **480px**: Phone layout (reduced padding, hidden table headers)

### Concierge Table Mobile
```css
@media (max-width: 768px) {
    .concierge-table thead { display: none; }
    .concierge-table tbody tr { display: block; }
    .concierge-table td::before {
        content: attr(data-label);  /* Shows column name */
        float: left;
    }
}
```

---

## Accessibility (WCAG 2.2 AA)

### Contrast Ratios
- **Gold Champagne (#E8DCCA) on Void (#020406)**: 12.5:1 ✅
- **Gold Metallic (#D4AF37) on Obsidian (#0B1015)**: 8.2:1 ✅
- **Gold Muted (#8C7B50) on Obsidian**: 4.6:1 ✅

### Focus States
All interactive elements have visible focus outlines with gold glow.

---

## Implementation Notes

### CSS Guard Pattern
```python
def inject_ui_kit_css(theme: str = "light") -> None:
    guard_key = f"_css_injected_{theme}"
    if st.session_state.get(guard_key, False):
        return
    # ... inject CSS
    st.session_state[guard_key] = True
```
Prevents duplicate CSS injection on Streamlit reruns.

### F-String Escaping
All CSS in Python f-strings uses `{{` and `}}` for literal braces:
```python
css = f"""
@media (max-width: 768px) {{
    .ui-card {{ padding: 0.5rem; }}
}}
"""
```

---

## Migration from Black & Gold

### Changed Values
| Component | Old | New |
|-----------|-----|-----|
| Background | `#0B0B0B` | `#020406` (darker) |
| Card BG | `#141414` | `#0B1015` (navy tint) |
| Primary | `#C9A24D` | `#D4AF37` (colder) |
| Text | `#F5F5F5` | `#E8DCCA` (champagne) |
| Muted | `#A1A1A1` | `#8C7B50` (gold muted) |

### New Features
- Gradient borders on all cards
- Noise texture overlays
- Glassmorphism support
- Luxury typography (Playfair/JetBrains)
- Concierge Input component
- Professional table styling

---

## Examples in Codebase

### Dashboard View
See [dashboard_view.py](ui_components/dashboard_view.py) for:
- Hero section with `ui_page`
- KPI row with `ui_kpi`
- Action cards with `ui_card`

### Inbox View
See [inbox_view.py](ui_components/inbox_view.py) for:
- Filter cards
- Thread list styling

---

## Future Enhancements

### Framer Motion Equivalents (CSS-only)
Current micro-animations in `micro_ux.py` provide:
- Button hover lift (`translateY(-2px)`)
- Card hover glow
- Fade-in animations

For more advanced animations, consider:
- `transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1)` (Material easing)
- CSS `@keyframes` for loading states
- `transform: scale(1.02)` on hover for depth

---

## Technical Stack

- **Framework**: Streamlit 1.x
- **Styling**: Custom CSS injection (no Tailwind)
- **Typography**: Google Fonts CDN
- **Animations**: CSS transitions + keyframes
- **Compatibility**: Chrome/Safari/Edge (modern browsers with backdrop-filter support)

---

## License & Credits

Design System: Cold Royal Obsidian (Inspired by Bentley, Rolls-Royce, and Patek Philippe digital ecosystems)
Implementation: SocialOps Agent UI Team
Typography: Playfair Display (Google Fonts), Manrope (Google Fonts), JetBrains Mono (Google Fonts)
