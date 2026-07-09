from typing import List
from optimizer.operators.base_operator import BaseOperator
from models.problem import Problem

class RelocateOperator(BaseOperator):
    def optimize_route(self, route: List[str], problem: Problem, day: int) -> List[str]:
        if len(route) <= 3:
            return route

        best_route = list(route)
        best_distance = self._calculate_route_distance(best_route, problem)
        improved = True

        while improved:
            improved = False
            n = len(best_route)
            for i in range(1, n - 1):
                # Remove node at index i
                cust_id = best_route[i]
                temp_route = best_route[:i] + best_route[i+1:]
                
                # Try to insert it at index j in the new list (from 1 to len(temp_route) - 1)
                for j in range(1, len(temp_route)):
                    if j == i:
                        continue
                    test_route = list(temp_route)
                    test_route.insert(j, cust_id)
                    
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
