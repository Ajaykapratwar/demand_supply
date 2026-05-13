"""
charts.py  ─  All chart builders for 9 dashboards.
Returns plotly Figure objects.
"""
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from components.theme import COLORS, CHART_COLORS, base_layout


def _rgba(hex_color: str, alpha: float = 0.12) -> str:
    """Convert 6-digit hex to rgba() — Plotly v6 compatible."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


# ═══════════════════════════════════════════════════════════════════════════════
# Dashboard 1 – Executive Summary
# ═══════════════════════════════════════════════════════════════════════════════

def plan_vs_actual_chart(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    # Confidence band
    fig.add_trace(go.Scatter(
        x=pd.concat([df["date"], df["date"].iloc[::-1]]),
        y=pd.concat([df["p90"], df["p10"].iloc[::-1]]),
        fill="toself", fillcolor=_rgba(COLORS["chart_1"], 0.10),
        line=dict(color="rgba(0,0,0,0)"), name="P10–P90 Band",
        showlegend=True,
    ))
    fig.add_trace(go.Scatter(
        x=df["date"], y=df["plan"], name="Plan",
        line=dict(color=COLORS["chart_1"], width=2, dash="dash"),
    ))
    fig.add_trace(go.Scatter(
        x=df["date"], y=df["actual"], name="Actual",
        line=dict(color=COLORS["chart_2"], width=2),
        mode="lines+markers", marker=dict(size=3),
    ))
    fig.update_layout(**base_layout("Plan vs Actual (Units)", height=280))
    return fig


def scenario_radar(scenarios: list) -> go.Figure:
    metrics = ["Cost Impact", "Service Level", "Carbon", "Inventory", "Risk"]
    fig = go.Figure()
    for i, s in enumerate(scenarios[:4]):
        vals = [
            min(abs(s["cost_delta"]) / 10000, 10),
            abs(s["service_delta"]),
            abs(s["carbon_delta"]) / 30,
            abs(s["inventory_delta"]) / 10000,
            abs(s["cost_delta"]) / 100000 + abs(s["service_delta"]),
        ]
        vals.append(vals[0])
        fig.add_trace(go.Scatterpolar(
            r=vals, theta=metrics + [metrics[0]],
            fill="toself", name=s["name"],
            line=dict(color=CHART_COLORS[i], width=1.5),
            fillcolor=_rgba(CHART_COLORS[i], 0.13),
            opacity=0.85,
        ))
    fig.update_layout(
        **base_layout("Scenario Radar", height=300),
        polar=dict(
            bgcolor=COLORS["card"],
            radialaxis=dict(visible=True, range=[0, 12],
                            gridcolor=COLORS["border"],
                            tickfont=dict(color=COLORS["text_secondary"], size=9)),
            angularaxis=dict(gridcolor=COLORS["border"],
                             tickfont=dict(color=COLORS["text_secondary"])),
        ),
    )
    return fig


# ═══════════════════════════════════════════════════════════════════════════════
# Dashboard 2 – Operational Planning
# ═══════════════════════════════════════════════════════════════════════════════

def supply_demand_heatmap(df: pd.DataFrame) -> go.Figure:
    pivot = df.pivot_table(index="region", columns=df["date"].dt.strftime("%m/%d"),
                           values="gap_pct", aggfunc="mean")
    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        x=pivot.columns.tolist(),
        y=pivot.index.tolist(),
        colorscale=[
            [0,    COLORS["danger"]],
            [0.45, COLORS["warning"]],
            [0.55, COLORS["card"]],
            [1,    COLORS["success"]],
        ],
        zmid=0,
        colorbar=dict(tickfont=dict(color=COLORS["text_secondary"], size=9),
                      outlinecolor=COLORS["border"]),
        hovertemplate="<b>%{y}</b><br>Week: %{x}<br>Gap: %{z:.1f}%<extra></extra>",
    ))
    fig.update_layout(**base_layout("Supply–Demand Gap % by Region & Week", height=220))
    return fig


def inventory_dos_gauge(dos: float, target: float, region: str) -> go.Figure:
    color = COLORS["danger"] if dos < 22 else (COLORS["warning"] if dos < 28 else COLORS["success"])
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=dos,
        number=dict(font=dict(color=color, size=26, family="JetBrains Mono")),
        gauge=dict(
            axis=dict(range=[0, 60], tickcolor=COLORS["text_secondary"],
                      tickfont=dict(size=8, color=COLORS["text_secondary"])),
            bar=dict(color=color, thickness=0.55),
            bgcolor=COLORS["surface"],
            bordercolor=COLORS["border"],
            steps=[
                dict(range=[0, 22],  color=_rgba(COLORS["danger"],  0.13)),
                dict(range=[22, 28], color=_rgba(COLORS["warning"], 0.13)),
                dict(range=[28, 60], color=_rgba(COLORS["success"], 0.13)),
            ],
            threshold=dict(line=dict(color=COLORS["primary"], width=2),
                           thickness=0.8, value=target),
        ),
        title=dict(text=region, font=dict(size=11, color=COLORS["text_secondary"])),
    ))
    fig.update_layout(
        paper_bgcolor=COLORS["card"], height=170,
        margin=dict(l=16, r=16, t=20, b=10),
        font=dict(color=COLORS["text_primary"]),
    )
    return fig


# ═══════════════════════════════════════════════════════════════════════════════
# Dashboard 3 – Forecast Analytics
# ═══════════════════════════════════════════════════════════════════════════════

def forecast_vs_actual_chart(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=pd.concat([df["date"], df["date"].iloc[::-1]]),
        y=pd.concat([df["p90"], df["p10"].iloc[::-1]]),
        fill="toself", fillcolor=_rgba(COLORS["chart_1"], 0.08),
        line=dict(color="rgba(0,0,0,0)"), name="P10–P90",
    ))
    for col, name, color, dash in [
        ("actual", "Actual", COLORS["chart_2"], "solid"),
        ("stat_forecast", "Statistical", COLORS["chart_1"], "dash"),
        ("consensus", "Consensus", COLORS["chart_5"], "dot"),
    ]:
        fig.add_trace(go.Scatter(
            x=df["date"], y=df[col], name=name,
            line=dict(color=color, width=2, dash=dash),
        ))
    fig.update_layout(**base_layout("Forecast vs Actual (Units)", height=300))
    return fig


def fva_waterfall(stages: list) -> go.Figure:
    labels = [s["stage"] for s in stages]
    values = [stages[0]["wape"]] + [s["delta"] for s in stages[1:]]
    colors = [COLORS["text_secondary"]] + [
        COLORS["success"] if v < 0 else COLORS["danger"] for v in values[1:]
    ]
    fig = go.Figure(go.Waterfall(
        name="WAPE %",
        orientation="v",
        measure=["absolute"] + ["relative"] * (len(labels) - 1),
        x=labels,
        y=values,
        connector=dict(line=dict(color=COLORS["border"], width=1)),
        increasing=dict(marker_color=COLORS["danger"]),
        decreasing=dict(marker_color=COLORS["success"]),
        totals=dict(marker_color=COLORS["chart_5"]),
        text=[f"{v:+.1f}%" if i else f"{v:.1f}%" for i, v in enumerate(values)],
        textposition="outside",
        textfont=dict(color=COLORS["text_primary"], size=10),
    ))
    fig.update_layout(**base_layout("Forecast Value Added (WAPE %)", height=280))
    return fig


def bias_by_category_chart(df: pd.DataFrame) -> go.Figure:
    colors = [COLORS["danger"] if b > 5 else (COLORS["warning"] if b > 0 else COLORS["success"])
              for b in df["bias_pct"]]
    fig = go.Figure(go.Bar(
        x=df["category"], y=df["bias_pct"],
        marker_color=colors,
        text=[f"{b:+.1f}%" for b in df["bias_pct"]],
        textposition="outside",
        textfont=dict(color=COLORS["text_secondary"], size=9),
    ))
    fig.add_hline(y=5,  line_dash="dash", line_color=COLORS["warning"], line_width=1)
    fig.add_hline(y=-5, line_dash="dash", line_color=COLORS["warning"], line_width=1)
    fig.update_layout(**base_layout("Forecast Bias by Category (%)", height=260))
    return fig


# ═══════════════════════════════════════════════════════════════════════════════
# Dashboard 4 – Inventory Optimization
# ═══════════════════════════════════════════════════════════════════════════════

def inventory_geo_scatter(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure(go.Scattergeo(
        lat=df["lat"], lon=df["lon"],
        text=df["region"],
        mode="markers+text",
        textposition="top center",
        marker=dict(
            size=df["inventory_value_m"] * 1.2,
            color=df["stockout_prob"],
            colorscale=[[0, COLORS["success"]], [0.5, COLORS["warning"]], [1, COLORS["danger"]]],
            colorbar=dict(title="Stockout Risk",
                          tickfont=dict(color=COLORS["text_secondary"], size=9),
                          outlinecolor=COLORS["border"]),
            line=dict(color=COLORS["border"], width=1),
            showscale=True,
        ),
        hovertemplate=(
            "<b>%{text}</b><br>"
            "Stockout Prob: %{marker.color:.1%}<br>"
            "DOS: %{customdata[0]:.1f} days<br>"
            "Inv. Value: $%{customdata[1]:.1f}M<extra></extra>"
        ),
        customdata=df[["dos", "inventory_value_m"]].values,
    ))
    fig.update_layout(
        **base_layout("Inventory Risk – Global Heatmap", height=320),
        geo=dict(
            bgcolor=COLORS["card"],
            showland=True, landcolor=COLORS["surface"],
            showocean=True, oceancolor=COLORS["background"],
            showcountries=True, countrycolor=COLORS["border"],
            showcoastlines=False,
        ),
    )
    return fig


def service_vs_inventory_scatter(df: pd.DataFrame) -> go.Figure:
    cat_colors = {c: CHART_COLORS[i] for i, c in enumerate(df["category"].unique())}
    fig = go.Figure()
    for cat in df["category"].unique():
        d = df[df["category"] == cat]
        fig.add_trace(go.Scatter(
            x=d["safety_stock"], y=d["service_level"],
            mode="markers", name=cat,
            marker=dict(color=cat_colors[cat], size=8, opacity=0.8,
                        line=dict(color=COLORS["border"], width=0.5)),
            hovertemplate=("<b>%{text}</b><br>Safety Stock: %{x:,.0f} units<br>"
                           "Service Level: %{y:.1f}%<extra></extra>"),
            text=d["sku"],
        ))
    fig.add_hline(y=95, line_dash="dash", line_color=COLORS["primary"], line_width=1,
                  annotation_text="95% SL Target", annotation_font_color=COLORS["primary"])
    fig.update_layout(**base_layout("Service Level vs Safety Stock", height=300))
    fig.update_xaxes(title_text="Safety Stock (units)",
                     title_font=dict(color=COLORS["text_secondary"], size=10))
    fig.update_yaxes(title_text="Service Level (%)",
                     title_font=dict(color=COLORS["text_secondary"], size=10))
    return fig


# ═══════════════════════════════════════════════════════════════════════════════
# Dashboard 5 – Capacity Planning
# ═══════════════════════════════════════════════════════════════════════════════

def capacity_gauge(utilization: float, plant: str, oee: float) -> go.Figure:
    color = (COLORS["danger"] if utilization > 0.92 else
             COLORS["warning"] if utilization > 0.80 else COLORS["success"])
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=round(utilization * 100, 1),
        delta=dict(reference=80, suffix="%", valueformat=".1f",
                   increasing=dict(color=COLORS["warning"]),
                   decreasing=dict(color=COLORS["success"])),
        number=dict(suffix="%", font=dict(size=24, color=color,
                                          family="JetBrains Mono")),
        gauge=dict(
            axis=dict(range=[0, 100], ticksuffix="%",
                      tickfont=dict(size=8, color=COLORS["text_secondary"])),
            bar=dict(color=color, thickness=0.55),
            bgcolor=COLORS["surface"], bordercolor=COLORS["border"],
            steps=[
                dict(range=[0, 80],  color=_rgba(COLORS["success"], 0.08)),
                dict(range=[80, 92], color=_rgba(COLORS["warning"], 0.08)),
                dict(range=[92, 100],color=_rgba(COLORS["danger"],  0.08)),
            ],
            threshold=dict(line=dict(color=COLORS["primary"], width=2),
                           thickness=0.8, value=92),
        ),
        title=dict(text=f"{plant}<br><span style='font-size:9px;color:{COLORS['text_secondary']}'>OEE {oee:.0%}</span>",
                   font=dict(size=11)),
    ))
    fig.update_layout(paper_bgcolor=COLORS["card"], height=180,
                      margin=dict(l=16, r=16, t=24, b=10),
                      font=dict(color=COLORS["text_primary"]))
    return fig


def capacity_load_profile(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    for i, plant in enumerate(df["plant"].unique()):
        d = df[df["plant"] == plant]
        fig.add_trace(go.Scatter(
            x=d["date"], y=d["utilization"] * 100,
            name=plant, mode="lines+markers",
            line=dict(color=CHART_COLORS[i], width=2),
            marker=dict(size=4),
        ))
    fig.add_hline(y=92, line_dash="dash", line_color=COLORS["danger"], line_width=1,
                  annotation_text="Critical 92%", annotation_font_color=COLORS["danger"])
    fig.add_hline(y=80, line_dash="dash", line_color=COLORS["warning"], line_width=1,
                  annotation_text="Warning 80%", annotation_font_color=COLORS["warning"])
    fig.update_layout(**base_layout("Capacity Load Profile (%)", height=300))
    return fig


# ═══════════════════════════════════════════════════════════════════════════════
# Dashboard 6 – Financial Impact
# ═══════════════════════════════════════════════════════════════════════════════

def pl_bridge_waterfall(stages: list) -> go.Figure:
    labels  = [s["label"] for s in stages]
    values  = [s["value"] for s in stages]
    measure = ["absolute" if s["type"] == "total" else "relative" for s in stages]
    fig = go.Figure(go.Waterfall(
        name="Revenue $M",
        orientation="v",
        measure=measure,
        x=labels, y=values,
        connector=dict(line=dict(color=COLORS["border"], width=1)),
        increasing=dict(marker_color=COLORS["success"]),
        decreasing=dict(marker_color=COLORS["danger"]),
        totals=dict(marker_color=COLORS["chart_1"]),
        text=[f"${v:.1f}M" for v in values],
        textposition="outside",
        textfont=dict(color=COLORS["text_primary"], size=10),
    ))
    fig.update_layout(**base_layout("P&L Bridge: Budget → Forecast ($M)", height=300))
    return fig


def budget_vs_forecast_chart(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["month"].dt.strftime("%b %Y"), y=df["budget"],
        name="Budget", marker_color=_rgba(COLORS["chart_2"], 0.60),
    ))
    fig.add_trace(go.Scatter(
        x=df["month"].dt.strftime("%b %Y"), y=df["forecast"],
        name="Forecast", mode="lines+markers",
        line=dict(color=COLORS["chart_1"], width=2),
        marker=dict(size=6),
    ))
    fig.update_layout(**base_layout("Budget vs Forecast ($M)", height=280))
    return fig


# ═══════════════════════════════════════════════════════════════════════════════
# Dashboard 7 – Risk Monitoring
# ═══════════════════════════════════════════════════════════════════════════════

def risk_score_gauge(score: float, supplier: str) -> go.Figure:
    color = (COLORS["danger"] if score > 0.7 else
             COLORS["warning"] if score > 0.4 else COLORS["success"])
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=round(score * 100, 0),
        number=dict(suffix="/100", font=dict(size=26, color=color,
                                              family="JetBrains Mono")),
        gauge=dict(
            axis=dict(range=[0, 100], tickfont=dict(size=8, color=COLORS["text_secondary"])),
            bar=dict(color=color, thickness=0.55),
            bgcolor=COLORS["surface"], bordercolor=COLORS["border"],
            steps=[
                dict(range=[0, 40],  color=_rgba(COLORS["success"], 0.08)),
                dict(range=[40, 70], color=_rgba(COLORS["warning"], 0.08)),
                dict(range=[70, 100],color=_rgba(COLORS["danger"],  0.08)),
            ],
        ),
        title=dict(text=supplier, font=dict(size=10, color=COLORS["text_secondary"])),
    ))
    fig.update_layout(paper_bgcolor=COLORS["card"], height=160,
                      margin=dict(l=12, r=12, t=20, b=8),
                      font=dict(color=COLORS["text_primary"]))
    return fig


def risk_probability_impact_matrix(df: pd.DataFrame) -> go.Figure:
    cat_colors = {c: CHART_COLORS[i] for i, c in enumerate(df["category"].unique())}
    fig = go.Figure()
    for cat in df["category"].unique():
        d = df[df["category"] == cat]
        fig.add_trace(go.Scatter(
            x=d["probability"], y=d["impact"],
            mode="markers+text", name=cat,
            text=d["risk"], textposition="top center",
            textfont=dict(size=8, color=COLORS["text_secondary"]),
            marker=dict(color=cat_colors[cat], size=14, opacity=0.85,
                        symbol="circle",
                        line=dict(color=COLORS["border"], width=1)),
        ))
    # Quadrant shading
    for x0, x1, y0, y1, col in [
        (0, 0.5, 0, 0.5, COLORS["success"]),
        (0.5, 1, 0, 0.5, COLORS["warning"]),
        (0, 0.5, 0.5, 1, COLORS["warning"]),
        (0.5, 1, 0.5, 1, COLORS["danger"]),
    ]:
        fig.add_shape(type="rect", x0=x0, y0=y0, x1=x1, y1=y1,
                      fillcolor=_rgba(col, 0.07), line=dict(width=0))

    fig.update_layout(**base_layout("Risk: Probability × Impact Matrix", height=320))
    fig.update_xaxes(title_text="Probability",
                     title_font=dict(color=COLORS["text_secondary"], size=10), range=[0, 1])
    fig.update_yaxes(title_text="Impact",
                     title_font=dict(color=COLORS["text_secondary"], size=10), range=[0, 1])
    return fig


# ═══════════════════════════════════════════════════════════════════════════════
# Dashboard 8 – Sustainability
# ═══════════════════════════════════════════════════════════════════════════════

def emissions_donut(breakdown: list) -> go.Figure:
    labels = [b["source"] for b in breakdown]
    values = [b["tco2e"] for b in breakdown]
    fig = go.Figure(go.Pie(
        labels=labels, values=values,
        hole=0.55,
        marker=dict(colors=CHART_COLORS[:len(labels)],
                    line=dict(color=COLORS["background"], width=2)),
        textinfo="percent+label",
        textfont=dict(size=10, color=COLORS["text_primary"]),
        hovertemplate="<b>%{label}</b><br>%{value:,} tCO2e<br>%{percent}<extra></extra>",
    ))
    fig.update_layout(**base_layout("Emissions by Source (tCO2e)", height=300))
    return fig


def pareto_cost_carbon(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure(go.Scatter(
        x=df["cost_delta_k"], y=df["carbon_delta"],
        mode="markers",
        marker=dict(
            size=10 + df["service_delta"].abs() * 3,
            color=df["carbon_delta"],
            colorscale=[[0, COLORS["danger"]], [0.5, COLORS["warning"]], [1, COLORS["success"]]],
            showscale=True,
            colorbar=dict(title="CO2 Δ", tickfont=dict(size=9, color=COLORS["text_secondary"])),
            line=dict(color=COLORS["border"], width=0.5),
            opacity=0.85,
        ),
        text=df["scenario"],
        hovertemplate="<b>%{text}</b><br>Cost Δ: $%{x:.0f}K<br>Carbon Δ: %{y:.0f} tCO2e<extra></extra>",
    ))
    fig.add_hline(y=0, line_color=COLORS["border"], line_width=1)
    fig.add_vline(x=0, line_color=COLORS["border"], line_width=1)
    fig.update_layout(**base_layout("Pareto: Cost vs Carbon Trade-off", height=320))
    fig.update_xaxes(title_text="Cost Delta ($K)",
                     title_font=dict(color=COLORS["text_secondary"], size=10))
    fig.update_yaxes(title_text="Carbon Delta (tCO2e)",
                     title_font=dict(color=COLORS["text_secondary"], size=10))
    return fig


# ═══════════════════════════════════════════════════════════════════════════════
# Dashboard 9 – Regional Planning
# ═══════════════════════════════════════════════════════════════════════════════

def regional_bar_chart(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    for i, region in enumerate(df["region"].unique()):
        d = df[df["region"] == region]
        fig.add_trace(go.Bar(
            x=d["date"].dt.strftime("%m/%d"), y=d["plan"],
            name=f"{region} Plan", marker_color=_rgba(CHART_COLORS[i], 0.33),
            legendgroup=region,
        ))
        fig.add_trace(go.Scatter(
            x=d["date"].dt.strftime("%m/%d"), y=d["actual"],
            name=f"{region} Actual", mode="lines+markers",
            line=dict(color=CHART_COLORS[i], width=2),
            marker=dict(size=4), legendgroup=region,
        ))
    fig.update_layout(**base_layout("Regional Plan vs Actual", height=300))
    return fig
