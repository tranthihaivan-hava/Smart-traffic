# 06 — `optimizer/` Folder Guide

## Purpose

This folder answers the question: **"What is the best WeightVector?"**

The solver needs 4 weights to score candidates. If the weights are wrong, the schedule is bad.  
This folder uses **Bayesian Optimization** (via Optuna) to automatically find the best weights  
by running the solver hundreds of times with different weight combinations.

It also contains **Local Search** — a post-construction improvement step  
that refines each day's route after the greedy solver finishes it.

---

## Files

---

### `objective_function.py` — `ObjectiveFunction`

Measures how good (or bad) a completed `State` is. Returns a single **loss number** to minimize.

```python
Loss = (failed_deliveries × penalty) + total_distance + (0.5 × total_waiting)
```

Default penalty = **10,000** — meaning one unserved customer is worth 10,000 km of distance.  
This forces the optimizer to prioritize serving everyone over saving distance.

**Three sub-calculations:**

| Method | What it measures |
|---|---|
| `_count_failed_deliveries(state)` | `state.pending_queue.get_unserved_count()` — customers left unserved |
| `_calculate_total_distance(state, problem)` | Sum of all km driven across all 7 days |
| `_calculate_total_waiting(state, problem)` | Sum of all minutes the vehicle waits at stops across all 7 days |

**`evaluate(state, problem)`** calls all three and combines them with the formula above.

---

### `bayesian_optimizer.py` — `BayesianOptimizer`

Uses **Optuna** (Tree-structured Parzen Estimator, TPE) to find the best `WeightVector`.

```python
class BayesianOptimizer:
    _problem: Problem
    _solver: GreedySolver
    _evaluator: ObjectiveFunction
    _study: optuna.study.Study
```

**How it works:**

```
optimizer.optimize(n_trials=100)
    │
    └── Optuna creates a "study" (minimize mode)
          │
          For each trial (0 to 99):
          │
          ├── Optuna's TPE sampler suggests 4 floats in [0.0, 1.0]:
          │     distance, urgency, waiting, delivery_risk
          │
          ├── Build WeightVector from those 4 floats
          │
          ├── solver.solve_complete_problem(weights, use_local_search=False)
          │     → returns a State
          │
          ├── evaluator.evaluate(state, problem)
          │     → returns a loss float
          │
          └── Optuna records (weights → loss)
                and learns which regions of weight space are promising
    │
    └── After 100 trials → return WeightVector with lowest loss
```

> `use_local_search=False` during trials for speed — local search is only  
> applied on the final solve with the best weights.

**Key methods:**

| Method | Returns |
|---|---|
| `optimize(n_trials)` | Best `WeightVector` found |
| `get_best_objective()` | The loss value of the best trial |
| `get_study()` | The raw Optuna study object (for inspection) |

---

### `local_search.py` — `LocalSearch`

A **post-construction improvement** step. After the greedy solver builds a day's route,  
local search tries small rearrangements to reduce total distance.

```python
class LocalSearch:
    operators: List[BaseOperator]   # [RelocateOperator, SwapOperator, TwoOptOperator]
```

**Algorithm (First-Improvement hill climbing):**

```
improved = True
while improved:
    improved = False
    for each operator (Relocate → Swap → 2-Opt):
        try to improve the route using this operator
        if the route changed:
            improved = True
            break  ← restart the operator loop from the beginning
```

It keeps looping until no operator can improve the route further.

**Why restart from the beginning after each improvement?**  
Because one improvement (e.g. a Relocate) may create new opportunities  
for a previously-tried operator (e.g. 2-Opt) to improve again.

---

### `operators/` — Move Operators

Each operator tries one type of small route modification.

---

#### `base_operator.py` — `BaseOperator` (Abstract)

The interface that all operators must implement:

```python
class BaseOperator(ABC):
    @abstractmethod
    def optimize_route(route, problem, day) -> List[str]:
        ...
    
    def _validate_route_constraints(route, problem, day) -> bool:
        # Shared feasibility check: capacity + time windows
        # Used by all concrete operators before accepting a move
```

`_validate_route_constraints` simulates the full timeline of a proposed route  
to confirm it doesn't violate any time windows or capacity limits.

---

#### `relocate_operator.py` — `RelocateOperator`

**Move**: Pick one customer and insert them at a different position.

```
Before: DEPOT → A → B → C → D → DEPOT
Move B elsewhere:
After:  DEPOT → A → C → B → D → DEPOT   (if this is better)
```

For every customer in the route, it tries every other insertion position.  
If the new route is shorter AND feasible → accept it.

---

#### `swap_operator.py` — `SwapOperator`

**Move**: Swap two customers' positions.

```
Before: DEPOT → A → B → C → D → DEPOT
Swap B and D:
After:  DEPOT → A → D → C → B → DEPOT   (if this is better)
```

Tries every pair of non-depot stops. Accepts the swap if the new route is shorter and feasible.

---

#### `two_opt_operator.py` — `TwoOptOperator`

**Move**: Reverse a segment of the route to untangle crossings.

```
Before: DEPOT → A → B → C → D → DEPOT
Reverse [B, C]:
After:  DEPOT → A → C → B → D → DEPOT
```

This is the classic 2-opt move from TSP research.  
Effective when the route "crosses over itself" geographically.

---

## Optimizer vs. Local Search: What's the Difference?

| | Bayesian Optimizer | Local Search |
|---|---|---|
| **Goal** | Find the best WeightVector | Improve a specific route |
| **What it changes** | The 4 weights used by the solver | The order of customers in one day's route |
| **When it runs** | Before the final solve (100 trials) | After each day is constructed |
| **Method** | Optuna TPE (probabilistic) | Greedy hill climbing with move operators |

---

## Full Optimization Flow

```
BayesianOptimizer.optimize(100 trials)
    │
    ├── Trial 1: weights=[0.3, 0.7, 0.2, 0.1] → Loss=4521.3
    ├── Trial 2: weights=[0.5, 0.4, 0.1, 0.3] → Loss=3891.7
    ├── Trial 3: weights=[0.4, 0.6, 0.1, 0.2] → Loss=3201.5
    │    ... (Optuna learns from results)
    └── Trial 100: weights=[...] → Loss=...
    │
    best_weights = trial with lowest loss
    │
    GreedySolver.solve_complete_problem(best_weights, use_local_search=True)
        │
        ├── Day 1: greedy build → LocalSearch.improve_day_route()
        ├── Day 2: greedy build → LocalSearch.improve_day_route()
        │    ...
        └── Day 7: greedy build → LocalSearch.improve_day_route()
        │
        Final State (optimal schedule)
```
