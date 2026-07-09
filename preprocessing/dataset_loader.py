from typing import Dict, List
from preprocessing.csv_loader import CSVLoader
from preprocessing.distance_matrix import DistanceMatrix
from preprocessing.travel_time_matrix import TravelTimeMatrix
from models.customer import Customer
from models.delivery_window import DeliveryWindow
from models.problem import Problem
from config.settings import get_settings

class DatasetLoader:
    def __init__(self, csv_loader: CSVLoader = None):
        self.csv_loader = csv_loader or CSVLoader()

    def _parse_time(self, time_str: str) -> float:
        parts = time_str.split(':')
        if len(parts) != 2:
            raise ValueError(f"Invalid time format: {time_str}")
        return float(int(parts[0]) * 60 + int(parts[1]))

    def build_problem_instance(self, locations_path: str, windows_path: str) -> Problem:
        settings = get_settings()
        raw_locs = self.csv_loader.load_locations(locations_path)
        raw_windows = self.csv_loader.load_time_windows(windows_path)

        # Parse windows
        windows_by_cust: Dict[str, List[DeliveryWindow]] = {}
        for row in raw_windows:
            cust_id = row['location_id']
            day = int(row['day_of_week'])
            start = self._parse_time(row['start_time'])
            end = self._parse_time(row['end_time'])
            
            if cust_id not in windows_by_cust:
                windows_by_cust[cust_id] = []
            windows_by_cust[cust_id].append(DeliveryWindow(day=day, start_time=start, end_time=end))

        # Parse customers & depot
        depot = None
        customers: Dict[str, Customer] = {}
        service_times: Dict[str, float] = {}

        for row in raw_locs:
            cust_id = row['location_id']
            x = float(row['x_km'])
            y = float(row['y_km'])
            demand = float(row['demand_kg'])
            service_time = float(row['service_time'])
            
            cust_windows = windows_by_cust.get(cust_id, [])
            cust = Customer(
                customer_id=cust_id,
                x_coord=x,
                y_coord=y,
                demand=demand,
                service_duration=service_time,
                windows=cust_windows
            )
            service_times[cust_id] = service_time

            if cust_id == settings.depot_id:
                depot = cust
            else:
                customers[cust_id] = cust

        if depot is None:
            raise ValueError("Depot not found in locations data")

        # Create matrices
        dist_matrix = DistanceMatrix(list(customers.values()), depot)
        time_matrix = TravelTimeMatrix(dist_matrix, settings.vehicle_speed, service_times)

        return Problem(
            depot=depot,
            customers=customers,
            distance_matrix=dist_matrix,
            travel_time_matrix=time_matrix,
            max_days=settings.max_days,
            vehicle_capacity=settings.vehicle_capacity
        )
