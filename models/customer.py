from typing import List
from models.delivery_window import DeliveryWindow

class Customer:
    def __init__(
        self,
        customer_id: str,
        x_coord: float,
        y_coord: float,
        demand: float,
        service_duration: float,
        windows: List[DeliveryWindow]
    ):
        self._id: str = customer_id
        self._x: float = x_coord
        self._y: float = y_coord
        self._demand: float = demand
        self._service_duration: float = service_duration
        self._windows: List[DeliveryWindow] = windows

    @property
    def id(self) -> str:
        return self._id

    @property
    def x(self) -> float:
        return self._x

    @property
    def y(self) -> float:
        return self._y

    @property
    def demand(self) -> float:
        return self._demand

    @property
    def service_duration(self) -> float:
        return self._service_duration

    def get_windows_for_day(self, day: int) -> List[DeliveryWindow]:
        return [w for w in self._windows if w.day == day]

    def get_all_windows(self) -> List[DeliveryWindow]:
        return self._windows

    def has_windows(self) -> bool:
        return len(self._windows) > 0
