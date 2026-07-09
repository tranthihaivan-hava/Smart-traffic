# SMART-TRAFFIC — Project Overview

## What this project solves

This project solves the **Vehicle Routing Problem with Time Windows (VRPTW)**:

> A single delivery vehicle must serve ~300 customers over **7 working days**.  
> Each customer has a specific day and time window when they accept delivery.  
> The goal is to **minimize** total distance traveled, waiting time, and the number of missed deliveries.

---

## The Full Pipeline

```
┌─────────────────────────────────────────────────────────────────────┐
│  Data_B/                  Raw CSV files (input data)                │
│  locations.csv            → where each customer is, what they need  │
│  time_windows.csv         → when each customer accepts delivery      │
└───────────────────────────────────┬─────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│  preprocessing/           Parse CSVs → build Problem object         │
│  csv_loader.py            → read and validate raw rows              │
│  dataset_loader.py        → assemble Customer + DeliveryWindow objs │
│  distance_matrix.py       → compute Euclidean N×N distance table    │
│  travel_time_matrix.py    → convert distances to travel times       │
└───────────────────────────────────┬─────────────────────────────────┘
                                    │  returns Problem
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│  models/                  Pure data structures (no logic)           │
│  customer.py              → one delivery stop                       │
│  delivery_window.py       → one (day, start, end) time slot        │
│  pending_queue.py         → the set of unserved customers           │
│  problem.py               → the complete problem (customers+matrix) │
│  state.py                 → the schedule being built day by day     │
│  candidate.py             → a possible customer insertion           │
│  vehicle.py               → vehicle model (capacity, route)         │
└───────────────────────────────────┬─────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│  config/                  Global constants and tunable parameters   │
│  settings.py              → depot ID, speed, capacity, max_days     │
│  weights_config.py        → WeightVector (4 floats to tune)         │
└───────────────────────────────────┬─────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│  solver/                  Build a 7-day schedule greedily           │
│  greedy_solver.py         → outer loop: day-by-day construction     │
│  solomon_insertion.py     → generates all feasible insertions       │
│  feature_extractor.py     → computes 4 features per candidate       │
│  normalizer.py            → min-max scales features to [0, 1]       │
│  score_calculator.py      → weighted sum → single score             │
│  baselines.py             → simpler solvers for comparison          │
└───────────────────────────────────┬─────────────────────────────────┘
                                    │  returns State
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│  optimizer/               Find the best WeightVector                │
│  objective_function.py    → Loss = penalty×failed + dist + 0.5×wait │
│  bayesian_optimizer.py    → Optuna TPE search over 100 trials       │
│  local_search.py          → improve each day's route post-build     │
│  operators/               → Relocate, Swap, 2-Opt move operators    │
└───────────────────────────────────┬─────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│  utils/                   Shared helpers                            │
│  logger.py                → structured console logging              │
│  validators.py            → CSV row validation before parsing       │
└───────────────────────────────────┬─────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│  visualize/               Standalone chart generation               │
│  generate_visuals.py      → produces 5 PNG figures                  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Entry Points

| File | Purpose |
|---|---|
| `main.py` | Run the full optimization pipeline |
| `run_comparison.py` | Compare our solver vs. baselines |
| `verify_solve.py` | Validate a produced solution |
| `visualize/generate_visuals.py` | Generate all charts |

---

## Key Concept: The WeightVector

The solver ranks customer insertion candidates using a **weighted score**:

```
score = w_distance       × (normalized distance cost)
      + w_urgency        × (normalized urgency)
      + w_waiting        × (normalized wait time)
      + w_delivery_risk  × (normalized delivery risk)
```

The **Bayesian Optimizer** automatically finds the best 4 weights across 100 trials.

---

## Loss Formula

```
Loss = (failed_deliveries × 10,000) + total_distance_km + (0.5 × total_waiting_min)
```

The optimizer minimizes this value.

---

## Read the other guides

| Guide | Covers |
|---|---|
| `01_data_b.md` | Raw input data format |
| `02_config.md` | Settings and WeightVector |
| `03_models.md` | All data structure classes |
| `04_preprocessing.md` | CSV loading and matrix building |
| `05_solver.md` | Greedy construction algorithm |
| `06_optimizer.md` | Bayesian tuning and local search |
| `07_utils.md` | Logger and validators |
| `08_visualize.md` | Chart generation |
