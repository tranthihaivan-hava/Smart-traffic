from typing import List, Set
from models.problem import Problem
from models.state import State
from models.pending_queue import PendingQueue
from solver.solomon_insertion import SolomonInsertion

class BaselineSolver:
    def __init__(self, problem: Problem):
        self.problem = problem
        # We can reuse Solomon's candidate checker or write a simple direct feasibility check
        # Let's reuse SolomonInsertion to find feasible insertions at the end of the route
        self.solomon = SolomonInsertion(problem)

    def solve_nearest_neighbor(self) -> State:
        # NN: always choose the closest customer (by distance) from the current node
        all_cust_ids = {c.id for c in self.problem.get_all_customers()}
        pending = PendingQueue(all_cust_ids)
        state = State(pending, self.problem.max_days)

        for day in range(1, self.problem.max_days + 1):
            while True:
                candidates = self.solomon.generate_candidates(state)
                # Filter to only keep insertions at the very end of the route
                # Current route length is len(route)
                route_len = len(state.current_route())
                end_candidates = [c for c in candidates if c.insertion_index == route_len]
                
                if not end_candidates:
                    break
                
                # Pick nearest customer from current route's last node
                current_node = state.current_route()[-1]
                
                def get_dist(cand):
                    return self.problem.get_distance(current_node, cand.customer_id)
                
                best_cand = min(end_candidates, key=get_dist)
                state.commit_insertion(
                    customer_id=best_cand.customer_id,
                    index=best_cand.insertion_index,
                    arrival=best_cand.arrival_time,
                    wait=best_cand.wait_time
                )
                self._update_timing_and_load(state)
            
            if day < self.problem.max_days:
                state.advance_day()
        return state

    def solve_earliest_deadline_first(self) -> State:
        # EDF: choose the feasible customer whose delivery window closes earliest
        all_cust_ids = {c.id for c in self.problem.get_all_customers()}
        pending = PendingQueue(all_cust_ids)
        state = State(pending, self.problem.max_days)

        for day in range(1, self.problem.max_days + 1):
            while True:
                candidates = self.solomon.generate_candidates(state)
                route_len = len(state.current_route())
                end_candidates = [c for c in candidates if c.insertion_index == route_len]
                
                if not end_candidates:
                    break
                
                # Find end time of the active window for each candidate
                def get_deadline(cand):
                    cust = self.problem.get_customer(cand.customer_id)
                    windows = cust.get_windows_for_day(day)
                    active_window = None
                    for w in sorted(windows, key=lambda x: x.start_time):
                        if cand.arrival_time <= w.end_time:
                            active_window = w
                            break
                    return active_window.end_time if active_window else 1440.0
                
                best_cand = min(end_candidates, key=get_deadline)
                state.commit_insertion(
                    customer_id=best_cand.customer_id,
                    index=best_cand.insertion_index,
                    arrival=best_cand.arrival_time,
                    wait=best_cand.wait_time
                )
                self._update_timing_and_load(state)
            
            if day < self.problem.max_days:
                state.advance_day()
        return state

    def _update_timing_and_load(self, state: State):
        route = state.current_route()
        day = state.current_day
        
        # Calculate current load
        total_load = 0.0
        for cid in route:
            if cid != "DEPOT":
                total_load += self.problem.get_customer(cid).demand
        state.current_load = total_load

        # Recalculate timing
        current_time = 0.0
        prev_id = "DEPOT"
        for i, cid in enumerate(route):
            if i == 0:
                continue
            travel_time = self.problem.get_travel_time(prev_id, cid)
            arrival = current_time + travel_time
            if cid == "DEPOT":
                current_time = arrival
                break
            cust = self.problem.get_customer(cid)
            windows = cust.get_windows_for_day(day)
            valid_window = None
            for w in sorted(windows, key=lambda x: x.start_time):
                if arrival <= w.end_time:
                    valid_window = w
                    break
            wait = max(0.0, valid_window.start_time - arrival) if valid_window else 0.0
            service_start = arrival + wait
            current_time = service_start + cust.service_duration
            prev_id = cid

        state.current_time = current_time
