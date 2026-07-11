from typing import List, Optional
from models.problem import Problem
from models.state import State
from models.candidate import Candidate
from models.customer import Customer

class SolomonInsertion:
    def __init__(self, problem: Problem):
        self._problem = problem

    def generate_candidates(self, state: State) -> List[Candidate]:
        candidates = []
        current_route = state.current_route()
        day = state.current_day
        pending_ids = state.pending_queue.get_pending()

        if not pending_ids:
            return []

        # Focus evaluation on the 45 closest pending customers to the last node of the current route
        last_node_id = current_route[-1]
        sorted_pending = sorted(
            pending_ids,
            key=lambda cid: self._problem.get_distance(last_node_id, cid)
        )
        target_pending = sorted_pending[:45]


        # For each target customer
        for cust_id in target_pending:
            customer = self._problem.get_customer(cust_id)
            # Evaluate all possible insertion positions in the current route (excluding before DEPOT at index 0)
            for idx in range(1, len(current_route) + 1):
                cand = self._evaluate_insertion(customer, current_route, idx, state, day)
                if cand is not None:
                    candidates.append(cand)
        return candidates


    def _evaluate_insertion(self, customer: Customer, route: List[str], index: int, state: State, day: int) -> Optional[Candidate]:
        from utils.route_validator import RouteValidator
        
        metrics = RouteValidator.validate_insertion(self._problem, customer, route, index, day)
        if metrics is None:
            return None
            
        return Candidate(
            customer_id=customer.id,
            day=day,
            insertion_index=index,
            arrival_time=metrics["arrival_time"],
            wait_time=metrics["wait_time"],
            service_start_time=metrics["service_start_time"],
            distance_delta=metrics["distance_delta"]
        )
