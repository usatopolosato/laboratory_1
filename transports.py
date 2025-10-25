from abc import ABC, abstractmethod
from typing import List
from seat import Seat
from enum import Enum


# Типы транспорта в системе
class TransportType(Enum):
    BUS = "автобус"
    TRAIN = "поезд"
    PLANE = "самолет"
    SHIP = "корабль"


# Абстрактный класс Transport - основа для всех видов транспорта
class Transport(ABC):
    def __init__(self, transport_id: str, model: str, capacity: int):
        self.__transport_id = transport_id  # Уникальный ID транспорта
        self.__model = model                # Модель
        self.__capacity = capacity          # Вместимость (количество мест)
        self.__seats: List[Seat] = []       # Список всех мест в транспорте

    # геттеры
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
        return self.__seats.copy()  # Возвращаем копию списка мест

    @abstractmethod
    def get_transport_info(self) -> str:
        pass  # Каждый тип транспорта должен уметь показывать информацию о себе

    def add_seat(self, seat: Seat) -> None:
        # Добавляем место в транспорт
        self.__seats.append(seat)


# Класс Bus - автобус, наследуется от Transport
class Bus(Transport):
    def __init__(self, transport_id: str, model: str, capacity: int, has_wifi: bool,
                 has_usb_charging: bool):
        super().__init__(transport_id, model, capacity)  # Вызываем конструктор родителя
        self.__has_wifi = has_wifi           # Есть ли Wi-Fi
        self.__has_usb_charging = has_usb_charging  # Есть ли USB-зарядки

    # геттеры
    @property
    def has_wifi(self) -> bool:
        return self.__has_wifi

    @property
    def has_usb_charging(self) -> bool:
        return self.__has_usb_charging

    def get_transport_info(self) -> str:
        # Показываем информацию об автобусе с его особенностями
        wifi_info = "с Wi-Fi" if self.__has_wifi else "без Wi-Fi"
        charging_info = "с USB-зарядкой" if self.__has_usb_charging else "без USB-зарядки"
        return f"Автобус {self.model} ({self.capacity} мест) {wifi_info} {charging_info}"


# Класс Train - поезд, наследуется от Transport
class Train(Transport):
    def __init__(self, transport_id: str, model: str, capacity: int, car_count: int):
        super().__init__(transport_id, model, capacity)
        self.__car_count = car_count  # Количество вагонов

    # геттер
    @property
    def car_count(self) -> int:
        return self.__car_count

    def get_transport_info(self) -> str:
        # Показываем информацию о поезде с количеством вагонов
        return f"Поезд {self.model} ({self.__car_count} вагонов, {self.capacity} мест)"
