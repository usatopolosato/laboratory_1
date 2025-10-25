import json
from datetime import datetime
from typing import Dict, List, Any
from abc import ABC, abstractmethod
import xml.etree.ElementTree as ET
from xml.dom import minidom
from general_system import BookingSystem
from my_exceptions import *
from transports import Bus, Train, Transport
from trip import Trip, Route
from seat import ClassSeat, Seat
from person import Passenger
from action import Payment, Booking, BookingStatus


# Абстрактные классы
class DataReader(ABC):
    @abstractmethod
    def read(self, filename: str) -> Any:
        pass


class DataWriter(ABC):
    @abstractmethod
    def write(self, system: BookingSystem, filename: str) -> None:
        pass


# Класс для записи в XML формат
class XMLWriter(DataWriter):
    def write(self, system: BookingSystem, filename: str) -> None:
        # Создаем структуру XML и сохраняем в файл
        root = self._create_xml_structure(system)
        xml_str = self._format_xml(root)  # перевод в читаемый формат

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(xml_str)
        except (IOError, ET.ParseError) as e:
            raise MyException(f"Ошибка записи XML: {e}")

    def _create_xml_structure(self, system: BookingSystem) -> ET.Element:
        root = ET.Element('BookingSystem')

        # Пассажиры
        passengers_elem = ET.SubElement(root, 'Passengers')
        for passenger in system.passengers.values():
            self._add_passenger_element(passengers_elem, passenger)

        # Транспорт
        transports_elem = ET.SubElement(root, 'Transports')
        for transport in system.transports.values():
            self._add_transport_element(transports_elem, transport)

        # Маршруты
        routes_elem = ET.SubElement(root, 'Routes')
        for route in system.routes.values():
            self._add_route_element(routes_elem, route)

        # Поездки
        trips_elem = ET.SubElement(root, 'Trips')
        for trip in system.trips.values():
            self._add_trip_element(trips_elem, trip)

        # Бронирования
        bookings_elem = ET.SubElement(root, 'Bookings')
        for booking in system.bookings.values():
            self._add_booking_element(bookings_elem, booking)

        return root

    # для удобства разбили на под задачи, чтобы не грузить кодом одну функцию
    @staticmethod
    def _add_passenger_element(parent: ET.Element, passenger: Passenger) -> None:
        passenger_elem = ET.SubElement(parent, 'Passenger')
        ET.SubElement(passenger_elem, 'Name').text = passenger.name
        ET.SubElement(passenger_elem, 'Email').text = passenger.email
        ET.SubElement(passenger_elem, 'Phone').text = passenger.phone
        ET.SubElement(passenger_elem, 'Passport').text = passenger.passport

    @staticmethod
    def _add_transport_element(parent: ET.Element, transport: Transport) -> None:
        transport_elem = ET.SubElement(parent, 'Transport')
        ET.SubElement(transport_elem, 'TransportID').text = transport.transport_id
        ET.SubElement(transport_elem, 'Model').text = transport.model
        ET.SubElement(transport_elem, 'Capacity').text = str(transport.capacity)
        ET.SubElement(transport_elem, 'Type').text = type(transport).__name__

        # Специфичные поля
        if isinstance(transport, Bus):
            ET.SubElement(transport_elem, 'HasWifi').text = str(transport.has_wifi)
            ET.SubElement(transport_elem, 'HasUSBCharging').text = str(transport.has_usb_charging)
        elif isinstance(transport, Train):
            ET.SubElement(transport_elem, 'CarCount').text = str(transport.car_count)

        # Места
        seats_elem = ET.SubElement(transport_elem, 'Seats')
        for seat in transport.seats:
            seat_elem = ET.SubElement(seats_elem, 'Seat')
            ET.SubElement(seat_elem, 'Number').text = seat.number
            ET.SubElement(seat_elem, 'Class').text = seat.seat_class.value
            ET.SubElement(seat_elem, 'Price').text = str(seat.price)
            ET.SubElement(seat_elem, 'IsAvailable').text = str(seat.is_available)

    @staticmethod
    def _add_route_element(parent: ET.Element, route: Route) -> None:
        route_elem = ET.SubElement(parent, 'Route')
        ET.SubElement(route_elem, 'RouteID').text = route.route_id
        ET.SubElement(route_elem, 'Departure').text = route.departure
        ET.SubElement(route_elem, 'Destination').text = route.destination
        ET.SubElement(route_elem, 'DepartureTime').text = route.departure_time.isoformat()
        ET.SubElement(route_elem, 'ArrivalTime').text = route.arrival_time.isoformat()

    @staticmethod
    def _add_trip_element(parent: ET.Element, trip: Trip) -> None:
        trip_elem = ET.SubElement(parent, 'Trip')
        ET.SubElement(trip_elem, 'TripID').text = trip.trip_id
        ET.SubElement(trip_elem, 'RouteID').text = trip.route.route_id
        ET.SubElement(trip_elem, 'TransportID').text = trip.transport.transport_id
        ET.SubElement(trip_elem, 'Revenue').text = str(trip.revenue)

    @staticmethod
    def _add_booking_element(parent: ET.Element, booking: Booking) -> None:
        booking_elem = ET.SubElement(parent, 'Booking')
        ET.SubElement(booking_elem, 'BookingID').text = booking.booking_id
        ET.SubElement(booking_elem, 'TripID').text = booking.trip.trip_id
        ET.SubElement(booking_elem, 'SeatNumber').text = booking.seat.number
        ET.SubElement(booking_elem, 'BookingDate').text = booking.booking_date.isoformat()
        ET.SubElement(booking_elem, 'Status').text = booking.status.value

        if booking.payment:
            payment_elem = ET.SubElement(booking_elem, 'Payment')
            ET.SubElement(payment_elem, 'PaymentID').text = booking.payment.payment_id
            ET.SubElement(payment_elem, 'Amount').text = str(booking.payment.amount)
            ET.SubElement(payment_elem, 'PaymentMethod').text = booking.payment.payment_method
            ET.SubElement(payment_elem,
                          'PaymentDate').text = booking.payment.payment_date.isoformat()
            ET.SubElement(payment_elem, 'IsPaid').text = str(booking.payment.is_paid)

    # Перевод в более читаемый формат
    @staticmethod
    def _format_xml(root: ET.Element) -> str:
        rough_string = ET.tostring(root, encoding='utf-8')
        parsed = minidom.parseString(rough_string)
        return parsed.toprettyxml(indent="  ")


# Класс для записи в JSON формат
class JsonWriter(DataWriter):
    def write(self, system: BookingSystem, filename: str) -> None:
        # Подготавливаем данные и сохраняем в JSON
        data = self._prepare_data(system)

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=self._json_serializer)
        except (IOError, TypeError) as e:
            raise MyException(f"Ошибка записи JSON: {e}")

    def _prepare_data(self, system: BookingSystem) -> Dict[str, Any]:
        # Собираем все данные системы в один большой словарь
        return {
            'passengers': self._serialize_passengers(system),      # Пассажиры
            'transports': self._serialize_transports(system),      # Транспорт
            'routes': self._serialize_routes(system),              # Маршруты
            'trips': self._serialize_trips(system),                # Поездки
            'bookings': self._serialize_bookings(system)           # Бронирования
        }

    # Далее преобразования в словари
    def _serialize_passengers(self, system: BookingSystem) -> List[Dict[str, str]]:
        return [
            {
                'name': p.name,
                'email': p.email,
                'phone': p.phone,
                'passport': p.passport
            } for p in system.passengers.values()
        ]

    def _serialize_transports(self, system: BookingSystem) -> List[Dict[str, Any]]:
        transports_data = []
        for transport in system.transports.values():
            transport_data = {
                'transport_id': transport.transport_id,
                'model': transport.model,
                'capacity': transport.capacity,
                'type': type(transport).__name__,
                'seats': [
                    {
                        'number': seat.number,
                        'seat_class': seat.seat_class.value,
                        'price': seat.price,
                        'is_available': seat.is_available
                    } for seat in transport.seats
                ]
            }

            # Добавляем специфичные поля для разных типов транспорта
            if isinstance(transport, Bus):
                transport_data.update({
                    'has_wifi': transport.has_wifi,
                    'has_usb_charging': transport.has_usb_charging
                })
            elif isinstance(transport, Train):
                transport_data.update({
                    'car_count': transport.car_count
                })

            transports_data.append(transport_data)
        return transports_data

    def _serialize_routes(self, system: BookingSystem) -> List[Dict[str, Any]]:
        return [
            {
                'route_id': r.route_id,
                'departure': r.departure,
                'destination': r.destination,
                'departure_time': r.departure_time.isoformat(),
                'arrival_time': r.arrival_time.isoformat()
            } for r in system.routes.values()
        ]

    def _serialize_trips(self, system: BookingSystem) -> List[Dict[str, Any]]:
        return [
            {
                'trip_id': t.trip_id,
                'route_id': t.route.route_id,
                'transport_id': t.transport.transport_id,
                'revenue': t.revenue
            } for t in system.trips.values()
        ]

    def _serialize_bookings(self, system: BookingSystem) -> List[Dict[str, Any]]:
        bookings_data = []
        for booking in system.bookings.values():
            booking_data = {
                'booking_id': booking.booking_id,
                'trip_id': booking.trip.trip_id,
                'seat_number': booking.seat.number,
                'booking_date': booking.booking_date.isoformat(),
                'status': booking.status.value
            }

            if booking.payment:
                booking_data['payment'] = {
                    'payment_id': booking.payment.payment_id,
                    'amount': booking.payment.amount,
                    'payment_method': booking.payment.payment_method,
                    'payment_date': booking.payment.payment_date.isoformat(),
                    'is_paid': booking.payment.is_paid
                }

            bookings_data.append(booking_data)
        return bookings_data

    @staticmethod
    def _json_serializer(obj):
        # Помощник для преобразования дат в строки
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


# Класс для чтения из JSON
class JsonReader(DataReader):
    def read(self, filename: str) -> BookingSystem:
        # Читаем JSON и восстанавливаем систему
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return self._restore_system_from_data(data)
        except FileNotFoundError:
            raise MyException(f"JSON файл не найден: {filename}")
        except json.JSONDecodeError as e:
            raise MyException(f"Некорректный JSON формат в файле {filename}: {e}")
        except UnicodeDecodeError as e:
            raise MyException(f"Ошибка кодировки в файле {filename}: {e}")

    def _restore_system_from_data(self, data: Dict[str, Any]) -> BookingSystem:
        # Восстанавливает систему из данных JSON
        system = BookingSystem()

        # Восстановление транспорта (должно быть первым, т.к. нужен для поездок)
        transport_map = {}
        for transport_data in data.get('transports', []):
            transport = self._create_transport_from_data(transport_data)
            transport_map[transport_data['transport_id']] = transport

        system.set_transports(transport_map)

        # Восстановление маршрутов
        route_map = {}
        for route_data in data.get('routes', []):
            route = self._create_route_from_data(route_data)
            route_map[route_data['route_id']] = route

        system.set_routes(route_map)

        # Восстановление поездок
        trip_map = {}
        for trip_data in data.get('trips', []):
            route = route_map.get(trip_data['route_id'])
            transport = transport_map.get(trip_data['transport_id'])
            if route and transport:
                trip = Trip(trip_data['trip_id'], route, transport)
                trip_map[trip_data['trip_id']] = trip

        system.set_trips(trip_map)

        # Восстановление пассажиров
        passenger_map = {}
        for passenger_data in data.get('passengers', []):
            passenger = Passenger(
                passenger_data['name'],
                passenger_data['email'],
                passenger_data['phone'],
                passenger_data['passport']
            )
            passenger_map[passenger_data['passport']] = passenger

        system.set_passengers(passenger_map)

        # Восстановление бронирований
        for booking_data in data.get('bookings', []):
            self._create_booking_from_data(system, booking_data, trip_map, passenger_map)

        return system

    def _create_transport_from_data(self, transport_data: Dict[str, Any]) -> Transport:
        # Создает транспорт из данных
        transport_type = transport_data['type']

        if transport_type == 'Bus':
            transport = Bus(
                transport_data['transport_id'],
                transport_data['model'],
                transport_data['capacity'],
                transport_data['has_wifi'],
                transport_data['has_usb_charging']
            )
        elif transport_type == 'Train':
            transport = Train(
                transport_data['transport_id'],
                transport_data['model'],
                transport_data['capacity'],
                transport_data['car_count']
            )
        else:
            transport = Transport(
                transport_data['transport_id'],
                transport_data['model'],
                transport_data['capacity']
            )

        # Восстанавливаем места
        for seat_data in transport_data.get('seats', []):
            seat_class = ClassSeat(seat_data['seat_class'])
            seat = Seat(seat_data['number'], seat_class, seat_data['price'])
            if not seat_data['is_available']:
                seat._Seat__is_available = False
            transport.add_seat(seat)

        return transport

    def _create_route_from_data(self, route_data: Dict[str, Any]) -> Route:
        # Создает маршрут из данных
        departure_time = datetime.fromisoformat(route_data['departure_time'])
        arrival_time = datetime.fromisoformat(route_data['arrival_time'])

        return Route(
            route_data['route_id'],
            route_data['departure'],
            route_data['destination'],
            departure_time,
            arrival_time
        )

    def _create_booking_from_data(self, system: BookingSystem, booking_data: Dict[str, Any],
                                  trip_map: Dict[str, Trip],
                                  passenger_map: Dict[str, Passenger]) -> None:
        # Создает бронирование из данных
        trip = trip_map.get(booking_data['trip_id'])
        if not trip:
            return

        # Находим место в транспорте
        seat = None
        for transport_seat in trip.transport.seats:
            if transport_seat.number == booking_data['seat_number']:
                seat = transport_seat
                break

        if not seat:
            return

        # Создаем бронирование
        booking = Booking(booking_data['booking_id'], trip, seat)
        booking._Booking__booking_date = datetime.fromisoformat(booking_data['booking_date'])
        booking._Booking__status = BookingStatus(booking_data['status'])

        # Восстанавливаем статус места
        if booking_data['status'] == BookingStatus.CONFIRMED.value:
            seat._Seat__is_available = False

        # Восстанавливаем платеж
        if 'payment' in booking_data:
            payment_data = booking_data['payment']
            payment = Payment(
                payment_data['payment_id'],
                payment_data['amount'],
                payment_data['payment_method']
            )
            payment._Payment__payment_date = datetime.fromisoformat(payment_data['payment_date'])
            payment._Payment__is_paid = payment_data['is_paid']
            booking.add_payment(payment)

        system.add_booking(booking)

        # Добавляем бронирование пассажиру
        for passenger in passenger_map.values():
            for passenger_booking in passenger.bookings:
                if passenger_booking.booking_id == booking_data['booking_id']:
                    # Уже добавлено
                    break
            else:
                # Ищем пассажира по бронированиям (это упрощенный подход)
                # В реальной системе нужно хранить связь пассажир-бронирование
                passenger.add_booking(booking)
                break


# Класс для чтения из XML
class XMLReader(DataReader):
    def read(self, filename: str) -> BookingSystem:
        try:
            # Читаем XML и восстанавливаем систему
            tree = ET.parse(filename)  # Парсим XML файл
            root = tree.getroot()  # Получаем корневой элемент
            return self._restore_system_from_xml_root(root)
        except FileNotFoundError:
            raise MyException(f"XML файл не найден: {filename}")
        except ET.ParseError as e:
            raise MyException(f"Некорректный XML формат в файле {filename}: {e}")

    def _restore_system_from_xml_root(self, root: ET.Element) -> BookingSystem:
        # Восстанавливает систему из XML
        system = BookingSystem()

        # Восстановление транспорта
        transport_map = {}
        transports_elem = root.find('Transports')
        if transports_elem is not None:
            for transport_elem in transports_elem.findall('Transport'):
                transport = self._create_transport_from_xml(transport_elem)
                transport_map[transport.transport_id] = transport
        system.set_transports(transport_map)

        # Восстановление маршрутов
        route_map = {}
        routes_elem = root.find('Routes')
        if routes_elem is not None:
            for route_elem in routes_elem.findall('Route'):
                route = self._create_route_from_xml(route_elem)
                route_map[route.route_id] = route

        system.set_routes(route_map)

        # Восстановление поездок
        trip_map = {}
        trips_elem = root.find('Trips')
        if trips_elem is not None:
            for trip_elem in trips_elem.findall('Trip'):
                trip_id = trip_elem.find('TripID').text
                route_id = trip_elem.find('RouteID').text
                transport_id = trip_elem.find('TransportID').text

                route = route_map.get(route_id)
                transport = transport_map.get(transport_id)

                if route and transport:
                    trip = Trip(trip_id, route, transport)
                    trip_map[trip_id] = trip

        system.set_trips(trip_map)

        # Восстановление пассажиров
        passenger_map = {}
        passengers_elem = root.find('Passengers')
        if passengers_elem is not None:
            for passenger_elem in passengers_elem.findall('Passenger'):
                name = passenger_elem.find('Name').text
                email = passenger_elem.find('Email').text
                phone = passenger_elem.find('Phone').text
                passport = passenger_elem.find('Passport').text

                passenger = Passenger(name, email, phone, passport)
                passenger_map[passport] = passenger

        system.set_passengers(passenger_map)

        # Восстановление бронирований
        bookings_elem = root.find('Bookings')
        if bookings_elem is not None:
            for booking_elem in bookings_elem.findall('Booking'):
                self._create_booking_from_xml(system, booking_elem, trip_map, passenger_map)

        return system

    def _create_transport_from_xml(self, transport_elem: ET.Element) -> Transport:
        # Создает транспорт из XML элемента
        transport_id = transport_elem.find('TransportID').text
        model = transport_elem.find('Model').text
        capacity = int(transport_elem.find('Capacity').text)
        transport_type = transport_elem.find('Type').text

        if transport_type == 'Bus':
            has_wifi = transport_elem.find('HasWifi').text.lower() == 'true'
            has_usb_charging = transport_elem.find('HasUSBCharging').text.lower() == 'true'
            transport = Bus(transport_id, model, capacity, has_wifi, has_usb_charging)
        elif transport_type == 'Train':
            car_count = int(transport_elem.find('CarCount').text)
            transport = Train(transport_id, model, capacity, car_count)
        else:
            transport = Transport(transport_id, model, capacity)

        # Восстанавливаем места
        seats_elem = transport_elem.find('Seats')
        if seats_elem is not None:
            for seat_elem in seats_elem.findall('Seat'):
                number = seat_elem.find('Number').text
                seat_class = ClassSeat(seat_elem.find('Class').text)
                price = float(seat_elem.find('Price').text)
                is_available = seat_elem.find('IsAvailable').text.lower() == 'true'

                seat = Seat(number, seat_class, price)
                if not is_available:
                    seat._Seat__is_available = False
                transport.add_seat(seat)

        return transport

    def _create_route_from_xml(self, route_elem: ET.Element) -> Route:
        # Создает маршрут из XML элемента
        route_id = route_elem.find('RouteID').text
        departure = route_elem.find('Departure').text
        destination = route_elem.find('Destination').text
        departure_time = datetime.fromisoformat(route_elem.find('DepartureTime').text)
        arrival_time = datetime.fromisoformat(route_elem.find('ArrivalTime').text)

        return Route(route_id, departure, destination, departure_time, arrival_time)

    def _create_booking_from_xml(self, system: BookingSystem, booking_elem: ET.Element,
                                 trip_map: Dict[str, Trip],
                                 passenger_map: Dict[str, Passenger]) -> None:
        # Создает бронирование из XML элемента
        booking_id = booking_elem.find('BookingID').text
        trip_id = booking_elem.find('TripID').text
        seat_number = booking_elem.find('SeatNumber').text
        booking_date = datetime.fromisoformat(booking_elem.find('BookingDate').text)
        status = BookingStatus(booking_elem.find('Status').text)

        trip = trip_map.get(trip_id)
        if not trip:
            return

        # Находим место
        seat = None
        for transport_seat in trip.transport.seats:
            if transport_seat.number == seat_number:
                seat = transport_seat
                break

        if not seat:
            return

        # Создаем бронирование
        booking = Booking(booking_id, trip, seat)
        booking._Booking__booking_date = booking_date
        booking._Booking__status = status

        # Восстанавливаем статус места
        if status == BookingStatus.CONFIRMED:
            seat._Seat__is_available = False

        # Восстанавливаем платеж
        payment_elem = booking_elem.find('Payment')
        if payment_elem is not None:
            payment_id = payment_elem.find('PaymentID').text
            amount = float(payment_elem.find('Amount').text)
            payment_method = payment_elem.find('PaymentMethod').text
            payment_date = datetime.fromisoformat(payment_elem.find('PaymentDate').text)
            is_paid = payment_elem.find('IsPaid').text.lower() == 'true'

            payment = Payment(payment_id, amount, payment_method)
            payment._Payment__payment_date = payment_date
            payment._Payment__is_paid = is_paid
            booking.add_payment(payment)

        # Добавляем бронирование в систему
        system.add_booking(booking)

        # Связываем с пассажиром (упрощенно - с первым подходящим)
        for passenger in passenger_map.values():
            passenger.add_booking(booking)
            break  # В реальной системе нужно правильное связывание


# Главный класс для работы с сохранением/загрузкой
class DataSerializer:
    def __init__(self):
        # Создаем экземпляры всех читателей и писателей
        self.json_writer = JsonWriter()
        self.json_reader = JsonReader()
        self.xml_writer = XMLWriter()
        self.xml_reader = XMLReader()

    # Статические методы для удобного использования(связан с классом, а не с объектом)
    @staticmethod
    def save_to_json(system: BookingSystem, filename: str) -> None:
        JsonWriter().write(system, filename)  # Сохраняем в JSON

    @staticmethod
    def load_from_json(filename: str) -> BookingSystem:
        return JsonReader().read(filename)  # Загружаем из JSON

    @staticmethod
    def save_to_xml(system: BookingSystem, filename: str) -> None:
        XMLWriter().write(system, filename)  # Сохраняем в XML

    @staticmethod
    def load_from_xml(filename: str) -> BookingSystem:
        return XMLReader().read(filename)  # Загружаем из XML
