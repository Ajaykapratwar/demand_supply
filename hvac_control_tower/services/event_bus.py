"""
services/event_bus.py
In-memory typed event bus for inter-service communication.
Replaces Kafka for local deployment. Partitioned by site_id.
Thread-safe for single-process use.
"""

import threading
from collections import defaultdict
from typing import Callable, List
from contracts.events import BaseEvent, validate_event


class EventBus:
    """Simple pub/sub event bus. Services publish events; subscribers consume."""

    def __init__(self):
        self._subscribers: dict[str, List[Callable]] = defaultdict(list)
        self._dead_letter: List[dict] = []
        self._lock = threading.Lock()
        self._event_log: List[BaseEvent] = []

    def subscribe(self, event_type: str, handler: Callable) -> None:
        with self._lock:
            self._subscribers[event_type].append(handler)

    def publish(self, event: BaseEvent) -> None:
        """Publish event to all subscribers of its type."""
        try:
            validate_event(event)
        except ValueError as e:
            self._dead_letter.append({
                "event": event.to_dict() if hasattr(event, "to_dict") else str(event),
                "error": str(e),
            })
            return

        with self._lock:
            self._event_log.append(event)
            handlers = self._subscribers.get(event.event_type, [])

        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                self._dead_letter.append({
                    "event": event.to_dict(),
                    "error": f"Handler {handler.__name__} failed: {e}",
                })

    def get_dead_letters(self) -> List[dict]:
        return list(self._dead_letter)

    def get_event_log(self, event_type: str = None) -> List[BaseEvent]:
        if event_type:
            return [e for e in self._event_log if e.event_type == event_type]
        return list(self._event_log)

    def clear(self) -> None:
        with self._lock:
            self._subscribers.clear()
            self._dead_letter.clear()
            self._event_log.clear()
