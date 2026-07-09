# 04 — `preprocessing/` Folder Guide

## Purpose

This folder **reads raw CSV files** and transforms them into a fully built `Problem` object  
that the solver can use. It is called once at startup.

---

## Files

---

### `csv_loader.py` — `CSVLoader`

The lowest-level reader. Opens CSV files and returns a list of row dictionaries.

```python
class CSVLoader:
    def load_locations(filepath) -> List[Dict[str, str]]
    def load_time_windows(filepath) -> List[Dict[str, str]]
```

**What it does:**
1. Opens the file using Python's built-in `csv.DictReader`
2. Strips whitespace from all keys and values
3. Calls `validators.validate_location_row()` or `validate_window_row()` on every row
4. Returns a raw list of dicts like `{"location_id": "C001", "x_km": "12.5", ...}`

> Everything is still a **string** at this point. Parsing to `float`/`int` happens in `DatasetLoader`.

---

### `validators.py` (in `utils/`) — called from here

Before any row is accepted, these functions check it:

- `validate_location_row`: ensures `location_id`, `x_km`, `y_km`, `demand_kg`, `service_time` exist and are numeric
- `validate_window_row`: ensures `location_id`, `day_of_week`, `start_time`, `end_time` exist and time format is `"HH:MM"`

If any row is invalid, a `KeyError` or `ValueError` is raised immediately.

---

### `distance_matrix.py` — `DistanceMatrix`

Builds a full **N×N Euclidean distance table** between every pair of locations (including depot).

```python
class DistanceMatrix:
    nodes: Dict[str, Customer]           # All locations by ID
    matrix: Dict[str, Dict[str, float]]  # matrix[from_id][to_id] = distance in km
```

**How it's built:**
```python
dist = sqrt((x1 - x2)² + (y1 - y2)²)   # Pure Euclidean distance
```

This is computed **once at startup** for all pairs. After that, `get_distance(from_id, to_id)` is an O(1) dictionary lookup.

**Key method:**

| Method | Returns |
|---|---|
| `get_distance(from_id, to_id)` | Distance in km between two location IDs |

---

### `travel_time_matrix.py` — `TravelTimeMatrix`

Wraps `DistanceMatrix` and converts distance to **travel time in minutes**.

```python
class TravelTimeMatrix:
    distance_matrix: DistanceMatrix
    speed_kmh: float          # from settings (50.0 km/h)
    service_times: Dict[str, float]
```

**Formula:**
```
travel_time (minutes) = (distance_km / speed_kmh) × 60
```

**Example:** 10 km at 50 km/h → `(10 / 50) × 60 = 12.0 minutes`

**Key methods:**

| Method | Returns |
|---|---|
| `get_travel_time(from_id, to_id)` | Drive time in minutes between two IDs |
| `get_service_time(customer_id)` | How long to serve this customer (from CSV) |

---

### `dataset_loader.py` — `DatasetLoader`  ⭐ Main Entry Point

Orchestrates everything. Takes two CSV paths, returns a complete `Problem`.

```python
class DatasetLoader:
    def build_problem_instance(locations_path, windows_path) -> Problem
```

**Step-by-step what it does:**

```
1. CSVLoader.load_time_windows()
        → parse "HH:MM" → float minutes
        → group windows by customer ID
        → build Dict[customer_id → List[DeliveryWindow]]

2. CSVLoader.load_locations()
        → for each row:
            → parse x, y, demand, service_time to float
            → look up that customer's DeliveryWindows
            → create Customer object
            → if location_id == "DEPOT" → store as depot
            → else → add to customers dict

3. DistanceMatrix(customers, depot)
        → compute all pairwise distances

4. TravelTimeMatrix(dist_matrix, speed, service_times)
        → wrap distances for time queries

5. return Problem(depot, customers, dist_matrix, time_matrix, max_days, capacity)
```

**`_parse_time()` helper:**
```python
def _parse_time("08:30") -> 510.0
# Parts: ["08", "30"] → 8*60 + 30 = 510.0 minutes
```

---

## Full Data Flow

```
locations.csv ──► CSVLoader.load_locations()
                       │ (validate each row)
                       ▼
              List[Dict[str,str]]   ← raw strings
                       │
                       ▼
              DatasetLoader parses floats
              + creates Customer objects
                       │
                       ▼
              DistanceMatrix(customers, depot)
                       │
                       ▼
              TravelTimeMatrix(dist_matrix, speed, service_times)
                       │
                       ▼
              Problem(depot, customers, dist, time, max_days, capacity)


time_windows.csv ──► CSVLoader.load_time_windows()
                          │ (validate each row)
                          ▼
                 List[Dict[str,str]]   ← raw strings
                          │
                          ▼
                 DatasetLoader._parse_time()
                 + creates DeliveryWindow objects
                          │
                          ▼
                 Attached to each Customer.windows
```
