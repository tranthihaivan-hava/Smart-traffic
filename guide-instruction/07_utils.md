# 07 — `utils/` Folder Guide

## Purpose

Shared utility helpers used across the entire codebase.  
No domain logic lives here — just tooling.

---

## Files

---

### `logger.py`

Sets up a single **global logger** that every module can import and use.

```python
logger = setup_logger()   # module-level singleton
```

**`setup_logger(name)`** creates a Python `logging.Logger` with:
- Level: `INFO` (shows INFO, WARNING, ERROR — not DEBUG)
- Output: `stdout` (printed to terminal)
- Format: `[2026-07-09 14:30:01] [INFO] [vrptw_solver]: message here`

**How to use anywhere in the project:**
```python
from utils.logger import logger

logger.info("Loading dataset...")
logger.warning("Customer C005 has no windows")
logger.error("File not found!")
```

> The `if not logger.handlers` check prevents duplicate log entries  
> if the logger is initialized more than once.

---

### `validators.py`

Contains two **pure validation functions** for CSV rows. Called by `CSVLoader` before  
any row is parsed into objects.

**`validate_location_row(row: Dict[str, str])`**

Checks that a row from `locations.csv` has:
- Required columns: `location_id`, `x_km`, `y_km`, `demand_kg`, `service_time`
- All numeric columns can be converted to `float`

Raises `KeyError` if a column is missing, `ValueError` if a value is not numeric.

---

**`validate_window_row(row: Dict[str, str])`**

Checks that a row from `time_windows.csv` has:
- Required columns: `location_id`, `day_of_week`, `start_time`, `end_time`
- `day_of_week` can be converted to `int`
- `start_time` and `end_time` follow `"HH:MM"` format (exactly one `:` separator)

Raises `KeyError` or `ValueError` on failure.

---

## Why validate early?

Validation happens at row-read time (in `CSVLoader`), **before** any objects are created.  
This gives an immediately clear error message pointing to the bad row,  
rather than a cryptic `AttributeError` deep inside the solver.

**Example error from bad data:**
```
ValueError: Invalid numeric value in locations row: {'location_id': 'C042', 'x_km': 'N/A', ...}
```
