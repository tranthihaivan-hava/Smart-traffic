from typing import List, Dict, Optional
from models.customer import Customer

class Problem:
    def __init__(
        self,
        depot: Customer,
        customers: Dict[str, Customer],
        distance_matrix,
        travel_time_matrix,
        max_days: int,
        vehicle_capacity: float
    ):
        self._depot: Customer = depot
        self._customers: Dict[str, Customer] = customers
        self._distance_matrix = distance_matrix
        self._travel_time_matrix = travel_time_matrix
        self._max_days: int = max_days
        self._vehicle_capacity: float = vehicle_capacity

    def get_customer(self, customer_id: str) -> Customer:
        if customer_id == "DEPOT":
            return self._depot
        return self._customers[customer_id]

    def get_all_customers(self) -> List[Customer]:
        return list(self._customers.values())

    def get_depot(self) -> Customer:
        return self._depot

    def get_distance(self, from_id: str, to_id: str) -> float:
        return self._distance_matrix.get_distance(from_id, to_id)

    def get_travel_time(self, from_id: str, to_id: str) -> float:
        return self._travel_time_matrix.get_travel_time(from_id, to_id)

    @property
    def max_days(self) -> int:
        return self._max_days

    @property
    def vehicle_capacity(self) -> float:
        return self._vehicle_capacity
