import os
import sys
import math
import csv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from preprocessing.dataset_loader import DatasetLoader
from solver.greedy_solver import GreedySolver
from config.weights_config import WeightVector

def brute_force_proofcheck():
    print("="*60)
    print("BẮT ĐẦU BRUTE-FORCE PROOFCHECK BẰNG TOÁN HỌC THUẦN TÚY")
    print("="*60)
    
    # 1. Đọc chay Data từ CSV để không phụ thuộc vào object
    locs = {}
    with open('Data_B/locations.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            locs[row['location_id']] = {
                'x': float(row['x_km']),
                'y': float(row['y_km']),
                'service_time': float(row['service_time'])
            }
            
    windows = {}
    with open('Data_B/time_windows.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cid = row['location_id']
            day = int(row['day_of_week'])
            
            def parse_time(t_str):
                h, m = map(int, t_str.split(':'))
                return float(h*60 + m)
                
            w = (parse_time(row['start_time']), parse_time(row['end_time']))
            
            if cid not in windows:
                windows[cid] = {}
            if day not in windows[cid]:
                windows[cid][day] = []
            windows[cid][day].append(w)
            
    print("[1] Đã nạp tọa độ và time windows thô từ file CSV.")
    
    # 2. Sinh route từ model
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
    
    print("[2] Đã sinh xong lộ trình. Bắt đầu đối chiếu Euclidean distance brute-force...\n")
    
    total_brute_force_distance = 0.0
    violation_count = 0
    
    for day in range(1, 8):
        route = routes[day]
        if len(route) <= 2: continue
        
        # Brute force Shift Start Time
        first_cust = route[1]
        x1, y1 = locs['DEPOT']['x'], locs['DEPOT']['y']
        x2, y2 = locs[first_cust]['x'], locs[first_cust]['y']
        
        # Euclidean Math
        dist = math.sqrt((x1-x2)**2 + (y1-y2)**2)
        travel_time = (dist / 50.0) * 60.0
        
        w_list = sorted(windows[first_cust][day], key=lambda x: x[0])
        valid_w = None
        for w in w_list:
            if max(travel_time, w[0]) + locs[first_cust]['service_time'] <= w[1]:
                valid_w = w
                break
        
        shift_start = max(0.0, ((valid_w[0] - travel_time) // 10) * 10) if valid_w else 0.0
        
        current_time = shift_start
        prev_id = 'DEPOT'
        
        day_dist = 0.0
        for i, cid in enumerate(route):
            if i == 0: continue
            
            x1, y1 = locs[prev_id]['x'], locs[prev_id]['y']
            x2, y2 = locs[cid]['x'], locs[cid]['y']
            dist = math.sqrt((x1-x2)**2 + (y1-y2)**2)
            day_dist += dist
            tt = (dist / 50.0) * 60.0
            
            arrival = current_time + tt
            
            if cid == 'DEPOT':
                current_time = arrival
                break
                
            w_list = sorted(windows[cid][day], key=lambda x: x[0])
            valid_w = None
            service_dur = locs[cid]['service_time']
            for w in w_list:
                if max(arrival, w[0]) + service_dur <= w[1]:
                    valid_w = w
                    break
                    
            if not valid_w:
                print(f"!!! LỖI VI PHẠM TẠI {cid} NGÀY {day}: Đến lúc {arrival}, nhưng ko có window nào hợp lệ trong {w_list}")
                violation_count += 1
                
            wait = max(0.0, valid_w[0] - arrival)
            service_start = arrival + wait
            current_time = service_start + service_dur
            prev_id = cid
            
        print(f"Day {day} -> Đã kiểm tra thuần toán học. Số khách hàng: {len(route)-2}. Quãng đường: {day_dist:.2f} km.")
        total_brute_force_distance += day_dist
        
    print("\n" + "="*60)
    print(f"TỔNG KẾT BRUTE-FORCE THỦ CÔNG:")
    print(f"- Số lỗi vi phạm ranh giới thời gian (Time Constraint Violations): {violation_count}")
    print(f"- Tổng quãng đường tính chay bằng tay (Euclidean Math): {total_brute_force_distance:.2f} km")
    print("="*60)

if __name__ == "__main__":
    brute_force_proofcheck()
