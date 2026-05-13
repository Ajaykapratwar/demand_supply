"""
data_loader.py  --  Bridges real HVAC model outputs to dashboard format.
Reads 5 raw CSVs + model outputs. Falls back to mock where data is unavailable.
"""
import numpy as np
import pandas as pd
from pathlib import Path
from functools import lru_cache

_ROOT    = Path(__file__).parent.parent.parent
_RAW     = _ROOT / "hvac_control_tower" / "data" / "raw"
_OUT     = _ROOT / "hvac_control_tower" / "data" / "outputs"
_OUT_F   = _ROOT / "hvac_forecast_system" / "data" / "outputs"
_EVAL    = _OUT_F / "evaluation_report.csv"
_QFCAST  = _OUT   / "quantile_forecasts.csv"

REGIONS = ["North", "South", "East", "West"]

# ── Raw loaders (cached) ──────────────────────────────────────────────────────
@lru_cache(maxsize=1)
def _orders():
    df = pd.read_csv(_RAW / "dataset1_order_history.csv")
    df["Date"] = pd.to_datetime(df["Date"])
    return df

@lru_cache(maxsize=1)
def _sales():
    df = pd.read_csv(_RAW / "dataset2_sales_revenue.csv")
    df["Date"] = pd.to_datetime(df["Date"])
    return df

@lru_cache(maxsize=1)
def _signals():
    df = pd.read_csv(_RAW / "dataset3_demand_signals.csv")
    df["Date"] = pd.to_datetime(df["Date"])
    return df

@lru_cache(maxsize=1)
def _warehouse():
    df = pd.read_csv(_RAW / "dataset4_warehouse_capacity.csv")
    df["Date"] = pd.to_datetime(df["Date"])
    return df

@lru_cache(maxsize=1)
def _logistics():
    df = pd.read_csv(_RAW / "dataset5_logistics_cost.csv")
    df["Date"] = pd.to_datetime(df["Date"])
    return df

@lru_cache(maxsize=1)
def _model_fc():
    if _QFCAST.exists():
        return pd.read_csv(_QFCAST)
    return None

@lru_cache(maxsize=1)
def _eval():
    if _EVAL.exists():
        return pd.read_csv(_EVAL)
    return None

def _filter(df, region="Global", category="All"):
    if df is None:
        return df
    res = df.copy()
    if region != "Global" and "Region" in res.columns:
        res = res[res["Region"] == region]
    
    if category != "All":
        sku_map = {
            "Split": "SKU001",
            "Window": "SKU002",
            "Cassette": "SKU003",
            "Portable": "SKU004",
            "Tower": "SKU005",
            "Central": "SKU006"
        }
        target_sku = sku_map.get(category)
        if "AC_Type" in res.columns:
            res = res[res["AC_Type"] == category]
        elif "Product_SKU" in res.columns and target_sku:
            res = res[res["Product_SKU"] == target_sku]
    return res

# ── Executive KPIs ────────────────────────────────────────────────────────────
def get_executive_kpis(region="Global", category="All"):
    o = _filter(_orders(), region, category)
    s = _filter(_sales(), region, category)
    w = _filter(_warehouse(), region, category)
    l = _filter(_logistics(), region, category)
    ev = _eval()

    otif      = round(o["Fulfillment_Rate_%"].mean() * 100, 1)
    fill_rate = round(o["Units_Fulfilled"].sum() / o["Units_Ordered"].sum() * 100, 1)
    stockout  = round(o["Units_Backordered"].sum() / o["Units_Ordered"].sum() * 100, 2)
    dos       = round(w["Days_Of_Supply_Remaining"].mean(), 1)
    revenue   = round(s["Net_Revenue_INR"].sum() / 1e7, 1)   # in Cr INR
    co2       = round(l["CO2_Emissions_Kg"].sum() / 1000, 0) # tCO2
    mape      = round(ev[ev["label"] == "XGBoost P50"]["MAPE_%"].values[0], 1) if ev is not None else 18.4
    r2        = round(ev[ev["label"] == "XGBoost P50"]["R2"].values[0], 3) if ev is not None else 0.650

    # Sparklines: last 14 weekly averages
    o_w = (o.set_index("Date")["Fulfillment_Rate_%"] * 100).resample("W").mean().dropna()
    w_w = w.set_index("Date")["Days_Of_Supply_Remaining"].resample("W").mean().dropna()
    s_w = s.set_index("Date")["Net_Revenue_INR"].resample("W").sum().dropna() / 1e7

    def tail14(series):
        return series.iloc[-14:].tolist() if len(series) >= 14 else series.tolist()

    return {
        "otif":           {"value": otif,      "target": 95.0, "delta": otif - 95.0,           "unit": "%",   "status": "warning" if otif < 95 else "success",  "spark": tail14(o_w)},
        "fill_rate":      {"value": fill_rate,  "target": 98.0, "delta": fill_rate - 98.0,       "unit": "%",   "status": "warning" if fill_rate < 98 else "success","spark": tail14(o_w)},
        "stockout_rate":  {"value": stockout,   "target": 1.0,  "delta": stockout - 1.0,         "unit": "%",   "status": "danger"  if stockout > 2 else "warning", "spark": [stockout]*14},
        "mape":           {"value": mape,       "target": 15.0, "delta": mape - 15.0,            "unit": "%",   "status": "warning" if mape > 15 else "success",   "spark": [mape]*14},
        "dos":            {"value": dos,        "target": 35.0, "delta": dos - 35.0,             "unit": "days","status": "warning" if dos > 35 else "success",    "spark": tail14(w_w)},
        "revenue":        {"value": revenue,    "target": revenue*1.05,"delta": revenue*0.05,    "unit": "Cr",  "status": "success",                               "spark": tail14(s_w)},
        "r2":             {"value": r2,         "target": 0.91, "delta": r2 - 0.91,             "unit": "",    "status": "warning" if r2 < 0.91 else "success",   "spark": [r2]*14},
        "co2":            {"value": co2,        "target": co2*0.95,"delta": -(co2*0.05),         "unit": "tCO2","status": "warning",                               "spark": [co2]*14},
    }

# ── Plan vs Actual ────────────────────────────────────────────────────────────
def get_plan_vs_actual(region="Global", category="All", weeks=26):
    o = _filter(_orders(), region, category)
    s = _filter(_sales(), region, category)
    weekly_ordered = o.groupby(pd.Grouper(key="Date", freq="W"))["Units_Ordered"].sum()
    weekly_fulfilled = o.groupby(pd.Grouper(key="Date", freq="W"))["Units_Fulfilled"].sum()
    weekly_sold = s.groupby(pd.Grouper(key="Date", freq="W"))["Net_Units_Sold_TARGET"].sum()
    df = pd.DataFrame({"plan": weekly_ordered, "actual": weekly_fulfilled, "sold": weekly_sold}).dropna().iloc[-weeks:]
    df = df.reset_index().rename(columns={"Date": "date"})
    df["p10"] = df["plan"] * 0.88
    df["p90"] = df["plan"] * 1.12
    return df

# ── Supply-Demand Balance ─────────────────────────────────────────────────────
def get_supply_demand_balance(region="Global", category="All"):
    o = _filter(_orders(), region, category)
    recent = o[o["Date"] >= o["Date"].max() - pd.Timedelta(weeks=8)]
    weekly = recent.groupby(["Region", pd.Grouper(key="Date", freq="W")]).agg(
        demand=("Units_Ordered","sum"), supply=("Units_Fulfilled","sum")
    ).reset_index()
    weekly["gap"]     = weekly["supply"] - weekly["demand"]
    weekly["gap_pct"] = weekly["gap"] / weekly["demand"] * 100
    return weekly.rename(columns={"Date":"date","Region":"region"})

# ── Inventory DOS by Region ───────────────────────────────────────────────────
def get_inventory_dos_gauges(region="Global", category="All"):
    w = _filter(_warehouse(), region, category)
    recent = w[w["Date"] >= w["Date"].max() - pd.Timedelta(days=30)]
    agg = recent.groupby("Region")["Days_Of_Supply_Remaining"].mean().reset_index()
    result = []
    for _, row in agg.iterrows():
        dos = round(row["Days_Of_Supply_Remaining"], 1)
        result.append({
            "region": row["Region"],
            "dos": dos,
            "target": 35,
            "status": "danger" if dos < 20 else ("warning" if dos < 28 else "success")
        })
    return result

# ── Forecast Fan Chart ────────────────────────────────────────────────────────
def get_forecast_fan_chart(region="Global", category="All", weeks=26):
    o = _filter(_orders(), region, category)
    weekly = o.groupby(pd.Grouper(key="Date", freq="W"))["Units_Ordered"].sum().dropna()
    hist = weekly.iloc[-13:].reset_index()
    hist.columns = ["date", "actual"]
    fc = _model_fc()
    if fc is not None:
        n = min(13, len(fc))
        future_dates = pd.date_range(hist["date"].iloc[-1] + pd.Timedelta(weeks=1), periods=n, freq="W")
        fdf = pd.DataFrame({
            "date":   future_dates,
            "actual": [None]*n,
            "p50":    fc["P50"].iloc[:n].values,
            "p90":    fc["P90"].iloc[:n].values,
            "p10":    fc["P50"].iloc[:n].values * 0.85,
        })
    else:
        last = hist["actual"].iloc[-1]
        future_dates = pd.date_range(hist["date"].iloc[-1] + pd.Timedelta(weeks=1), periods=13, freq="W")
        fdf = pd.DataFrame({"date": future_dates, "actual": [None]*13,
                            "p50": last * np.linspace(1,1.1,13), "p90": last*np.linspace(1.1,1.3,13),
                            "p10": last*np.linspace(0.9,0.85,13)})
    hist["p50"] = hist["actual"]
    hist["p90"] = hist["actual"] * 1.08
    hist["p10"] = hist["actual"] * 0.92
    return pd.concat([hist, fdf], ignore_index=True)

# ── Forecast Accuracy KPIs ────────────────────────────────────────────────────
def get_forecast_accuracy_kpis(region="Global", category="All"):
    ev = _eval()
    mape = ev[ev["label"] == "XGBoost P50"]["MAPE_%"].values[0] if ev is not None else 18.4
    r2   = ev[ev["label"] == "XGBoost P50"]["R2"].values[0]    if ev is not None else 0.65
    mae  = ev[ev["label"] == "XGBoost P50"]["MAE"].values[0]   if ev is not None else 4833
    wape = mape * 0.77
    bias = -2.3
    return {
        "mape": {"value": round(mape,1), "target": 15.0, "delta": round(mape-15,1), "status":"warning"},
        "wape": {"value": round(wape,1), "target": 12.0, "delta": round(wape-12,1), "status":"success" if wape<12 else "warning"},
        "r2":   {"value": round(r2,3),   "target": 0.91, "delta": round(r2-0.91,3), "status":"success" if r2>=0.91 else "warning"},
        "bias": {"value": round(bias,1), "target": 0.0,  "delta": round(bias,1),    "status":"success"},
        "mae":  {"value": round(mae,0),  "target": 0,    "delta": 0,                "status":"info"},
    }

def get_fva_waterfall(region="Global", category="All"):
    # Generate FVA waterfall data
    return pd.DataFrame([
        {"step": "Naïve Forecast", "value": 72.0, "type": "absolute"},
        {"step": "Stat Baseline",  "value": 5.5,  "type": "relative"},
        {"step": "ML Enrichment",  "value": 8.2,  "type": "relative"},
        {"step": "Sales Override", "value": -2.1, "type": "relative"},
        {"step": "Final Consensus","value": 83.6, "type": "total"},
    ])

# ── Capacity (Warehouse Utilization) ─────────────────────────────────────────
def get_capacity_utilization(region="Global", category="All"):
    w = _filter(_warehouse(), region, category)
    recent = w[w["Date"] >= w["Date"].max() - pd.Timedelta(days=30)]
    agg = recent.groupby("Region")["Utilization_%"].mean().reset_index()
    result = []
    for _, row in agg.iterrows():
        u = round(row["Utilization_%"], 1) # Note: changed from /100 because capacity gauges use 0-100 values
        result.append({"plant": f"WH-{row['Region']}", "utilization": u,
                        "capacity": 10000, "oee": round(u * 0.92, 1)})
    return pd.DataFrame(result) if result else pd.DataFrame([{"plant": "WH-Default", "utilization": 85.0, "capacity": 10000, "oee": 78.0}])

def get_capacity_load_profile(region="Global", category="All"):
    w = _filter(_warehouse(), region, category)
    recent = w[w["Date"] >= w["Date"].max() - pd.Timedelta(weeks=12)]
    weekly = recent.groupby(["Region", pd.Grouper(key="Date", freq="W")])["Utilization_%"].mean().reset_index()
    
    # Pivot to match expected format
    df = weekly.pivot(index="Date", columns="Region", values="Utilization_%").reset_index()
    df.rename(columns={"Date": "week"}, inplace=True)
    return df

def get_capacity_gantt(region="Global", category="All"):
    # Generate schedule based on region
    import datetime
    today = pd.Timestamp(datetime.date.today())
    plants = [f"WH-{r}" for r in REGIONS]
    if region != "Global":
        plants = [f"WH-{region}"]
        
    data = []
    for p in plants:
        data.extend([
            {"plant": p, "task": "HVAC Assembly", "start": today, "finish": today + pd.Timedelta(days=3)},
            {"plant": p, "task": "Quality Testing", "start": today + pd.Timedelta(days=3), "finish": today + pd.Timedelta(days=5)},
            {"plant": p, "task": "Packaging", "start": today + pd.Timedelta(days=5), "finish": today + pd.Timedelta(days=7)},
        ])
    return pd.DataFrame(data)

# ── Financial ─────────────────────────────────────────────────────────────────
def get_financial_summary(region="Global", category="All"):
    s = _filter(_sales(), region, category)
    l = _filter(_logistics(), region, category)
    total_rev  = round(s["Net_Revenue_INR"].sum() / 1e7, 1)
    avg_disc   = round(s["Discount_%"].mean(), 2) if not s.empty else 0
    log_cost   = round(l["Cost_Per_Unit_INR"].sum() / 1e6, 2)
    # create kpis format
    return {
        "revenue":   {"value": total_rev, "target": round(total_rev*0.95,1), "delta": round(total_rev*0.05,1), "status": "success"},
        "margin":    {"value": round(25.0 - avg_disc*0.1, 1), "target": 25.5, "delta": round(-0.5 - avg_disc*0.1, 1), "status": "warning"},
        "logistics": {"value": log_cost, "target": round(log_cost*0.9, 1), "delta": round(log_cost*0.1, 1), "status": "danger"},
        "discount":  {"value": avg_disc, "target": 10.0, "delta": round(avg_disc-10.0, 1), "status": "danger" if avg_disc>10 else "success"},
    }

def get_scenario_pl_bridge(region="Global", category="All"):
    s = _filter(_sales(), region, category)
    rev = s["Net_Revenue_INR"].sum() / 1e7
    if rev == 0: rev = 100
    base_rev = rev * 0.9
    vol_impact = rev * 0.15
    price_impact = rev * -0.02
    cost_impact = rev * -0.03
    return pd.DataFrame([
        {"component": "Base Plan", "value": round(base_rev, 1)},
        {"component": "Volume", "value": round(vol_impact, 1)},
        {"component": "Price", "value": round(price_impact, 1)},
        {"component": "Costs", "value": round(cost_impact, 1)},
        {"component": "Scenario", "value": round(rev, 1)}
    ])

def get_budget_vs_forecast_real(region="Global", category="All", months=12):
    s = _filter(_sales(), region, category)
    monthly = s.groupby(pd.Grouper(key="Date", freq="MS"))["Net_Revenue_INR"].sum().dropna() / 1e7
    monthly = monthly.iloc[-months:].reset_index()
    monthly.columns = ["month", "actual"]
    monthly["budget"]   = monthly["actual"] * np.random.uniform(0.96, 1.04, len(monthly))
    monthly["forecast"] = monthly["actual"] * np.random.uniform(0.97, 1.05, len(monthly))
    return monthly

# ── Risk ──────────────────────────────────────────────────────────────────────
def get_supplier_risk(region="Global", category="All"):
    o = _filter(_orders(), region, category)
    recent = o[o["Date"] >= o["Date"].max() - pd.Timedelta(days=90)]
    agg = recent.groupby("Region").agg(
        fill_rate=("Fulfillment_Rate_%","mean"),
        backorder_rate=("Units_Backordered","sum"),
        ordered=("Units_Ordered","sum"),
    ).reset_index()
    agg["backorder_pct"] = agg["backorder_rate"] / agg["ordered"]
    agg["risk_score"] = round((1 - agg["fill_rate"]) * 3 + agg["backorder_pct"] * 2, 3).clip(0.1, 0.95)
    agg["risk_category"] = agg["risk_score"].apply(
        lambda x: "critical" if x>0.7 else ("high" if x>0.5 else ("medium" if x>0.3 else "low"))
    )
    return agg.rename(columns={"Region":"supplier"})

def get_risk_kpis(region="Global", category="All"):
    # Generate risk KPIs dynamically based on supplier risk
    risk_df = get_supplier_risk(region, category)
    avg_score = round(risk_df["risk_score"].mean(), 2) if not risk_df.empty else 0.5
    critical_count = len(risk_df[risk_df["risk_category"] == "critical"])
    return {
        "composite_risk": {"value": avg_score, "target": 0.4, "delta": round(avg_score-0.4, 2), "status": "danger" if avg_score > 0.5 else "success"},
        "critical_suppliers": {"value": critical_count, "target": 0, "delta": critical_count, "status": "danger" if critical_count > 0 else "success"},
        "at_risk_revenue": {"value": round(avg_score * 15.4, 1), "target": 5.0, "delta": round(avg_score * 15.4 - 5.0, 1), "status": "warning"},
        "mitigation_completion": {"value": 68, "target": 100, "delta": -32, "status": "warning"},
    }

def get_risk_probability_impact(region="Global", category="All"):
    # Mocking risk scenarios with some dynamic element
    import random
    random.seed(len(region) + len(category))
    return pd.DataFrame([
        {"risk": "Supplier Insolvency", "category": "Supply", "probability": random.uniform(0.1, 0.4), "impact": random.uniform(0.6, 0.9)},
        {"risk": "Port Strike", "category": "Logistics", "probability": random.uniform(0.3, 0.6), "impact": random.uniform(0.5, 0.8)},
        {"risk": "Sudden Demand Spike", "category": "Demand", "probability": random.uniform(0.4, 0.7), "impact": random.uniform(0.4, 0.7)},
        {"risk": "Regulatory Change", "category": "External", "probability": random.uniform(0.2, 0.5), "impact": random.uniform(0.7, 0.9)},
        {"risk": "Component Shortage", "category": "Supply", "probability": random.uniform(0.5, 0.8), "impact": random.uniform(0.6, 0.9)},
        {"risk": "Machine Failure", "category": "Operational", "probability": random.uniform(0.2, 0.4), "impact": random.uniform(0.3, 0.6)},
    ])

def get_mitigation_actions(region="Global", category="All"):
    return pd.DataFrame([
        {"risk": "Component Shortage", "action": "Identify secondary sources in NA", "owner": "Procurement", "status": "In Progress"},
        {"risk": "Port Strike", "action": "Reroute shipments to alternative ports", "owner": "Logistics", "status": "Planned"},
        {"risk": "Sudden Demand Spike", "action": "Increase buffer stock targets", "owner": "Planning", "status": "Completed"},
        {"risk": "Supplier Insolvency", "action": "Audit top 5 critical suppliers", "owner": "Risk", "status": "In Progress"},
    ])

# ── Sustainability ────────────────────────────────────────────────────────────
def get_sustainability_kpis(region="Global", category="All"):
    l = _filter(_logistics(), region, category)
    total_co2 = round(l["CO2_Emissions_Kg"].sum() / 1000, 0)
    return {
        "total_emissions": {"value": total_co2, "target": round(total_co2*0.9, 0), "delta": round(total_co2*0.1, 0), "status": "danger"},
        "emissions_intensity": {"value": 14.2, "target": 15.0, "delta": -0.8, "status": "success"},
        "renewable_energy": {"value": 34, "target": 40, "delta": -6, "status": "warning"},
    }

def get_emissions_breakdown(region="Global", category="All"):
    l = _filter(_logistics(), region, category)
    by_mode = l.groupby("Transport_Mode")["CO2_Emissions_Kg"].sum().reset_index()
    by_mode.columns = ["category","tco2e"]
    by_mode["tco2e"] = (by_mode["tco2e"] / 1000).round(0)
    return by_mode

def get_cost_vs_carbon_pareto(region="Global", category="All"):
    l = _filter(_logistics(), region, category)
    base_co2 = l["CO2_Emissions_Kg"].sum() / 1000
    base_cost = l["Cost_Per_Unit_INR"].sum() / 1e6
    if base_co2 == 0: base_co2 = 1000
    if base_cost == 0: base_cost = 10
    
    return pd.DataFrame([
        {"scenario": "Air Expedited", "carbon": round(base_co2 * 1.5, 0), "cost_usd": round(base_cost * 1.3, 1)},
        {"scenario": "Current Baseline", "carbon": round(base_co2, 0), "cost_usd": round(base_cost, 1)},
        {"scenario": "Ocean Routing", "carbon": round(base_co2 * 0.4, 0), "cost_usd": round(base_cost * 0.7, 1)},
        {"scenario": "Rail Hybrid", "carbon": round(base_co2 * 0.6, 0), "cost_usd": round(base_cost * 0.85, 1)},
        {"scenario": "EV Last Mile", "carbon": round(base_co2 * 0.8, 0), "cost_usd": round(base_cost * 1.1, 1)},
    ])

def get_sustainability_summary(region="Global", category="All"):
    return {"total_tco2": get_sustainability_kpis(region, category)["total_emissions"]["value"], "by_mode": get_emissions_breakdown(region, category)}

def get_co2_trend(region="Global", category="All"):
    l = _filter(_logistics(), region, category)
    weekly = l.groupby(pd.Grouper(key="Date", freq="W"))["CO2_Emissions_Kg"].sum().dropna() / 1000
    return weekly.iloc[-26:].reset_index().rename(columns={"Date":"date","CO2_Emissions_Kg":"tco2"})

# ── Regional ──────────────────────────────────────────────────────────────────
def get_regional_kpis(region="Global", category="All"):
    o = _filter(_orders(), region, category)
    s = _filter(_sales(), region, category)
    w = _filter(_warehouse(), region, category)
    o_agg = o.groupby("Region").agg(otif=("Fulfillment_Rate_%","mean"),
                                     backorder=("Units_Backordered","sum"),
                                     ordered=("Units_Ordered","sum")).reset_index()
    o_agg["stockout_pct"] = round(o_agg["backorder"] / o_agg["ordered"] * 100, 2)
    o_agg["otif"] = (o_agg["otif"] * 100).round(1)
    s_agg = s.groupby("Region")["Net_Revenue_INR"].sum().reset_index()
    s_agg["revenue_cr"] = (s_agg["Net_Revenue_INR"] / 1e7).round(1)
    w_agg = w.groupby("Region")["Days_Of_Supply_Remaining"].mean().reset_index()
    w_agg["dos"] = w_agg["Days_Of_Supply_Remaining"].round(1)
    df = o_agg.merge(s_agg[["Region","revenue_cr"]], on="Region")
    df = df.merge(w_agg[["Region","dos"]], on="Region")
    df["fill_rate"] = df["otif"]
    df["plan_attainment"] = (df["otif"] * 0.98).round(1)
    
    # Map regions to dummy ISO codes for choropleth if actual geo data is missing
    iso_map = {"North": "USA", "South": "BRA", "East": "IND", "West": "DEU"}
    df["iso_a3"] = df["Region"].map(iso_map).fillna("USA")
    
    # Calculate mock risk score
    df["risk_score"] = round(((100 - df["otif"]) / 100) * 3 + (df["stockout_pct"] / 100) * 2, 2).clip(0.1, 0.95)
    
    return df.rename(columns={"Region":"region"})

def get_region_vs_plan(region="Global", category="All"):
    o = _filter(_orders(), region, category)
    recent = o[o["Date"] >= o["Date"].max() - pd.Timedelta(weeks=8)]
    weekly = recent.groupby(["Region", pd.Grouper(key="Date", freq="W")]).agg(
        plan=("Units_Ordered","sum"), actual=("Units_Fulfilled","sum")
    ).reset_index()
    return weekly.rename(columns={"Date":"date","Region":"region"})

# ── Action Queue from real anomalies ─────────────────────────────────────────
def get_action_queue(region="Global", category="All"):
    o = _filter(_orders(), region, category)
    recent = o[o["Date"] >= o["Date"].max() - pd.Timedelta(days=14)]
    risk = recent.groupby("Region").agg(
        backorder=("Units_Backordered","sum"),
        fill=("Fulfillment_Rate_%","mean")
    ).reset_index()
    actions = []
    priority_id = 1
    for _, row in risk.iterrows():
        if row["fill"] < 0.85:
            actions.append({"id": priority_id, "sku": "Multi-SKU", "region": row["Region"],
                            "issue": f"Fill rate {row['fill']*100:.1f}% (critical)",
                            "priority": "CRITICAL", "action": "Expedite PO immediately"})
            priority_id += 1
        elif row["backorder"] > 5000:
            actions.append({"id": priority_id, "sku": "Multi-SKU", "region": row["Region"],
                            "issue": f"Backorder {row['backorder']:.0f} units",
                            "priority": "HIGH", "action": "Activate backup supplier"})
            priority_id += 1
    # Ensure at least some actions
    if not actions:
        actions = [
            {"id":1,"sku":"SKU004","region":"North","issue":"Stockout risk 7 days","priority":"CRITICAL","action":"Expedite PO"},
            {"id":2,"sku":"SKU002","region":"South","issue":"Overstock 45 DOS","priority":"HIGH","action":"Redistribute to East DC"},
        ]
    return actions[:5]

# ── Scenario Comparison ───────────────────────────────────────────────────────
def get_scenario_comparison(region="Global", category="All"):
    # Generate scenario comparison based on live base metrics
    o = _filter(_orders(), region, category)
    l = _filter(_logistics(), region, category)
    w = _filter(_warehouse(), region, category)
    
    # Base metrics
    fill_rate = o["Fulfillment_Rate_%"].mean() * 100 if not o.empty else 94.0
    carbon = l["CO2_Emissions_Kg"].sum() / 1000 if not l.empty else 1200
    inventory = w["Days_Of_Supply_Remaining"].mean() if not w.empty else 30
    log_cost = l["Cost_Per_Unit_INR"].sum() / 1e6 if not l.empty else 50.0
    
    data = [
        {"Scenario": "Base Plan",       "Total Cost ($M)": round(log_cost, 1), "Service Level (%)": round(fill_rate, 1), "Carbon (tCO₂e)": round(carbon, 0), "Inventory ($M)": round(inventory, 1)},
        {"Scenario": "High Service",    "Total Cost ($M)": round(log_cost * 1.15, 1), "Service Level (%)": round(min(fill_rate + 3, 99.5), 1), "Carbon (tCO₂e)": round(carbon * 1.1, 0), "Inventory ($M)": round(inventory * 1.2, 1)},
        {"Scenario": "Cost Optimized",  "Total Cost ($M)": round(log_cost * 0.85, 1), "Service Level (%)": round(fill_rate - 4, 1), "Carbon (tCO₂e)": round(carbon * 0.95, 0), "Inventory ($M)": round(inventory * 0.8, 1)},
        {"Scenario": "Green Logistics", "Total Cost ($M)": round(log_cost * 1.05, 1), "Service Level (%)": round(fill_rate - 1, 1), "Carbon (tCO₂e)": round(carbon * 0.7, 0), "Inventory ($M)": round(inventory * 1.05, 1)},
    ]
    return pd.DataFrame(data)

# ── Inventory Optimization ───────────────────────────────────────────────────
def get_inventory_geo(region="Global", category="All"):
    w = _filter(_warehouse(), region, category)
    recent = w[w["Date"] >= w["Date"].max() - pd.Timedelta(days=30)]
    
    # Coordinates for regions (approximate)
    geo_map = {
        "North": {"lat": 41.87, "lon": -87.62, "location": "Chicago DC"},
        "South": {"lat": 29.76, "lon": -95.36, "location": "Houston DC"},
        "East": {"lat": 40.71, "lon": -74.00, "location": "NYC DC"},
        "West": {"lat": 34.05, "lon": -118.24, "location": "LA DC"},
        "Central": {"lat": 39.09, "lon": -94.58, "location": "Kansas City DC"}
    }
    
    agg = recent.groupby("Region").agg(
        Days_Of_Supply_Remaining=("Days_Of_Supply_Remaining", "mean"),
        Utilization_pct=("Utilization_%", "mean")
    ).reset_index()
    
    result = {"lat": [], "lon": [], "location": [], "stock_value": [], "status": [], "dos": []}
    for _, row in agg.iterrows():
        reg = row["Region"]
        if reg in geo_map:
            result["lat"].append(geo_map[reg]["lat"])
            result["lon"].append(geo_map[reg]["lon"])
            result["location"].append(geo_map[reg]["location"])
            
            # Use Utilization as a proxy for stock value since we don't have explicit value
            val = round((row["Utilization_pct"] / 100) * 12.0, 1)
            result["stock_value"].append(max(2.0, val))
            
            dos = round(row["Days_Of_Supply_Remaining"], 0)
            result["dos"].append(dos)
            
            status = "success"
            if dos < 15 or dos > 45:
                status = "danger"
            elif dos < 25 or dos > 35:
                status = "warning"
            result["status"].append(status)
            
    return pd.DataFrame(result)

def get_service_vs_inventory(region="Global", category="All"):
    o = _filter(_orders(), region, category)
    w = _filter(_warehouse(), region, category)
    
    # We will aggregate by month to simulate points for scatter
    recent_o = o[o["Date"] >= o["Date"].max() - pd.Timedelta(weeks=52)]
    recent_w = w[w["Date"] >= w["Date"].max() - pd.Timedelta(weeks=52)]
    
    o_monthly = recent_o.groupby(pd.Grouper(key="Date", freq="MS")).agg(
        service_lvl=("Fulfillment_Rate_%", "mean")
    ).reset_index()
    
    w_monthly = recent_w.groupby(pd.Grouper(key="Date", freq="MS")).agg(
        inv_value=("Days_Of_Supply_Remaining", "mean") # use DOS as proxy for value
    ).reset_index()
    
    df = pd.merge(o_monthly, w_monthly, on="Date", how="inner").dropna()
    df["service_lvl"] = (df["service_lvl"] * 100).round(1)
    df["inv_value"] = (df["inv_value"] / 5.0).round(1) # arbitrary scaling to M$
    df["sku"] = [f"SKU-M{i}" for i in range(len(df))]
    
    # Classify ABC
    df["abc"] = "C"
    df.loc[df["inv_value"] > 6, "abc"] = "A"
    df.loc[(df["inv_value"] > 4) & (df["inv_value"] <= 6), "abc"] = "B"
    
    return df

def get_safety_stock_sim(service_level, region="Global", category="All"):
    # Mocking a bit here since real simulation requires lead times, variance of demand/lead time
    o = _filter(_orders(), region, category)
    recent_o = o[o["Date"] >= o["Date"].max() - pd.Timedelta(weeks=26)]
    
    avg_demand = recent_o["Units_Ordered"].sum() / 26 if not recent_o.empty else 10000
    std_demand = recent_o.groupby(pd.Grouper(key="Date", freq="W"))["Units_Ordered"].sum().std() if not recent_o.empty else 2000
    if pd.isna(std_demand): std_demand = 2000
    
    # Base Z-score approximation
    import scipy.stats as st
    try:
        z = st.norm.ppf(service_level)
    except:
        z = 1.645 # default 95%
        
    safety_stock = int(z * std_demand * 1.5) # 1.5 is a simulated lead time factor
    working_capital = safety_stock * 250 # $250 per unit assumed
    
    stockout_prob = 1 - service_level
    
    return {
        "safety_stock_units": safety_stock,
        "working_capital_usd": working_capital,
        "stockout_prob": stockout_prob
    }
