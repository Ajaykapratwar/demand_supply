"""
components/charts.py  ─  Centralized Plotly chart factory.
"""
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from config import COLORS, LEGEND_STYLE, apply_dark_layout, hex_to_rgba

# A list of colors for the radar chart scenarios
CHART_COLORS = [
    COLORS["primary"],
    COLORS["warning"],
    COLORS["danger"],
    COLORS["success"],
    COLORS["info"]
]

def plan_vs_actual_chart(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    x_col = "date" if "date" in df.columns else ("week" if "week" in df.columns else df.columns[0])
    fig.add_trace(go.Scatter(x=df[x_col], y=df["plan"], name="Plan",
        line=dict(color=COLORS["primary"], width=2, dash="dash")))
    fig.add_trace(go.Scatter(x=df[x_col], y=df["actual"], name="Actual",
        line=dict(color=COLORS["success"], width=2),
        fill="tonexty", fillcolor=hex_to_rgba(COLORS["success"], 0.1)))
    apply_dark_layout(fig, title="Plan vs Actual — Demand Units", height=260,
                      legend=dict(**LEGEND_STYLE, orientation="h", y=1.12))
    return fig


def scenario_radar(df: pd.DataFrame) -> go.Figure:
    """
    Takes the scenario_comparison() DataFrame and generates a radar chart.
    Metrics: Total Cost, Service Level, Carbon, Inventory, Risk (optional, mock added).
    """
    # Assuming columns are: Scenario, Total Cost ($M), Service Level (%), Carbon (tCO₂e), Inventory ($M)
    metrics = ["Cost Impact", "Service Level", "Carbon", "Inventory"]
    fig = go.Figure()

    for i, row in df.iterrows():
        # Normalize values roughly for visual comparison (0-12 scale)
        cost_norm = row["Total Cost ($M)"] / 5.0
        service_norm = row["Service Level (%)"] / 10.0
        carbon_norm = row["Carbon (tCO₂e)"] / 120.0
        inventory_norm = row["Inventory ($M)"] / 2.0
        
        vals = [cost_norm, service_norm, carbon_norm, inventory_norm]
        vals.append(vals[0])  # Close the radar loop
        
        fig.add_trace(go.Scatterpolar(
            r=vals,
            theta=metrics + [metrics[0]],
            fill="toself",
            name=row["Scenario"],
            line=dict(color=CHART_COLORS[i % len(CHART_COLORS)], width=1.5),
            fillcolor=hex_to_rgba(CHART_COLORS[i % len(CHART_COLORS)], 0.13),
            opacity=0.85,
        ))

    apply_dark_layout(fig, title="Scenario Radar", height=300)
    fig.update_layout(
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


def fan_chart(dates: list, p10: list, p25: list, p50: list, p75: list, p90: list,
              actuals: list = None, title: str = "Forecast Fan Chart") -> "go.Figure":
    """§16.3 Uncertainty visualization — quantile fan chart with optional actuals overlay."""
    fig = go.Figure()
    # P10–P90 outer band
    fig.add_trace(go.Scatter(
        x=dates + dates[::-1], y=p90 + p10[::-1],
        fill="toself", fillcolor=hex_to_rgba(COLORS["primary"], 0.08),
        line=dict(color="rgba(0,0,0,0)"), hoverinfo="skip", name="P10–P90",
    ))
    # P25–P75 inner band
    fig.add_trace(go.Scatter(
        x=dates + dates[::-1], y=p75 + p25[::-1],
        fill="toself", fillcolor=hex_to_rgba(COLORS["primary"], 0.18),
        line=dict(color="rgba(0,0,0,0)"), hoverinfo="skip", name="P25–P75",
    ))
    # P50 median
    fig.add_trace(go.Scatter(
        x=dates, y=p50, name="P50 (Median)",
        line=dict(color=COLORS["primary"], width=2.5),
    ))
    # Actuals overlay
    if actuals:
        fig.add_trace(go.Scatter(
            x=dates[:len(actuals)], y=actuals, name="Actual",
            line=dict(color=COLORS["success"], width=2, dash="dot"),
        ))
    apply_dark_layout(fig, title=title, height=300,
                      legend=dict(**LEGEND_STYLE, orientation="h", y=1.12))
    return fig

def quantile_dot_plot(outcomes: list, title: str = "Quantile Dot Plot") -> go.Figure:
    """§16.3 Visualization of discrete probabilistic outcomes using a dot-density approximation."""
    # Create bins and counts
    bins = pd.cut(outcomes, bins=20)
    counts = bins.value_counts().sort_index()
    
    x_vals = []
    y_vals = []
    for interval, count in counts.items():
        midpoint = interval.mid
        for i in range(count):
            x_vals.append(midpoint)
            y_vals.append(i + 1)
            
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x_vals, y=y_vals, mode="markers",
        marker=dict(size=10, color=COLORS["primary"], opacity=0.7),
        name="Outcome Distribution"
    ))
    apply_dark_layout(fig, title=title, height=300)
    fig.update_yaxes(visible=False, showgrid=False)
    return fig

def density_plot(scenarios: dict, title: str = "Outcome Density") -> go.Figure:
    """§16.3 Visualization of full probability density of scenario outcomes."""
    fig = go.Figure()
    for idx, (name, values) in enumerate(scenarios.items()):
        color = CHART_COLORS[idx % len(CHART_COLORS)]
        fig.add_trace(go.Violin(
            x=values, name=name,
            line_color=color, fillcolor=hex_to_rgba(color, 0.4),
            spanmode="hard", orientation="h"
        ))
    apply_dark_layout(fig, title=title, height=300, 
                      legend=dict(**LEGEND_STYLE, orientation="h", y=1.12))
    return fig

def tornado_chart(sensitivity_data: dict, title: str = "Sensitivity Analysis (Tornado)") -> go.Figure:
    """§16.3 Sensitivity analysis mapping top drivers sorted by impact magnitude.
    sensitivity_data: {"Driver Name": {"downside": -X, "upside": +Y}}
    """
    drivers = list(sensitivity_data.keys())
    downside = [sensitivity_data[d].get("downside", 0) for d in drivers]
    upside = [sensitivity_data[d].get("upside", 0) for d in drivers]
    
    # Sort by total magnitude
    magnitudes = [abs(d) + abs(u) for d, u in zip(downside, upside)]
    sorted_idx = np.argsort(magnitudes)
    
    drivers_sorted = [drivers[i] for i in sorted_idx]
    downside_sorted = [downside[i] for i in sorted_idx]
    upside_sorted = [upside[i] for i in sorted_idx]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=drivers_sorted, x=downside_sorted, name="Downside Impact",
        orientation="h", marker_color=COLORS["danger"]
    ))
    fig.add_trace(go.Bar(
        y=drivers_sorted, x=upside_sorted, name="Upside Impact",
        orientation="h", marker_color=COLORS["success"]
    ))
    
    apply_dark_layout(fig, title=title, height=350)
    fig.update_layout(barmode="relative")
    return fig

def supplier_network_graph(nodes: list, edges: list, title: str = "Supplier Network Risk Graph") -> go.Figure:
    """§17.8 Force-directed supplier network graph"""
    # A simple layout rendering using Scatter
    for i, node in enumerate(nodes):
        if 'x' not in node or 'y' not in node:
            angle = 2 * np.pi * i / len(nodes)
            node['x'] = np.cos(angle)
            node['y'] = np.sin(angle)
            
    edge_x, edge_y = [], []
    for edge in edges:
        s_idx, t_idx = edge["source"], edge["target"]
        if s_idx < len(nodes) and t_idx < len(nodes):
            x0, y0 = nodes[s_idx]['x'], nodes[s_idx]['y']
            x1, y1 = nodes[t_idx]['x'], nodes[t_idx]['y']
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1.5, color=COLORS["border"]),
        hoverinfo='none', mode='lines'
    ))
    
    node_x = [n['x'] for n in nodes]
    node_y = [n['y'] for n in nodes]
    node_colors = [n.get('color', COLORS["primary"]) for n in nodes]
    node_text = [n.get('label', f"Node {i}") for i, n in enumerate(nodes)]
    
    fig.add_trace(go.Scatter(
        x=node_x, y=node_y, mode='markers+text',
        text=node_text, textposition="top center",
        marker=dict(color=node_colors, size=[n.get('size', 20) for n in nodes], line_width=2),
        textfont=dict(color=COLORS["text_secondary"], size=10)
    ))
    apply_dark_layout(fig, title=title, height=350)
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    fig.update_layout(showlegend=False)
    return fig

def pareto_frontier_chart(scenarios: list, title: str = "Pareto Frontier (Cost vs Service)") -> go.Figure:
    """§17.8 Pareto frontier interaction for multi-objective optimization"""
    fig = go.Figure()
    frontier_x = [s["cost"] for s in scenarios if s.get("is_frontier")]
    frontier_y = [s["service"] for s in scenarios if s.get("is_frontier")]
    if frontier_x:
        sorted_indices = np.argsort(frontier_x)
        frontier_x = [frontier_x[i] for i in sorted_indices]
        frontier_y = [frontier_y[i] for i in sorted_indices]
        fig.add_trace(go.Scatter(
            x=frontier_x, y=frontier_y, mode='lines',
            line=dict(color=COLORS["success"], width=2, dash='dash'),
            name="Pareto Frontier"
        ))
        
    x = [s["cost"] for s in scenarios]
    y = [s["service"] for s in scenarios]
    text = [s["name"] for s in scenarios]
    colors = [COLORS["success"] if s.get("is_frontier") else COLORS["chart_3"] for s in scenarios]
    sizes = [s.get("carbon", 20) for s in scenarios]
    
    fig.add_trace(go.Scatter(
        x=x, y=y, mode='markers+text', text=text, textposition="bottom center",
        marker=dict(color=colors, size=sizes, sizemode='area', sizeref=2.*max(sizes)/(30.**2), sizemin=6),
        name="Scenarios"
    ))
    apply_dark_layout(fig, title=title, height=350,
                      xaxis=dict(title="Cost ($M)", gridcolor=COLORS["border"]),
                      yaxis=dict(title="Service Level (%)", gridcolor=COLORS["border"]))
    return fig
