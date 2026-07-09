# 02 — `config/` Folder Guide

## Purpose

This folder stores **global constants** and the **WeightVector** definition.  
Nothing in this folder does computation — it just defines values that the rest of the system uses.

---

## Files

### `settings.py`

Defines a frozen dataclass `SettingsConfig` with all system-wide constants.

```python
@dataclass(frozen=True)
class SettingsConfig:
    max_days: int = 7             # Planning horizon (1 week)
    vehicle_capacity: float = 1e9 # Effectively unlimited capacity
    vehicle_speed: float = 50.0   # km/h — used to calculate travel time
    depot_id: str = "DEPOT"       # The ID string that marks the warehouse row
```

**`get_settings()`** — a simple factory function that returns a fresh `SettingsConfig`.  
Called by `DatasetLoader` to know the depot ID, speed, and max days.

> `vehicle_capacity = 1e9` means capacity is intentionally not a hard constraint
> in this problem version. All customers can fit on the truck.

---

### `weights_config.py`

Defines the **WeightVector** — the most important tunable parameter in the system.

```python
@dataclass(frozen=True)
class WeightVector:
    distance: float       # How much to penalize distance cost of insertion
    urgency: float        # How much to prioritize customers with tight deadlines
    waiting: float        # How much to penalize waiting time
    delivery_risk: float  # How much to prioritize high-risk (likely-to-be-missed) customers
```

**Helper functions:**

| Function | Returns |
|---|---|
| `get_default_weights()` | `WeightVector(distance=0.4, urgency=0.3, waiting=0.1, delivery_risk=0.2)` |
| `get_weight_bounds()` | Dict of `{feature: (min, max)}` → all are `(0.0, 1.0)` |

---

## How WeightVector is used

```
WeightVector
    │
    ▼
ScoreCalculator.compute_scores(candidates, weights)
    │
    score = w_dist   × norm_distance
          + w_urg    × norm_urgency
          + w_wait   × norm_waiting
          + w_risk   × norm_delivery_risk
    │
    ▼
solver picks the candidate with the LOWEST score
```

The Bayesian optimizer changes the 4 weights trial by trial to find the best combination.

---

## Why `frozen=True`?

Both `SettingsConfig` and `WeightVector` are `frozen=True` dataclasses, meaning their values  
**cannot be changed after creation**. This prevents accidental mutation during a solve run.
