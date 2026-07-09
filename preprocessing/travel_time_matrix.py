from typing import Dict
from preprocessing.distance_matrix import DistanceMatrix
from models.customer import Customer

class TravelTimeMatrix:
    def __init__(self, distance_matrix: DistanceMatrix, speed_kmh: float, service_times: Dict[str, float]):
        self.distance_matrix = distance_matrix
        self.speed_kmh = speed_kmh
        self.service_times = service_times

    def get_travel_time(self, from_id: str, to_id: str) -> float:
        dist = self.distance_matrix.get_distance(from_id, to_id)
        # speed_kmh is in km/h. Travel time in minutes is (dist / speed_kmh) * 60
        return (dist / self.speed_kmh) * 60.0

    def get_service_time(self, customer_id: str) -> float:
        return self.service_times.get(customer_id, 0.0)
