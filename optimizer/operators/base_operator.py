from abc import ABC, abstractmethod
from typing import List
from models.problem import Problem

class BaseOperator(ABC):
    @abstractmethod
    def optimize_route(self, route: List[str], problem: Problem, day: int) -> List[str]:
        """
        Evaluates neighborhood mutations for the provided route sequence.
        Returns an improved route sequence, or the original sequence if locally optimal.
        """
        pass

    def _validate_route_constraints(self, route: List[str], problem: Problem, day: int) -> bool:
        # Simple simulation to verify time and capacity constraints for the proposed route
        if len(route) <= 2:
            return True
            
        # Check capacity
        total_demand = sum(problem.get_customer(cid).demand for cid in route if cid != "DEPOT")
        if total_demand > problem.vehicle_capacity:
            return False

        # Check time window feasibility for all nodes
        current_time = 0.0
        prev_id = "DEPOT"
        for i, cid in enumerate(route):
            if i == 0:
                continue
            travel_time = problem.get_travel_time(prev_id, cid)
            arrival = current_time + travel_time
            
            if cid == "DEPOT":
                current_time = arrival
                continue
                
            cust = problem.get_customer(cid)
            windows = cust.get_windows_for_day(day)
            valid_window = None
            for w in sorted(windows, key=lambda x: x.start_time):
                # Strict rule: entire service must finish within the window
                service_start_cand = max(arrival, w.start_time)
                service_end_cand = service_start_cand + cust.service_duration
                if service_end_cand <= w.end_time:
                    valid_window = w
                    break
            if valid_window is None:
                return False
                
            wait = max(0.0, valid_window.start_time - arrival)
            service_start = arrival + wait
            current_time = service_start + cust.service_duration
            prev_id = cid
            
        return True
