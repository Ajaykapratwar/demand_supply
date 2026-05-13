"""pages/regional.py — Dashboard 9: Regional Planning"""
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import dcc, html, Input, Output, callback, register_page
import json

from config import COLORS, LEGEND_STYLE, apply_dark_layout
from data.data_loader import get_regional_kpis, get_region_vs_plan

register_page(__name__, path="/regional", name="Regional Planning")

def _region_card(row):
    oc = COLORS["success"] if row["otif"]>=95 else COLORS["warning"] if row["otif"]>=90 else COLORS["danger"]
    rc = COLORS["danger"] if row["risk_score"]>0.6 else COLORS["warning"] if row["risk_score"]>0.4 else COLORS["success"]
    return dbc.Card([dbc.CardBody([
        html.Div(row["region"], style={"fontWeight": "700", "fontSize": "0.9rem",
                                        "color": COLORS["text_primary"], "marginBottom": "8px"}),
        dbc.Row([
            dbc.Col([html.Div("OTIF", style={"fontSize": "0.65rem", "color": COLORS["text_secondary"],
                              "fontWeight": "700", "letterSpacing": "0.08em"}),
                     html.Div(f"{row['otif']:.1f}%", style={"fontSize": "1.4rem", "fontWeight": "700", "color": oc})]),
            dbc.Col([html.Div("DOS", style={"fontSize": "0.65rem", "color": COLORS["text_secondary"],
                              "fontWeight": "700", "letterSpacing": "0.08em"}),
                     html.Div(f"{row['dos']:.0f}d", style={"fontSize": "1.4rem", "fontWeight": "700",
                              "color": COLORS["text_primary"]})]),
            dbc.Col([html.Div("RISK", style={"fontSize": "0.65rem", "color": COLORS["text_secondary"],
                              "fontWeight": "700", "letterSpacing": "0.08em"}),
                     html.Div(f"{row['risk_score']:.2f}", style={"fontSize": "1.4rem", "fontWeight": "700", "color": rc})]),
        ]),
    ], style={"padding": "12px 14px"})],
    style={"backgroundColor": COLORS["card"], "border": f"1px solid {COLORS['border']}", "borderRadius": "8px"})

layout = html.Div([
    html.H5("Regional Planning", style={"color": COLORS["text_primary"], "fontWeight": "700", "marginBottom": "4px"}),
    html.Div("Choropleth OTIF map • Region vs plan • Local scenario adjustments",
             style={"color": COLORS["text_secondary"], "fontSize": "0.83rem", "marginBottom": "20px"}),
    dcc.Loading(id="loading-regional-cards", type="default", color=COLORS["primary"],
                children=html.Div(id="regional-cards-container", className="mb-3")),
    dbc.Row([
        dbc.Col(dcc.Loading(id="loading-choro", type="default", color=COLORS["primary"],
                            children=dcc.Graph(id="choro-map", config={"displayModeBar": False})), md=7, className="mb-3"),
        dbc.Col(dcc.Loading(id="loading-rvp", type="default", color=COLORS["primary"],
                            children=dcc.Graph(id="rvp-bar", config={"displayModeBar": False})), md=5, className="mb-3"),
    ]),
    dbc.Card([
        dbc.CardHeader(html.Span("LOCAL SCENARIO ADJUSTMENTS",
            style={"fontSize": "0.72rem", "fontWeight": "700", "letterSpacing": "0.08em",
                   "color": COLORS["text_secondary"]}),
            style={"backgroundColor": COLORS["surface"], "borderBottom": f"1px solid {COLORS['border']}"}),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([html.Div("North Demand Adjustment", style={"fontSize":"0.82rem","color":COLORS["text_secondary"],"marginBottom":"4px"}),
                         dcc.Slider(id="region-north-slider", min=-20, max=30, step=5, value=0,
                                    marks={v: f"{v:+d}%" for v in [-20,-10,0,10,20,30]})], md=3),
                dbc.Col([html.Div("South Demand Adjustment", style={"fontSize":"0.82rem","color":COLORS["text_secondary"],"marginBottom":"4px"}),
                         dcc.Slider(id="region-south-slider", min=-20, max=30, step=5, value=0,
                                    marks={v: f"{v:+d}%" for v in [-20,-10,0,10,20,30]})], md=3),
                dbc.Col([html.Div("East Demand Adjustment", style={"fontSize":"0.82rem","color":COLORS["text_secondary"],"marginBottom":"4px"}),
                         dcc.Slider(id="region-east-slider", min=-20, max=30, step=5, value=0,
                                    marks={v: f"{v:+d}%" for v in [-20,-10,0,10,20,30]})], md=3),
                dbc.Col([html.Div("West Demand Adjustment", style={"fontSize":"0.82rem","color":COLORS["text_secondary"],"marginBottom":"4px"}),
                         dcc.Slider(id="region-west-slider", min=-20, max=30, step=5, value=0,
                                    marks={v: f"{v:+d}%" for v in [-20,-10,0,10,20,30]})], md=3),
            ]),
            html.Div(id="region-scenario-output", style={"marginTop": "16px"}),
        ], style={"backgroundColor": COLORS["card"]}),
    ], style={"border": f"1px solid {COLORS['border']}", "borderRadius": "10px"}),
])

@callback(
    Output("regional-cards-container", "children"),
    Output("choro-map", "figure"),
    Output("rvp-bar", "figure"),
    Input("global-filter-store", "data")
)
def update_regional_page(filter_data):
    filters = filter_data if isinstance(filter_data, dict) else {}
    region = filters.get("region", "Global")
    category = filters.get("category", "All")
    
    _reg = get_regional_kpis(region, category)
    _rvp = get_region_vs_plan(region, category)
    
    # 1. Cards
    if _reg.empty:
        cards = html.Div("No regional data available for selected filters.", style={"color": COLORS["text_secondary"]})
    else:
        cards = dbc.Row([dbc.Col(_region_card(_reg.iloc[i]), xs=6, sm=4, md=3, className="mb-3") for i in range(len(_reg))])
        
    # 2. Choropleth Map
    if _reg.empty:
        _choro_fig = go.Figure()
        _choro_fig.update_layout(paper_bgcolor=COLORS["card"], plot_bgcolor=COLORS["card"])
    else:
        _choro_fig = go.Figure(go.Choropleth(
            locations=_reg["iso_a3"], z=_reg["otif"],
            colorscale=[[0.0, COLORS["danger"]], [0.5, COLORS["warning"]], [1.0, COLORS["success"]]],
            zmin=85, zmax=100, text=_reg["region"],
            hovertemplate="<b>%{text}</b><br>OTIF: %{z:.1f}%<extra></extra>",
            colorbar=dict(title=dict(text="OTIF %", font=dict(color=COLORS["text_secondary"])),
                          tickfont=dict(color=COLORS["text_secondary"]),
                          bgcolor=COLORS["card"], bordercolor=COLORS["border"]),
            marker=dict(line=dict(color=COLORS["border"], width=0.5)),
        ))
        _choro_fig.update_layout(
            paper_bgcolor=COLORS["card"],
            font=dict(color=COLORS["text_primary"], family="Inter, sans-serif"),
            title=dict(text="Regional OTIF Performance", font=dict(color=COLORS["text_primary"], size=13)),
            height=320, margin=dict(l=0, r=0, t=40, b=0),
            geo=dict(showframe=False, showcoastlines=True, coastlinecolor=COLORS["border"],
                     showland=True, landcolor=COLORS["surface"],
                     showocean=True, oceancolor=COLORS["background"],
                     showcountries=True, countrycolor=COLORS["border"],
                     bgcolor=COLORS["background"], projection_type="natural earth"),
        )
        
    # 3. RVP Bar Chart
    _rvp_fig = go.Figure()
    if not _rvp.empty:
        _rvp_fig.add_trace(go.Bar(x=_rvp["region"], y=_rvp["plan"], name="Plan",
                                   marker_color=COLORS["primary"], opacity=0.8))
        _rvp_fig.add_trace(go.Bar(
            x=_rvp["region"], y=_rvp["actual"], name="Actual",
            marker_color=[COLORS["success"] if a >= p else COLORS["danger"]
                          for a, p in zip(_rvp["actual"], _rvp["plan"])], opacity=0.88))
    
    apply_dark_layout(_rvp_fig, title="Region vs Plan ($M)", height=320, barmode="group",
                      yaxis=dict(title="Units", gridcolor=COLORS["border"]),
                      legend=dict(**LEGEND_STYLE, orientation="h", y=1.1))

    return cards, _choro_fig, _rvp_fig

@callback(Output("region-scenario-output", "children"),
          Input("region-north-slider", "value"),
          Input("region-south-slider", "value"),
          Input("region-east-slider", "value"),
          Input("region-west-slider", "value"))
def update_region_scenario(north, south, east, west):
    delta = (north + south + east + west) * 0.04
    return html.Div([
        html.Span("Estimated cost impact: ", style={"color": COLORS["text_secondary"], "fontSize": "0.83rem"}),
        html.Span(f"${delta:+.1f}M", style={"color": COLORS["success"] if delta<=0 else COLORS["danger"],
                                              "fontWeight": "700", "fontSize": "1.1rem", "marginLeft": "8px"}),
        html.Span(f"  (Total: ${45.2 + delta:.1f}M)",
                  style={"color": COLORS["text_secondary"], "fontSize": "0.82rem", "marginLeft": "8px"}),
    ])
