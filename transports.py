from abc import ABC, abstractmethod
from typing import List
from seat import Seat


class Transport(ABC):
    def __init__(self, model: str, capacity: int):
        self.__model = model
        self.__capacity = capacity
        self.__seats: List[Seat] = []

    @abstractmethod
    def get_transport_info(self) -> str:
        pass

    def add_seat(self, seat: Seat) -> None:
        self.__seats.append(seat)
