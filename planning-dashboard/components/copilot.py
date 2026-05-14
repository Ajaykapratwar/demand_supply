"""components/copilot.py — Collapsible AI Copilot right panel (blueprint §3.7)"""
import dash_bootstrap_components as dbc
from dash import dcc, html
from config import COLORS


_CANNED_RESPONSES = {
    "stockout": {
        "text": "⚠️ **Critical:** SKU-047 at DC-APAC has 12 DOS — 3.2× below safety stock target. "
                "Expediting PO-4821 (5,000 units) will resolve within 8 days. "
                "Estimated stockout cost if unresolved: **$280K**. [AI Generated]",
        "badge_color": COLORS["danger"],
    },
    "forecast": {
        "text": "📈 **Forecast Accuracy:** Portfolio WAPE improved 1.8pp MoM to 14.1%. "
                "Planner overrides on SKU-112 category degraded WAPE by 3.2pp — recommend reverting. "
                "FVA positive for 82% of SKUs this month. [AI Generated]",
        "badge_color": COLORS["success"],
    },
    "scenario": {
        "text": "🔀 **Demand Surge Scenario (+20%):** Running simulation... "
                "Estimated cost impact: **+$6.9M**. Service level drops to 91.3%. "
                "Recommend pre-positioning 8,500 units in DC-APAC and DC-US. [AI Generated]",
        "badge_color": COLORS["warning"],
    },
    "default": {
        "text": "I'm your AI Supply Chain Copilot. Ask me about stockouts, forecast accuracy, "
                "scenario impacts, or risk factors. [AI Generated]",
        "badge_color": COLORS["primary"],
    },
}


def _response_card(resp: dict) -> dbc.Card:
    return dbc.Card(
        dbc.CardBody([
            html.Span("🤖 AI Generated",
                      style={"fontSize": "0.65rem", "color": resp["badge_color"],
                             "fontWeight": "700", "letterSpacing": "0.06em",
                             "border": f"1px solid {resp['badge_color']}",
                             "borderRadius": "4px", "padding": "1px 6px", "display": "inline-block",
                             "marginBottom": "8px"}),
            dcc.Markdown(resp["text"], style={"color": COLORS["text_primary"], "fontSize": "0.83rem"}),
        ], style={"padding": "10px"}),
        style={"backgroundColor": COLORS["surface"], "border": f"1px solid {COLORS['border']}",
               "borderRadius": "8px", "marginBottom": "8px"},
    )


def narrative_card(text: str, dashboard_id: str = "") -> html.Div:
    """§14.1 Component 1 — AI narrative insight card shown at top of each dashboard."""
    return html.Div([
        html.Div([
            html.Span("✨", style={"fontSize": "0.9rem", "marginRight": "6px",
                                    "color": COLORS["accent"]}),
            html.Span("AI NARRATIVE", style={
                "fontSize": "0.65rem", "fontWeight": "700",
                "color": COLORS["accent"], "letterSpacing": "0.08em",
            }),
        ], style={"marginBottom": "6px"}),
        dcc.Markdown(text, style={"color": COLORS["text_primary"], "fontSize": "0.84rem",
                                   "margin": "0"}),
    ], style={
        "backgroundColor": f"{COLORS['accent']}12",
        "border": f"1px solid {COLORS['accent']}44",
        "borderLeft": f"3px solid {COLORS['accent']}",
        "borderRadius": "8px",
        "padding": "12px 16px",
        "marginBottom": "16px",
    })


def ai_recommendation_card(action: str, impact: str, confidence: float = 0.0) -> html.Div:
    """§14.1 Component 10 — Prescriptive action card with expected impact and confidence."""
    conf_color = COLORS["success"] if confidence >= 0.75 else (
        COLORS["warning"] if confidence >= 0.5 else COLORS["danger"]
    )
    return html.Div([
        html.Div([
            html.Span("⚡ Recommended Action", style={
                "fontSize": "0.65rem", "fontWeight": "700",
                "color": COLORS["primary"], "letterSpacing": "0.06em",
            }),
            html.Span(f"{confidence:.0%} confidence", style={
                "fontSize": "0.62rem", "color": conf_color,
                "border": f"1px solid {conf_color}", "borderRadius": "3px",
                "padding": "0 5px", "marginLeft": "8px",
            }),
        ], style={"marginBottom": "6px"}),
        html.Div(action, style={"color": COLORS["text_primary"],
                                "fontSize": "0.84rem", "marginBottom": "4px"}),
        html.Div(f"Expected impact: {impact}",
                 style={"color": COLORS["text_secondary"], "fontSize": "0.78rem"}),
    ], style={
        "backgroundColor": f"{COLORS['primary']}10",
        "border": f"1px solid {COLORS['border']}",
        "borderLeft": f"3px solid {COLORS['primary']}",
        "borderRadius": "8px",
        "padding": "10px 14px",
        "marginBottom": "8px",
    })


def build_copilot_panel():
    return html.Div([
        # Header
        html.Div([
            html.Span("🤖", style={"fontSize": "1rem", "marginRight": "6px"}),
            html.Span("AI Copilot", style={
                "fontWeight": "700", "fontSize": "0.9rem", "color": COLORS["text_primary"],
            }),
            html.Span(" Beta", style={
                "fontSize": "0.62rem", "color": COLORS["accent"],
                "border": f"1px solid {COLORS['accent']}", "borderRadius": "4px",
                "padding": "1px 5px", "marginLeft": "8px",
            }),
        ], style={"display": "flex", "alignItems": "center", "padding": "12px 14px",
                   "borderBottom": f"1px solid {COLORS['border']}"}),

        # Narrative brief (always shown)
        html.Div([
            html.Div("EXECUTIVE BRIEF", style={
                "fontSize": "0.65rem", "fontWeight": "700", "color": COLORS["text_secondary"],
                "letterSpacing": "0.08em", "marginBottom": "6px",
            }),
            dcc.Markdown(
                "**Critical:** Stockout risk on 4 A-class SKUs in APAC. "
                "**Opportunity:** Shift 3,000 units to DC-US to improve OTIF +1.2pp. "
                "**Risk:** Supplier A lead time extended 15d — $2.1M expediting exposure. [AI Generated]",
                style={"color": COLORS["text_primary"], "fontSize": "0.82rem"},
            ),
        ], style={"padding": "12px 14px", "borderBottom": f"1px solid {COLORS['border']}",
                   "backgroundColor": f"{COLORS['primary']}11"}),

        # Query input
        html.Div([
            dbc.Input(
                id="copilot-input",
                placeholder="Ask about stockouts, scenarios, forecasts…",
                type="text",
                style={
                    "backgroundColor": COLORS["surface"],
                    "border": f"1px solid {COLORS['border']}",
                    "color": COLORS["text_primary"],
                    "fontSize": "0.82rem",
                    "borderRadius": "6px",
                },
            ),
            dbc.Button("Ask", id="copilot-ask-btn", color="primary", size="sm",
                       style={"marginTop": "8px", "width": "100%", "fontWeight": "600"}),
        ], style={"padding": "12px 14px", "borderBottom": f"1px solid {COLORS['border']}"}),

        # Response area
        html.Div(id="copilot-response-area",
                 children=[_response_card(_CANNED_RESPONSES["default"])],
                 style={"padding": "12px 14px", "overflowY": "auto", "flex": "1"}),

        # Quick prompts
        html.Div([
            html.Div("QUICK PROMPTS", style={
                "fontSize": "0.65rem", "color": COLORS["text_secondary"],
                "letterSpacing": "0.08em", "marginBottom": "6px", "fontWeight": "700",
            }),
            html.Div([
                dbc.Button(label, id=f"quick-{key}", size="sm", outline=True, color="secondary",
                           style={"marginBottom": "4px", "marginRight": "4px",
                                  "fontSize": "0.72rem", "borderColor": COLORS["border"]})
                for label, key in [
                    ("Stockout risk", "stockout"),
                    ("Forecast accuracy", "forecast"),
                    ("Run demand surge +20%", "scenario"),
                ]
            ]),
        ], style={"padding": "10px 14px", "borderTop": f"1px solid {COLORS['border']}"}),

    ], style={
        "backgroundColor": "var(--surface)",
        "borderLeft": "1px solid var(--border)",
        "width": "380px",
        "flexShrink": "0",
        "display": "flex",
        "flexDirection": "column",
        "height": "100vh",
        "overflowY": "hidden",
    }, id="copilot-panel")
