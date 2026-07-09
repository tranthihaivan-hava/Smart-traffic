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
        # Form the proposed new route
        new_route = list(route)
        new_route.insert(index, customer.id)
        
        # Ensure we always end at DEPOT when calculating timeline
        if new_route[-1] != "DEPOT":
            new_route.append("DEPOT")

        # Capacity check
        total_demand = sum(self._problem.get_customer(cid).demand for cid in new_route if cid != "DEPOT")
        if total_demand > self._problem.vehicle_capacity:
            return None

        # Simulate timeline from start of route
        current_time = 0.0
        prev_id = "DEPOT"
        
        target_arrival = None
        target_wait = None
        target_service_start = None

        for i, cid in enumerate(new_route):
            if i == 0:
                continue
            
            travel_time = self._problem.get_travel_time(prev_id, cid)
            arrival = current_time + travel_time
            
            if cid == "DEPOT":
                current_time = arrival
                prev_id = cid
                continue
                
            cust = self._problem.get_customer(cid)
            windows = cust.get_windows_for_day(day)
            
            # Find a valid window we can satisfy
            valid_window = None
            # Sort windows by start time
            for w in sorted(windows, key=lambda x: x.start_time):
                if arrival <= w.end_time:
                    valid_window = w
                    break
            
            if valid_window is None:
                # Infeasible
                return None
                
            wait = max(0.0, valid_window.start_time - arrival)
            service_start = arrival + wait
            service_end = service_start + cust.service_duration
            
            if cid == customer.id and i == index:
                target_arrival = arrival
                target_wait = wait
                target_service_start = service_start
                
            current_time = service_end
            prev_id = cid

        # If we reached here, simulation is feasible!
        # Calculate distance detour: d_{i,u} + d_{u,j} - d_{i,j}
        # where i = new_route[index-1], u = customer.id, j = new_route[index+1]
        i_id = new_route[index - 1]
        j_id = new_route[index + 1]
        d_iu = self._problem.get_distance(i_id, customer.id)
        d_uj = self._problem.get_distance(customer.id, j_id)
        d_ij = self._problem.get_distance(i_id, j_id)
        distance_delta = d_iu + d_uj - d_ij

        return Candidate(
            customer_id=customer.id,
            day=day,
            insertion_index=index,
            arrival_time=target_arrival,
            wait_time=target_wait,
            service_start_time=target_service_start,
            distance_delta=distance_delta
        )
