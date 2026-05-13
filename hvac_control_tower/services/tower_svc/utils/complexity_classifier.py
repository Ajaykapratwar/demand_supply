# Keyword-based complexity classification
def classify_complexity(user_message: str) -> str:
    """
    Classifies the user query into 'simple', 'medium', or 'complex' 
    to determine the appropriate LLM model routing.
    """
    msg = user_message.lower()
    
    complex_keywords = ["scenario", "what if", "compare", "recommend", "strategic", "simulate", "optimize"]
    medium_keywords = ["why", "explain", "trade-off", "breakdown", "variance", "trend"]
    
    if any(k in msg for k in complex_keywords):
        return "complex"
    if any(k in msg for k in medium_keywords):
        return "medium"
    return "simple"
