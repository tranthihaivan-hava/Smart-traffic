# SMART-TRAFFIC Algorithm Flow
==============================

This document describes the complete algorithmic pipeline used in the SMART-TRAFFIC delivery scheduling system, from raw CSV data to the final optimized weekly route.

---

## 1. High-Level System Overview

```mermaid
flowchart TD
    A([📂 Load CSV Data\nlocations.csv + time_windows.csv]) --> B[Build Problem Instance\nCustomers · Distance Matrix · Time Windows]
    B --> C{Bayesian Hyperparameter\nOptimizer\n100 Trials via Optuna TPE}
    C -->|Suggest weight vector w| D[Greedy Construction\nSolve 7 Days WITHOUT local search]
    D --> E[Objective Function\nEvaluate Loss Score]
    E -->|Return loss to Optuna| C
    C -->|Best weights found| F[Final Solve\nGreedy + Local Search with best weights]
    F --> G([📅 Final Weekly Schedule\n298 served / 300 customers])
```

---

## 2. Data Loading & Problem Setup

```mermaid
flowchart LR
    A[locations.csv\nID · Name · x_km · y_km · demand_kg · service_time] --> C[DatasetLoader]
    B[time_windows.csv\nID · day_of_week · start_time · end_time] --> C
    C --> D[Problem Instance]
    D --> E[Customer Objects\nwith per-day window lists]
    D --> F[Distance Matrix\nEuclidean km between all pairs]
    D --> G[Travel Time Matrix\ndistance / 50 km/h × 60]
    D --> H[PendingQueue\nAll 300 customers unserved]
```

**Key constants:**

| Parameter | Value |
|---|---|
| Speed limit | 50 km/h |
| Vehicle capacity | Effectively unlimited (≥ total demand) |
| Planning horizon | 7 days (Mon → Sun) |
| Penalty per unserved customer | 10,000 |

---

## 3. Greedy Construction Heuristic (Core Daily Solver)

Each day is solved using the **Solomon-style insertion heuristic**, which builds the route one customer at a time using a scored candidate pool.

```mermaid
flowchart TD
    A([Start Day d\nRoute = DEPOT]) --> B[Generate Candidates\nSolomonInsertion]
    B --> C{Any feasible\ncandidates?}
    C -- No --> G([End of Day\nAdvance to next day])
    C -- Yes --> D[Extract Features\nFeatureExtractor]
    D --> E[Normalize Features\nmin-max per batch]
    E --> F["Score Candidates\nscore = Σ wᵢ × fᵢ"]
    F --> H[Select Best\nmin score candidate]
    H --> I[Commit Insertion\nInsert into route at best index]
    I --> J[Recalculate Route Timing\narrival · wait · service_start]
    J --> B
```

### 3a. Candidate Generation — Solomon Insertion

For each greedy step, only the **45 closest pending customers** to the current last node in the route are evaluated (for speed). For each of those customers, **all valid insertion positions** in the current route are tested.

```mermaid
flowchart TD
    A[Pending Queue: remaining customers] --> B[Sort by distance to last node in route]
    B --> C[Take top 45 nearest customers]
    C --> D{For each customer u\nFor each position i in route}
    D --> E[Simulate inserting u at index i\nCheck entire new route timeline]
    E --> F{Does every customer\nstill meet its time window?}
    F -- No --> G[Discard - infeasible]
    F -- Yes --> H[Create Candidate\nwith distance_delta · arrival · wait]
    H --> D
```

**Feasibility check** for an insertion at index `i`:
- Simulate travel time from predecessor → `u` → successor
- Check that `arrival ≤ window.end` for customer `u`
- Check that all subsequent customers in the route **still meet their windows** (cascade check)
- Check vehicle capacity not exceeded

### 3b. Feature Extraction

Four features are computed per candidate:

| Feature | Formula | Meaning |
|---|---|---|
| **Distance** | `d(prev, u) + d(u, next) − d(prev, next)` | Extra km added by inserting `u` |
| **Urgency** | `window_end − current_time` | How soon the window closes |
| **Waiting** | `max(0, window_start − arrival)` | Idle time if arriving early |
| **Delivery Risk** | `1 / (remaining_windows × days_left)` | Penalty risk if skipped today |

### 3c. Scoring

Features are **min-max normalized** across the current candidate batch, then combined into a single scalar score:

```
score = w_distance × f̂_distance
      + w_urgency  × f̂_urgency
      + w_waiting  × f̂_waiting
      + w_risk     × f̂_risk
```

The candidate with the **lowest score** is selected (greedy-minimum).

---

## 4. Local Search Improvement

After the greedy route for a day is built, **three neighbourhood operators** are applied in a loop until no further improvement is found (first-improvement strategy):

```mermaid
flowchart TD
    A([Daily Route\nfrom Greedy]) --> B{Any improvement\nfound this pass?}
    B -- Yes --> C[Try Relocate Operator\nMove one node to a better position]
    C --> D{Improved?}
    D -- Yes --> B
    D -- No --> E[Try Swap Operator\nExchange two nodes]
    E --> F{Improved?}
    F -- Yes --> B
    F -- No --> G[Try 2-Opt Operator\nReverse a sub-segment]
    G --> H{Improved?}
    H -- Yes --> B
    H -- No --> I([Route Finalized\nfor this day])
    B -- No --> I
```

| Operator | What it does |
|---|---|
| **Relocate** | Removes one customer node and re-inserts it at every other position; keeps the best feasible move |
| **Swap** | Swaps two customer nodes; keeps the move if it reduces total travel time |
| **2-Opt** | Reverses a contiguous sub-sequence of the route; keeps the move if it reduces total travel time |

All moves are **feasibility-checked** — time windows must still be satisfied after every move.

---

## 5. Bayesian Hyperparameter Optimization (Optuna TPE)

The four scoring weights `(w_distance, w_urgency, w_waiting, w_risk)` are automatically tuned using **Optuna's Tree-structured Parzen Estimator (TPE)** over 100 trials.

```mermaid
flowchart TD
    A([Optuna Study\ndirection = minimize]) --> B["TPE Sampler\nSuggests weight vector w ∈ [0,1]⁴"]
    B --> C[Run GreedySolver\n7 days NO local search\nfor speed]
    C --> D["Evaluate Objective\nLoss = 10000×Failed + Distance + 0.5×Wait"]
    D --> E[Report loss to Optuna]
    E --> F{Trial 100\ncomplete?}
    F -- No --> B
    F -- Yes --> G[Extract Best Weights]
    G --> H[Final Solve\nGreedy + Local Search\nwith best weights]
    H --> I([📅 Optimal Weekly Route])
```

**Optimal weights discovered (100 trials):**

| Weight | Value |
|---|---|
| `w_distance` | 0.5628 |
| `w_urgency` | 0.3238 |
| `w_waiting` | 0.8143 |
| `w_delivery_risk` | 0.5429 |

---

## 6. Objective Function

The loss function used to evaluate any schedule:

```
Loss = (Failed Deliveries × 10,000) + Total Distance (km) + 0.5 × Total Waiting Time (min)
```

| Component | Weight | Meaning |
|---|---|---|
| **Failed deliveries** | ×10,000 | Strongly penalizes any unserved customer |
| **Total distance** | ×1 | Minimize fuel/time cost |
| **Total waiting time** | ×0.5 | Soft penalty for idle time at customers |

**Final scores achieved:**

| Method | Unserved | Loss Score |
|---|---|---|
| Nearest Neighbor Baseline | 102 | ~1,020,000+ |
| Earliest Deadline First | 13 | ~130,000+ |
| Proposed Heuristic (default weights) | 7 | ~70,000+ |
| **Proposed Heuristic (Optuna weights)** | **2** | **23,581.48** |

---

## 7. Full End-to-End Pipeline Summary

```mermaid
flowchart LR
    subgraph INPUT
        A1[locations.csv]
        A2[time_windows.csv]
    end

    subgraph SETUP
        B1[DatasetLoader]
        B2["Problem Instance\nCustomers + Windows\n+ Distance Matrix"]
    end

    subgraph OPTUNA["Bayesian Tuning (100 Trials)"]
        C1[TPE Sampler]
        C2["GreedySolver\nno local search"]
        C3[Objective\nEvaluator]
    end

    subgraph FINAL["Final Solve"]
        D1["GreedySolver\n+ Local Search"]
        D2["3 Operators:\nRelocate · Swap · 2-Opt"]
    end

    subgraph OUTPUT
        E1["Weekly Schedule\n298 / 300 served"]
        E2[route_calendar.md]
    end

    A1 --> B1
    A2 --> B1
    B1 --> B2
    B2 --> C1
    C1 -->|w vector| C2
    C2 --> C3
    C3 -->|loss| C1
    C1 -->|best w| D1
    D1 <--> D2
    D1 --> E1
    E1 --> E2
```
