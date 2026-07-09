from typing import List
from models.state import State
from models.problem import Problem
from optimizer.operators.base_operator import BaseOperator
from optimizer.operators.swap_operator import SwapOperator
from optimizer.operators.relocate_operator import RelocateOperator
from optimizer.operators.two_opt_operator import TwoOptOperator

class LocalSearch:
    def __init__(self, operators: List[BaseOperator] = None):
        self.operators = operators or [
            RelocateOperator(),
            SwapOperator(),
            TwoOptOperator()
        ]

    def improve_day_route(self, state: State, day: int, problem: Problem) -> State:
        route = state._daily_routes[day]
        if len(route) <= 3:
            return state

        # Strip ending DEPOT if present to run operators, but make sure it ends at DEPOT
        has_ending_depot = (route[-1] == "DEPOT")
        clean_route = list(route)
        if has_ending_depot:
            clean_route = clean_route[:-1]

        improved = True
        while improved:
            improved = False
            for op in self.operators:
                # Add DEPOT back to clean_route for operator execution
                route_to_optimize = clean_route + ["DEPOT"]
                optimized = op.optimize_route(route_to_optimize, problem, day)
                
                # Strip ending DEPOT from optimized
                if len(optimized) > 0 and optimized[-1] == "DEPOT":
                    optimized = optimized[:-1]
                
                if optimized != clean_route:
                    clean_route = optimized
                    improved = True
                    break # Restart operator loop from beginning for prioritization

        # Put final route back into state
        final_route = clean_route + ["DEPOT"] if has_ending_depot else clean_route
        state._daily_routes[day] = final_route
        return state
