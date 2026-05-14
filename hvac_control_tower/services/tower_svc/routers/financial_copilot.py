from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import json
from datetime import datetime, timezone
import hashlib

from utils.complexity_classifier import classify_complexity, MODEL_ROUTING
from utils.semantic_cache import global_semantic_cache
from tools.financial_tools import get_financial_kpis, get_cost_breakdown, run_what_if_scenario, get_budget_variance

router = APIRouter()

class FinancialChatRequest(BaseModel):
    user_message: str
    conversation_history: List[dict]
    active_dashboard: str
    active_scenario: str
    user_role: str
    region_filter: str
    complexity_hint: Optional[str] = None

class FinancialChatResponse(BaseModel):
    natural_language: str
    tool_calls_made: List[str]
    data_payload: Optional[dict] = None
    chart_type: Optional[str] = None
    confidence: float
    data_freshness: str
    citations: List[str]
    model_used: str

# In-memory mock briefing cache
_briefing_cache = {}

def load_system_prompt():
    try:
        with open("prompts/financial_copilot_system.txt", "r") as f:
            return f.read()
    except:
        return "You are the Financial Copilot."

@router.post("/chat", response_model=FinancialChatResponse)
async def chat(request: FinancialChatRequest):
    kpi_snapshot_hash = "mock_hash_v1" # Mock
    cached_response = global_semantic_cache.get(request.user_message, kpi_snapshot_hash)
    if cached_response:
        cached_response["model_used"] += " (cached)"
        return FinancialChatResponse(**cached_response)

    complexity = request.complexity_hint or classify_complexity(request.user_message)
    model = MODEL_ROUTING.get(complexity, "claude-haiku-4-5-20251001")
    
    # Mock behavior simulating LLM calling tools based on user input
    tool_calls = []
    data_payload = {}
    natural_language = ""
    query_lower = request.user_message.lower()

    if "scenario" in query_lower or "surge" in query_lower:
        tool_calls.append("run_what_if_scenario")
        data_payload = run_what_if_scenario("Demand Surge +20%", {"demand_pct": 20}, ["cost", "service_level", "margin"])
        natural_language = "🔀 **Demand Surge Scenario (+20%):**\n\nI have run the simulation for a 20% demand surge across the network.\n\n*   **Estimated Cost Impact:** +$6.9M (Logistics & Expediting)\n*   **Service Level Drop:** 91.3% (from 95.0% base)\n*   **Margin Delta:** -1.2%\n\n**Recommendation:** Pre-positioning 8,500 units in DC-APAC and DC-US now can mitigate the service level drop back to 94.1% with only a $2.1M holding cost increase."
    elif "eva" in query_lower or "roic" in query_lower:
        tool_calls.append("get_financial_kpis")
        data_payload = get_financial_kpis(["EVA", "ROIC"], region=request.region_filter)
        natural_language = f"Here is the analysis for EVA and ROIC:\n\n*   **EVA**: {data_payload['EVA']['value']} {data_payload['EVA']['unit']} (Target: {data_payload['EVA']['vs_target']})\n*   **ROIC**: {data_payload['ROIC']['value']}% (Prior: {data_payload['ROIC']['vs_prior_period']})\n\nOverall, value creation is stable, but ROIC requires optimization in the APAC region."
    elif "cost" in query_lower or "margin" in query_lower:
        tool_calls.append("get_cost_breakdown")
        data_payload = get_cost_breakdown(region=request.region_filter)
        natural_language = f"The cost breakdown reveals that **Logistics** accounts for ${data_payload['logistics']['value_usd']:,.0f} and **Manufacturing** accounts for ${data_payload['manufacturing']['value_usd']:,.0f}. Logistics is slightly over budget compared to the prior period."
    elif "stockout" in query_lower or "shortage" in query_lower:
        tool_calls.append("get_budget_variance")
        natural_language = "⚠️ **Critical Stockout Risk:**\n\nSKU-047 at DC-APAC currently has 12 Days of Supply, which is 3.2× below the safety stock target.\n\n**Action Required:** Expediting PO-4821 (5,000 units) will resolve this shortage within 8 days. The estimated cost of a stockout if unresolved is **$280K**."
    elif "forecast" in query_lower or "accuracy" in query_lower:
        natural_language = "📈 **Forecast Accuracy:**\n\nPortfolio WAPE has improved by 1.8 percentage points month-over-month to 14.1%.\nHowever, planner overrides on the SKU-112 category degraded WAPE by 3.2pp. I recommend reverting to the baseline ML forecast for this category."
    else:
        natural_language = f"I've analyzed your request: '{request.user_message}'. Currently, the metrics are stable. Let me know if you want to run a specific scenario or check a particular KPI like EVA or Inventory Turns."

    response_data = {
        "natural_language": natural_language,
        "tool_calls_made": tool_calls,
        "data_payload": data_payload,
        "chart_type": "bar" if data_payload else None,
        "confidence": 0.92,
        "data_freshness": datetime.now(timezone.utc).isoformat(),
        "citations": ["fact_financial (mock)"],
        "model_used": model
    }
    
    global_semantic_cache.set(request.user_message, kpi_snapshot_hash, response_data)
    return FinancialChatResponse(**response_data)


@router.get("/briefing")
async def get_financial_briefing(role: str, region: str = "All"):
    cache_key = f"{role}_{region}"
    cached = _briefing_cache.get(cache_key)
    if cached and cached["generated_at"] >= datetime.now(timezone.utc).replace(hour=0, minute=0, second=0):
        return {"source": "cache", **cached["briefing_json"]}
    
    # Generate live (mock)
    briefing = {
        "summary": "Daily financial briefing looks stable. Logistics costs are within budget.",
        "key_metrics": get_financial_kpis(["EVA", "ROIC"], region=region)
    }
    _briefing_cache[cache_key] = {
        "briefing_json": briefing,
        "generated_at": datetime.now(timezone.utc)
    }
    return {"source": "live", **briefing}


@router.post("/what-if")
async def what_if_query(request: dict):
    # Mock what-if response
    return {"status": "success", "results": "Scenario analyzed."}
