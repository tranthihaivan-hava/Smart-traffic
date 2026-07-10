from models.state import State
from models.problem import Problem

class ObjectiveFunction:
    def __init__(self, unserved_penalty: float = 1000000.0):
        self._penalty = unserved_penalty

    def evaluate(self, state: State, problem: Problem) -> float:
        failed = self._count_failed_deliveries(state)
        distance = self._calculate_total_distance(state, problem)
        waiting = self._calculate_total_waiting(state, problem)
        return (failed * self._penalty) + distance + (0.5 * waiting)  # Matches formula from walkthrough: Loss = (Failed * penalty) + Distance + 0.5 * Waiting

    def _count_failed_deliveries(self, state: State) -> int:
        return state.pending_queue.get_unserved_count()

    def _calculate_total_distance(self, state: State, problem: Problem) -> float:
        total_dist = 0.0
        routes = state.get_completed_routes()
        for day, route in routes.items():
            if len(route) <= 1:
                continue
            # Ensure route starts and ends at DEPOT
            prev = route[0]
            for node in route[1:]:
                total_dist += problem.get_distance(prev, node)
                prev = node
        return total_dist

    def _calculate_total_waiting(self, state: State, problem: Problem) -> float:
        total_wait = 0.0
        routes = state.get_completed_routes()
        for day, route in routes.items():
            if len(route) <= 1:
                continue
            current_time = 0.0
            prev_id = "DEPOT"
            for node in route[1:]:
                travel_time = problem.get_travel_time(prev_id, node)
                arrival = current_time + travel_time
                if node == "DEPOT":
                    break
                
                cust = problem.get_customer(node)
                windows = cust.get_windows_for_day(day)
                valid_window = None
                for w in sorted(windows, key=lambda x: x.start_time):
                    if arrival <= w.end_time:
                        valid_window = w
                        break
                
                wait = max(0.0, valid_window.start_time - arrival) if valid_window else 0.0
                total_wait += wait
                service_start = arrival + wait
                current_time = service_start + cust.service_duration
                prev_id = node
        return total_wait
