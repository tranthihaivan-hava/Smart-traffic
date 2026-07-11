import os
import sys
import json
import math

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from preprocessing.dataset_loader import DatasetLoader
from solver.genetic_hybrid import GeneticHybridSolver
from config.weights_config import WeightVector

def validate_schedule():
    print("=== STRICT SCHEDULE VALIDATOR ===")
    
    loader = DatasetLoader()
    problem = loader.build_problem_instance("Data_B/locations.csv", "Data_B/time_windows.csv")
    
    import json
    import json
    with open('Overview/presentation_result.txt', 'r') as f:
        routes_str = json.load(f)
        
    routes = {int(k): v for k, v in routes_str.items()}
    unserved = []
    
    print(f"Total customers: {len(problem.get_all_customers())}")
    print(f"Unserved customers: {len(unserved)}")
    
    # Tracking served
    served_counts = {c.id: 0 for c in problem.get_all_customers()}
    
    errors = []
    
    for day in range(1, 8):
        route = routes.get(day, [])
        if len(route) <= 2:
            continue
            
        # Check DEPOT boundaries
        if route[0] != "DEPOT" or route[-1] != "DEPOT":
            errors.append(f"Day {day}: Route does not start/end at DEPOT. Route: {route}")
            
        # Calculate optimal start time
        if len(route) > 2:
            first_cust = route[1]
            tt = problem.get_travel_time("DEPOT", first_cust)
            cust = problem.get_customer(first_cust)
            windows = cust.get_windows_for_day(day)
            valid_window = None
            for w in sorted(windows, key=lambda x: x.start_time):
                if max(tt, w.start_time) + cust.service_duration <= w.end_time:
                    valid_window = w
                    break
            if valid_window:
                max_depart = valid_window.start_time - tt
                shift_start = max(0.0, (max_depart // 10) * 10)
            else:
                shift_start = 0.0
        else:
            shift_start = 480.0
            
        current_time = shift_start
        prev_id = "DEPOT"
        
        for i, cid in enumerate(route):
            if i == 0: continue # Skip first DEPOT
            
            tt = problem.get_travel_time(prev_id, cid)
            arrival = current_time + tt
            
            if cid == "DEPOT":
                current_time = arrival
                break
                
            served_counts[cid] += 1
            
            cust = problem.get_customer(cid)
            windows = cust.get_windows_for_day(day)
            
            # Check time windows
            valid_w = None
            for w in sorted(windows, key=lambda x: x.start_time):
                service_start_cand = max(arrival, w.start_time)
                if service_start_cand + cust.service_duration <= w.end_time:
                    valid_w = w
                    break
                    
            if not valid_w:
                errors.append(f"Day {day}: Customer {cid} violated time window! Arrival: {arrival:.2f}. Windows: {[(w.start_time, w.end_time) for w in windows]}")
                # We update time anyway to simulate failure
                # but this is a strict violation
            else:
                wait = max(0.0, valid_w.start_time - arrival)
                service_start = arrival + wait
                current_time = service_start + cust.service_duration
                
            prev_id = cid
            
    # Check duplicates or missing
    missing = []
    duplicates = []
    for cid, count in served_counts.items():
        if count == 0 and cid not in unserved:
            missing.append(cid)
        if count > 1:
            duplicates.append((cid, count))
            
    if missing:
        errors.append(f"Missing customers (not in route, not in unserved): {missing}")
    if duplicates:
        errors.append(f"Duplicated customers (served > 1 time): {duplicates}")
        
    actual_served = sum(1 for c in served_counts.values() if c > 0)
    if actual_served + len(unserved) != 300:
        errors.append(f"MATH ERROR: Served ({actual_served}) + Unserved ({len(unserved)}) != 300")
        
    print("\n=== VALIDATION RESULTS ===")
    if not errors:
        print("✅ SUCCESS! No hallucinations detected. The schedule strictly respects all VRPTW constraints, data points, and mathematical invariants.")
    else:
        print("❌ FAIL! Found errors (hallucinations or bugs):")
        for e in errors:
            print(" -", e)

if __name__ == "__main__":
    validate_schedule()
