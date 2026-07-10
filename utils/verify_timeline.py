import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from preprocessing.dataset_loader import DatasetLoader
from solver.greedy_solver import GreedySolver
from config.weights_config import WeightVector

def mins_to_time(m):
    h = int(m // 60)
    mn = int(m % 60)
    am_pm = "AM"
    if h >= 24: h -= 24
    if h >= 12:
        am_pm = "PM"
        if h > 12: h -= 12
    if h == 0: h = 12
    return f"{h:02d}:{mn:02d} {am_pm}"

def calculate_optimal_start_time(problem, route, day: int) -> float:
    if len(route) <= 2:
        return 0.0
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
        return max(0.0, (max_depart // 10) * 10)
    return 0.0

print("Đang tải dữ liệu và chạy solver (vui lòng đợi vài giây)...\n")
loader = DatasetLoader()
problem = loader.build_problem_instance("Data_B/locations.csv", "Data_B/time_windows.csv")
solver = GreedySolver(problem)
weights = WeightVector(
    distance=0.04937285751085062, 
    urgency=0.7116648907564567, 
    waiting=0.48155705278840216, 
    delivery_risk=0.9061216371003185
)
state = solver.solve_complete_problem(weights)
routes = state.get_completed_routes()

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

print("="*80)
print("CHI TIẾT LỊCH TRÌNH VÀ THỜI GIAN GIAO HÀNG (TERMINAL VIEW)")
print("="*80)

for day in range(1, 8):
    route = routes[day]
    if len(route) <= 2:
        continue
        
    shift_start = calculate_optimal_start_time(problem, route, day)
    
    print(f"\n--- DAY {day} ({days[day-1]}) ---")
    print(f"Giờ xe xuất phát từ DEPOT (Tự động tối ưu): {mins_to_time(shift_start)}")
    print(f"Lộ trình gốc từ bộ nhớ thuật toán: {route}")
    print("-" * 80)
    print(f"{'Stop':<5} | {'Customer':<10} | {'Arrival':<10} | {'Wait':<6} | {'All Windows (Mở-Đóng)':<35} | {'Service Start':<13} | {'Departure'}")
    print("-" * 80)
    
    current_time = shift_start
    prev_id = "DEPOT"
    
    for i, cid in enumerate(route):
        if i == 0: continue # Bỏ qua điểm đầu tiên (DEPOT)
        
        tt = problem.get_travel_time(prev_id, cid)
        arrival = current_time + tt
        
        if cid == "DEPOT":
            print(f"{i:<5} | {'DEPOT':<10} | {mins_to_time(arrival):<10} | {'-':<6} | {'-':<35} | {'-':<13} | {'-'}")
            break
            
        cust = problem.get_customer(cid)
        windows = cust.get_windows_for_day(day)
        
        # Tìm window hợp lệ
        valid_window = None
        for w in sorted(windows, key=lambda x: x.start_time):
            if max(arrival, w.start_time) + cust.service_duration <= w.end_time:
                valid_window = w
                break
                
        wait = max(0.0, valid_window.start_time - arrival) if valid_window else 0.0
        service_start = arrival + wait
        departure = service_start + cust.service_duration
        
        # In ra TẤT CẢ các khung giờ của khách hàng trong ngày đó để user không bị nhầm lẫn
        all_windows_str = ", ".join([f"{mins_to_time(w.start_time)}-{mins_to_time(w.end_time)}" for w in windows])
        
        print(f"{i:<5} | {cid:<10} | {mins_to_time(arrival):<10} | {f'{wait:.1f}m':<6} | {all_windows_str:<35} | {mins_to_time(service_start):<13} | {mins_to_time(departure)}")
        
        current_time = departure
        prev_id = cid

print("\n" + "="*80)
print("Hoàn thành in lịch trình. Bạn có thể kiểm tra từng dòng thời gian.")
print("="*80)
