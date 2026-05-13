"""
theme.py  ─  Design system tokens (blueprint §6.6 / §6.7)
"""

COLORS = {
    "background":     "#0d1117",
    "surface":        "#161b22",
    "card":           "#1c2128",
    "border":         "#30363d",
    "primary":        "#58a6ff",
    "success":        "#3fb950",
    "warning":        "#d29922",
    "danger":         "#f85149",
    "info":           "#58a6ff",
    "text_primary":   "#e6edf3",
    "text_secondary": "#8b949e",
    "accent":         "#bc8cff",
    "chart_1":        "#58a6ff",
    "chart_2":        "#3fb950",
    "chart_3":        "#d29922",
    "chart_4":        "#f85149",
    "chart_5":        "#bc8cff",
    "chart_6":        "#39d353",
}

STATUS_COLOR = {
    "success": COLORS["success"],
    "warning": COLORS["warning"],
    "danger":  COLORS["danger"],
    "info":    COLORS["info"],
}

CHART_COLORS = [
    COLORS["chart_1"], COLORS["chart_2"], COLORS["chart_3"],
    COLORS["chart_4"], COLORS["chart_5"], COLORS["chart_6"],
]


def base_layout(title: str = "", height: int = 320) -> dict:
    """Shared Plotly layout matching dark theme."""
    return dict(
        title=dict(text=title, font=dict(size=13, color=COLORS["text_secondary"],
                                         family="Inter, sans-serif")),
        paper_bgcolor=COLORS["card"],
        plot_bgcolor=COLORS["card"],
        font=dict(color=COLORS["text_primary"], family="Inter, sans-serif", size=11),
        height=height,
        margin=dict(l=40, r=20, t=36, b=36),
        xaxis=dict(gridcolor=COLORS["border"], zerolinecolor=COLORS["border"],
                   linecolor=COLORS["border"]),
        yaxis=dict(gridcolor=COLORS["border"], zerolinecolor=COLORS["border"],
                   linecolor=COLORS["border"]),
        legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor=COLORS["border"],
                    font=dict(size=10)),
        hoverlabel=dict(bgcolor=COLORS["surface"], bordercolor=COLORS["border"],
                        font=dict(color=COLORS["text_primary"])),
    )


# ── CSS injected into dash app ────────────────────────────────────────────────
CUSTOM_CSS = f"""
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

body {{
    background: {COLORS['background']};
    color: {COLORS['text_primary']};
    font-family: 'Inter', sans-serif;
    font-size: 0.875rem;
    overflow-x: hidden;
}}

/* ── Scrollbar ── */
::-webkit-scrollbar {{ width: 6px; height: 6px; }}
::-webkit-scrollbar-track {{ background: {COLORS['background']}; }}
::-webkit-scrollbar-thumb {{ background: {COLORS['border']}; border-radius: 3px; }}

/* ── Top Nav ── */
#top-nav {{
    display: flex; align-items: center; gap: 12px;
    background: {COLORS['surface']};
    border-bottom: 1px solid {COLORS['border']};
    padding: 0 20px; height: 56px; position: sticky; top: 0; z-index: 1000;
}}

#top-nav .brand {{
    font-size: 1rem; font-weight: 700; color: {COLORS['primary']};
    letter-spacing: -0.3px; white-space: nowrap;
}}

#top-nav .brand span {{ color: {COLORS['text_secondary']}; font-weight: 400; }}

.nav-sep {{ flex: 1; }}

.horizon-btn {{
    background: none; border: 1px solid {COLORS['border']};
    color: {COLORS['text_secondary']}; padding: 4px 12px;
    border-radius: 6px; cursor: pointer; font-size: 0.8rem;
    font-family: 'Inter', sans-serif; transition: all 0.2s;
}}
.horizon-btn:hover, .horizon-btn.active {{
    background: {COLORS['primary']}22;
    border-color: {COLORS['primary']}; color: {COLORS['primary']};
}}

.nav-badge {{
    background: {COLORS['danger']}33; color: {COLORS['danger']};
    padding: 2px 8px; border-radius: 20px; font-size: 0.72rem; font-weight: 600;
}}
.nav-user {{ color: {COLORS['text_secondary']}; font-size: 0.82rem; }}

/* ── Layout ── */
#app-layout {{ display: flex; height: calc(100vh - 56px); overflow: hidden; }}

/* ── Sidebar ── */
#sidebar {{
    width: 220px; min-width: 220px;
    background: {COLORS['surface']};
    border-right: 1px solid {COLORS['border']};
    overflow-y: auto; padding: 12px 0;
    transition: width 0.2s;
}}

.sidebar-section {{
    padding: 6px 16px 2px;
    font-size: 0.7rem; font-weight: 600; letter-spacing: 0.08em;
    color: {COLORS['text_secondary']}; text-transform: uppercase;
}}

.nav-item {{
    display: flex; align-items: center; gap: 10px;
    padding: 8px 16px; cursor: pointer; border-radius: 0;
    color: {COLORS['text_secondary']}; font-size: 0.83rem;
    transition: all 0.15s; border-left: 3px solid transparent;
    text-decoration: none;
}}
.nav-item:hover {{
    background: {COLORS['card']}; color: {COLORS['text_primary']};
}}
.nav-item.active {{
    background: {COLORS['primary']}15;
    color: {COLORS['primary']}; border-left-color: {COLORS['primary']};
    font-weight: 500;
}}
.nav-icon {{ font-size: 1rem; width: 18px; text-align: center; }}

/* ── Main content ── */
#main-content {{ flex: 1; overflow-y: auto; padding: 20px; }}

/* ── Cards ── */
.card {{
    background: {COLORS['card']};
    border: 1px solid {COLORS['border']};
    border-radius: 10px; padding: 16px;
    transition: border-color 0.2s;
}}
.card:hover {{ border-color: {COLORS['primary']}44; }}

/* ── KPI Cards ── */
.kpi-card {{
    background: {COLORS['card']};
    border: 1px solid {COLORS['border']};
    border-radius: 10px; padding: 14px 16px;
    position: relative; overflow: hidden;
    transition: transform 0.2s, border-color 0.2s;
}}
.kpi-card:hover {{ transform: translateY(-2px); border-color: {COLORS['primary']}55; }}

.kpi-label {{
    font-size: 0.68rem; font-weight: 600; text-transform: uppercase;
    letter-spacing: 0.06em; color: {COLORS['text_secondary']}; margin-bottom: 4px;
}}
.kpi-value {{
    font-size: 2rem; font-weight: 700; line-height: 1;
    font-family: 'JetBrains Mono', monospace;
    color: {COLORS['text_primary']}; margin-bottom: 2px;
}}
.kpi-unit {{ font-size: 0.8rem; color: {COLORS['text_secondary']}; margin-left: 4px; }}
.kpi-target {{ font-size: 0.72rem; color: {COLORS['text_secondary']}; }}
.kpi-delta {{ font-size: 0.78rem; font-weight: 600; }}
.kpi-delta.pos {{ color: {COLORS['success']}; }}
.kpi-delta.neg {{ color: {COLORS['danger']}; }}
.kpi-delta.neu {{ color: {COLORS['text_secondary']}; }}

.status-dot {{
    width: 8px; height: 8px; border-radius: 50%;
    display: inline-block; margin-right: 4px;
    animation: pulse 2s infinite;
}}
.status-dot.success {{ background: {COLORS['success']}; }}
.status-dot.warning {{ background: {COLORS['warning']}; }}
.status-dot.danger  {{ background: {COLORS['danger']}; }}

@keyframes pulse {{
    0%, 100% {{ opacity: 1; }}
    50% {{ opacity: 0.5; }}
}}

/* ── AI Brief ── */
.ai-brief {{
    background: linear-gradient(135deg, {COLORS['primary']}11, {COLORS['accent']}11);
    border: 1px solid {COLORS['primary']}33;
    border-radius: 10px; padding: 14px 16px;
}}
.ai-badge {{
    display: inline-block;
    background: {COLORS['accent']}22; color: {COLORS['accent']};
    padding: 2px 8px; border-radius: 4px;
    font-size: 0.68rem; font-weight: 600; letter-spacing: 0.05em;
    margin-bottom: 8px;
}}
.ai-brief p {{ color: {COLORS['text_secondary']}; line-height: 1.55; font-size: 0.82rem; }}

/* ── Section headers ── */
.section-header {{
    font-size: 0.78rem; font-weight: 600; text-transform: uppercase;
    letter-spacing: 0.06em; color: {COLORS['text_secondary']};
    margin-bottom: 12px; padding-bottom: 8px;
    border-bottom: 1px solid {COLORS['border']};
}}

/* ── Action Queue ── */
.action-item {{
    display: flex; align-items: flex-start; gap: 12px;
    padding: 10px 0; border-bottom: 1px solid {COLORS['border']};
}}
.action-item:last-child {{ border-bottom: none; }}
.priority-badge {{
    padding: 2px 7px; border-radius: 4px;
    font-size: 0.68rem; font-weight: 700; letter-spacing: 0.04em;
    white-space: nowrap;
}}
.priority-badge.CRITICAL {{
    background: {COLORS['danger']}22; color: {COLORS['danger']};
    border: 1px solid {COLORS['danger']}44;
}}
.priority-badge.HIGH {{
    background: {COLORS['warning']}22; color: {COLORS['warning']};
    border: 1px solid {COLORS['warning']}44;
}}
.priority-badge.MEDIUM {{
    background: {COLORS['info']}22; color: {COLORS['info']};
    border: 1px solid {COLORS['info']}44;
}}
.action-text {{ font-size: 0.82rem; color: {COLORS['text_primary']}; }}
.action-sub  {{ font-size: 0.74rem; color: {COLORS['text_secondary']}; margin-top: 2px; }}

/* ── Gauge container ── */
.gauge-row {{ display: flex; gap: 12px; flex-wrap: wrap; }}
.gauge-item {{
    flex: 1; min-width: 160px;
    background: {COLORS['card']};
    border: 1px solid {COLORS['border']};
    border-radius: 10px; padding: 12px; text-align: center;
}}

/* ── Tables ── */
.dash-table-container .dash-spreadsheet-container .dash-spreadsheet-inner th {{
    background: {COLORS['surface']} !important;
    color: {COLORS['text_secondary']} !important;
    font-size: 0.72rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
    border-color: {COLORS['border']} !important;
}}
.dash-table-container .dash-spreadsheet-container .dash-spreadsheet-inner td {{
    background: {COLORS['card']} !important;
    color: {COLORS['text_primary']} !important;
    font-size: 0.82rem !important;
    border-color: {COLORS['border']} !important;
}}

/* ── Page title ── */
.page-title {{
    font-size: 1.15rem; font-weight: 700;
    color: {COLORS['text_primary']}; margin-bottom: 16px;
    display: flex; align-items: center; gap: 8px;
}}
.page-title .icon {{ font-size: 1.3rem; }}

/* ── Scenario comparison table ── */
.scenario-table {{ width: 100%; border-collapse: collapse; }}
.scenario-table th {{
    text-align: left; padding: 8px 12px;
    font-size: 0.7rem; text-transform: uppercase;
    letter-spacing: 0.05em; color: {COLORS['text_secondary']};
    border-bottom: 1px solid {COLORS['border']};
}}
.scenario-table td {{
    padding: 8px 12px; font-size: 0.82rem;
    border-bottom: 1px solid {COLORS['border']}55;
}}
.scenario-table tr.active-row td {{
    background: {COLORS['primary']}11; color: {COLORS['primary']};
}}
.val-pos {{ color: {COLORS['danger']}; }}
.val-neg {{ color: {COLORS['success']}; }}

/* ── Slider ── */
.rc-slider-track {{ background: {COLORS['primary']} !important; }}
.rc-slider-handle {{ border-color: {COLORS['primary']} !important; }}

/* ── Right panel / Copilot ── */
#copilot-panel {{
    width: 280px; min-width: 280px;
    background: {COLORS['surface']};
    border-left: 1px solid {COLORS['border']};
    overflow-y: auto; padding: 16px;
}}
.copilot-title {{
    font-size: 0.78rem; font-weight: 600; text-transform: uppercase;
    letter-spacing: 0.06em; color: {COLORS['accent']};
    margin-bottom: 12px; display: flex; align-items: center; gap: 6px;
}}
.copilot-msg {{
    background: {COLORS['card']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px; padding: 10px 12px;
    font-size: 0.8rem; color: {COLORS['text_secondary']};
    line-height: 1.5; margin-bottom: 10px;
}}
.copilot-query {{
    width: 100%;
    background: {COLORS['card']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px; padding: 8px 10px;
    color: {COLORS['text_primary']}; font-size: 0.82rem;
    font-family: 'Inter', sans-serif;
    resize: none; outline: none;
    transition: border-color 0.2s;
}}
.copilot-query:focus {{ border-color: {COLORS['accent']}; }}

/* ── Responsive grid ── */
.grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }}
.grid-3 {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 14px; }}
.grid-4 {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; }}
.grid-kpi {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(170px, 1fr)); gap: 12px; margin-bottom: 16px; }}

@media (max-width: 1200px) {{
    .grid-4 {{ grid-template-columns: repeat(2, 1fr); }}
    #copilot-panel {{ display: none; }}
}}
@media (max-width: 900px) {{
    .grid-3, .grid-2 {{ grid-template-columns: 1fr; }}
    #sidebar {{ width: 48px; }}
    .nav-item span {{ display: none; }}
}}
"""
