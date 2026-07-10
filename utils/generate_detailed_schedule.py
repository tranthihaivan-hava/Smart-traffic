import sys
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from preprocessing.dataset_loader import DatasetLoader
from solver.greedy_solver import GreedySolver
from config.weights_config import WeightVector

def mins_to_time(m):
    h = int(m // 60)
    mn = int(m % 60)
    am_pm = "AM"
    if h >= 24:
        h -= 24 # Wrap around just in case, though it shouldn't
    
    # Absolute 24h format might be clearer for debugging, but let's stick to 12h AM/PM
    if h >= 12:
        am_pm = "PM"
        if h > 12: h -= 12
    if h == 0: h = 12
    return f"{h:02d}:{mn:02d} {am_pm}"

def generate_schedule():
    loader = DatasetLoader()
    problem = loader.build_problem_instance("Data_B/locations.csv", "Data_B/time_windows.csv")
    solver = GreedySolver(problem)
    
    weights = WeightVector(distance=0.04937285751085062, urgency=0.7116648907564567, waiting=0.48155705278840216, delivery_risk=0.9061216371003185)
    state = solver.solve_complete_problem(weights)
    
    routes = state.get_completed_routes()
    
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    lines = []
    lines.append("# Detailed 300-Customer Delivery Schedule")
    lines.append("=========================================")
    lines.append("\nĐây là bảng lịch trình chi tiết theo từng phút cho toàn bộ 300 khách hàng trong tuần. Thời gian bắt đầu làm việc mỗi ngày là 08:00 AM.\n")
    
    total_served = 0
    for day in range(1, 8):
        route = routes[day]
        if len(route) <= 2:
            continue
            
        lines.append(f"## Day {day} - {days[day-1]}")
        lines.append("| Stop | Customer ID | Arrival | Wait | Window | Service Start | Service Time | Departure |")
        lines.append("| --- | --- | --- | --- | --- | --- | --- | --- |")
        
        current_time = 480.0
        prev_id = "DEPOT"
        
        stop_idx = 1
        for i, cid in enumerate(route):
            if i == 0: continue
            tt = problem.get_travel_time(prev_id, cid)
            arrival = current_time + tt
            
            if cid == "DEPOT":
                end_time_str = mins_to_time(arrival)
                lines.append(f"| **END** | DEPOT | {end_time_str} | - | - | - | - | - |")
                break
                
            cust = problem.get_customer(cid)
            windows = cust.get_windows_for_day(day)
            
            valid_window = None
            for w in sorted(windows, key=lambda x: x.start_time):
                service_start_cand = max(arrival, w.start_time)
                service_end_cand = service_start_cand + cust.service_duration
                if service_end_cand <= w.end_time:
                    valid_window = w
                    break
                    
            wait = max(0.0, valid_window.start_time - arrival) if valid_window else 0.0
            service_start = arrival + wait
            departure = service_start + cust.service_duration
            
            arr_str = mins_to_time(arrival)
            wait_str = f"{wait:.1f}m"
            win_str = f"{mins_to_time(valid_window.start_time)} - {mins_to_time(valid_window.end_time)}"
            srv_str = mins_to_time(service_start)
            dur_str = f"{cust.service_duration:.0f}m"
            dep_str = mins_to_time(departure)
            
            lines.append(f"| {stop_idx:02d} | **{cid}** | {arr_str} | {wait_str} | {win_str} | {srv_str} | {dur_str} | {dep_str} |")
            
            current_time = departure
            prev_id = cid
            stop_idx += 1
            total_served += 1
            
        lines.append("\n---\n")

    lines.append(f"\n**Total Served:** {total_served}/300 customers.")
    
    with open("Overview/detailed_schedule.md", "w") as f:
        f.write("\n".join(lines))
        
    print(f"Detailed schedule generated successfully with {total_served} customers.")

if __name__ == "__main__":
    generate_schedule()
