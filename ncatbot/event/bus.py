from __future__ import annotations

from dataclasses import dataclass, field

from .base import BaseEvent

__all__ = [
    "BusEvent",
]


@dataclass(slots=True)
class BusEvent:
    """EventBus 信封"""

    type: str
    data: BaseEvent
    _propagation_stopped: bool = field(default=False, repr=False)

    def stop_propagation(self) -> None:
        self._propagation_stopped = True

    @property
    def stopped(self) -> bool:
        return self._propagation_stopped
