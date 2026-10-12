from __future__ import annotations


class SimulatedClock:
    def __init__(self, start_day: int = 0) -> None:
        self.day = start_day

    def advance(self, days: int = 1) -> int:
        self.day += days
        return self.day
