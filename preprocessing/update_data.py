import sys
import os
sys.path.append('.')
from preprocessing.dataset_loader import DatasetLoader
from config.weights_config import WeightVector
from solver.greedy_solver import GreedySolver

def get_routes_and_times(weights, is_strict):
    loader = DatasetLoader()
    problem = loader.build_problem_instance('Data_B/locations.csv', 'Data_B/time_windows.csv')
    solver = GreedySolver(problem)
    
    # We must patch solomon_insertion temporarily if we want lenient vs strict?
    # Wait, the current codebase has Strict hardcoded in solomon_insertion.py!
    # Let me check if there's a setting for it.
    pass
