import sys
import os
import time

# Add root folder to python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from preprocessing.dataset_loader import DatasetLoader
from solver.greedy_solver import GreedySolver
from solver.baselines import BaselineSolver
from config.weights_config import get_default_weights
from optimizer.objective_function import ObjectiveFunction
from optimizer.bayesian_optimizer import BayesianOptimizer

def run_evaluation(name, state, problem, evaluator):
    total_loss = evaluator.evaluate(state, problem)
    unserved_count = evaluator._count_failed_deliveries(state)
    total_distance = evaluator._calculate_total_distance(state, problem)
    total_waiting = evaluator._calculate_total_waiting(state, problem)
    
    print(f"\n{name} Results:")
    print(f"  - Failed Deliveries: {unserved_count}")
    print(f"  - Total Distance: {total_distance:.2f} km")
    print(f"  - Total Waiting Time: {total_waiting:.2f} minutes")
    print(f"  - Loss (Score): {total_loss:.4f}")
    
    return {
        "name": name,
        "unserved": unserved_count,
        "distance": total_distance,
        "waiting": total_waiting,
        "loss": total_loss
    }

def main():
    print("====================================================")
    print(" SMART-TRAFFIC: Route Optimization & Hyperparameter Tuning ")
    print("====================================================")
    
    loader = DatasetLoader()
    locations_path = "Data_B/locations.csv"
    windows_path = "Data_B/time_windows.csv"
    
    problem = loader.build_problem_instance(locations_path, windows_path)
    evaluator = ObjectiveFunction(unserved_penalty=10000.0)
    
    results = []

    # 1. Nearest Neighbor Baseline
    print("\nRunning Baseline 1: Nearest Neighbor...")
    start_time = time.time()
    nn_solver = BaselineSolver(problem)
    nn_state = nn_solver.solve_nearest_neighbor()
    results.append(run_evaluation("Nearest Neighbor Baseline", nn_state, problem, evaluator))
    print(f"Execution Time: {time.time() - start_time:.2f} seconds")

    # 2. Earliest Deadline First Baseline
    print("\nRunning Baseline 2: Earliest Deadline First (EDF)...")
    start_time = time.time()
    edf_solver = BaselineSolver(problem)
    edf_state = edf_solver.solve_earliest_deadline_first()
    results.append(run_evaluation("Earliest Deadline First", edf_state, problem, evaluator))
    print(f"Execution Time: {time.time() - start_time:.2f} seconds")

    # 3. Greedy Solomon Solver with Default Weights + Local Search
    print("\nRunning Heuristic Solver with Default Weights + Local Search...")
    start_time = time.time()
    greedy_solver = GreedySolver(problem)
    default_weights = get_default_weights()
    default_state = greedy_solver.solve_complete_problem(default_weights)
    results.append(run_evaluation("Proposed Heuristic (Default Weights)", default_state, problem, evaluator))
    print(f"Execution Time: {time.time() - start_time:.2f} seconds")

    # 4. Bayesian Optimizer + Solomon Solver + Local Search
    print("\nRunning Bayesian Meta-Optimization (Optuna - 100 Trials) + Local Search...")
    start_time = time.time()
    opt = BayesianOptimizer(problem, greedy_solver, evaluator)
    best_weights = opt.optimize(n_trials=100)
    best_state = greedy_solver.solve_complete_problem(best_weights)
    results.append(run_evaluation("Proposed Heuristic (Optuna Optimized)", best_state, problem, evaluator))
    print(f"Execution Time: {time.time() - start_time:.2f} seconds")
    print(f"Optimal Weights Discovered: {best_weights}")

    # Display Comparison Table and write to comparison.txt
    summary_lines = []
    summary_lines.append("====================================================================================")
    summary_lines.append("                                   COMPARISON SUMMARY                               ")
    summary_lines.append("====================================================================================")
    summary_lines.append(f"{'Algorithm / Policy':<40} | {'Unserved':<8} | {'Distance (km)':<15} | {'Wait Time (m)':<15} | {'Loss Score':<12}")
    summary_lines.append("-" * 92)
    for r in results:
        summary_lines.append(f"{r['name']:<40} | {r['unserved']:<8} | {r['distance']:15.2f} | {r['waiting']:15.2f} | {r['loss']:12.4f}")
    summary_lines.append("====================================================================================")

    summary_text = "\n".join(summary_lines)
    print("\n" + summary_text)
    
    # Save detailed comparison report to comparison.txt
    with open("comparison.txt", "w", encoding="utf-8") as f:
        f.write("SMART-TRAFFIC SYSTEM COMPARISON REPORT\n")
        f.write("======================================\n\n")
        for r in results:
            f.write(f"Algorithm: {r['name']}\n")
            f.write(f"  - Failed Deliveries: {r['unserved']}\n")
            f.write(f"  - Total Distance: {r['distance']:.2f} km\n")
            f.write(f"  - Total Waiting Time: {r['waiting']:.2f} minutes\n")
            f.write(f"  - Loss Score: {r['loss']:.4f}\n\n")
        f.write("\n" + summary_text + "\n\n")
        f.write("Optimal Weights Discovered:\n")
        f.write(f"  - Distance Weight: {best_weights.distance}\n")
        f.write(f"  - Urgency Weight: {best_weights.urgency}\n")
        f.write(f"  - Waiting Time Weight: {best_weights.waiting}\n")
        f.write(f"  - Delivery Risk Weight: {best_weights.delivery_risk}\n")
        
    print("\nResults successfully saved to comparison.txt!")

if __name__ == "__main__":
    main()

