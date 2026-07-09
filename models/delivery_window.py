from dataclasses import dataclass

@dataclass(frozen=True)
class DeliveryWindow:
    day: int
    start_time: float  # Minutes from midnight (e.g., 480.0 for 08:00)
    end_time: float    # Minutes from midnight (e.g., 720.0 for 12:00)

    def contains(self, time: float) -> bool:
        return self.start_time <= time <= self.end_time

    def time_until_close(self, current_time: float) -> float:
        return self.end_time - current_time

    def duration(self) -> float:
        return self.end_time - self.start_time
