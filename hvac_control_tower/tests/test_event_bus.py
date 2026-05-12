"""
tests/test_event_bus.py
Infrastructure tests for the in-memory event bus.
"""

import pytest
from services.event_bus import EventBus
from contracts.events import BaseEvent, TelemetryEvent, AnomalyAlert
from datetime import datetime


def _make_event(event_type="telemetry", **kwargs):
    """Helper to create a valid BaseEvent."""
    return BaseEvent(
        event_id="test-001",
        timestamp=datetime.now().isoformat(),
        event_type=event_type,
        **kwargs,
    )


@pytest.mark.unit
class TestEventBus:
    def test_subscribe_and_publish(self):
        bus = EventBus()
        received = []
        bus.subscribe("telemetry", lambda e: received.append(e))
        bus.publish(_make_event("telemetry"))
        assert len(received) == 1
        assert received[0].event_id == "test-001"

    def test_multiple_subscribers(self):
        bus = EventBus()
        r1, r2 = [], []
        bus.subscribe("telemetry", lambda e: r1.append(e))
        bus.subscribe("telemetry", lambda e: r2.append(e))
        bus.publish(_make_event("telemetry"))
        assert len(r1) == 1 and len(r2) == 1

    def test_no_crosstalk(self):
        bus = EventBus()
        received = []
        bus.subscribe("telemetry", lambda e: received.append(e))
        bus.publish(_make_event("weather"))  # different event type
        assert len(received) == 0

    def test_error_goes_to_dlq(self):
        bus = EventBus()

        def bad_handler(e):
            raise ValueError("boom")

        bus.subscribe("telemetry", bad_handler)
        bus.publish(_make_event("telemetry"))
        assert len(bus.get_dead_letters()) == 1

    def test_event_log_recorded(self):
        bus = EventBus()
        bus.publish(_make_event("telemetry"))
        bus.publish(_make_event("weather"))
        assert len(bus.get_event_log()) == 2
        assert len(bus.get_event_log("telemetry")) == 1

    def test_clear(self):
        bus = EventBus()
        bus.subscribe("telemetry", lambda e: None)
        bus.publish(_make_event("telemetry"))
        bus.clear()
        assert len(bus.get_event_log()) == 0
        assert len(bus.get_dead_letters()) == 0

    def test_invalid_event_to_dlq(self):
        bus = EventBus()
        # Event with empty event_id should fail validation
        bad_event = BaseEvent(event_id="", timestamp="", event_type="")
        bus.publish(bad_event)
        assert len(bus.get_dead_letters()) == 1
