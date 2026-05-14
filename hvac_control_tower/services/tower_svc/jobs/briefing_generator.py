import asyncio
from datetime import datetime, timezone

# Mocking the database and the actual LLM call for the spec
def call_llm_for_briefing(role: str, region: str):
    from tools.financial_tools import get_financial_kpis
    return {
        "summary": f"Automated daily financial briefing for {role} in {region}.",
        "key_metrics": get_financial_kpis(["EVA", "ROIC"], region=region)
    }

def cache_briefing(role: str, region: str, briefing: dict):
    from routers.financial_copilot import _briefing_cache
    cache_key = f"{role}_{region}"
    _briefing_cache[cache_key] = {
        "briefing_json": briefing,
        "generated_at": datetime.now(timezone.utc)
    }

ROLES = ["CFO", "CSO", "COO"]
REGIONS = ["All"]

def generate_daily_briefings():
    """
    Scheduled job (cron / Celery beat — 6:00 AM daily)
    """
    for role in ROLES:
        for region in REGIONS:
            briefing = call_llm_for_briefing(role=role, region=region)
            cache_briefing(role, region, briefing)

if __name__ == "__main__":
    import sys
    sys.path.append('..')
    generate_daily_briefings()
    print("Briefings generated and cached.")
