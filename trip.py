from seat import Seat
from datetime import datetime
from typing import List, Optional
from transports import Transport


# Класс Route - маршрут поездки
class Route:
    def __init__(self, route_id: str, departure: str, destination: str,
                 departure_time: datetime, arrival_time: datetime):
        self.__route_id = route_id          # ID маршрута
        self.__departure = departure        # Город отправления
        self.__destination = destination    # Город назначения
        self.__departure_time = departure_time  # Время отправления
        self.__arrival_time = arrival_time      # Время прибытия

    # геттеры
    @property
    def route_id(self) -> str:
        return self.__route_id

    @property
    def departure(self) -> str:
        return self.__departure

    @property
    def destination(self) -> str:
        return self.__destination

    @property
    def departure_time(self) -> datetime:
        return self.__departure_time

    @property
    def arrival_time(self) -> datetime:
        return self.__arrival_time

    # Рассчитывает длительность поездки
    def get_duration(self) -> str:
        duration = self.__arrival_time - self.__departure_time
        hours = duration.total_seconds() // 3600
        minutes = (duration.total_seconds() % 3600) // 60
        return f"{int(hours)}ч {int(minutes)}м"

    # Показывает информацию о маршруте
    def get_info(self) -> str:
        return (f"Маршрут {self.__departure} -> {self.__destination} | "
                f"Отправление: {self.__departure_time.strftime('%d.%m.%Y %H:%M')} | "
                f"Прибытие: {self.__arrival_time.strftime('%d.%m.%Y %H:%M')}")


# Класс Trip - конкретная поездка (маршрут + транспорт)
class Trip:
    def __init__(self, trip_id: str, route: Route, transport: Transport):
        self.__trip_id = trip_id            # ID поездки
        self.__route = route                # Маршрут
        self.__transport = transport        # Транспорт
        # Список свободных мест (вычисляется автоматически)
        self.__available_seats = [seat for seat in transport.seats if seat.is_available]

    # геттеры
    @property
    def trip_id(self) -> str:
        return self.__trip_id

    @property
    def route(self) -> Route:
        return self.__route

    @property
    def transport(self) -> Transport:
        return self.__transport

    @property
    def revenue(self) -> float:
        # Выручка от проданных билетов (сумма цен занятых мест)
        return sum(seat.price for seat in self.__transport.seats if not seat.is_available)

    def get_available_seats(self) -> List[Seat]:
        # Возвращает список свободных мест
        return [seat for seat in self.__transport.seats if seat.is_available]

    def find_seat_by_number(self, seat_number: str) -> Optional[Seat]:
        # Ищет свободное место по номеру
        for seat in self.__transport.seats:
            if seat.number == seat_number and seat.is_available:
                return seat  # Возвращает место если найдено и свободно
        return None  # Если место не найдено или занято

    def get_info(self) -> str:
        # Показывает информацию о поездке
        available_count = len(self.get_available_seats())
        return (f"Рейс {self.__trip_id} | {self.__route.get_info()} | "
                f"Доступно мест: {available_count}/{self.__transport.capacity}")
