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
        # Хранилища для всех данных системы
        self.__passengers: Dict[str, Passenger] = {}  # Пассажиры по паспорту
        self.__transports: Dict[str, Transport] = {}  # Транспорт по ID
        self.__routes: Dict[str, Route] = {}          # Маршруты по ID
        self.__trips: Dict[str, Trip] = {}            # Поездки по ID
        self.__bookings: Dict[str, Booking] = {}      # Бронирования по ID

    def __repr__(self) -> str:
        """Красивое строковое представление системы"""
        lines = ["=" * 80, "СИСТЕМА БРОНИРОВАНИЯ БИЛЕТОВ", "=" * 80,
                 f"\nПАССАЖИРЫ ({len(self.__passengers)}):", "-" * 40]

        # Пассажиры
        for passport, passenger in self.__passengers.items():
            bookings_count = len(passenger.bookings)
            lines.append(f"  {passenger.name:<20} | Телефон: {passenger.phone:<15} | "
                         f"Email: {passenger.email:<20} | Паспорт: {passport}")
            lines.append(f"    Бронирований: {bookings_count}")

        # Транспорт
        lines.append(f"\nТРАНСПОРТ ({len(self.__transports)}):")
        lines.append("-" * 40)
        for transport_id, transport in self.__transports.items():
            available_seats = sum(1 for seat in transport.seats if seat.is_available)
            total_seats = len(transport.seats)
            transport_type = "Автобус" if isinstance(transport, Bus) else "Поезд" if isinstance(
                transport, Train) else "Транспорт"

            lines.append(f"  {transport_type:<10} {transport.model:<15} | ID: {transport_id} | "
                         f"Места: {available_seats}/{total_seats} свободно")

            if isinstance(transport, Bus):
                lines.append(f"    Wi-Fi: {'Да' if transport.has_wifi else 'Нет'}, "
                             f"USB-зарядка: {'Да' if transport.has_usb_charging else 'Нет'}")
            elif isinstance(transport, Train):
                lines.append(f"    Вагонов: {transport.car_count}")

        # Маршруты
        lines.append(f"\nМАРШРУТЫ ({len(self.__routes)}):")
        lines.append("-" * 40)
        for route_id, route in self.__routes.items():
            duration = route.get_duration()
            lines.append(f"  {route.departure:<15} -> {route.destination:<15} | ID: {route_id}")
            lines.append(f"    Отправление: {route.departure_time.strftime('%d.%m.%Y %H:%M')}")
            lines.append(f"    Прибытие:    {route.arrival_time.strftime('%d.%m.%Y %H:%M')}")
            lines.append(f"    В пути:      {duration}")

        # Поездки
        lines.append(f"\nПОЕЗДКИ ({len(self.__trips)}):")
        lines.append("-" * 40)
        for trip_id, trip in self.__trips.items():
            available_seats = len(trip.get_available_seats())
            total_seats = trip.transport.capacity
            revenue = trip.revenue

            lines.append(
                f"  Поездка {trip_id} | Маршрут: {trip.route.departure} -> {trip.route.destination}")
            lines.append(f"    Транспорт: {trip.transport.model} | "
                         f"Свободных мест: {available_seats}/{total_seats} | "
                         f"Выручка: {revenue} руб.")

        # Бронирования
        lines.append(f"\nБРОНИРОВАНИЯ ({len(self.__bookings)}):")
        lines.append("-" * 40)

        status_translation = {
            "подтверждено": "ПОДТВЕРЖДЕНО",
            "ожидает": "ОЖИДАЕТ",
            "отменено": "ОТМЕНЕНО",
            "завершено": "ЗАВЕРШЕНО"
        }

        for booking_id, booking in self.__bookings.items():
            # Находим пассажира для этого бронирования
            passenger_name = "Неизвестно"
            for passenger in self.__passengers.values():
                if booking in passenger.bookings:
                    passenger_name = passenger.name
                    break

            status = status_translation.get(booking.status.value, booking.status.value.upper())

            lines.append(f"  Бронирование {booking_id}")
            lines.append(f"    Пассажир: {passenger_name}")
            lines.append(
                f"    Маршрут:  {booking.trip.route.departure} -> {booking.trip.route.destination}")
            lines.append(f"    Место:    {booking.seat.number} ({booking.seat.seat_class.value})")
            lines.append(f"    Цена:     {booking.seat.price} руб.")
            lines.append(f"    Дата:     {booking.booking_date.strftime('%d.%m.%Y %H:%M')}")
            lines.append(f"    Статус:   {status}")

            if booking.payment:
                payment_status = "Оплачено" if booking.payment.is_paid else "Не оплачено"
                lines.append(
                    f"    Оплата:   {booking.payment.amount} руб. ({booking.payment.payment_method}) - {payment_status}")

        # Статистика
        lines.append(f"\nСТАТИСТИКА СИСТЕМЫ:")
        lines.append("-" * 40)
        total_revenue = sum(trip.revenue for trip in self.__trips.values())
        confirmed_bookings = sum(1 for b in self.__bookings.values()
                                 if b.status.value == "подтверждено")
        pending_bookings = sum(1 for b in self.__bookings.values()
                               if b.status.value == "ожидает")

        lines.append(f"  Общая выручка:           {total_revenue} руб.")
        lines.append(f"  Всего бронирований:      {len(self.__bookings)}")
        lines.append(f"    - подтвержденных:      {confirmed_bookings}")
        lines.append(f"    - ожидает подтверждения: {pending_bookings}")
        lines.append(f"  Всего пассажиров:        {len(self.__passengers)}")
        lines.append(f"  Всего транспорта:        {len(self.__transports)}")
        lines.append(f"  Всего маршрутов:         {len(self.__routes)}")
        lines.append(f"  Всего поездок:           {len(self.__trips)}")

        lines.append("=" * 80)
        return "\n".join(lines)

    # геттеры
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

    # Сеттеры для восстановления системы
    def set_passengers(self, passengers: Dict[str, Passenger]) -> None:
        self.__passengers = passengers

    def set_transports(self, transports: Dict[str, Transport]) -> None:
        self.__transports = transports

    def set_routes(self, routes: Dict[str, Route]) -> None:
        self.__routes = routes

    def set_trips(self, trips: Dict[str, Trip]) -> None:
        self.__trips = trips

    def set_bookings(self, bookings: Dict[str, Booking]) -> None:
        self.__bookings = bookings

    # Методы для добавления отдельных объектов
    def add_passenger(self, passenger: Passenger) -> None:
        self.__passengers[passenger.passport] = passenger

    def add_transport(self, transport: Transport) -> None:
        self.__transports[transport.transport_id] = transport

    def add_route(self, route: Route) -> None:
        self.__routes[route.route_id] = route

    def add_trip(self, trip: Trip) -> None:
        self.__trips[trip.trip_id] = trip

    def add_booking(self, booking: Booking) -> None:
        self.__bookings[booking.booking_id] = booking

    # Методы создания новых объектов
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
        # Отменяем бронирование и удаляем из системы
        booking.cancel_booking()
        del self.__bookings[booking.booking_id]

    def find_booking_by_id(self, booking_id: str) -> Booking:
        # Ищем бронирование по ID
        if booking_id not in self.__bookings:
            raise BookingNotFoundException(f"Бронирование с ID {booking_id} не найдено")
        return self.__bookings[booking_id]

    def get_passenger_bookings(self, passport: str) -> List[Booking]:
        # Получаем все бронирования пассажира
        if passport not in self.__passengers:
            return []
        return self.__passengers[passport].bookings

    def clear_all_data(self) -> None:
        # Очищаем все данные системы (для тестирования)
        self.__passengers.clear()
        self.__transports.clear()
        self.__routes.clear()
        self.__trips.clear()
        self.__bookings.clear()
