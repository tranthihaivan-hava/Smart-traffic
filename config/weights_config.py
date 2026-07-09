from dataclasses import dataclass
from typing import Dict

@dataclass(frozen=True)
class WeightVector:
    distance: float
    urgency: float
    waiting: float
    delivery_risk: float

def get_default_weights() -> WeightVector:
    return WeightVector(distance=0.4, urgency=0.3, waiting=0.1, delivery_risk=0.2)

def get_weight_bounds() -> Dict[str, tuple]:
    return {
        "distance": (0.0, 1.0),
        "urgency": (0.0, 1.0),
        "waiting": (0.0, 1.0),
        "delivery_risk": (0.0, 1.0)
    }
