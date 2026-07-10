from typing import List
from models.problem import Problem
from models.state import State
from models.pending_queue import PendingQueue
from models.candidate import Candidate
from config.weights_config import WeightVector
from solver.solomon_insertion import SolomonInsertion
from solver.feature_extractor import FeatureExtractor
from solver.normalizer import Normalizer
from solver.score_calculator import ScoreCalculator
from optimizer.local_search import LocalSearch
from optimizer.repair_operator import RepairOperator

class GreedySolver:
    def __init__(self, problem: Problem):
        self.problem = problem
        self.solomon = SolomonInsertion(problem)
        self.extractor = FeatureExtractor(problem)
        self.normalizer = Normalizer()
        self.scorer = ScoreCalculator()
        self.local_search = LocalSearch()

    def solve_day(self, state: State, day: int, weights: WeightVector, use_local_search: bool = True) -> State:
        # Construct route for the day greedily
        while True:
            # 1. Generate candidates
            candidates = self.solomon.generate_candidates(state)
            if not candidates:
                break
                
            # 2. Extract features
            self.extractor.extract_features(candidates, state, day)
            
            # 3. Normalize features
            self.normalizer.normalize(candidates)
            
            # 4. Compute scores
            self.scorer.compute_scores(candidates, weights)
            
            # 5. Select best candidate
            best_candidate = min(candidates, key=lambda c: c.score)
            
            # 6. Apply candidate
            self._apply_candidate(state, best_candidate)
            
        if use_local_search:
            # Run local search to improve the constructed daily route
            self.local_search.improve_day_route(state, day, self.problem)
            # Re-apply the timing updates since route might have changed order
            self._recalculate_route_timing(state)
        return state


    def solve_complete_problem(self, weights: WeightVector, use_local_search: bool = True) -> State:
        # Initialize state with all customers in pending queue
        all_cust_ids = {c.id for c in self.problem.get_all_customers()}
        pending_queue = PendingQueue(all_cust_ids)
        state = State(pending_queue, self.problem.max_days)

        for day in range(1, self.problem.max_days + 1):
            self.solve_day(state, day, weights, use_local_search=use_local_search)
            if day < self.problem.max_days:
                state.advance_day()

        if use_local_search:
            repair = RepairOperator(self.problem)
            repair.run(state)

        return state

    def _apply_candidate(self, state: State, candidate: Candidate):
        # Commit the insertion to the state
        state.commit_insertion(
            customer_id=candidate.customer_id,
            index=candidate.insertion_index,
            arrival=candidate.arrival_time,
            wait=candidate.wait_time
        )
        self._recalculate_route_timing(state)

    def _recalculate_route_timing(self, state: State):
        route = state.current_route()
        day = state.current_day
        
        # Calculate current load
        total_load = 0.0
        for cid in route:
            if cid != "DEPOT":
                total_load += self.problem.get_customer(cid).demand
        state.current_load = total_load

        # Recalculate timing along the route
        current_time = 0.0
        prev_id = "DEPOT"

        # Reset arrival and wait maps for the current day
        state._daily_arrival_times[day].clear()
        state._daily_wait_times[day].clear()

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
                service_start_cand = max(arrival, w.start_time)
                service_end_cand = service_start_cand + cust.service_duration
                if service_end_cand <= w.end_time:
                    valid_window = w
                    break
            
            wait = max(0.0, valid_window.start_time - arrival) if valid_window else 0.0
            service_start = arrival + wait
            current_time = service_start + cust.service_duration
            
            # Save recalculated times to state maps
            state._daily_arrival_times[day][cid] = arrival
            state._daily_wait_times[day][cid] = wait
            prev_id = cid

        state.current_time = current_time
