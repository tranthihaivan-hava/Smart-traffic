import sys
import optuna
from preprocessing.dataset_loader import DatasetLoader
from config.weights_config import WeightVector
from solver.greedy_solver import GreedySolver
from optimizer.objective_function import ObjectiveFunction
from optimizer.bayesian_optimizer import BayesianOptimizer

# Custom objective function with 1,000,000 penalty
evaluator = ObjectiveFunction(unserved_penalty=1000000.0)

loader = DatasetLoader()
problem = loader.build_problem_instance('Data_B/locations.csv', 'Data_B/time_windows.csv')
solver = GreedySolver(problem)

opt = BayesianOptimizer(problem, solver, evaluator)
print("Running 500 trials of Optuna on LENIENT...")

# WE MUST PATCH solomon_insertion.py inside python memory!
# Wait, solomon_insertion is already loaded. 
# We need to monkey-patch the evaluate method?
# Easier: Just replace the file content temporarily.
