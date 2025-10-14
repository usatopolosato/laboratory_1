from seat import Seat
from datetime import datetime
from typing import List, Optional
from transports import Transport


class Route:
    def __init__(self, route_id: str, departure: str, destination: str,
                 departure_time: datetime, arrival_time: datetime):
        self.__route_id = route_id
        self.__departure = departure
        self.__destination = destination
        self.__departure_time = departure_time
        self.__arrival_time = arrival_time

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

    def get_duration(self) -> str:
        duration = self.__arrival_time - self.__departure_time
        hours = duration.total_seconds() // 3600
        minutes = (duration.total_seconds() % 3600) // 60
        return f"{int(hours)}ч {int(minutes)}м"

    def get_info(self) -> str:
        return (f"Маршрут {self.__departure} -> {self.__destination} | "
                f"Отправление: {self.__departure_time.strftime('%d.%m.%Y %H:%M')} | "
                f"Прибытие: {self.__arrival_time.strftime('%d.%m.%Y %H:%M')}")


class Trip:
    def __init__(self, trip_id: str, route: Route, transport: Transport):
        self.__trip_id = trip_id
        self.__route = route
        self.__transport = transport
        self.__available_seats = [seat for seat in transport.seats if seat.is_available]

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
        return sum(seat.price for seat in self.__transport.seats if not seat.is_available)

    def get_available_seats(self) -> List[Seat]:
        return [seat for seat in self.__transport.seats if seat.is_available]

    def find_seat_by_number(self, seat_number: str) -> Optional[Seat]:
        for seat in self.__transport.seats:
            if seat.number == seat_number and seat.is_available:
                return seat
        return None

    def get_info(self) -> str:
        available_count = len(self.get_available_seats())
        return (f"Рейс {self.__trip_id} | {self.__route.get_info()} | "
                f"Доступно мест: {available_count}/{self.__transport.capacity}")
