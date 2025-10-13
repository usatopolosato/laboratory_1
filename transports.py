from abc import ABC, abstractmethod
from typing import List
from seat import Seat


class Transport(ABC):
    def __init__(self, transport_id: str, model: str, capacity: int):
        self.__transport_id = transport_id
        self.__model = model
        self.__capacity = capacity
        self.__seats: List[Seat] = []

    @property
    def transport_id(self):
        return self.__transport_id

    @property
    def model(self) -> str:
        return self.__model

    @property
    def capacity(self) -> int:
        return self.__capacity

    @property
    def seats(self) -> List[Seat]:
        return self.__seats.copy()

    @abstractmethod
    def get_transport_info(self) -> str:
        pass

    def add_seat(self, seat: Seat) -> None:
        self.__seats.append(seat)
