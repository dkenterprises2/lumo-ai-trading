import time
from typing import List, Generator, Optional
from .validation_scenario import ReplayTickData, ValidationScenario

class ReplayMarketFeed:
    """Historical Replay Market Feed Streaming Provider."""

    def __init__(self, scenario: ValidationScenario, playback_speed: int = 1):
        self.scenario = scenario
        self.playback_speed = min(50, max(1, playback_speed))
        self.ticks = scenario.ticks
        self.current_index = 0

    def stream_ticks(self) -> Generator[ReplayTickData, None, None]:
        """Yield ticks with microsecond timestamp progression."""
        base_time = time.time()
        for idx, tick in enumerate(self.ticks):
            tick.timestamp = base_time + (idx * (1.0 / self.playback_speed))
            self.current_index = idx + 1
            yield tick

    def reset(self):
        self.current_index = 0
