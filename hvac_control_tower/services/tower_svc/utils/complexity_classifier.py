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
    "simple":  "claude-haiku-4-5-20251001",
    "medium":  "claude-haiku-4-5-20251001",
    "complex": "claude-sonnet-4-6",
}
