import sys
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from preprocessing.dataset_loader import DatasetLoader
from solver.greedy_solver import GreedySolver
from config.weights_config import WeightVector
from config.settings import get_settings

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

def calculate_optimal_start_time(problem, route, day: int) -> float:
    """Tự động tính giờ xuất phát tối ưu cho mỗi ngày.
    Dựa trên khách hàng đầu tiên trong lộ trình của ngày hôm đó,
    lùi thời gian di chuyển để xe đến vừa đúng lúc window mở (hoặc sớm nhất có thể).
    """
    if len(route) <= 2:
        return 480.0
        
    first_cust = route[1]
    tt = problem.get_travel_time("DEPOT", first_cust)
    cust = problem.get_customer(first_cust)
    windows = cust.get_windows_for_day(day)
    
    valid_window = None
    # Mô phỏng đơn giản để tìm window sẽ được chọn nếu xuất phát từ 0
    for w in sorted(windows, key=lambda x: x.start_time):
        if max(tt, w.start_time) + cust.service_duration <= w.end_time:
            valid_window = w
            break
            
    if valid_window:
        max_depart = valid_window.start_time - tt
        # Làm tròn xuống mốc 10 phút gần nhất (vd: 07:53 -> 07:50)
        return max(0.0, (max_depart // 10) * 10)
    return 0.0

def generate_schedule():
    loader = DatasetLoader()
    problem = loader.build_problem_instance("Data_B/locations.csv", "Data_B/time_windows.csv")
    solver = GreedySolver(problem)
    
    weights = WeightVector(distance=0.04937285751085062, urgency=0.7116648907564567, waiting=0.48155705278840216, delivery_risk=0.9061216371003185)
    state = solver.solve_complete_problem(weights)
    
    routes = state.get_completed_routes()
    lines = []
    lines.append("# Detailed 300-Customer Delivery Schedule")
    lines.append("=========================================")
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    lines.append("\nĐây là bảng lịch trình chi tiết. Thời gian xuất phát được tự động tối ưu cho từng ngày để giảm thiểu thời gian chờ đợi tại khách hàng đầu tiên.\n")
    
    total_served = 0
    for day in range(1, 8):
        route = routes[day]
        if len(route) <= 2:
            continue
            
        shift_start = calculate_optimal_start_time(problem, route, day)
        
        lines.append(f"## Day {day} - {days[day-1]} (Shift: {mins_to_time(shift_start)})")
        lines.append("| Stop | Customer ID | Arrival | Wait | All Windows | Service Start | Service Time | Departure |")
        lines.append("| --- | --- | --- | --- | --- | --- | --- | --- |")
        
        current_time = shift_start
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
            all_windows_str = ", ".join([f"{mins_to_time(w.start_time)}-{mins_to_time(w.end_time)}" for w in windows])
            srv_str = mins_to_time(service_start)
            dur_str = f"{cust.service_duration:.0f}m"
            dep_str = mins_to_time(departure)
            
            lines.append(f"| {stop_idx:02d} | **{cid}** | {arr_str} | {wait_str} | {all_windows_str} | {srv_str} | {dur_str} | {dep_str} |")
            
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
