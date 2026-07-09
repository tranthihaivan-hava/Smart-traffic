from dataclasses import dataclass, field
from typing import Dict

@dataclass
class Candidate:
    customer_id: str
    day: int
    insertion_index: int
    arrival_time: float
    wait_time: float
    service_start_time: float
    distance_delta: float
    
    # Raw extracted features
    raw_features: Dict[str, float] = field(default_factory=dict)
    # Normalized features [0.0 - 1.0]
    norm_features: Dict[str, float] = field(default_factory=dict)
    # Weighted composite scalar score
    score: float = float('inf')
