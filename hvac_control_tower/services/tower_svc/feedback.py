"""
tower_svc/feedback.py
L5: Closed-loop feedback writer (spec §4.5, §9 task 9).
Persists actual outcomes back to the Digital Twin for model retraining.
Verification: actuals appear in twin within 5 min.
"""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime, timezone


FEEDBACK_DIR = Path("data/feedback")


class FeedbackWriter:
    """Writes actual outcomes to feedback store for closed-loop learning."""

    def __init__(self, output_dir: str = None):
        self.output_dir = Path(output_dir) if output_dir else FEEDBACK_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._buffer = []

    def record_actual(self, region: str, period: str, actual_demand: float,
                      forecast_p50: float, forecast_p90: float,
                      actual_fill_rate: float = None) -> dict:
        """Record one period's actual outcome for future retraining."""
        record = {
            "region": region,
            "period": period,
            "actual_demand": actual_demand,
            "forecast_p50": forecast_p50,
            "forecast_p90": forecast_p90,
            "forecast_error": actual_demand - forecast_p50,
            "error_pct": round((actual_demand - forecast_p50) / max(actual_demand, 1) * 100, 2),
            "actual_fill_rate": actual_fill_rate,
            "recorded_at": datetime.now(timezone.utc).isoformat(),
        }
        self._buffer.append(record)
        return record

    def flush(self) -> str:
        """Write buffered records to Parquet. Returns output path."""
        if not self._buffer:
            return ""
        df = pd.DataFrame(self._buffer)
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        path = self.output_dir / f"feedback_{ts}.parquet"
        df.to_parquet(path, index=False)
        count = len(self._buffer)
        self._buffer.clear()
        return str(path)

    def load_feedback_history(self) -> pd.DataFrame:
        """Load all feedback records for retraining."""
        files = sorted(self.output_dir.glob("feedback_*.parquet"))
        if not files:
            return pd.DataFrame()
        return pd.concat([pd.read_parquet(f) for f in files], ignore_index=True)

    def get_buffer_size(self) -> int:
        return len(self._buffer)

