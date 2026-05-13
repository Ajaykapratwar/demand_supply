import os
import json
import asyncio
from datetime import datetime
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from groq import AsyncGroq

from services.tower_svc.utils.complexity_classifier import classify_complexity
from services.tower_svc.utils.semantic_cache import check_semantic_cache, set_semantic_cache
from services.tower_svc.tools.financial_tools import (
    get_financial_kpis,
    get_cost_breakdown,
    get_budget_variance,
    get_cash_flow_forecast,
    run_what_if_scenario,
    get_kpi_tradeoffs
)

load_dotenv()

router = APIRouter(prefix="/copilot", tags=["Financial Copilot"])

# --- Models ---
class FinancialChatRequest(BaseModel):
    user_message: str
    active_dashboard: str = "Dashboard 6"
    active_scenario: str = "Baseline"
    user_role: str = "CFO"
    region_filter: str = "GLOBAL"

class BriefingRequest(BaseModel):
    role: str = "CFO"

MODEL_ROUTING = {
    "simple":  "llama-3.1-8b-instant",                # Free via Groq
    "medium":  "llama-3.3-70b-versatile",                # Free via Groq
    "complex": "llama-3.3-70b-versatile",               # Free via Groq
}

# --- Tool Definitions ---
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_financial_kpis",
            "description": "Retrieves current or historical financial KPIs. Useful to check financial health metrics like EVA, carrying cost, revenue.",
            "parameters": {
                "type": "object",
                "properties": {
                    "kpi_names": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of KPI names to retrieve"
                    },
                    "period": {
                        "type": "string",
                        "description": "The time period (e.g., 'current', 'historical')"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_cost_breakdown",
            "description": "Breaks down costs by category, region, or plant.",
            "parameters": {
                "type": "object",
                "properties": {
                    "dimension": {
                        "type": "string",
                        "description": "Dimension to break down costs by (e.g. 'category', 'region', 'plant')"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_budget_variance",
            "description": "Retrieves budget vs actual variance.",
            "parameters": {
                "type": "object",
                "properties": {
                    "period": {
                        "type": "string",
                        "description": "The time period (e.g. 'current')"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_cash_flow_forecast",
            "description": "Retrieves cash flow forecast over the specified horizon.",
            "parameters": {
                "type": "object",
                "properties": {
                    "horizon_days": {
                        "type": "integer",
                        "description": "Forecast horizon in days (e.g. 90)"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_what_if_scenario",
            "description": "Executes a financial what-if scenario to simulate impact of changes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "scenario_name": {
                        "type": "string",
                        "description": "Name of the scenario"
                    },
                    "parameters": {
                        "type": "object",
                        "description": "Parameters for the scenario"
                    },
                    "target_kpis": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Target KPIs to evaluate"
                    }
                },
                "required": ["scenario_name", "parameters", "target_kpis"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_kpi_tradeoffs",
            "description": "Retrieves KPI interdependency tradeoff data.",
            "parameters": {
                "type": "object",
                "properties": {
                    "source_kpi": {
                        "type": "string",
                        "description": "The KPI that is changing"
                    },
                    "target_kpis": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "The KPIs that are impacted"
                    },
                    "direction": {
                        "type": "string",
                        "description": "The direction of change ('increase' or 'decrease')"
                    }
                },
                "required": ["source_kpi", "target_kpis", "direction"]
            }
        }
    }
]

available_functions = {
    "get_financial_kpis": get_financial_kpis,
    "get_cost_breakdown": get_cost_breakdown,
    "get_budget_variance": get_budget_variance,
    "get_cash_flow_forecast": get_cash_flow_forecast,
    "run_what_if_scenario": run_what_if_scenario,
    "get_kpi_tradeoffs": get_kpi_tradeoffs
}

class GroqLLMGateway:
    def __init__(self):
        # We will initialize this dynamically in case the key isn't set yet
        self._client = None

    @property
    def client(self):
        if self._client is None:
            api_key = os.environ.get("GROQ_API_KEY")
            if not api_key:
                raise ValueError("GROQ_API_KEY environment variable is not set")
            self._client = AsyncGroq(api_key=api_key)
        return self._client

    async def chat_with_tools(self, system_prompt: str, user_message: str, model: str, max_tokens: int, stream: bool = True):
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]

        try:
            # First pass: Check if the model wants to call a tool
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                tools=tools,
                tool_choice="auto",
                max_tokens=max_tokens
            )

            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls

            citations = []
            
            if tool_calls:
                messages.append(response_message)
                
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_to_call = available_functions.get(function_name)
                    
                    if function_to_call:
                        try:
                            function_args = json.loads(tool_call.function.arguments)
                        except:
                            function_args = {}
                        
                        function_response = function_to_call(**function_args)
                        
                        # Extract citations from function response if present
                        if isinstance(function_response, list):
                            for item in function_response:
                                if isinstance(item, dict) and "citations" in item:
                                    citations.extend(item["citations"])
                        elif isinstance(function_response, dict) and "citations" in function_response:
                            citations.extend(function_response["citations"])
                        
                        messages.append(
                            {
                                "tool_call_id": tool_call.id,
                                "role": "tool",
                                "name": function_name,
                                "content": json.dumps(function_response),
                            }
                        )

                # Second pass: get final response
                if stream:
                    response_stream = await self.client.chat.completions.create(
                        model=model,
                        messages=messages,
                        stream=True,
                        max_tokens=max_tokens
                    )
                    return response_stream, citations
                else:
                    final_response = await self.client.chat.completions.create(
                        model=model,
                        messages=messages,
                        stream=False,
                        max_tokens=max_tokens
                    )
                    return final_response.choices[0].message.content, citations
            else:
                if stream:
                    response_stream = await self.client.chat.completions.create(
                        model=model,
                        messages=messages,
                        stream=True,
                        max_tokens=max_tokens
                    )
                    return response_stream, citations
                else:
                    return response_message.content, citations
        except Exception as e:
            print(f"Groq API Error: {str(e)}")
            # Fallback if API key missing or error
            error_msg = f"Error communicating with AI: {str(e)}. Please check your GROQ_API_KEY."
            if stream:
                async def err_stream():
                    yield type("obj", (object,), {"choices": [type("obj", (object,), {"delta": type("obj", (object,), {"content": error_msg})()})]})()
                return err_stream(), []
            else:
                return error_msg, []

llm_gateway = GroqLLMGateway()

@router.post("/chat/stream")
async def stream_financial_chat(request: FinancialChatRequest):
    """Stream response from the financial copilot using Llama 3 models via Groq."""
    
    # 1. Semantic Cache check
    cached = check_semantic_cache(request.user_message, request.active_dashboard)
    if cached:
        async def cache_generator():
            yield f"data: {json.dumps({'token': cached['text']})}\n\n"
            yield f"data: {json.dumps({'type': 'metadata', 'citations': cached['citations'], 'source': 'cache'})}\n\n"
            yield "data: [DONE]\n\n"
        return StreamingResponse(cache_generator(), media_type="text/event-stream")

    complexity = classify_complexity(request.user_message)
    model_to_use = MODEL_ROUTING.get(complexity, "llama-3.3-70b-versatile")
    
    # 2. Setup System Prompt
    system_prompt = f"""You are a Financial Copilot integrated into an HVAC Control Tower.
You provide precise, executive-level financial insights.
Active Dashboard: {request.active_dashboard}
User Role: {request.user_role}
Region Filter: {request.region_filter}
Use the provided tools to answer the user's questions. Always rely on the data returned from tools.
"""

    async def event_generator():
        try:
            stream, citations = await llm_gateway.chat_with_tools(
                system_prompt=system_prompt,
                user_message=request.user_message,
                model=model_to_use,
                max_tokens=1024,
                stream=True
            )
            
            full_response = ""
            async for chunk in stream:
                if chunk.choices and hasattr(chunk.choices[0], "delta") and hasattr(chunk.choices[0].delta, "content") and chunk.choices[0].delta.content:
                    token = chunk.choices[0].delta.content
                    full_response += token
                    yield f"data: {json.dumps({'token': token})}\n\n"
            
            # Remove duplicate citations
            citations = list(set(citations))
            
            yield f"data: {json.dumps({'type': 'metadata', 'citations': citations, 'model_used': model_to_use})}\n\n"
            yield "data: [DONE]\n\n"
            
            # Save to cache asynchronously after streaming
            if full_response:
                set_semantic_cache(request.user_message, request.active_dashboard, {
                    "text": full_response,
                    "citations": citations
                })
        except Exception as e:
            yield f"data: {json.dumps({'token': f'Error: {str(e)}'})}\n\n"
            yield "data: [DONE]\n\n"
        
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.post("/chat")
async def sync_financial_chat(request: FinancialChatRequest):
    """Synchronous response from the financial copilot for simpler clients like Dash."""
    cached = check_semantic_cache(request.user_message, request.active_dashboard)
    if cached:
        return {"response": cached["text"], "citations": cached["citations"], "source": "cache"}

    complexity = classify_complexity(request.user_message)
    model_to_use = MODEL_ROUTING.get(complexity, "llama-3.3-70b-versatile")
    
    system_prompt = f"""You are a Financial Copilot integrated into an HVAC Control Tower.
You provide precise, executive-level financial insights.
Active Dashboard: {request.active_dashboard}
User Role: {request.user_role}
Region Filter: {request.region_filter}
Use the provided tools to answer the user's questions. Always rely on the data returned from tools.
"""
    
    response_text, citations = await llm_gateway.chat_with_tools(
        system_prompt=system_prompt,
        user_message=request.user_message,
        model=model_to_use,
        max_tokens=1024,
        stream=False
    )
    
    citations = list(set(citations))
    
    if "Error communicating with AI" not in response_text:
        set_semantic_cache(request.user_message, request.active_dashboard, {
            "text": response_text,
            "citations": citations
        })
    
    return {"response": response_text, "citations": citations, "model_used": model_to_use}

@router.post("/briefing")
async def generate_briefing(request: BriefingRequest):
    """Generates an executive briefing."""
    return {
        "role": request.role,
        "briefing": "Cash flow remains steady. Logistics costs in EMEA require attention.",
        "model_used": MODEL_ROUTING["complex"],
        "generated_at": datetime.now().isoformat()
    }
