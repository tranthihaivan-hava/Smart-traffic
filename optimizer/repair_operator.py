from typing import List, Tuple
from models.problem import Problem
from models.state import State
import copy

class RepairOperator:
    """
    Implements an Ejection Chain (Ruin and Recreate) heuristic.
    Forcefully inserts unserved customers by ejecting conflicting customers,
    and then attempts to re-insert the ejected customers into other days.
    """

    def __init__(self, problem: Problem):
        self.problem = problem

    def run(self, state: State) -> None:
        unserved = state.pending_queue.get_pending()
        if not unserved:
            return

        for u_id in list(unserved):
            success = self._attempt_repair(u_id, state)
            if success:
                state.pending_queue.remove(u_id)

    def _attempt_repair(self, u_id: str, state: State) -> bool:
        u_cust = self.problem.get_customer(u_id)
        # Find which days are valid for the unserved customer
        valid_days = [day for day in range(1, self.problem.max_days + 1) if u_cust.get_windows_for_day(day)]

        for day in valid_days:
            original_route = state.get_route(day)
            
            for idx in range(1, len(original_route)):
                # Step 1: Force insert u_id
                test_route = list(original_route)
                test_route.insert(idx, u_id)
                
                # Step 2: Simulate route and collect violated customers (ejection)
                ejected = self._simulate_and_eject(test_route, day)
                if ejected is None or u_id in ejected:
                    continue # Capacity exceeded or u_id itself is invalid
                
                # The route after ejection
                repaired_route = [c for c in test_route if c not in ejected]
                
                # Step 3: Try to re-insert ejected customers into ANY day without causing new ejections
                reinsertion_success, new_routes_mapping = self._try_reinsert_all(ejected, state, skip_day=day)
                
                if reinsertion_success:
                    # COMMIT changes
                    state.set_route(day, repaired_route)
                    for d, r in new_routes_mapping.items():
                        state.set_route(d, r)
                    return True
        return False

    def _simulate_and_eject(self, route: List[str], day: int) -> List[str]:
        """
        Simulates the route. Returns a list of ejected customer IDs.
        Returns None if the route is fundamentally invalid (e.g., capacity exceeded or the inserted customer is invalid).
        """
        total_demand = sum(self.problem.get_customer(cid).demand for cid in route if cid != "DEPOT")
        if total_demand > self.problem.vehicle_capacity:
            return None

        ejected = []
        
        # We need a robust simulation that allows skipping ejected customers
        # To do this cleanly, we iterate and if a customer is invalid, we add it to ejected,
        # but we DO NOT update the current_time based on it (as if it wasn't there).
        
        current_time = 0.0
        prev_id = "DEPOT"
        
        for i, cid in enumerate(route):
            if i == 0:
                continue
                
            travel_time = self.problem.get_travel_time(prev_id, cid)
            arrival = current_time + travel_time
            
            if cid == "DEPOT":
                current_time = arrival
                continue
                
            cust = self.problem.get_customer(cid)
            windows = cust.get_windows_for_day(day)
            
            valid_window = None
            for w in sorted(windows, key=lambda x: x.start_time):
                # Strict rule
                service_start_cand = max(arrival, w.start_time)
                service_end_cand = service_start_cand + cust.service_duration
                if service_end_cand <= w.end_time:
                    valid_window = w
                    break
                    
            if valid_window is None:
                ejected.append(cid)
                # DO NOT update current_time, prev_id remains the same for the NEXT node
                continue
                
            wait = max(0.0, valid_window.start_time - arrival)
            service_start = arrival + wait
            current_time = service_start + cust.service_duration
            prev_id = cid

        # If the newly inserted customer itself was ejected, this insertion path is invalid.
        # But we don't know the newly inserted customer ID from this function signature easily,
        # However, we can just check if ANY customer was ejected, maybe the inserted one is in there.
        # Actually, in attempt_repair, u_id was just inserted. If u_id is in ejected, it failed.
        return ejected

    def _try_reinsert_all(self, cids: List[str], state: State, skip_day: int) -> Tuple[bool, dict]:
        """
        Attempts to reinsert all cids into the state without causing further ejections.
        Returns (success, dict_of_updated_routes).
        """
        if not cids:
            return True, {}
            
        temp_routes = {}
        for day in range(1, self.problem.max_days + 1):
            if day != skip_day:
                temp_routes[day] = list(state.get_route(day))
                
        for cid in cids:
            inserted = False
            for day in temp_routes.keys():
                if inserted: break
                
                cust = self.problem.get_customer(cid)
                if not cust.get_windows_for_day(day):
                    continue
                    
                route = temp_routes[day]
                for idx in range(1, len(route)):
                    test_route = list(route)
                    test_route.insert(idx, cid)
                    
                    ejected = self._simulate_and_eject(test_route, day)
                    if ejected is not None and len(ejected) == 0:
                        # Success! No one was ejected.
                        temp_routes[day] = test_route
                        inserted = True
                        break
            if not inserted:
                return False, {}
                
        return True, temp_routes
