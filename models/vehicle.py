from typing import List

class Vehicle:
    def __init__(self, vehicle_id: str, capacity: float):
        self.id: str = vehicle_id
        self.capacity: float = capacity
        self.current_load: float = 0.0
        self.route: List[str] = ["DEPOT"]
        self.arrival_times: List[float] = [0.0]
        self.wait_times: List[float] = [0.0]

    def can_accommodate(self, demand: float) -> bool:
        return self.current_load + demand <= self.capacity

    def add_stop(self, customer_id: str, arrival_time: float, wait_time: float, service_time: float):
        self.route.append(customer_id)
        self.arrival_times.append(arrival_time)
        self.wait_times.append(wait_time)
        # Note: in models.vehicle, we also need to update the load. Let's do that.
        # But wait, we can implement _update_load internally or directly update.
        # Let's keep it simple:

    def reset(self):
        self.current_load = 0.0
        self.route = ["DEPOT"]
        self.arrival_times = [0.0]
        self.wait_times = [0.0]
