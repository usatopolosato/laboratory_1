from abc import ABC, abstractmethod
from typing import List
from seat import Seat
from enum import Enum


class TransportType(Enum):
    BUS = "автобус"
    TRAIN = "поезд"
    PLANE = "самолет"
    SHIP = "корабль"


class Transport(ABC):
    def __init__(self, transport_id: str, model: str, capacity: int):
        self.__transport_id = transport_id
        self.__model = model
        self.__capacity = capacity
        self.__seats: List[Seat] = []

    @property
    def transport_id(self) -> str:
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


class Bus(Transport):
    def __init__(self, transport_id: str, model: str, capacity: int, has_wifi: bool,
                 has_usb_charging: bool):
        super().__init__(transport_id, model, capacity)
        self.__has_wifi = has_wifi
        self.__has_usb_charging = has_usb_charging

    @property
    def has_wifi(self) -> bool:
        return self.__has_wifi

    @property
    def has_usb_charging(self) -> bool:
        return self.__has_usb_charging

    def get_transport_info(self) -> str:
        wifi_info = "с Wi-Fi" if self.__has_wifi else "без Wi-Fi"
        charging_info = "с USB-зарядкой" if self.__has_wifi else "без USB-зарядки"
        return f"Автобус {self.model} ({self.capacity} мест) {wifi_info} {charging_info}"


class Train(Transport):
    def __init__(self, transport_id: str, model: str, capacity: int, car_count: int):
        super().__init__(transport_id, model, capacity)
        self.__car_count = car_count

    @property
    def car_count(self) -> int:
        return self.__car_count

    def get_transport_info(self) -> str:
        return f"Поезд {self.model} ({self.__car_count} вагонов, {self.capacity} мест)"
