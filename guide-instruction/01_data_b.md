# 01 — `Data_B/` Folder Guide

## Purpose

This folder is the **only external input** to the entire system.  
It contains two CSV files that describe the delivery problem.

---

## Files

### `locations.csv`

Each row is one delivery location (or the depot).

| Column | Type | Meaning |
|---|---|---|
| `location_id` | string | Unique ID — `"DEPOT"` for the warehouse, `"C001"` etc. for customers |
| `x_km` | float | X coordinate in kilometers on a 2D map |
| `y_km` | float | Y coordinate in kilometers on a 2D map |
| `demand_kg` | float | How many kg of goods this customer needs |
| `service_time` | float | Minutes it takes to unload and serve this customer |

**Example row:**
```
location_id, x_km, y_km, demand_kg, service_time
C001,        12.5, 8.3,  25.0,      15.0
DEPOT,       0.0,  0.0,  0.0,       0.0
```

> The DEPOT row has `demand_kg = 0` and `service_time = 0`. It is the start and end of every route.

---

### `time_windows.csv`

Each row says: *"Customer X can receive delivery on day D, between start and end time."*

| Column | Type | Meaning |
|---|---|---|
| `location_id` | string | Which customer this window belongs to |
| `day_of_week` | int | Day number: 1 = Monday, 7 = Sunday |
| `start_time` | string | Earliest delivery time in `"HH:MM"` format |
| `end_time` | string | Latest delivery time in `"HH:MM"` format |

**Example rows:**
```
location_id, day_of_week, start_time, end_time
C001,        1,           08:00,      12:00
C001,        3,           14:00,      17:00
C002,        2,           09:30,      11:00
```

> One customer can have **multiple windows** across different days.  
> The solver will try to serve them on whichever day it can fit them best.

---

## How times are stored internally

The `DatasetLoader` converts `"HH:MM"` strings into **minutes from midnight**:

```python
"08:00"  →  480.0   (8 × 60)
"14:30"  →  870.0   (14 × 60 + 30)
```

This makes all arithmetic (arrival time, wait time) simple subtraction/addition.

---

## What happens to this data

```
locations.csv  ──┐
                 ├──► DatasetLoader.build_problem_instance()
time_windows.csv ─┘         │
                             ▼
                         Problem object
                    (contains all Customers,
                     DistanceMatrix,
                     TravelTimeMatrix)
```
