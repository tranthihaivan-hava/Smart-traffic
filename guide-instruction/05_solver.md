# 05 — `solver/` Folder Guide

## Purpose

This folder contains the **core construction algorithm**.  
Given a `Problem` and a `WeightVector`, it builds a complete 7-day delivery schedule (`State`).

The approach is a **greedy insertion heuristic** — it picks one customer at a time,  
scores every possible way to insert them, and chooses the best option.

---

## The Inner Loop (How One Day Is Built)

```
REPEAT until no more customers can fit today:
  │
  ├─ 1. SolomonInsertion.generate_candidates(state)
  │         → for each pending customer (top 45 nearest):
  │             → for each position in today's route:
  │                 → simulate inserting them there
  │                 → if feasible → create a Candidate
  │
  ├─ 2. FeatureExtractor.extract_features(candidates, state, day)
  │         → compute 4 raw numbers for each Candidate:
  │             distance_delta, urgency, wait_time, delivery_risk
  │
  ├─ 3. Normalizer.normalize(candidates)
  │         → min-max scale each feature to [0.0, 1.0]
  │
  ├─ 4. ScoreCalculator.compute_scores(candidates, weights)
  │         → score = w1*dist + w2*urg + w3*wait + w4*risk
  │
  ├─ 5. Pick candidate with LOWEST score
  │
  └─ 6. State.commit_insertion(customer_id, index, arrival, wait)
             → insert into today's route
             → remove from pending_queue
             → recalculate all timing
```

---

## Files

---

### `greedy_solver.py` — `GreedySolver`  ⭐ Main Solver

The top-level solver that orchestrates everything.

```python
class GreedySolver:
    problem: Problem
    solomon: SolomonInsertion
    extractor: FeatureExtractor
    normalizer: Normalizer
    scorer: ScoreCalculator
    local_search: LocalSearch
```

**Key methods:**

| Method | What it does |
|---|---|
| `solve_day(state, day, weights, use_local_search)` | Runs the inner loop for one day, then optionally runs local search |
| `solve_complete_problem(weights, use_local_search)` | Calls `solve_day()` for all 7 days, returns completed `State` |
| `_apply_candidate(state, candidate)` | Commits the chosen insertion and recalculates timing |
| `_recalculate_route_timing(state)` | Re-simulates the full route to update all arrival/wait times |

**`_recalculate_route_timing` detail:**  
After every insertion, it re-walks the route from DEPOT to recalculate:
- `current_load` (sum of all demands on today's route)
- `arrival_time` and `wait_time` for every stop

This is needed because inserting a new customer shifts the timing of all subsequent stops.

---

### `solomon_insertion.py` — `SolomonInsertion`

Generates **all feasible `Candidate` insertions** for the current state.

**Performance optimization:**  
Instead of testing all pending customers, it only considers the **45 closest** to the last node  
in the current route. This reduces work from O(N²) to O(45 × route_length).

**For each (customer, position) pair, `_evaluate_insertion` does:**
1. Constructs the proposed new route (with customer inserted)
2. Checks capacity constraint
3. Simulates the full timeline from DEPOT
4. At each stop, finds a valid time window (arrives before it closes)
5. If any stop has no valid window → **infeasible** → return `None`
6. If all feasible → computes `distance_delta = d(i→customer) + d(customer→j) - d(i→j)`
7. Returns a `Candidate` object

> `distance_delta` is the **extra distance** added to the route by inserting this customer  
> between the previous node `i` and the next node `j`.

---

### `feature_extractor.py` — `FeatureExtractor`

Computes **4 raw feature values** for each `Candidate` (stored in `cand.raw_features`).

| Feature | Formula | Intuition |
|---|---|---|
| `distance` | `candidate.distance_delta` | How much extra km does this insertion cost? |
| `urgency` | `window_end - current_time` | How much time is left before this window closes? (lower = more urgent) |
| `waiting` | `candidate.wait_time` | How long does the vehicle idle before service starts? |
| `delivery_risk` | `1.0 / (remaining_windows × remaining_days)` | How likely is it we'll miss this customer if we skip them today? (higher = more risky) |

---

### `normalizer.py` — `Normalizer`

Applies **min-max normalization** across all candidates so features are on the same scale.

```python
normalized = (value - min_value) / (max_value - min_value + ε)
```

**Special rule for `delivery_risk`:**  
`delivery_risk` is inverted: `1.0 - normalized`  
→ Because a HIGH raw risk means we should PRIORITIZE this customer (want a LOW score for them).

> Without normalization, a feature with large values (e.g. distance in km)  
> would dominate features with small values (e.g. risk ≈ 0.01) regardless of weights.

---

### `score_calculator.py` — `ScoreCalculator`

Computes the final **weighted composite score** for each candidate.

```python
score = w_distance      × norm_features["distance"]
      + w_urgency       × norm_features["urgency"]
      + w_waiting       × norm_features["waiting"]
      + w_delivery_risk × norm_features["delivery_risk"]
```

Stored in `candidate.score`. The solver then picks `min(candidates, key=lambda c: c.score)`.

---

### `baselines.py` — `BaselineSolver`

Provides two simpler solvers used for **comparison** in `run_comparison.py`.

| Method | Strategy |
|---|---|
| `solve_nearest_neighbor()` | Always pick the closest pending customer from the current location |
| `solve_earliest_deadline_first()` | Always pick the customer whose time window closes soonest |

Both reuse `SolomonInsertion` for feasibility checking but use a fixed, simple selection rule  
instead of the weighted score system.

---

### `normalizer.py` — `Normalizer`

*(Already covered above — same file.)*

---

## Solver Pipeline Summary

```
Problem + WeightVector
        │
        ▼
GreedySolver.solve_complete_problem()
        │
        ├── Day 1:
        │     SolomonInsertion → [Candidate, ...]
        │     FeatureExtractor → raw_features
        │     Normalizer       → norm_features
        │     ScoreCalculator  → score
        │     pick best → commit → recalculate timing
        │     ... repeat until day full ...
        │     LocalSearch.improve_day_route()
        │
        ├── Day 2: (same)
        │     ...
        │
        └── Day 7: (same)
              │
              ▼
           State  (complete 7-day schedule)
```
