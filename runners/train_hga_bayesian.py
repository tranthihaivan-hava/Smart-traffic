import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import optuna
import time
from models.problem import Problem
from solver.genetic_hybrid import GeneticHybridSolver
from config.weights_config import WeightVector

from preprocessing.dataset_loader import DatasetLoader

def load_problem():
    loader = DatasetLoader()
    problem = loader.build_problem_instance("Data_B/locations.csv", "Data_B/time_windows.csv")
    return problem

import os

def objective(trial):
    # CHẶN GIAN LẬN: Xóa trí nhớ của HGA trước mỗi lần thử trọng số mới
    if os.path.exists("temp_hga_checkpoint.json"):
        os.remove("temp_hga_checkpoint.json")
        
    print(f"\n--- Bắt đầu Trial {trial.number} ---")
    
    # 1. Optuna (Bayesian Optimization) generates random weights
    distance_w = trial.suggest_float("distance", 0.0, 1.0)
    urgency_w = trial.suggest_float("urgency", 0.0, 1.0)
    waiting_w = trial.suggest_float("waiting", 0.0, 1.0)
    delivery_risk_w = trial.suggest_float("delivery_risk", 0.0, 1.0)

    weights = WeightVector(
        distance=distance_w,
        urgency=urgency_w,
        waiting=waiting_w,
        delivery_risk=delivery_risk_w
    )
    
    print(f"[Optuna] Thử nghiệm Trọng số: Dist={distance_w:.2f}, Urg={urgency_w:.2f}, Wait={waiting_w:.2f}, Risk={delivery_risk_w:.2f}")

    # Load problem
    problem = load_problem()
    
    # 2. BOMA (Inner Loop)
    # Theo đúng luồng của bạn: Cho HGA sinh 20 thế hệ (gen=20), nhưng để đảm bảo tốc độ, ta giữ Pop=5
    hga = GeneticHybridSolver(problem, pop_size=5, generations=20, weights=weights)
    
    start_time = time.time()
    # Chạy HGA, không lưu checkpoint để các trial độc lập với nhau
    best_state = hga.solve(checkpoint_file="temp_hga_checkpoint.json")
    t_hga = time.time() - start_time
    
    # Tính quãng đường cuối cùng (để làm Fitness)
    unserved = len(best_state.pending_queue.get_pending())
    dist = 0.0
    for day in range(1, problem.max_days + 1):
        route = best_state.get_route(day)
        for i in range(len(route) - 1):
            dist += problem.get_distance(route[i], route[i+1])
            
    # Fitness = Số đơn rớt * 100000 + Quãng đường
    # (Ở Phase 1, ta không bật Local Search để đánh giá chính xác sức mạnh thô của HGA)
    fitness = unserved * 100000.0 + dist
    
    print(f"[Optuna] Trial {trial.number} xong trong {t_hga:.1f}s | Unserved: {unserved} | Distance: {dist:.2f}")
    return fitness

if __name__ == "__main__":
    print("======================================================================")
    print("   BẮT ĐẦU TRAINING: BOMA (Bayesian-Optimized Memetic Algorithm) ")
    print("======================================================================")
    print("Mục tiêu: Dùng Optuna nắn trọng số Bayesian cho vòng lặp HGA.")
    print("Cấu hình Demo: HGA(Pop=5, Gen=2), Optuna(n_trials=10).")
    
    # 3. Outer Loop: Chạy Optuna Optimization (Tạo DB mới cho kiến trúc Two-Phase)
    study = optuna.create_study(
        study_name="boma_two_phase", 
        storage="sqlite:///Data_B/boma_two_phase.db", 
        load_if_exists=True,
        direction="minimize"
    )
    
    # Ép Optuna bắt đầu bằng trọng số chia đều 0.25 cho 4 features (như bạn yêu cầu)
    study.enqueue_trial({
        "distance": 0.25,
        "urgency": 0.25,
        "waiting": 0.25,
        "delivery_risk": 0.25
    })
    # Theo ý bạn, chỉ chạy 20 trials để tiết kiệm thời gian chờ đợi
    study.optimize(objective, n_trials=20)

    print("\n======================================================================")
    print("QUÁ TRÌNH TRAINING HOÀN TẤT!")
    print("Trọng số tốt nhất (Best Weights) tìm được để HGA chạy mượt nhất là:")
    print(study.best_params)
    print(f"Quãng đường ngắn nhất đạt được (Fitness): {study.best_value:.2f} km")
