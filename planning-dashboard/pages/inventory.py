"""pages/inventory.py — Dashboard 4: Inventory Optimization"""
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import dcc, html, Input, Output, callback, register_page

from config import COLORS, LEGEND_STYLE, apply_dark_layout, hex_to_rgba
from data.mock_data import inventory_geo, service_vs_inventory, safety_stock_sim

register_page(__name__, path="/inventory", name="Inventory Optimization")

_geo = inventory_geo()
_svi = service_vs_inventory()
_SC = {"success": COLORS["success"], "warning": COLORS["warning"], "danger": COLORS["danger"]}

_geo_fig = go.Figure(go.Scattergeo(
    lat=_geo["lat"], lon=_geo["lon"], text=_geo["location"], mode="markers+text",
    textposition="top center",
    marker=dict(size=_geo["stock_value"]*8, color=[_SC[s] for s in _geo["status"]],
                opacity=0.85, line=dict(color=COLORS["border"], width=1)),
    customdata=list(zip(_geo["dos"], _geo["stock_value"])),
    hovertemplate="<b>%{text}</b><br>DOS: %{customdata[0]:.0f}d<br>Value: $%{customdata[1]:.1f}M<extra></extra>",
))
_geo_fig.update_layout(
    paper_bgcolor=COLORS["card"],
    font=dict(color=COLORS["text_primary"], family="Inter, sans-serif"),
    title=dict(text="Inventory Levels by Location", font=dict(color=COLORS["text_primary"], size=13)),
    height=320, margin=dict(l=0, r=0, t=40, b=0),
    geo=dict(showland=True, landcolor=COLORS["surface"], showocean=True, oceancolor=COLORS["background"],
             showcountries=True, countrycolor=COLORS["border"], showframe=False,
             bgcolor=COLORS["background"], projection_type="natural earth"),
)

_abc_color = {"A": COLORS["danger"], "B": COLORS["warning"], "C": COLORS["success"]}
_svi_fig = go.Figure()
for abc, color in _abc_color.items():
    mask = _svi["abc"] == abc
    _svi_fig.add_trace(go.Scatter(
        x=_svi.loc[mask, "inv_value"], y=_svi.loc[mask, "service_lvl"],
        mode="markers", name=f"Class {abc}",
        marker=dict(color=color, size=8, opacity=0.8, line=dict(color=COLORS["border"], width=0.5)),
        hovertemplate="SKU: %{text}<br>Inv $M: %{x}<br>Service: %{y}%<extra></extra>",
        text=_svi.loc[mask, "sku"],
    ))
_svi_fig.add_hrect(y0=95, y1=100, fillcolor=hex_to_rgba(COLORS["success"], 0.09), line_width=0,
                    annotation_text="Target ≥95%", annotation_font=dict(color=COLORS["success"], size=9))
apply_dark_layout(_svi_fig, title="Service Level vs Inventory Investment", height=310,
                  xaxis=dict(title="Inventory Value ($M)", gridcolor=COLORS["border"]),
                  yaxis=dict(title="Service Level (%)", gridcolor=COLORS["border"]),
                  legend=dict(**LEGEND_STYLE, orientation="h", y=1.08))

def _ss_metric(label, value):
    return dbc.Col(html.Div([
        html.Div(label, style={"fontSize": "0.72rem", "color": COLORS["text_secondary"],
                               "fontWeight": "600", "letterSpacing": "0.06em"}),
        html.Div(value, style={"fontSize": "1.5rem", "fontWeight": "700", "color": COLORS["text_primary"]}),
    ], style={"backgroundColor": COLORS["surface"], "borderRadius": "8px",
               "padding": "12px 16px", "border": f"1px solid {COLORS['border']}"}),
    xs=12, sm=4, className="mb-2")

def _ss_display(service_level):
    res = safety_stock_sim(service_level)
    return dbc.Row([_ss_metric("Safety Stock", f"{res['safety_stock_units']:,} units"),
                    _ss_metric("Working Capital", f"${res['working_capital_usd']:,}"),
                    _ss_metric("Stockout Prob", f"{res['stockout_prob']:.1%}")])

layout = html.Div([
    html.H5("Inventory Optimization", style={"color": COLORS["text_primary"], "fontWeight": "700", "marginBottom": "4px"}),
    html.Div("Geographic inventory • Service-inventory scatter • Safety stock simulator",
             style={"color": COLORS["text_secondary"], "fontSize": "0.83rem", "marginBottom": "20px"}),
    dbc.Row([
        dbc.Col(dcc.Graph(figure=_geo_fig, config={"displayModeBar": False}), md=6, className="mb-3"),
        dbc.Col(dcc.Graph(figure=_svi_fig, config={"displayModeBar": False}), md=6, className="mb-3"),
    ]),
    dbc.Card([
        dbc.CardHeader(html.Span("SAFETY STOCK SIMULATOR",
            style={"fontSize": "0.75rem", "fontWeight": "700", "letterSpacing": "0.08em",
                   "color": COLORS["text_secondary"]}),
            style={"backgroundColor": COLORS["surface"], "borderBottom": f"1px solid {COLORS['border']}"}),
        dbc.CardBody([
            html.Div([
                html.Span("Target Service Level: ", style={"color": COLORS["text_secondary"], "fontSize": "0.83rem"}),
                html.Span(id="ss-level-display", style={"color": COLORS["primary"], "fontWeight": "700"}),
            ], style={"marginBottom": "12px"}),
            dcc.Slider(id="ss-slider", min=0.85, max=0.99, step=0.01, value=0.95,
                       marks={v: f"{int(v*100)}%" for v in [0.85, 0.90, 0.95, 0.98, 0.99]}),
            html.Div(id="ss-output", style={"marginTop": "20px"}),
        ], style={"backgroundColor": COLORS["card"]}),
    ], style={"border": f"1px solid {COLORS['border']}", "borderRadius": "10px"}),
])

@callback(Output("ss-output", "children"), Output("ss-level-display", "children"),
          Input("ss-slider", "value"))
def update_ss(service_level):
    return _ss_display(service_level), f"{service_level:.0%}"
