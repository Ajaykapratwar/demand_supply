from prometheus_client import Counter, Histogram, Gauge

copilot_queries_total      = Counter("copilot_queries_total", "Total copilot queries", ["model", "dashboard", "user_role"])
copilot_latency_seconds    = Histogram("copilot_latency_seconds", "Query latency", ["model", "complexity"])
copilot_token_cost_usd     = Counter("copilot_token_cost_usd", "Cumulative LLM cost", ["model"])
copilot_cache_hit_rate     = Gauge("copilot_cache_hit_rate", "Cache hit ratio (rolling 1hr)")
copilot_tool_calls_total   = Counter("copilot_tool_calls_total", "Tool invocations", ["tool_name"])
copilot_errors_total       = Counter("copilot_errors_total", "Errors", ["error_type"])
