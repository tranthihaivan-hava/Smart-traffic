from typing import List
from optimizer.operators.base_operator import BaseOperator
from models.problem import Problem

class SwapOperator(BaseOperator):
    def optimize_route(self, route: List[str], problem: Problem, day: int) -> List[str]:
        # If route has fewer than 2 customers, no swap is possible
        if len(route) <= 3:
            return route

        best_route = list(route)
        best_distance = self._calculate_route_distance(best_route, problem)
        improved = True

        while improved:
            improved = False
            # Customers are from index 1 to len(route) - 2
            n = len(best_route)
            for i in range(1, n - 2):
                for j in range(i + 1, n - 1):
                    # Attempt swap
                    test_route = list(best_route)
                    test_route[i], test_route[j] = test_route[j], test_route[i]
                    
                    if self._validate_route_constraints(test_route, problem, day):
                        dist = self._calculate_route_distance(test_route, problem)
                        if dist < best_distance - 1e-4:
                            best_route = test_route
                            best_distance = dist
                            improved = True
                            break
                if improved:
                    break

        return best_route

    def _calculate_route_distance(self, route: List[str], problem: Problem) -> float:
        total = 0.0
        for i in range(len(route) - 1):
            total += problem.get_distance(route[i], route[i+1])
        return total
