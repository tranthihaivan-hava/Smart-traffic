import os
from dataclasses import dataclass

@dataclass(frozen=True)
class SettingsConfig:
    max_days: int = 7
    vehicle_capacity: float = 1e9  # Extremely large as capacity is not strictly constrained, but modelable
    vehicle_speed: float = 50.0    # Speed limit 50 km/h
    depot_id: str = "DEPOT"

def get_settings() -> SettingsConfig:
    return SettingsConfig()
