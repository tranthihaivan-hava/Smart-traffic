from typing import Dict, List

def validate_location_row(row: Dict[str, str]) -> None:
    required = ["location_id", "x_km", "y_km", "demand_kg", "service_time"]
    for col in required:
        if col not in row:
            raise KeyError(f"Missing required column in locations: {col}")
    try:
        float(row["x_km"])
        float(row["y_km"])
        float(row["demand_kg"])
        float(row["service_time"])
    except ValueError as e:
        raise ValueError(f"Invalid numeric value in locations row: {row}") from e

def validate_window_row(row: Dict[str, str]) -> None:
    required = ["location_id", "day_of_week", "start_time", "end_time"]
    for col in required:
        if col not in row:
            raise KeyError(f"Missing required column in time windows: {col}")
    try:
        int(row["day_of_week"])
    except ValueError as e:
        raise ValueError(f"Invalid day_of_week value in time windows row: {row}") from e
    
    for time_col in ["start_time", "end_time"]:
        parts = row[time_col].split(':')
        if len(parts) != 2:
            raise ValueError(f"Invalid time format in row: {row} ({time_col}={row[time_col]})")
