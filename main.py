import sys
import os

# Add root folder to python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from preprocessing.dataset_loader import DatasetLoader
from solver.greedy_solver import GreedySolver
from optimizer.objective_function import ObjectiveFunction
from optimizer.bayesian_optimizer import BayesianOptimizer
from utils.logger import logger

def main():
    logger.info("Starting SMART-TRAFFIC optimization system...")
    
    # Paths
    locations_path = "Data_B/locations.csv"
    windows_path = "Data_B/time_windows.csv"
    
    if not os.path.exists(locations_path) or not os.path.exists(windows_path):
        logger.error("Dataset files locations.csv or time_windows.csv not found in Data_B/")
        return

    logger.info(f"Loading datasets from {locations_path} and {windows_path}...")
    loader = DatasetLoader()
    problem = loader.build_problem_instance(locations_path, windows_path)
    
    logger.info(f"Loaded problem instance: {len(problem.get_all_customers())} customers, {problem.max_days} planning days.")
    
    # Solvers & Optimizers
    greedy_solver = GreedySolver(problem)
    evaluator = ObjectiveFunction(unserved_penalty=10000.0)
    
    # We use the best weights discovered by previous Bayesian Optimization (Optuna)
    from config.weights_config import WeightVector
    best_weights = WeightVector(distance=0.04937285751085062, urgency=0.7116648907564567, waiting=0.48155705278840216, delivery_risk=0.9061216371003185)
    
    logger.info("Running complete solver with best optimized weights (Greedy + Local Search + Repair Operator)...")
    
    # Solve one final time with the best weights to print final route details
    final_state = greedy_solver.solve_complete_problem(best_weights)
    final_loss = evaluator.evaluate(final_state, problem)
    unserved = evaluator._count_failed_deliveries(final_state)
    dist = evaluator._calculate_total_distance(final_state, problem)
    wait = evaluator._calculate_total_waiting(final_state, problem)
    
    logger.info("=== Final Optimal Schedule Details ===")
    logger.info(f"Failed Deliveries: {unserved}")
    logger.info(f"Total Traveled Distance: {dist:.2f} km")
    logger.info(f"Total Waiting Time: {wait:.2f} minutes")
    logger.info(f"Global Objective Loss: {final_loss:.4f}")
    
    routes = final_state.get_completed_routes()
    for day in sorted(routes.keys()):
        route = routes[day]
        logger.info(f"Day {day} Route ({len(route) - 2 if len(route) > 2 else 0} customers): {' -> '.join(route)}")

if __name__ == "__main__":
    main()
