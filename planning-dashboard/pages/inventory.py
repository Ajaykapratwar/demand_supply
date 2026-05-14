"""pages/inventory.py — Dashboard 4: Inventory Optimization"""
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import dcc, html, Input, Output, callback, register_page

from config import COLORS, LEGEND_STYLE, apply_dark_layout, hex_to_rgba
from data.data_loader import get_inventory_geo, get_service_vs_inventory, get_safety_stock_sim

register_page(__name__, path="/inventory", name="Inventory Optimization")

_SC = {"success": COLORS["success"], "warning": COLORS["warning"], "danger": COLORS["danger"]}
_abc_color = {"A": COLORS["danger"], "B": COLORS["warning"], "C": COLORS["success"]}

def _ss_metric(label, value):
    return html.Div([
        html.Div(label, style={"fontSize": "0.72rem", "color": "var(--text-2)",
                               "fontWeight": "600", "letterSpacing": "0.06em"}),
        html.Div(value, style={"fontSize": "1.5rem", "fontWeight": "700", "color": "var(--text-1)"}),
    ], className="col-span-4 chart-card", style={"padding": "12px 16px"})

layout = html.Div([
    html.Div([
        html.Div([
            html.H5("Inventory Optimization", style={
                "color": COLORS["text_primary"], "fontWeight": "700",
                "fontSize": "1.1rem", "margin": "0", "letterSpacing": "-0.01em",
            }),
            html.Div("Geographic inventory · Service-inventory scatter · Safety stock simulator",
                     style={"color": COLORS["text_secondary"], "fontSize": "0.8rem", "marginTop": "2px"}),
        ]),
    ], style={"display": "flex", "justifyContent": "space-between",
              "alignItems": "center", "marginBottom": "20px"}),
    html.Div([
        html.Div(dcc.Loading(dcc.Graph(id="inventory-geo-chart", config={"displayModeBar": False}), type="dot"), className="col-span-6 chart-card"),
        html.Div(dcc.Loading(dcc.Graph(id="inventory-svi-chart", config={"displayModeBar": False}), type="dot"), className="col-span-6 chart-card"),
    ], className="dashboard-grid mb-4"),
    html.Div([
        html.Div([
            html.Span("Safety Stock Simulator", style={
                "fontSize": "0.78rem", "fontWeight": "700",
                "color": COLORS["text_secondary"], "letterSpacing": "0.06em",
                "textTransform": "uppercase",
            }),
        ], style={"padding": "14px 16px", "borderBottom": f"1px solid {COLORS['border']}"}),
        html.Div([
            html.Div([
                html.Span("Target Service Level: ", style={"color": COLORS["text_secondary"], "fontSize": "0.83rem"}),
                html.Span(id="ss-level-display", style={"color": COLORS["primary"], "fontWeight": "700"}),
            ], style={"marginBottom": "14px"}),
            dcc.Slider(id="ss-slider", min=0.85, max=0.99, step=0.01, value=0.95,
                       marks={v: f"{int(v*100)}%" for v in [0.85, 0.90, 0.95, 0.98, 0.99]}),
            dcc.Loading(html.Div(id="ss-output", style={"marginTop": "20px"}), type="dot"),
        ], style={"padding": "16px", "backgroundColor": COLORS["card"]}),
    ], className="chart-card"),
], className="page-wrapper")

@callback(
    Output("inventory-geo-chart", "figure"),
    Output("inventory-svi-chart", "figure"),
    Output("ss-output", "children"),
    Output("ss-level-display", "children"),
    Input("global-filter-store", "data"),
    Input("ss-slider", "value")
)
def update_inventory(filter_data, service_level):
    filter_data = filter_data or {}
    region = filter_data.get("region", "Global")
    category = filter_data.get("category", "All")
    
    # 1. Geographic Inventory
    _geo = get_inventory_geo(region, category)
    if not _geo.empty:
        _geo_fig = go.Figure(go.Scattergeo(
            lat=_geo["lat"], lon=_geo["lon"], text=_geo["location"], mode="markers+text",
            textposition="top center",
            marker=dict(size=_geo["stock_value"]*8, color=[_SC.get(s, COLORS["primary"]) for s in _geo["status"]],
                        opacity=0.85, line=dict(color=COLORS["border"], width=1)),
            customdata=list(zip(_geo["dos"], _geo["stock_value"])),
            hovertemplate="<b>%{text}</b><br>DOS: %{customdata[0]:.0f}d<br>Value Proxy: %{customdata[1]:.1f}M<extra></extra>",
        ))
    else:
        _geo_fig = go.Figure()
        
    _geo_fig.update_layout(
        paper_bgcolor=COLORS["card"],
        font=dict(color=COLORS["text_primary"], family="Inter, sans-serif"),
        title=dict(text=f"Inventory Levels ({region} | {category})", font=dict(color=COLORS["text_primary"], size=13)),
        height=320, margin=dict(l=0, r=0, t=40, b=0),
        geo=dict(showland=True, landcolor=COLORS["surface"], showocean=True, oceancolor=COLORS["background"],
                 showcountries=True, countrycolor=COLORS["border"], showframe=False,
                 bgcolor=COLORS["background"], projection_type="natural earth",
                 center=dict(lon=-95.7129, lat=37.0902) if region == "Global" else None,
                 projection_scale=3 if region == "Global" else 5),
    )

    # 2. Service vs Inventory Scatter
    _svi = get_service_vs_inventory(region, category)
    _svi_fig = go.Figure()
    if not _svi.empty:
        for abc, color in _abc_color.items():
            mask = _svi["abc"] == abc
            if mask.sum() > 0:
                _svi_fig.add_trace(go.Scatter(
                    x=_svi.loc[mask, "inv_value"], y=_svi.loc[mask, "service_lvl"],
                    mode="markers", name=f"Class {abc}",
                    marker=dict(color=color, size=8, opacity=0.8, line=dict(color=COLORS["border"], width=0.5)),
                    hovertemplate="SKU: %{text}<br>Inv $M Proxy: %{x}<br>Service: %{y}%<extra></extra>",
                    text=_svi.loc[mask, "sku"],
                ))
    _svi_fig.add_hrect(y0=95, y1=100, fillcolor=hex_to_rgba(COLORS["success"], 0.09), line_width=0,
                        annotation_text="Target ≥95%", annotation_font=dict(color=COLORS["success"], size=9))
    apply_dark_layout(_svi_fig, title=f"Service Level vs Inventory ({region} | {category})", height=310,
                      xaxis=dict(title="Inventory Value Proxy", gridcolor=COLORS["border"]),
                      yaxis=dict(title="Service Level (%)", gridcolor=COLORS["border"]),
                      legend=dict(**LEGEND_STYLE, orientation="h", y=1.08))

    # 3. Safety Stock Simulator
    res = get_safety_stock_sim(service_level, region, category)
    ss_display = html.Div([
        _ss_metric("Safety Stock", f"{res['safety_stock_units']:,} units"),
        _ss_metric("Working Capital", f"${res['working_capital_usd']:,}"),
        _ss_metric("Stockout Prob", f"{res['stockout_prob']:.1%}")
    ], className="dashboard-grid")
    
    ss_level_text = f"{service_level:.0%}"

    return _geo_fig, _svi_fig, ss_display, ss_level_text
