import sys
import os
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from preprocessing.dataset_loader import DatasetLoader
from solver.genetic_hybrid import GeneticHybridSolver
from config.weights_config import WeightVector
import optuna

def export():
    loader = DatasetLoader()
    problem = loader.build_problem_instance("Data_B/locations.csv", "Data_B/time_windows.csv")
    
    study = optuna.load_study(study_name="boma_two_phase", storage="sqlite:///Data_B/boma_two_phase.db")
    bp = study.best_params
    best_weights = WeightVector(distance=bp["distance"], urgency=bp["urgency"], waiting=bp["waiting"], delivery_risk=bp["delivery_risk"])
    
    solver = GeneticHybridSolver(problem, pop_size=50, generations=30, weights=best_weights)
    
    with open('Data_B/final_checkpoint.json', 'r') as f_in:
        pop = json.load(f_in)
    best_chromo = pop[0]
    
    state, _ = solver._decode(best_chromo)
    if len(state.pending_queue.get_pending()) > 0:
        solver.repair_operator.run(state)
        
    routes = state.get_completed_routes()
    
    with open("Overview/presentation_result.txt", "w") as f:
        json.dump(routes, f, indent=4)
        
    print("Successfully exported presentation_result.txt")

if __name__ == "__main__":
    export()
