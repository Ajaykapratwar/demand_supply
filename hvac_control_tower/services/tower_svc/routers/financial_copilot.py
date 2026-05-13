from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json
import asyncio
from datetime import datetime

from services.tower_svc.utils.complexity_classifier import classify_complexity
from services.tower_svc.utils.semantic_cache import check_semantic_cache, set_semantic_cache
from services.tower_svc.tools.financial_tools import get_financial_kpis

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
    "simple":  "llama3-8b-8192",                # Free via Groq
    "medium":  "llama3-8b-8192",                # Free via Groq
    "complex": "llama3-70b-8192",               # Free via Groq
}

# --- Dummy LLM Streaming Gateway ---
class DummyLLMGateway:
    async def stream(self, system_prompt, user_message, tool_results, model, max_tokens):
        # MVP implementation simulating LLM streaming
        response_text = f"Simulated response from {model} based on tool results: {json.dumps(tool_results)}."
        for word in response_text.split(" "):
            await asyncio.sleep(0.05)
            yield word + " "

llm_gateway = DummyLLMGateway()

@router.post("/chat/stream")
async def stream_financial_chat(request: FinancialChatRequest):
    """Stream response from the financial copilot using Llama 3 free models via Groq."""
    
    # 1. Semantic Cache check
    cached = check_semantic_cache(request.user_message, request.active_dashboard)
    if cached:
        async def cache_generator():
            yield f"data: {json.dumps({'token': cached['text']})}\\n\\n"
            yield f"data: {json.dumps({'type': 'metadata', 'citations': cached['citations'], 'source': 'cache'})}\\n\\n"
            yield "data: [DONE]\\n\\n"
        return StreamingResponse(cache_generator(), media_type="text/event-stream")

    complexity = classify_complexity(request.user_message)
    model_to_use = MODEL_ROUTING.get(complexity, "llama3-8b-8192")
    
    # 2. Tool Selection & Execution (Simulated)
    # In reality, the LLM would be prompted to select tools. Here we just call get_financial_kpis as an example.
    tool_results = {"kpis": get_financial_kpis(period="current")}
    
    # 3. Stream Synthesis
    async def event_generator():
        system_prompt = f"System context for {request.active_dashboard}" # In reality load from text file
        
        full_response = ""
        async for token in llm_gateway.stream(
            system_prompt=system_prompt,
            user_message=request.user_message,
            tool_results=tool_results,
            model=model_to_use,
            max_tokens=800
        ):
            full_response += token
            yield f"data: {json.dumps({'token': token})}\\n\\n"
        
        citations = ["fact_financial.eva"] # Extracted from tool_results in reality
        yield f"data: {json.dumps({'type': 'metadata', 'citations': citations, 'model_used': model_to_use})}\\n\\n"
        yield "data: [DONE]\\n\\n"
        
        # Save to cache asynchronously after streaming
        set_semantic_cache(request.user_message, request.active_dashboard, {
            "text": full_response,
            "citations": citations
        })
        
        # Log conversation (would insert into copilot_conversation_log here)
        
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.post("/chat")
async def sync_financial_chat(request: FinancialChatRequest):
    """Synchronous response from the financial copilot for simpler clients like Dash."""
    cached = check_semantic_cache(request.user_message, request.active_dashboard)
    if cached:
        return {"response": cached["text"], "citations": cached["citations"], "source": "cache"}

    complexity = classify_complexity(request.user_message)
    model_to_use = MODEL_ROUTING.get(complexity, "llama3-8b-8192")
    
    tool_results = {"kpis": get_financial_kpis(period="current")}
    system_prompt = f"System context for {request.active_dashboard}"
    
    full_response = ""
    async for token in llm_gateway.stream(
        system_prompt=system_prompt,
        user_message=request.user_message,
        tool_results=tool_results,
        model=model_to_use,
        max_tokens=800
    ):
        full_response += token
        
    citations = ["fact_financial.eva"]
    
    set_semantic_cache(request.user_message, request.active_dashboard, {
        "text": full_response,
        "citations": citations
    })
    
    return {"response": full_response, "citations": citations, "model_used": model_to_use}

@router.post("/briefing")
async def generate_briefing(request: BriefingRequest):
    """Generates an executive briefing."""
    return {
        "role": request.role,
        "briefing": "Cash flow remains steady. Logistics costs in EMEA require attention.",
        "model_used": MODEL_ROUTING["complex"],
        "generated_at": datetime.now().isoformat()
    }
