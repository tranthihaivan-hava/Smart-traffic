import sys
import os
import time

# Thêm thư mục gốc vào biến môi trường để import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from preprocessing.dataset_loader import DatasetLoader
from solver.greedy_solver import GreedySolver
from optimizer.objective_function import ObjectiveFunction
from optimizer.bayesian_optimizer import BayesianOptimizer

def main():
    print("=========================================================")
    print(" SMART-TRAFFIC: BAYESIAN OPTIMIZATION (WEIGHT TRAINING) ")
    print("=========================================================")
    
    # 1. Load Data
    print("\n[1] Loading datasets...")
    loader = DatasetLoader()
    problem = loader.build_problem_instance("Data_B/locations.csv", "Data_B/time_windows.csv")
    print(f"Loaded problem with {len(problem.customers)} customers.")
    
    # 2. Setup Solver & Evaluator
    solver = GreedySolver(problem)
    # Penalty rất lớn để AI sợ việc bỏ sót khách hàng (Unserved)
    evaluator = ObjectiveFunction(unserved_penalty=100000.0)
    
    # 3. Setup Optuna Optimizer
    opt = BayesianOptimizer(problem, solver, evaluator)
    
    # 4. Bắt đầu Train
    n_trials = 100
    print(f"\n[2] Starting Optuna with {n_trials} trials...")
    start_time = time.time()
    
    best_weights = opt.optimize(n_trials=n_trials)
    
    print(f"\n✅ Training completed in {time.time() - start_time:.2f} seconds.")
    print("=========================================================")
    print("🌟 NEW OPTIMAL WEIGHTS DISCOVERED 🌟")
    print("=========================================================")
    print(f"distance      = {best_weights.distance}")
    print(f"urgency       = {best_weights.urgency}")
    print(f"waiting       = {best_weights.waiting}")
    print(f"delivery_risk = {best_weights.delivery_risk}")
    print("=========================================================")
    print("Cách dùng: Hãy copy 4 giá trị trên và dán đè vào biến 'weights' trong file main.py và visualize/generate_visuals.py")

if __name__ == "__main__":
    main()
