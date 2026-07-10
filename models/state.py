import copy
from typing import List, Dict, Optional
from models.pending_queue import PendingQueue

class State:
    def __init__(self, pending_queue: PendingQueue, max_days: int):
        self._pending_queue: PendingQueue = pending_queue
        self._max_days: int = max_days
        self._current_day: int = 1
        self._current_time: float = 0.0
        self._current_load: float = 0.0
        # Initialize route for each day starting at DEPOT
        self._daily_routes: Dict[int, List[str]] = {day: ["DEPOT"] for day in range(1, max_days + 1)}
        self._daily_arrival_times: Dict[int, Dict[str, float]] = {day: {} for day in range(1, max_days + 1)}
        self._daily_wait_times: Dict[int, Dict[str, float]] = {day: {} for day in range(1, max_days + 1)}
        # Also store arrival and wait as lists to track route sequence times
        self._daily_arrival_list: Dict[int, List[float]] = {day: [0.0] for day in range(1, max_days + 1)}
        self._daily_wait_list: Dict[int, List[float]] = {day: [0.0] for day in range(1, max_days + 1)}

    @property
    def current_day(self) -> int:
        return self._current_day

    @property
    def current_time(self) -> float:
        return self._current_time

    @current_time.setter
    def current_time(self, val: float):
        self._current_time = val

    @property
    def current_load(self) -> float:
        return self._current_load

    @current_load.setter
    def current_load(self, val: float):
        self._current_load = val

    @property
    def pending_queue(self) -> PendingQueue:
        return self._pending_queue

    def current_route(self) -> List[str]:
        return self._daily_routes[self._current_day]

    def get_route(self, day: int) -> List[str]:
        return self._daily_routes[day]

    def set_route(self, day: int, route: List[str]) -> None:
        self._daily_routes[day] = list(route)

    def advance_day(self) -> bool:
        if self._current_day >= self._max_days:
            return False
        # Append DEPOT to finish the current route if it isn't finished yet
        route = self._daily_routes[self._current_day]
        if len(route) > 1 and route[-1] != "DEPOT":
            route.append("DEPOT")
            # We can calculate travel back to DEPOT if we want to in solver,
            # but let's make sure it is handled.
        self._current_day += 1
        self._current_time = 0.0
        self._current_load = 0.0
        return True

    def commit_insertion(self, customer_id: str, index: int, arrival: float, wait: float) -> None:
        # Mutate current daily route by inserting a customer at index
        self._daily_routes[self._current_day].insert(index, customer_id)
        self._daily_arrival_times[self._current_day][customer_id] = arrival
        self._daily_wait_times[self._current_day][customer_id] = wait
        
        # Remove from pending queue
        self._pending_queue.remove(customer_id)

    def get_completed_routes(self) -> Dict[int, List[str]]:
        # Ensure all routes end with DEPOT if they have moves
        for day in range(1, self._max_days + 1):
            route = self._daily_routes[day]
            if len(route) > 1 and route[-1] != "DEPOT":
                route.append("DEPOT")
        return self._daily_routes

    def clone(self) -> 'State':
        cloned_queue = PendingQueue(self._pending_queue.get_pending())
        cloned = State(cloned_queue, self._max_days)
        cloned._current_day = self._current_day
        cloned._current_time = self._current_time
        cloned._current_load = self._current_load
        cloned._daily_routes = copy.deepcopy(self._daily_routes)
        cloned._daily_arrival_times = copy.deepcopy(self._daily_arrival_times)
        cloned._daily_wait_times = copy.deepcopy(self._daily_wait_times)
        cloned._daily_arrival_list = copy.deepcopy(self._daily_arrival_list)
        cloned._daily_wait_list = copy.deepcopy(self._daily_wait_list)
        return cloned
