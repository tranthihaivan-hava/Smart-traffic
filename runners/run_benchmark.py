import time
import os
import sys

# Ensure imports work from the root directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from preprocessing.dataset_loader import DatasetLoader
from solver.baselines import BaselineSolver
from solver.greedy_solver import GreedySolver
from solver.genetic_hybrid import GeneticHybridSolver
from config.weights_config import WeightVector

def run_benchmark():
    print("="*70)
    print("   BẮT ĐẦU BENCHMARK 4 THUẬT TOÁN (VRPTW SMART-TRAFFIC)")
    print("="*70)
    print("Đang tải dữ liệu (300 khách hàng)...")
    loader = DatasetLoader()
    problem = loader.build_problem_instance("Data_B/locations.csv", "Data_B/time_windows.csv")
    
    results = []

    # -------------------------------------------------------------
    # 1. Baseline 1: Nearest Neighbor
    # -------------------------------------------------------------
    print("\n[1/4] Chạy Baseline 1: Nearest Neighbor...")
    start_time = time.time()
    baseline = BaselineSolver(problem)
    nn_state = baseline.solve_nearest_neighbor()
    t_nn = time.time() - start_time
    
    nn_unserved = len(nn_state.pending_queue.get_pending())
    nn_dist = 0.0
    for day in range(1, problem.max_days + 1):
        route = nn_state.get_route(day)
        for i in range(len(route) - 1):
            nn_dist += problem.get_distance(route[i], route[i+1])
            
    results.append(("Nearest Neighbor", t_nn, nn_unserved, nn_dist))

    # -------------------------------------------------------------
    # 2. Baseline 2: Earliest Deadline First
    # -------------------------------------------------------------
    print("\n[2/4] Chạy Baseline 2: Earliest Deadline First...")
    start_time = time.time()
    edf_state = baseline.solve_earliest_deadline_first()
    t_edf = time.time() - start_time
    
    edf_unserved = len(edf_state.pending_queue.get_pending())
    edf_dist = 0.0
    for day in range(1, problem.max_days + 1):
        route = edf_state.get_route(day)
        for i in range(len(route) - 1):
            edf_dist += problem.get_distance(route[i], route[i+1])
            
    results.append(("Earliest Deadline First", t_edf, edf_unserved, edf_dist))

    # -------------------------------------------------------------
    # 3. Proposed: Greedy Solomon + Bayesian Weights (NO REPAIR)
    # -------------------------------------------------------------
    print("\n[3/4] Chạy Proposed: Solomon + Bayesian Weights (No Repair)...")
    start_time = time.time()
    greedy_solver = GreedySolver(problem)
    # Fetch the weights obtained from Optuna training database
    import optuna
    try:
        study = optuna.load_study(study_name="boma_two_phase", storage="sqlite:///Data_B/boma_two_phase.db")
        bp = study.best_params
        best_weights = WeightVector(distance=bp["distance"], urgency=bp["urgency"], waiting=bp["waiting"], delivery_risk=bp["delivery_risk"])
        print("FOUND best_weights in the database")
    except Exception:
        print("KHÔNG TÌM THẤY FILE DATABASE, SỬ DỤNG TRỌNG SỐ TỪ run_hga_bayesian")
        best_weights = WeightVector(
            distance=0.04937285751085062, 
            urgency=0.7116648907564567, 
            waiting=0.48155705278840216, 
            delivery_risk=0.9061216371003185
        )
    print(f"      -> [Weights Loaded] Dist={best_weights.distance:.3f}, Urg={best_weights.urgency:.3f}, Wait={best_weights.waiting:.3f}, Risk={best_weights.delivery_risk:.3f}")
    # We turn off local search / repair to isolate the Greedy performance
    greedy_state = greedy_solver.solve_complete_problem(best_weights, use_local_search=False)
    t_greedy = time.time() - start_time
    
    greedy_unserved = len(greedy_state.pending_queue.get_pending())
    greedy_dist = 0.0
    for day in range(1, problem.max_days + 1):
        route = greedy_state.get_route(day)
        for i in range(len(route) - 1):
            greedy_dist += problem.get_distance(route[i], route[i+1])
            
    results.append(("Proposed (Solomon+Bayesian)", t_greedy, greedy_unserved, greedy_dist))

    # -------------------------------------------------------------
    # 4. Master Algorithm: HGA + Solomon I1 + Bayesian Weights
    # -------------------------------------------------------------
    print("\n[4/4] Chạy Master Algorithm: HGA + Bayesian (Two-Phase Inference)...")
    print("      (Phase 1: Đã train offline. Phase 2: Load Checkpoint + Local Search...)")
    start_time = time.time()
    
    import json
    with open('Data_B/final_checkpoint.json', 'r') as f:
        pop = json.load(f)
    best_chromo = pop[0]
    
    hga = GeneticHybridSolver(problem, pop_size=50, generations=30, weights=best_weights)
    hga_state, _ = hga._decode(best_chromo)
    
    unserved_count = len(hga_state.pending_queue.get_pending())
    if unserved_count > 0:
        print(f"      -> [Two-Phase Optimization] Áp dụng Local Search (Repair) để fix {unserved_count} đơn rớt...")
        hga.repair_operator.run(hga_state)
        
    t_hga = time.time() - start_time
    
    hga_unserved = len(hga_state.pending_queue.get_pending())
    hga_dist = 0.0
    for day in range(1, problem.max_days + 1):
        route = hga_state.get_route(day)
        for i in range(len(route) - 1):
            hga_dist += problem.get_distance(route[i], route[i+1])
            
    results.append(("Master Algorithm (HGA+Bayesian)", t_hga, hga_unserved, hga_dist))

    # -------------------------------------------------------------
    # 5. LƯU LỘ TRÌNH RA FILE
    # -------------------------------------------------------------
    print("\n[5/5] Đang lưu chi tiết lộ trình ra file best_routes.txt ...")
    with open("best_routes.txt", "w", encoding="utf-8") as f:
        f.write("=== LỘ TRÌNH PROPOSED (Greedy + Bayesian) ===\n")
        for day in range(1, problem.max_days + 1):
            route = greedy_state.get_route(day)
            if len(route) > 2: # Bỏ qua ngày trống (chỉ có DEPOT -> DEPOT)
                f.write(f"Ngày {day}: {' -> '.join(route)}\n")
            
        f.write("\n=== LỘ TRÌNH MASTER ALGORITHM (HGA + Bayesian) ===\n")
        for day in range(1, problem.max_days + 1):
            route = hga_state.get_route(day)
            if len(route) > 2:
                f.write(f"Ngày {day}: {' -> '.join(route)}\n")
    
    # -------------------------------------------------------------
    # BẢNG TỔNG KẾT
    # -------------------------------------------------------------
    print("\n\n" + "="*85)
    print(f"{'THUẬT TOÁN (ALGORITHM)':<35} | {'TỐC ĐỘ (giây)':<15} | {'RỚT KHÁCH (người)':<20} | {'QUÃNG ĐƯỜNG (km)':<15}")
    print("-" * 85)
    
    for name, t_time, unserved, dist in results:
        print(f"{name:<35} | {t_time:<15.2f} | {unserved:<20} | {dist:<15.2f}")
        
    print("="*85)
    print("Ghi chú:")
    print("- Proposed (Solomon+Bayesian): Chạy cực nhanh (< 1 giây), phù hợp thời gian thực.")
    print("- HGA (Genetic Hybrid): Chạy lâu hơn, nhưng có khả năng đè bẹp các baseline và ép tổng quãng đường xuống cực sâu nếu tăng Generations lên cao.")
    print("- Đã lưu chi tiết lộ trình của Proposed và HGA vào file: best_routes.txt")
    print("="*85)

if __name__ == "__main__":
    run_benchmark()
