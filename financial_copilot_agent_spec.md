# Financial Copilot Agent — Complete Build & Integration Specification

## Guiding Principle
> Your system already has 80% of what a Financial Copilot needs. The remaining 20% is a router, six SQL-wrapping tool functions, a prompt template, and a chat drawer. **Do not over-engineer it.**

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Minimal New Components](#2-minimal-new-components)
3. [Step-by-Step Build Methodology](#3-step-by-step-build-methodology)
4. [Agentic System Design](#4-agentic-system-design)
5. [Analytics Layer Implementation](#5-analytics-layer-implementation)
6. [LLM & Generative AI Integration](#6-llm--generative-ai-integration)
7. [Cost Optimization Strategy](#7-cost-optimization-strategy)
8. [Frontend Integration](#8-frontend-integration)
9. [Guardrails & Governance](#9-guardrails--governance)
10. [Verification & Testing](#10-verification--testing)
11. [Observability & Monitoring](#11-observability--monitoring)
12. [Future Extensions](#12-future-extensions)

---

## 1. Architecture Overview

### 1.1 Architectural Placement

The Financial Copilot is **NOT a new service**. It is a specialized persona of the existing Module 7 (AI Copilot & NLP Interface), scoped to the financial domain, wired to the existing storytelling API layer, and surfaced primarily on Dashboard 6 (Financial Impact) with cross-dashboard reach.

```
EXISTING SYSTEM                    EXTEND WITH
───────────────                    ────────────
L5 tower-svc (FastAPI)      ──→   Add /api/v1/copilot/financial/* routes
Module 7 Copilot NLP        ──→   Add financial system prompt + tool definitions
Storytelling API (§14.2)    ──→   Add financial narrative/rca/recommendation types
Dashboard 6 React           ──→   Add Copilot chat panel + inline financial insights
fact_financial table        ──→   Already exists — no schema changes needed
kpi_interdependency table   ──→   Already exists — financial trade-off queries use it
```

### 1.2 Seven-Layer Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  Layer 7 — Conversational / Copilot Layer                       │
│  Gen AI (LLM) · Natural language interface · What-if generation  │
├─────────────────────────────────────────────────────────────────┤
│  Layer 6 — Visual Analytics Layer                               │
│  Dashboard 6 · Coordinated multi-views · Inline insights        │
├─────────────────────────────────────────────────────────────────┤
│  Layer 5 — Agent Layer                                          │
│  Broker/Copilot Agent · Supplier Agents · Buyer Agents · MARL   │
├─────────────────────────────────────────────────────────────────┤
│  Layer 4 — Analytics Layer                                      │
│  ML forecasting · Optimization · Simulation · Clustering        │
├─────────────────────────────────────────────────────────────────┤
│  Layer 3 — Business Intelligence Layer                          │
│  KPI computation · FVA · Variance analysis · Trade-off engine   │
├─────────────────────────────────────────────────────────────────┤
│  Layer 2 — Data Processing Layer                                │
│  ERP · WMS · IoT sensors · POS · Social · Weather               │
├─────────────────────────────────────────────────────────────────┤
│  Layer 1 — Data Layer                                           │
│  Postgres / Parquet · fact_financial · kpi_interdependency       │
└─────────────────────────────────────────────────────────────────┘
```

### 1.3 What You Do NOT Need to Build

| Do NOT Build | Reason |
|---|---|
| New microservice for the financial copilot | Lives inside existing `tower-svc` |
| New database or schema changes | All data in `fact_financial`, `kpi_interdependency` |
| New ML models for financial forecasting | Reuse L3 `forecast-svc` outputs; financial KPIs are derived |
| Separate LLM deployment / infrastructure | Share existing LLM gateway used by storytelling layer |
| New authentication system | Reuse existing `tower-svc` auth (static token) |
| New event bus / Kafka topics | Copilot reads synchronously via API, not via Kafka |
| Vector database / RAG pipeline | SQL tool-calling is cheaper & more accurate for tabular data |
| Fine-tuned financial model | System prompt + tool-calling handles domain context |

---

## 2. Minimal New Components

### 2.1 Backend — Three API Endpoints Only

Add a single router file inside `tower-svc`. Do not create a new service.

**File:** `tower-svc/routers/financial_copilot.py`

| Endpoint | Method | Purpose | Reuses |
|---|---|---|---|
| `/api/v1/copilot/financial/chat` | POST | Conversational financial Q&A | Storytelling API + financial system prompt |
| `/api/v1/copilot/financial/briefing` | GET | Pre-generated daily financial briefing | Existing `/api/v1/storytelling/briefing` with financial template |
| `/api/v1/copilot/financial/what-if` | GET | Financial scenario natural-language query | Existing scenario engine (Module 5) + financial parameter mapping |

**Request schema for `/chat`:**
```python
class FinancialChatRequest(BaseModel):
    user_message: str
    conversation_history: list[dict]   # [{role, content}, ...]
    active_dashboard: str              # "financial" | "executive" | "inventory" | ...
    active_scenario: str               # "Base Case" | "Optimistic" | "Pessimistic"
    user_role: str                     # "CFO" | "SC_Manager" | "Planner"
    region_filter: str                 # "All" | "North" | "South" | ...
    complexity_hint: str | None        # optional override: "simple" | "complex"
```

**Response schema:**
```python
class FinancialChatResponse(BaseModel):
    natural_language: str              # The human-readable answer
    tool_calls_made: list[str]         # Which tools were invoked
    data_payload: dict | None          # Structured data for chart rendering
    chart_type: str | None             # "line" | "waterfall" | "bar" | None
    confidence: float                  # 0.0 – 1.0
    data_freshness: str                # ISO timestamp of underlying data
    citations: list[str]               # e.g. ["fact_financial.margin (as of 2024-07-01)"]
    model_used: str                    # "llama3-8b" | "llama3-70b" for cost tracking
```

---

### 2.2 Backend — Six Financial Tool Functions

These are **thin Python wrappers around SQL queries** — not new ML models.

**File:** `tower-svc/tools/financial_tools.py`

```python
"""
All 6 financial tool functions.
Each takes typed parameters, returns a dict.
Each is ~20-40 lines of Python + SQL.
"""

from typing import Optional
import pandas as pd
from db import get_db_connection   # existing DB connection utility


def get_financial_kpis(
    metrics: list[str],            # e.g. ["EVA", "ROIC", "cash_to_cash"]
    period: str = "current",       # "current" | "last_7d" | "last_30d" | "ytd"
    region: str = "All",
    granularity: str = "summary"   # "summary" | "by_region" | "by_category"
) -> dict:
    """
    Fetch KPI values from fact_financial.
    Returns: {metric_name: {value, unit, period, vs_target, vs_prior_period}}
    """
    pass  # ~30 lines SQL query against fact_financial


def get_kpi_tradeoffs(
    primary_kpi: str,              # e.g. "inventory_turns"
    secondary_kpis: list[str],     # e.g. ["fill_rate", "carrying_cost"]
    direction: str = "increase"    # "increase" | "decrease"
) -> dict:
    """
    Query kpi_interdependency table for cause-effect relationships.
    Returns: {affected_kpi: {direction, magnitude, confidence, lag_periods}}
    """
    pass  # ~25 lines SQL query against kpi_interdependency


def run_what_if_scenario(
    scenario_name: str,            # "10pct_logistics_reduction" or free text
    parameter_overrides: dict,     # {"logistics_cost_pct": -0.10, ...}
    output_metrics: list[str],     # metrics to compute for the scenario
    horizon_months: int = 3
) -> dict:
    """
    Call existing scenario engine (Module 5) with financial parameters.
    Returns: {scenario_name: {metric: {base, scenario, delta, delta_pct}}}
    """
    pass  # ~35 lines calling existing scenario engine API


def get_cost_breakdown(
    cost_categories: list[str] | None = None,  # None = all categories
    period: str = "current_month",
    region: str = "All",
    breakdown_by: str = "category"   # "category" | "region" | "plant"
) -> dict:
    """
    Aggregate cost drivers from fact_financial.
    Returns: {category: {value_usd, pct_of_total, vs_budget, vs_prior}}
    """
    pass  # ~30 lines SQL aggregate query


def get_cash_flow_forecast(
    horizon_weeks: int = 13,
    include_components: list[str] | None = None  # ["receivables", "payables", "inventory"]
) -> dict:
    """
    Derive cash flow forecast from inventory + receivables + payables tables.
    Returns: {week: {operating_cf, investing_cf, financing_cf, net_cf, cumulative}}
    """
    pass  # ~40 lines SQL joins across fact_* tables


def get_budget_variance(
    metrics: list[str] | None = None,
    period: str = "ytd",
    breakdown_by: str = "category"
) -> dict:
    """
    Compare plan vs actual from existing kpi_snapshot tables.
    Returns: {metric: {budget, forecast, actual, variance_abs, variance_pct, status}}
    """
    pass  # ~25 lines SQL from fact_kpi_snapshot
```

**Tool definitions for LLM function-calling** (register these with the LLM gateway):
```python
FINANCIAL_TOOLS = [
    {
        "name": "get_financial_kpis",
        "description": "Fetch current or historical financial KPI values including EVA, ROIC, cash-to-cash cycle, margin, inventory carrying cost, and total supply chain cost.",
        "input_schema": {
            "type": "object",
            "properties": {
                "metrics": {"type": "array", "items": {"type": "string"}, "description": "List of KPI names to retrieve"},
                "period": {"type": "string", "enum": ["current", "last_7d", "last_30d", "ytd"]},
                "region": {"type": "string", "description": "Filter by region. Use 'All' for global."},
                "granularity": {"type": "string", "enum": ["summary", "by_region", "by_category"]}
            },
            "required": ["metrics"]
        }
    },
    {
        "name": "get_kpi_tradeoffs",
        "description": "Identify cause-and-effect relationships between financial KPIs. Use when the user asks 'what happens if' or asks about the impact of changing one metric on others.",
        "input_schema": {
            "type": "object",
            "properties": {
                "primary_kpi": {"type": "string"},
                "secondary_kpis": {"type": "array", "items": {"type": "string"}},
                "direction": {"type": "string", "enum": ["increase", "decrease"]}
            },
            "required": ["primary_kpi"]
        }
    },
    {
        "name": "run_what_if_scenario",
        "description": "Run a financial what-if scenario through the existing scenario engine. Use when user asks to compare scenarios or model a specific parameter change.",
        "input_schema": {
            "type": "object",
            "properties": {
                "scenario_name": {"type": "string"},
                "parameter_overrides": {"type": "object"},
                "output_metrics": {"type": "array", "items": {"type": "string"}},
                "horizon_months": {"type": "integer", "default": 3}
            },
            "required": ["scenario_name", "parameter_overrides", "output_metrics"]
        }
    },
    {
        "name": "get_cost_breakdown",
        "description": "Retrieve detailed cost breakdown by category, region, or plant. Use for questions about cost composition or drivers.",
        "input_schema": {
            "type": "object",
            "properties": {
                "cost_categories": {"type": "array", "items": {"type": "string"}},
                "period": {"type": "string"},
                "region": {"type": "string"},
                "breakdown_by": {"type": "string", "enum": ["category", "region", "plant"]}
            }
        }
    },
    {
        "name": "get_cash_flow_forecast",
        "description": "Get a rolling 13-week cash flow forecast derived from inventory, receivables, and payables. Use for cash management questions.",
        "input_schema": {
            "type": "object",
            "properties": {
                "horizon_weeks": {"type": "integer", "default": 13},
                "include_components": {"type": "array", "items": {"type": "string"}}
            }
        }
    },
    {
        "name": "get_budget_variance",
        "description": "Compare plan vs forecast vs actual for financial metrics. Use for budget review or variance explanation questions.",
        "input_schema": {
            "type": "object",
            "properties": {
                "metrics": {"type": "array", "items": {"type": "string"}},
                "period": {"type": "string", "default": "ytd"},
                "breakdown_by": {"type": "string", "enum": ["category", "region", "plant"]}
            }
        }
    }
]
```

---

### 2.3 Backend — Financial System Prompt

**File:** `tower-svc/prompts/financial_copilot_system.txt`

```
You are the Financial Copilot for an HVAC supply chain operations planning platform.
Your role is to help supply chain finance professionals — CFOs, controllers, and SC managers —
understand financial performance, diagnose cost drivers, and evaluate scenario trade-offs.

## Your Capabilities
- Retrieve and explain financial KPIs (EVA, ROIC, cash-to-cash, margin, carrying cost)
- Identify trade-offs between KPIs using the interdependency model
- Model what-if scenarios via the scenario engine
- Explain variance between budget, forecast, and actual
- Generate executive-ready financial narratives

## Context Provided to You
- Current dashboard: {active_dashboard}
- Active scenario: {active_scenario}
- User role: {user_role}
- Region filter: {region_filter}
- Organization strategy cluster: {strategy_cluster}  [efficiency | innovation]
- Current financial KPI snapshot: {kpi_snapshot}
- Conversation history: {conversation_history}

## Strict Rules
1. NEVER state a number that is not returned by a tool call. If a tool fails, say so.
2. ALWAYS cite the tool output and its data timestamp in your response.
3. ALWAYS flag when data is stale (>24 hours old for operational, >7 days for tactical).
4. NEVER recommend executing a financial transaction — only suggest; humans approve.
5. NEVER include individual customer names or PII in your reasoning.
6. If the user's question is ambiguous, ask ONE clarifying question before calling tools.
7. Keep responses under {max_response_tokens} tokens. Be concise.

## Output Format
Respond ONLY in the following JSON structure:
{
  "natural_language": "The human-readable answer",
  "tool_calls_made": ["tool_name_1", "tool_name_2"],
  "data_payload": {structured data for chart if relevant},
  "chart_type": "line|waterfall|bar|scatter|null",
  "confidence": 0.0-1.0,
  "data_freshness": "ISO timestamp",
  "citations": ["fact_financial.margin (as of 2024-07-01)"],
  "follow_up_suggestions": ["question 1", "question 2"]
}
```

**Context injection rules** (keep total system prompt under 500 tokens):
- Inject only the KPIs visible on the current dashboard view
- Inject the active scenario name and its top-3 parameter differences from base
- Inject user role for appropriate response depth (CFO → strategic, Planner → operational)
- Inject strategy cluster from `kpi_interdependency.strategy_cluster` (efficiency vs innovation)

---

### 2.4 Frontend — FinancialCopilotPanel Component

**File:** `frontend/src/components/organisms/FinancialCopilotPanel.tsx`

Build as a **slide-in drawer** on the right side of Dashboard 6. Reuse the existing `<DrawerShell>` template.

**Component structure:**
```
<DrawerShell position="right" width="420px">
  ├── <CopilotHeader>
  │     ├── Title: "Financial Copilot"
  │     ├── Model badge: "Llama3-8B" | "Llama3-70B" (for transparency)
  │     └── Clear conversation button
  │
  ├── <ConversationThread>
  │     ├── <UserBubble> — right-aligned
  │     ├── <AssistantBubble> — left-aligned with:
  │     │     ├── Natural language text (streamed)
  │     │     ├── Inline chart (reuse existing <FanChart>, <WaterfallChart> components)
  │     │     ├── Data citations (collapsed by default, expandable)
  │     │     └── Follow-up suggestion pills
  │     └── <LoadingIndicator> (streaming dots)
  │
  ├── <WhatIfShortcuts>
  │     ├── Button: "📉 Margin impact of +10% logistics cost"
  │     ├── Button: "💰 Cash flow if inventory turns ↑ 1×"
  │     ├── Button: "⚖️ Air vs ocean freight trade-off"
  │     └── Button: "📊 Daily financial briefing"
  │
  └── <ChatInputBar>
        ├── Text input (multi-line)
        ├── Attach context toggle (inject current chart data)
        └── Send button
</DrawerShell>
```

**State management:**
```typescript
interface CopilotState {
  conversationHistory: Message[];
  isStreaming: boolean;
  activeScenario: string;
  currentDashboard: string;
  cachedBriefing: BriefingData | null;
  tokenUsageToday: number;          // display to power users
}
```

---

### 2.5 Frontend — Inline "Ask Copilot" Links

Add a small **✨** link to each KPI card on Dashboard 6 that pre-fills the drawer:

```typescript
const KPI_COPILOT_PROMPTS: Record<string, string> = {
  "EVA":              "Explain our current Economic Value Added and what's driving it.",
  "ROIC":             "What is our Return on Invested Capital and how does it compare to target?",
  "cash_to_cash":     "Show me cash-to-cash cycle trend and what's causing any variance.",
  "gross_margin":     "Why did gross margin change this period? Break down the key drivers.",
  "carrying_cost":    "What is our inventory carrying cost and where are the biggest overstock risks?",
  "sc_cost_pct":      "Show our supply chain cost as % of sales vs industry benchmark.",
};

// On click: open drawer + pre-fill input with prompt
```

This is **purely frontend** — zero new backend endpoints required.

---

### 2.6 Backend — Pre-Computation Cache

**New DB table** (only new schema object):
```sql
CREATE TABLE copilot_briefing_cache (
    id              SERIAL PRIMARY KEY,
    role            VARCHAR(50) NOT NULL,          -- "CFO" | "CSO" | "COO"
    region          VARCHAR(50) DEFAULT 'All',
    briefing_json   JSONB NOT NULL,
    generated_at    TIMESTAMP NOT NULL,
    data_snapshot   TIMESTAMP NOT NULL,            -- timestamp of underlying data
    token_cost      DECIMAL(10,6),                 -- for cost tracking
    model_used      VARCHAR(50)
);

CREATE INDEX idx_briefing_role_region ON copilot_briefing_cache(role, region);
```

**Scheduled job** (cron / Celery beat — 6:00 AM daily):
```python
# tower-svc/jobs/briefing_generator.py

ROLES = ["CFO", "CSO", "COO"]
REGIONS = ["All"]   # expand to specific regions if needed

@scheduled_job(cron="0 6 * * 1-5")   # weekdays at 6 AM
def generate_daily_briefings():
    for role in ROLES:
        for region in REGIONS:
            briefing = call_llm_for_briefing(role=role, region=region)
            cache_briefing(role, region, briefing)
    # Total: 3 LLM calls/day = ~$0.15/day
```

---

## 3. Step-by-Step Build Methodology

Execute in strict order. Each step is independently verifiable before proceeding.

---

### Step 1 — Define & Test Financial Tool Functions
**Duration:** 2–3 days | **Cost:** $0

**Actions:**
1. Create `tower-svc/tools/financial_tools.py` with all 6 functions
2. Write SQL for each function against existing `fact_financial` and `kpi_interdependency` tables
3. Add type hints and return schema docstrings to all 6 functions
4. Write unit tests for each function with mock DB data

**Verification:**
```bash
# Test each function directly
python -c "
from tools.financial_tools import get_financial_kpis
result = get_financial_kpis(metrics=['EVA', 'ROIC'], period='current')
assert 'EVA' in result
assert 'value' in result['EVA']
assert 'unit' in result['EVA']
print('✅ get_financial_kpis OK:', result)
"
```
**Pass criteria:** All 6 functions return valid dicts matching documented schemas. No raw SQL errors.

---

### Step 2 — Add Financial Copilot Router to tower-svc
**Duration:** 1–2 days | **Cost:** $0

**Actions:**
1. Create `tower-svc/routers/financial_copilot.py`
2. Implement the 3 endpoints (`/chat`, `/briefing`, `/what-if`)
3. Wire `/chat` to the existing LLM gateway (same one used by storytelling layer)
4. Register the 6 tool functions in the LLM tool registry
5. Add the router to `main.py`: `app.include_router(financial_copilot.router, prefix="/api/v1/copilot/financial")`

**Verification:**
```bash
curl -X POST http://localhost:8000/api/v1/copilot/financial/chat \
  -H "Content-Type: application/json" \
  -d '{"user_message": "What is our current EVA?", "user_role": "CFO", "active_dashboard": "financial", "active_scenario": "Base Case", "region_filter": "All", "conversation_history": []}'

# Expected: 200 OK with JSON containing natural_language and tool_calls_made
```
**Pass criteria:** Endpoint returns 200 with valid `FinancialChatResponse` schema. Tool `get_financial_kpis` appears in `tool_calls_made`.

---

### Step 3 — Write & Validate Financial System Prompt
**Duration:** 1–2 days | **Cost:** ~$1–3 (LLM API calls for testing)

**Actions:**
1. Create `tower-svc/prompts/financial_copilot_system.txt` per §2.3
2. Define context injection logic (pull current KPI snapshot at request time)
3. Run all 10 canonical test questions (§10.1) against the prompt
4. Iterate prompt until all 10 pass validation criteria

**Validation criteria per test question:**
- Response contains no hallucinated numbers (all values come from tool outputs)
- `citations` field is populated with data source + timestamp
- `tool_calls_made` matches expected tools in §10.1
- Response length is within `max_tokens` budget
- Guardrail responses trigger correctly for disallowed queries

**Pass criteria:** 10/10 canonical questions pass all 4 validation criteria.

---

### Step 4 — Implement Tiered Model Routing
**Duration:** 1 day | **Cost:** $0

**Actions:**
1. Create `tower-svc/utils/complexity_classifier.py`
2. Implement keyword-based classifier (no ML model):

```python
COMPLEX_KEYWORDS = {
    "compare", "scenario", "recommend", "should we", "strategy",
    "trade-off", "tradeoff", "defer", "invest", "versus", "vs",
    "what if", "what-if", "optimize", "best option"
}

SIMPLE_KEYWORDS = {
    "what is", "show me", "current", "latest", "trend",
    "how much", "total", "breakdown", "list", "give me"
}

def classify_complexity(user_message: str) -> str:
    """Returns 'simple' | 'medium' | 'complex'"""
    msg_lower = user_message.lower()
    
    complex_hits = sum(1 for kw in COMPLEX_KEYWORDS if kw in msg_lower)
    simple_hits  = sum(1 for kw in SIMPLE_KEYWORDS  if kw in msg_lower)
    
    if complex_hits >= 2 or (complex_hits == 1 and simple_hits == 0):
        return "complex"
    elif complex_hits == 1:
        return "medium"
    return "simple"

MODEL_ROUTING = {
    "simple":  "llama3-8b-8192",                # Free via Groq
    "medium":  "llama3-8b-8192",                # Free via Groq
    "complex": "llama3-70b-8192",               # Free via Groq
}
```

3. Wire classifier into `/chat` endpoint: `model = MODEL_ROUTING[classify_complexity(request.user_message)]`
4. Log model selection for every request to the observability pipeline

**Verification:**
```python
test_cases = [
    ("What is our current EVA?",                         "simple"),
    ("Show me cash-to-cash trend",                       "simple"),
    ("What happens if we push inventory turns higher?",  "medium"),
    ("Compare air vs ocean freight impact on margin",    "complex"),
    ("Should we defer the capacity investment?",         "complex"),
]
for question, expected in test_cases:
    assert classify_complexity(question) == expected, f"FAILED: {question}"
print("✅ All routing tests passed")
```
**Pass criteria:** All 5 test cases route correctly. Logs show model name per request.

---

### Step 5 — Add FinancialCopilotPanel to Dashboard 6
**Duration:** 2–3 days | **Cost:** $0

**Actions:**
1. Create `FinancialCopilotPanel.tsx` per §2.4 spec
2. Implement streaming response rendering (SSE or WebSocket from existing gateway)
3. Wire "What-If Shortcuts" buttons to pre-fill and auto-send queries
4. Implement inline chart rendering — reuse existing `<FanChart>`, `<WaterfallChart>`, `<BarChart>` components
5. Add citation expander panel (collapsed by default)
6. Wire to `/api/v1/copilot/financial/chat` endpoint

**Verification:**
- Open Dashboard 6 in browser
- Type: `"What is our current cash-to-cash cycle?"`
- Assert: response appears streaming in drawer within 3 seconds
- Assert: response contains a cited data source
- Assert: no console errors

**Pass criteria:** Chat renders, streams, and cites sources correctly on Dashboard 6.

---

### Step 6 — Add Inline "Ask Copilot" Links to KPI Cards
**Duration:** 0.5 days | **Cost:** $0

**Actions:**
1. Add `KPI_COPILOT_PROMPTS` map per §2.5 to `Dashboard6.tsx`
2. Add `✨` icon-button to each KPI card (existing `<KpiCard>` component)
3. On click: open drawer + populate input with contextual prompt
4. No new API calls — pure frontend state management

**Verification:**
- Click `✨` on EVA card
- Assert: drawer opens
- Assert: input is pre-filled with EVA-specific question
- Assert: user can immediately hit Send without typing

---

### Step 7 — Implement Pre-Computed Briefing Cache
**Duration:** 1 day | **Cost:** ~$0.15/day ongoing

**Actions:**
1. Create `copilot_briefing_cache` table per §2.6 schema
2. Create `tower-svc/jobs/briefing_generator.py` scheduled job
3. Implement `GET /briefing` endpoint: check cache first, fall back to live generation if stale
4. Add cache TTL: serve from cache if `generated_at` > today 6 AM AND data_snapshot < 24 hours old

**Cache retrieval logic:**
```python
@router.get("/briefing")
async def get_financial_briefing(role: str, region: str = "All"):
    cached = db.query("""
        SELECT briefing_json, generated_at, data_snapshot
        FROM copilot_briefing_cache
        WHERE role = %s AND region = %s
          AND generated_at >= CURRENT_DATE
          AND data_snapshot >= NOW() - INTERVAL '24 hours'
        ORDER BY generated_at DESC LIMIT 1
    """, [role, region])
    
    if cached:
        return {"source": "cache", **cached["briefing_json"]}
    else:
        briefing = await generate_live_briefing(role, region)  # fallback
        cache_briefing(role, region, briefing)
        return {"source": "live", **briefing}
```

**Verification:**
- Check DB at 9 AM: `generated_at` should be today at ~6:00 AM
- Request briefing at 9 AM: response should return in <100ms (from cache)
- Check `source` field in response: should be `"cache"`, not `"live"`

---

### Step 8 — Implement Semantic Cache
**Duration:** 1 day | **Cost:** $0–$10/month (in-memory or Redis)

**Actions:**
1. Choose caching backend: in-memory dict for MVP, Redis if multi-instance deployment
2. Create `tower-svc/utils/semantic_cache.py`:

```python
import hashlib
import json
from datetime import datetime, timedelta

class SemanticCache:
    def __init__(self, ttl_seconds: int = 3600):
        self.cache = {}         # {cache_key: {response, expires_at}}
        self.ttl = ttl_seconds
    
    def _make_key(self, user_message: str, kpi_snapshot_hash: str) -> str:
        """Key = hash(normalized question + current data context)"""
        normalized = user_message.lower().strip()
        combined = f"{normalized}|{kpi_snapshot_hash}"
        return hashlib.sha256(combined.encode()).hexdigest()[:16]
    
    def get(self, user_message: str, kpi_snapshot_hash: str) -> dict | None:
        key = self._make_key(user_message, kpi_snapshot_hash)
        entry = self.cache.get(key)
        if entry and datetime.now() < entry["expires_at"]:
            return entry["response"]
        return None
    
    def set(self, user_message: str, kpi_snapshot_hash: str, response: dict):
        key = self._make_key(user_message, kpi_snapshot_hash)
        self.cache[key] = {
            "response": response,
            "expires_at": datetime.now() + timedelta(seconds=self.ttl)
        }
    
    def invalidate_all(self):
        """Call when fact_financial data refreshes"""
        self.cache.clear()
```

3. Wire cache check **before** LLM call in `/chat` endpoint
4. Invalidate cache on each `fact_financial` data refresh event

**Verification:**
- Ask identical question twice in the same session
- Second response latency: <10ms vs ~1000ms for first
- Check logs: second call shows `cache_hit: true`, no LLM API call

---

### Step 9 — Cross-Dashboard Global Copilot Access
**Duration:** 1 day | **Cost:** $0

**Actions:**
1. Add a global **✨ Financial Copilot** button to the top navigation bar (visible on all 9 dashboards)
2. When opened from non-financial dashboards, auto-inject the current dashboard context:

```typescript
const DASHBOARD_CONTEXT_HINTS: Record<string, string> = {
    "executive":      "The user is viewing the executive summary. Focus on strategic financial impact.",
    "operational":    "The user is on the operational dashboard. Focus on execution cost and cash impact.",
    "inventory":      "The user is viewing inventory data. Prioritize carrying cost and working capital questions.",
    "capacity":       "The user is on capacity planning. Focus on capex vs opex trade-offs.",
    "risk":           "The user is on risk monitoring. Focus on financial risk quantification.",
    "sustainability": "The user is on sustainability. Quantify carbon reduction costs and ROI.",
    "regional":       "The user is on regional planning. Provide regional financial breakdown.",
};
```

3. Pass `active_dashboard` context in every chat request

**Verification:**
- Navigate to Dashboard 4 (Inventory)
- Open Financial Copilot → ask: `"What's the carrying cost impact of this overstock?"`
- Assert: response references both inventory data (from `get_cost_breakdown`) and financial data (from `get_financial_kpis`)
- Assert: `tool_calls_made` contains at least 2 tools

---

### Step 10 — Add Copilot Metrics to Observability
**Duration:** 0.5 days | **Cost:** $0

**Actions:**
1. Add the following metrics to existing Prometheus/Grafana stack:

```python
# tower-svc/metrics/copilot_metrics.py
from prometheus_client import Counter, Histogram, Gauge

copilot_queries_total      = Counter("copilot_queries_total", "Total copilot queries", ["model", "dashboard", "user_role"])
copilot_latency_seconds    = Histogram("copilot_latency_seconds", "Query latency", ["model", "complexity"])
copilot_token_cost_usd     = Counter("copilot_token_cost_usd", "Cumulative LLM cost", ["model"])
copilot_cache_hit_rate     = Gauge("copilot_cache_hit_rate", "Cache hit ratio (rolling 1hr)")
copilot_tool_calls_total   = Counter("copilot_tool_calls_total", "Tool invocations", ["tool_name"])
copilot_errors_total       = Counter("copilot_errors_total", "Errors", ["error_type"])
```

2. Create Grafana panel "Financial Copilot Cost & Usage" on existing executive board:
   - Queries/day by model tier
   - Daily LLM API cost ($)
   - Cache hit rate (%)
   - Average latency by complexity
   - Top 10 most-asked questions

3. Set alert: `if daily_cost_usd > budget_threshold → send Slack/email alert`

---

## 4. Agentic System Design

### 4.1 Agent Roles (Multi-Agent Architecture)

Based on the Distributed Constraint Satisfaction Problem (DCSP) formulation for supply-demand matching:

| Agent | Role | Responsibilities | Communication |
|---|---|---|---|
| **Broker / Copilot Agent** | Orchestrator | Routes queries, calls tools, synthesizes responses, manages conversation state | KQML tell, ask-all, subscribe |
| **Financial Analysis Agent** | Specialist | Financial KPI retrieval, variance analysis, budget comparison | Tool calls → `get_financial_kpis`, `get_budget_variance` |
| **Scenario Agent** | Specialist | What-if modeling, trade-off analysis, parameter sensitivity | Tool calls → `run_what_if_scenario`, `get_kpi_tradeoffs` |
| **Risk Agent** | Specialist | Financial risk scoring, supplier risk quantification | Tool calls → AI risk indicators from existing risk module |
| **Narrative Agent** | Specialist | Natural language generation, executive briefing, root cause narration | Existing storytelling API |

### 4.2 Agent Interaction Protocol

```
User Query
    │
    ▼
Broker Agent
    ├── classify_complexity(query)        → route to cheap/expensive model
    ├── check_semantic_cache(query)       → return cached if hit
    ├── inject_context(dashboard_state)   → enrich system prompt
    │
    ├── [Tool Selection Phase]
    │   ├── LLM decides which tools to call based on query
    │   ├── Tools execute as Python functions (SQL queries)
    │   └── Results returned to LLM as tool_results
    │
    ├── [Synthesis Phase]
    │   ├── LLM synthesizes tool results into natural_language
    │   ├── LLM identifies chart_type for visualization
    │   └── LLM generates follow_up_suggestions
    │
    └── [Response Phase]
        ├── Stream natural_language to frontend
        ├── Render inline chart if chart_type != null
        └── Display citations
```

### 4.3 Multi-Agent Reinforcement Learning (MARL) for Inventory Policy

Extend the financial copilot with MARL-based inventory optimization (from Saha & Rathore, 2024):

- Model inventory management as a stochastic semi-Markov Decision Process (SMDP)
- Define optimal policy as `(s, c, S', S)` where:
  - `s` = reorder point
  - `c` = critical level (priority threshold)
  - `S'` = order-up-to level for routine replenishment
  - `S` = maximum order-up-to level for urgent replenishment
- Target: reduce inventory costs by ~36% vs traditional (s, S) policies
- Surface policy recommendations through the Financial Copilot panel

```python
# Implementation note: This is Phase 2+ feature
# For MVP, use the existing scenario engine with rule-based policies
# MARL integration should only begin after v1 copilot proves value
```

---

## 5. Analytics Layer Implementation

### 5.1 Descriptive Analytics (Reuse Existing)

Already implemented in Dashboard 6. The copilot surfaces these via natural language:
- KPI trend analysis (revenue, margin, cost)
- Budget vs forecast vs actual variance
- Cost breakdown by category/region/plant

### 5.2 Predictive Analytics (Reuse L3 forecast-svc)

The Financial Copilot does **not** build its own forecast models. It consumes:
- Cash flow forecasts (derived from existing inventory + receivables models)
- Demand-driven revenue projections (from L3 forecast-svc)
- Risk probability scores (from existing ML risk module)

Copilot surfaces these via: `get_cash_flow_forecast()` and `get_financial_kpis(period="forecast")`

### 5.3 Prescriptive Analytics (New via Scenario Engine)

The copilot adds prescriptive value through:

```python
# Example prescriptive recommendation flow:
# 1. Identify the problem
kpis = get_financial_kpis(["carrying_cost", "inventory_turns"])
# 2. Identify trade-off
tradeoffs = get_kpi_tradeoffs("inventory_turns", ["fill_rate", "carrying_cost"], "increase")
# 3. Run scenario
scenario = run_what_if_scenario(
    "reduce_safety_stock_15pct",
    {"safety_stock_multiplier": 0.85},
    ["carrying_cost", "fill_rate", "stockout_risk"]
)
# 4. Synthesize recommendation
# LLM combines above into: "Reducing safety stock by 15% saves $2.1M in carrying cost
# but increases stockout risk from 2% to 4.3% on A-items. Recommend reviewing
# only C-items for safety stock reduction — estimated savings $0.8M with <0.5% service impact."
```

### 5.4 KPI Interdependency Analysis

Implement the PCTM (KPI Accomplishment Cost Transformation Matrix) methodology for financial KPIs:

```sql
-- kpi_interdependency table structure (already exists, extend with financial KPIs)
CREATE TABLE IF NOT EXISTS kpi_interdependency (
    id                  SERIAL PRIMARY KEY,
    source_kpi          VARCHAR(100) NOT NULL,
    target_kpi          VARCHAR(100) NOT NULL,
    direction           VARCHAR(10) NOT NULL,          -- "positive" | "negative"
    magnitude           DECIMAL(5,3),                  -- 0.0-1.0 (eigenvector weight)
    lag_periods         INT DEFAULT 0,                 -- periods until effect materializes
    confidence          DECIMAL(5,3),                  -- statistical confidence
    strategy_cluster    VARCHAR(20),                   -- "efficiency" | "innovation"
    notes               TEXT
);

-- Key financial interdependencies to seed:
-- inventory_turns ↑ → carrying_cost ↓ (magnitude: 0.85, lag: 1 period)
-- inventory_turns ↑ → fill_rate ↓ (magnitude: 0.45, lag: 2 periods)
-- fill_rate ↑ → revenue ↑ (magnitude: 0.70, lag: 1 period)
-- logistics_cost ↑ → EBITDA ↓ (magnitude: 0.90, lag: 0 periods)
-- EVA ↑ → ROIC ↑ (magnitude: 0.95, lag: 0 periods)
```

### 5.5 Big Data Analytics (BDA) Method Mapping

| User Query Type | BDA Method | Tool Called | Output |
|---|---|---|---|
| "Show me demand pattern" | Time-series decomposition | `get_financial_kpis` + L3 forecast | Seasonal trend chart |
| "Cluster our SKUs by margin" | K-means / ABC analysis | `get_cost_breakdown` | ABC-XYZ matrix |
| "Predict cash flow next quarter" | Regression + simulation | `get_cash_flow_forecast` | Fan chart |
| "Which supplier is highest risk?" | Classification (existing risk module) | Risk API | Risk heatmap |
| "Optimize safety stock" | Stochastic optimization | `run_what_if_scenario` | Policy recommendation |
| "What drives our margin variance?" | Root cause / attribution | `get_budget_variance` + `get_kpi_tradeoffs` | Waterfall chart |

---

## 6. LLM & Generative AI Integration

### 6.1 Use Case Mapping to Gen AI Capabilities

| Supply Chain Use Case | Gen AI Capability | Implementation |
|---|---|---|
| Demand sensing & forecasting | Pattern recognition in structured data | Tool-calling → L3 forecast-svc |
| Materials & capacity planning | Scenario generation & comparison | `run_what_if_scenario` + LLM synthesis |
| Transportation planning | Trade-off optimization (air vs ocean) | `run_what_if_scenario` with mode parameters |
| Real-time supply chain tracking | Natural language status updates | Streaming response from existing event data |
| SCOR benchmarking | Knowledge-base comparison | System prompt + industry benchmark data |
| Executive briefing generation | Long-form narrative generation | `/briefing` endpoint with Sonnet |

### 6.2 Customer Model Integration

For personalized demand-driven financial recommendations, extend the copilot with a lightweight customer model:

```python
# Customer model (simplified — based on da Silva et al., 2022)
def get_customer_demand_signals(
    product_category: str,
    time_horizon: str = "next_quarter"
) -> dict:
    """
    Uses existing customer model outputs (RNN/transformer-based).
    Returns: demand probability distribution by product/category
    WITHOUT including customer PII in the LLM prompt.
    """
    # Aggregate customer signals → category-level demand distribution
    # Never pass individual customer data to LLM
    pass
```

### 6.3 Streaming Implementation

```python
# tower-svc/routers/financial_copilot.py — streaming endpoint
from fastapi.responses import StreamingResponse
import json

@router.post("/chat/stream")
async def stream_financial_chat(request: FinancialChatRequest):
    async def event_generator():
        # Step 1: Tool selection (not streamed — internal)
        tools_to_call = await select_tools(request)
        tool_results  = await execute_tools(tools_to_call)
        
        # Step 2: Stream LLM synthesis
        async for token in llm_gateway.stream(
            system_prompt=build_system_prompt(request),
            user_message=request.user_message,
            tool_results=tool_results,
            model=MODEL_ROUTING[classify_complexity(request.user_message)],
            max_tokens=get_max_tokens(request)
        ):
            yield f"data: {json.dumps({'token': token})}\n\n"
        
        # Step 3: Send metadata after stream completes
        yield f"data: {json.dumps({'type': 'metadata', 'citations': tool_results.citations})}\n\n"
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")
```

---

## 7. Cost Optimization Strategy

### 7.1 Tiered Model Routing

| Query Type | Example | Model | Approx. Cost/Query |
|---|---|---|---|
| Simple KPI lookup | "What is our current EVA?" | Llama3-8B | $0 (Free) |
| Trade-off explanation | "What happens if inventory turns increase?" | Llama3-8B + tools | $0 (Free) |
| Scenario reasoning | "Compare air vs ocean freight on margin" | Llama3-70B | $0 (Free) |
| Strategic recommendation | "Should we defer capacity investment?" | Llama3-70B + full context | $0 (Free) |
| Executive briefing (pre-computed) | Daily CFO briefing | Llama3-70B (scheduled) | $0 (Free) |

### 7.2 Monthly Cost Projection

**Assumptions:** 5 active financial users · 50 queries/user/day · 22 working days/month

| Strategy | LLM Cost | Infrastructure | Total |
|---|---|---|---|
| No optimization (all Llama3-70B, all on-demand) | $0/mo | $0 | **$0/mo** |
| Tiered routing (80% Llama3-8B / 20% Llama3-70B) | $0/mo | $0 | **$0/mo** |
| + Pre-computed briefings | $0/mo | $0 | **$0/mo** |
| + Semantic cache (20–30% hit rate) | $0/mo | $0–$10 (Redis) | **$0–10/mo** |
| + Constrained output tokens | $0/mo | $0 | **$0–10/mo** |

**Target: <$10/month for 5 users = <$2/user/month**

### 7.3 Output Token Constraints

```python
MAX_TOKENS_BY_COMPLEXITY = {
    "simple":  300,    # KPI lookup
    "medium":  800,    # explanation + data
    "complex": 1500,   # scenario comparison + recommendation
    "briefing": 2000,  # daily executive briefing (pre-computed)
}

# Anti-pattern: Never include "explain your reasoning step by step" in production
# Anti-pattern: Never send full DB schema in system prompt
# Anti-pattern: Never request JSON + markdown formatting (pick one)
```

### 7.4 Context Minimization

```python
def build_system_prompt(request: FinancialChatRequest) -> str:
    """
    Keep system prompt under 500 tokens.
    Only inject what the LLM needs for THIS query.
    """
    # Inject only KPIs on current dashboard view (not all KPIs)
    current_kpis = get_visible_kpis(request.active_dashboard)
    
    # Inject only top-3 scenario differences (not full scenario matrix)
    scenario_diff = get_scenario_summary(request.active_scenario, top_n=3)
    
    # Base prompt + context = target < 500 tokens
    return FINANCIAL_SYSTEM_PROMPT.format(
        active_dashboard=request.active_dashboard,
        active_scenario=request.active_scenario,
        user_role=request.user_role,
        region_filter=request.region_filter,
        strategy_cluster=get_strategy_cluster(),
        kpi_snapshot=json.dumps(current_kpis),     # only ~5 KPIs
        scenario_diff=json.dumps(scenario_diff),    # top-3 only
        max_response_tokens=MAX_TOKENS_BY_COMPLEXITY[classify_complexity(request.user_message)]
    )
```

---

## 8. Frontend Integration

### 8.1 Component Architecture

```
Dashboard 6 (Financial Impact)
├── <FinancialCopilotPanel>          ← NEW (§2.4)
│   ├── Slide-in drawer (right)
│   ├── Streaming chat thread
│   ├── Inline Plotly charts
│   └── What-if shortcuts
│
├── <KpiCard id="EVA">
│   └── ✨ Ask Copilot link          ← NEW (§2.5) — pure frontend
│
├── <KpiCard id="ROIC">
│   └── ✨ Ask Copilot link
│
└── [existing charts unchanged]

Global Navigation Bar (all dashboards)
└── ✨ Financial Copilot button      ← NEW (§3, Step 9)
```

### 8.2 Visualization Integration

When the copilot returns `chart_type != null`, render an inline chart using existing components:

```typescript
const CHART_RENDERERS: Record<string, React.FC> = {
    "line":       LineChartInline,      // reuse existing <LineChart>
    "waterfall":  WaterfallChartInline, // reuse existing <WaterfallChart>
    "bar":        BarChartInline,       // reuse existing <BarChart>
    "fan":        FanChartInline,       // reuse existing <FanChart>
    "scatter":    ScatterPlotInline,    // reuse existing <ScatterPlot>
};

// In AssistantBubble:
{response.chart_type && response.data_payload && (
    <ChartContainer>
        {React.createElement(CHART_RENDERERS[response.chart_type], {
            data: response.data_payload,
            height: 200,
            compact: true,      // compact mode for inline rendering
        })}
    </ChartContainer>
)}
```

### 8.3 Visual Analytics Tactics (from Costa et al., 2021)

Map copilot responses to the appropriate visualization technique:

| Analytical Goal | Visualization Tactic | Chart Component |
|---|---|---|
| Financial trend identification | Temporal pattern analysis | `<FanChart>` with confidence bands |
| Cost driver analysis | Multi-dimensional analysis | `<WaterfallChart>` |
| Regional financial performance | Spatial pattern analysis | `<ChoroplethMap>` |
| Supplier financial risk | Network analysis | `<NetworkGraph>` (existing) |
| Scenario comparison | Multiple coordinated views | `<ScenarioComparisonTable>` |
| KPI trade-off identification | Sensitivity analysis | `<ScatterPlot>` with efficient frontier |

---

## 9. Guardrails & Governance

### 9.1 Hard Rules — Never Cross

1. **No transaction execution.** Copilot recommends; humans approve. `approval_threshold_usd` from `collab_mode_config` still applies.
2. **No direct Kafka writes.** Copilot reads via synchronous API calls only.
3. **No raw LLM responses in analytical tables.** Store in `copilot_conversation_log` only — not source-of-truth financial data.
4. **No PII in LLM prompts.** Aggregate before sending. Customer identity never enters the prompt.
5. **No RAG on tabular data.** SQL tool-calling is superior for structured financial data — cheaper, auditable, accurate.
6. **No fine-tuning.** Domain context is handled by system prompt + tool results. Fine-tuning costs $5K–$20K and is unjustified at this stage.
7. **No vector search for financial tables.** SQL only for tabular data.

### 9.2 Data Quality Guardrails

```python
def validate_tool_response(tool_name: str, result: dict) -> dict:
    """Validate tool responses before sending to LLM."""
    
    # Check for stale data
    if "data_freshness" in result:
        age_hours = (datetime.now() - parse(result["data_freshness"])).seconds / 3600
        if age_hours > STALENESS_THRESHOLD[tool_name]:
            result["staleness_warning"] = f"Data is {age_hours:.1f}h old. Treat with caution."
    
    # Redact any PII fields that slipped through
    result = redact_pii_fields(result, PII_FIELD_PATTERNS)
    
    # Check for nulls in critical fields
    if result.get("value") is None:
        raise ToolResponseError(f"{tool_name} returned null value — do not hallucinate")
    
    return result
```

### 9.3 Conversation Logging

```sql
CREATE TABLE copilot_conversation_log (
    id                  SERIAL PRIMARY KEY,
    session_id          UUID NOT NULL,
    user_role           VARCHAR(50),
    active_dashboard    VARCHAR(50),
    user_message        TEXT NOT NULL,
    assistant_response  JSONB NOT NULL,
    tools_called        TEXT[],
    model_used          VARCHAR(50),
    input_tokens        INT,
    output_tokens       INT,
    cost_usd            DECIMAL(10,6),
    latency_ms          INT,
    cache_hit           BOOLEAN DEFAULT FALSE,
    created_at          TIMESTAMP DEFAULT NOW()
);
-- NOTE: This table is for audit/cost tracking only.
-- NEVER join this table into financial analytics queries.
-- NEVER expose raw LLM responses to downstream systems.
```

---

## 10. Verification & Testing

### 10.1 Canonical Test Questions

Run these 10 questions after every code change to validate the copilot:

| # | Question | Expected Tool Calls | Expected Model | Pass Criteria |
|---|---|---|---|---|
| 1 | "What is our current EVA?" | `get_financial_kpis` | Llama3-8B | Returns EVA value with unit and timestamp |
| 2 | "Show me cash-to-cash trend" | `get_financial_kpis` | Llama3-8B | Returns time-series data, `chart_type="line"` |
| 3 | "What happens if we push inventory turns higher?" | `get_kpi_tradeoffs`, `get_financial_kpis` | Llama3-8B | Lists cascading effects on fill rate, carrying cost |
| 4 | "Compare air vs ocean freight impact on margin" | `run_what_if_scenario`, `get_financial_kpis` | Llama3-70B | Side-by-side scenario data, `chart_type="bar"` |
| 5 | "Should we defer the capacity investment?" | `run_what_if_scenario`, `get_kpi_tradeoffs`, `get_financial_kpis` | Llama3-70B | Pros/cons with quantified financial impact |
| 6 | "Why did margin drop this week?" | `get_financial_kpis`, `get_cost_breakdown` | Llama3-8B | Root cause with cost driver breakdown, `chart_type="waterfall"` |
| 7 | "What's the carrying cost of overstock in EMEA?" | `get_financial_kpis`, `get_cost_breakdown` | Llama3-8B | Region-specific carrying cost with % of total |
| 8 | "Give me my daily briefing" | (from cache) | Cache hit | Response in <100ms, `source="cache"` |
| 9 | "What is the trade-off between fill rate and inventory cost?" | `get_kpi_tradeoffs` | Llama3-8B | Quantified trade-off with direction and magnitude |
| 10 | "Run a budget scenario with 10% logistics cost reduction" | `run_what_if_scenario`, `get_financial_kpis` | Llama3-70B | P&L impact table, `chart_type="waterfall"` |

**All 10 must pass:**
- No hallucinated numbers (all values cite a tool result)
- `citations` field is populated
- `tool_calls_made` matches expected column above
- Response within token budget
- Guardrail: Question 5 includes "only recommend, do not execute" caveat

### 10.2 Regression Test Suite

```python
# tests/test_financial_copilot.py

def test_no_hallucination():
    """Assert LLM never returns a number not in tool results"""
    pass

def test_citations_populated():
    """Assert all responses have at least one citation"""
    pass

def test_model_routing():
    """Assert all 10 canonical questions route to correct model tier"""
    pass

def test_cache_hit():
    """Assert identical queries within TTL return from cache"""
    pass

def test_pii_not_in_prompt():
    """Assert customer names/IDs never appear in LLM prompt"""
    pass

def test_streaming_response():
    """Assert streaming endpoint delivers first token within 500ms"""
    pass

def test_guardrail_no_execution():
    """Assert copilot refuses to execute transactions"""
    pass
```

---

## 11. Observability & Monitoring

### 11.1 Grafana Dashboard — "Financial Copilot Operations"

Add the following panels to the existing Grafana executive board:

| Panel | Metric | Alert Threshold |
|---|---|---|
| Daily Query Volume | `copilot_queries_total` (sum/day) | >500/day (review capacity) |
| Model Routing Split | Llama3-8B% vs Llama3-70B% | Llama3-70B% >30% → investigate |
| Daily LLM Cost ($) | `copilot_token_cost_usd` (sum/day) | >$5/day → alert |
| Cache Hit Rate | `copilot_cache_hit_rate` | <15% → investigate cache |
| Average Latency | `copilot_latency_seconds` (p50, p95) | p95 >5s → alert |
| Top 10 Questions | (logged in `copilot_conversation_log`) | N/A — insight only |
| Error Rate | `copilot_errors_total` / total | >2% → alert |
| Tool Call Distribution | `copilot_tool_calls_total` by tool | Identifies most-used paths |

### 11.2 Cost Alerts

```yaml
# alertmanager rules
- alert: CopilotDailyCostExceeded
  expr: increase(copilot_token_cost_usd[24h]) > 5.0
  severity: warning
  message: "Financial Copilot daily LLM cost exceeded $5. Check model routing."

- alert: CopilotCacheHitLow
  expr: copilot_cache_hit_rate < 0.15
  severity: info
  message: "Cache hit rate below 15%. Consider increasing TTL or cache size."
```

---

## 12. Future Extensions

Execute only after v1 proves value (>50% user adoption).

| Extension | Trigger | Additional Cost | Effort |
|---|---|---|---|
| Proactive alerts ("Cash-to-Cash exceeded threshold") | Adoption >50% | ~$0 (reuse alert pipeline + Llama3-8B) | 1 day |
| Multi-turn scenario exploration | Users request it | ~$0 (LLM already multi-turn; add state management) | 2 days |
| MARL inventory policy optimization | After 6 months of conversation logs | ~$500 cloud compute for training | 3 weeks |
| Voice interface for mobile executives | Mobile dashboard mature | ~$0.02/query (Whisper API + Llama3-8B) | 1 week |
| Copilot fine-tuning | >5,000 rated conversations | ~$2K one-time + marginal inference savings | 2 weeks |
| RAG on financial documents (policies, contracts) | When unstructured financial docs are onboarded | ~$20/month (vector DB) | 1 week |
| Supply chain resilience scoring | After risk module matures | ~$0 (reuse existing risk API) | 3 days |

---

## Appendix A — File Structure

```
tower-svc/
├── main.py                                 ← Add: include_router(financial_copilot)
├── routers/
│   └── financial_copilot.py               ← NEW: 3 endpoints
├── tools/
│   └── financial_tools.py                 ← NEW: 6 SQL-wrapping functions
├── prompts/
│   └── financial_copilot_system.txt       ← NEW: system prompt template
├── utils/
│   ├── complexity_classifier.py           ← NEW: keyword-based routing
│   └── semantic_cache.py                  ← NEW: in-memory / Redis cache
└── jobs/
    └── briefing_generator.py              ← NEW: scheduled briefing job

frontend/src/
├── components/organisms/
│   └── FinancialCopilotPanel.tsx          ← NEW: chat drawer
├── pages/
│   └── Dashboard6.tsx                     ← EXTEND: add drawer + ✨ links
└── navigation/
    └── NavBar.tsx                         ← EXTEND: add global ✨ button

database/
└── migrations/
    └── 001_copilot_tables.sql             ← NEW: 2 tables only
        -- copilot_briefing_cache
        -- copilot_conversation_log
```

---

## Appendix B — Expected Monthly Cost Summary

| Component | Cost |
|---|---|
| LLM API (chat queries, tiered routing) | $0/mo |
| LLM API (pre-computed briefings, 3/day) | $0/mo |
| Infrastructure (compute, reuses tower-svc) | $0 |
| Cache (in-memory MVP / Redis production) | $0–$10/mo |
| Observability (reuses existing Grafana) | $0 |
| **Total** | **$0–10/mo for 5 active users** |
| Per-user cost | **~$0–2/user/month** |
