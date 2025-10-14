from datetime import datetime
from my_exceptions import *
from enum import Enum
from typing import Optional, Dict
from trip import *
from seat import Seat
from person import Passenger
from transports import *
import uuid


class BookingStatus(Enum):
    CONFIRMED = "подтверждено"
    PENDING = "ожидает"
    CANCELLED = "отменено"
    COMPLETED = "завершено"


class Payment:
    def __init__(self, payment_id: str, amount: float, payment_method: str):
        self.__payment_id = payment_id
        self.__amount = amount
        self.__payment_method = payment_method
        self.__payment_date = datetime.now()
        self.__is_paid = False

    @property
    def payment_id(self) -> str:
        return self.__payment_id

    @property
    def amount(self) -> float:
        return self.__amount

    @property
    def payment_method(self) -> str:
        return self.__payment_method

    @property
    def payment_date(self) -> datetime:
        return self.__payment_date

    @property
    def is_paid(self) -> bool:
        return self.__is_paid

    def process_payment(self, balance: float) -> None:
        if balance < self.__amount:
            raise NoMoneyException(
                f"Недостаточно средств. Требуется: {self.__amount}, доступно: {balance}"
            )
        self.__is_paid = True

    def get_info(self) -> str:
        status = "оплачено" if self.__is_paid else "не оплачено"
        return (f"Оплата {self.__payment_id}: {self.__amount} руб. "
                f"({self.__payment_method}) - {status}")


class Booking:
    def __init__(self, booking_id: str, passenger: Passenger, trip: Trip, seat: Seat):
        self.__booking_id = booking_id
        self.__passenger = passenger
        self.__trip = trip
        self.__seat = seat
        self.__booking_date = datetime.now()
        self.__status = BookingStatus.PENDING
        self.__payment: Optional[Payment] = None

    @property
    def booking_id(self) -> str:
        return self.__booking_id

    @property
    def passenger(self) -> Passenger:
        return self.__passenger

    @property
    def trip(self) -> Trip:
        return self.__trip

    @property
    def seat(self) -> Seat:
        return self.__seat

    @property
    def booking_date(self) -> datetime:
        return self.__booking_date

    @property
    def status(self) -> BookingStatus:
        return self.__status

    @property
    def payment(self) -> Optional[Payment]:
        return self.__payment

    def calculate_total_price(self) -> float:
        return self.__seat.price

    def add_payment(self, payment: Payment) -> None:
        self.__payment = payment

    def confirm_booking(self) -> None:
        if self.__payment and self.__payment.is_paid:
            self.__status = BookingStatus.CONFIRMED
            self.__seat.reserve()
            self.__passenger.add_booking(self)
        else:
            raise MyException("Невозможно подтвердить бронирование без оплаты")

    def cancel_booking(self) -> None:
        self.__status = BookingStatus.CANCELLED
        self.__seat.release()
        if self.__payment:
            pass

    def get_info(self) -> str:
        return (f"Бронирование {self.__booking_id} | {self.__passenger.name} | "
                f"Статус: {self.__status.value} | Место: {self.__seat.number}")


class BookingSystem:
    def __init__(self):
        self.__passengers: Dict[str, Passenger] = {}
        self.__transports: Dict[str, Transport] = {}
        self.__routes: Dict[str, Route] = {}
        self.__trips: Dict[str, Trip] = {}
        self.__bookings: Dict[str, Booking] = {}

    @property
    def passengers(self) -> Dict[str, Passenger]:
        return self.__passengers.copy()

    @property
    def transports(self) -> Dict[str, Transport]:
        return self.__transports.copy()

    @property
    def routes(self) -> Dict[str, Route]:
        return self.__routes.copy()

    @property
    def trips(self) -> Dict[str, Trip]:
        return self.__trips.copy()

    @property
    def bookings(self) -> Dict[str, Booking]:
        return self.__bookings.copy()

    def create_passenger(self, name: str, email: str, phone: str, passport: str) -> Passenger:
        passenger = Passenger(name, email, phone, passport)
        self.__passengers[passport] = passenger
        return passenger

    def create_transport(self, transport_type: TransportType, **kwargs) -> Transport:
        transport_id = str(uuid.uuid4())[:8]
        if transport_type == TransportType.BUS:
            transport = Bus(transport_id, kwargs['model'], kwargs['capacity'], kwargs['has_wifi'])
        elif transport_type == TransportType.TRAIN:
            transport = Train(transport_id, kwargs['model'], kwargs['capacity'],
                              kwargs['car_count'])
        else:
            transport = Transport(transport_id, kwargs['model'], kwargs['capacity'])

        self.__transports[transport_id] = transport
        return transport

    def create_route(self, departure: str, destination: str,
                     departure_time: datetime, arrival_time: datetime) -> Route:
        route_id = str(uuid.uuid4())[:8]
        route = Route(route_id, departure, destination, departure_time, arrival_time)
        self.__routes[route_id] = route
        return route

    def create_trip(self, route: Route, transport: Transport) -> Trip:
        trip_id = str(uuid.uuid4())[:8]
        trip = Trip(trip_id, route, transport)
        self.__trips[trip_id] = trip
        return trip

    def create_booking(self, passenger: Passenger, trip: Trip, seat_number: str) -> Booking:
        seat = trip.find_seat_by_number(seat_number)
        if not seat:
            raise SeatNotAvailableException(f"Место {seat_number} недоступно")

        booking_id = str(uuid.uuid4())[:8]
        booking = Booking(booking_id, passenger, trip, seat)
        self.__bookings[booking_id] = booking
        return booking

    def find_booking_by_id(self, booking_id: str) -> Booking:
        if booking_id not in self.__bookings:
            raise BookingNotFoundException(f"Бронирование с ID {booking_id} не найдено")
        return self.__bookings[booking_id]

    def get_passenger_bookings(self, passport: str) -> List[Booking]:
        if passport not in self.__passengers:
            return []
        return self.__passengers[passport].bookings
