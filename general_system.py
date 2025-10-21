import uuid
from datetime import datetime
from typing import Dict, List

from action import Booking
from my_exceptions import SeatNotAvailableException, BookingNotFoundException
from person import Passenger
from transports import Transport, TransportType, Bus, Train
from trip import Route, Trip


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
            transport = Bus(transport_id, kwargs['model'], kwargs['capacity'], kwargs['has_wifi'],
                            kwargs['has_usb_charging'])
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
        booking = Booking(booking_id, trip, seat)
        passenger.add_booking(booking)
        self.__bookings[booking_id] = booking
        return booking

    def cancel_booking(self, booking: Booking):
        booking.cancel_booking()
        del self.__bookings[booking.booking_id]

    def find_booking_by_id(self, booking_id: str) -> Booking:
        if booking_id not in self.__bookings:
            raise BookingNotFoundException(f"Бронирование с ID {booking_id} не найдено")
        return self.__bookings[booking_id]

    def get_passenger_bookings(self, passport: str) -> List[Booking]:
        if passport not in self.__passengers:
            return []
        return self.__passengers[passport].bookings
