import sys
import os

# Add root folder to python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from preprocessing.dataset_loader import DatasetLoader
from solver.greedy_solver import GreedySolver
from config.weights_config import get_default_weights
from optimizer.objective_function import ObjectiveFunction

def main():
    print("Initializing Dataset Loader...")
    loader = DatasetLoader()
    
    locations_path = "Data_B/locations.csv"
    windows_path = "Data_B/time_windows.csv"
    
    print(f"Loading data from {locations_path} and {windows_path}...")
    problem = loader.build_problem_instance(locations_path, windows_path)
    
    print("\nProblem Loaded Successfully:")
    print(f"- Total Customers: {len(problem.get_all_customers())}")
    print(f"- Max Planning Days: {problem.max_days}")
    print(f"- Vehicle Speed: 50.0 km/h")
    print(f"- Vehicle Capacity: {problem.vehicle_capacity}")
    
    # Initialize Solver
    solver = GreedySolver(problem)
    default_weights = get_default_weights()
    
    print(f"\nRunning Solomon Greedy Solver with weights: {default_weights}...")
    state = solver.solve_complete_problem(default_weights)
    
    # Evaluate Route Quality
    evaluator = ObjectiveFunction()
    total_loss = evaluator.evaluate(state, problem)
    unserved_count = evaluator._count_failed_deliveries(state)
    total_distance = evaluator._calculate_total_distance(state, problem)
    total_waiting = evaluator._calculate_total_waiting(state, problem)
    
    print("\n--- RESULTS ---")
    print(f"Failed / Unserved Deliveries: {unserved_count}")
    print(f"Total Traveled Distance: {total_distance:.2f} km")
    print(f"Total Waiting Time: {total_waiting:.2f} minutes")
    print(f"Global Objective Loss: {total_loss:.4f}")
    
    print("\nDaily Routes Details:")
    routes = state.get_completed_routes()
    for day in sorted(routes.keys()):
        route = routes[day]
        print(f"  Day {day} Route ({len(route) - 2 if len(route) > 2 else 0} customers): {' -> '.join(route)}")

if __name__ == "__main__":
    main()
