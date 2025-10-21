from __future__ import annotations
import json
import xml.etree.ElementTree as ET
from services import BookingSystem, Booking
from my_exceptions import MyException
from xml.dom import minidom
from typing import Dict, List, Any
from abc import ABC, abstractmethod
from person import Passenger


class DataReader(ABC):
    @abstractmethod
    def read(self, filename: str) -> Any:
        pass


class DataWriter(ABC):
    @abstractmethod
    def write(self, system: BookingSystem, filename: str) -> None:
        pass


def _serialize_passengers(system: BookingSystem) -> List[Dict[str, str]]:
    return [
        {
            'name': p.name,
            'email': p.email,
            'phone': p.phone,
            'passport': p.passport
        } for p in system.passengers.values()
    ]


class JsonWriter(DataWriter):
    def write(self, system: BookingSystem, filename: str) -> None:
        data = self._prepare_data(system)

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except (IOError, TypeError) as e:
            raise MyException(f"Ошибка записи JSON: {e}")

    def _prepare_data(self, system: BookingSystem) -> Dict[str, Any]:
        return {
            'passengers': _serialize_passengers(system),
            'bookings': self._serialize_bookings(system)
        }

    @staticmethod
    def _serialize_bookings(system: BookingSystem) -> List[Dict[str, str]]:
        return [
            {
                'booking_id': b.booking_id,
                'passenger_passport': b.passenger.passport,
                'trip_id': b.trip.trip_id,
                'seat_number': b.seat.number,
                'status': b.status.value
            } for b in system.bookings.values()
        ]


class JsonReader(DataReader):
    def read(self, filename: str) -> Dict[str, Any]:
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise MyException(f"JSON файл не найден: {filename}")
        except json.JSONDecodeError as e:
            raise MyException(f"Некорректный JSON формат в файле {filename}: {e}")
        except UnicodeDecodeError as e:
            raise MyException(f"Ошибка кодировки в файле {filename}: {e}")


class XMLWriter(DataWriter):
    def write(self, system: BookingSystem, filename: str) -> None:
        root = self._create_xml_structure(system)
        xml_str = self._format_xml(root)

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(xml_str)
        except (IOError, ET.ParseError) as e:
            raise MyException(f"Ошибка записи XML: {e}")

    def _create_xml_structure(self, system: BookingSystem) -> ET.Element:
        root = ET.Element('BookingSystem')
        passengers_elem = ET.SubElement(root, 'Passengers')
        for passenger in system.passengers.values():
            self._add_passenger_element(passengers_elem, passenger)
        bookings_elem = ET.SubElement(root, 'Bookings')
        for booking in system.bookings.values():
            self._add_booking_element(bookings_elem, booking)

        return root

    @staticmethod
    def _add_passenger_element(parent: ET.Element, passenger: Passenger) -> None:
        passenger_elem = ET.SubElement(parent, 'Passenger')
        ET.SubElement(passenger_elem, 'Name').text = passenger.name
        ET.SubElement(passenger_elem, 'Email').text = passenger.email
        ET.SubElement(passenger_elem, 'Phone').text = passenger.phone
        ET.SubElement(passenger_elem, 'Passport').text = passenger.passport

    @staticmethod
    def _add_booking_element(parent: ET.Element, booking: Booking) -> None:
        booking_elem = ET.SubElement(parent, 'Booking')
        ET.SubElement(booking_elem, 'BookingID').text = booking.booking_id
        ET.SubElement(booking_elem, 'PassengerPassport').text = booking.passenger.passport
        ET.SubElement(booking_elem, 'TripID').text = booking.trip.trip_id
        ET.SubElement(booking_elem, 'SeatNumber').text = booking.seat.number
        ET.SubElement(booking_elem, 'Status').text = booking.status.value

    @staticmethod
    def _format_xml(root: ET.Element) -> str:
        rough_string = ET.tostring(root, encoding='utf-8')
        parsed = minidom.parseString(rough_string)
        return parsed.toprettyxml(indent="  ")


class XMLReader(DataReader):
    def read(self, filename: str) -> ET.Element:
        try:
            tree = ET.parse(filename)
            return tree.getroot()
        except FileNotFoundError:
            raise MyException(f"XML файл не найден: {filename}")
        except ET.ParseError as e:
            raise MyException(f"Некорректный XML формат в файле {filename}: {e}")


class DataSerializer:
    def __init__(self):
        self.json_writer = JsonWriter()
        self.json_reader = JsonReader()
        self.xml_writer = XMLWriter()
        self.xml_reader = XMLReader()

    @staticmethod
    def save_to_json(system: BookingSystem, filename: str) -> None:
        JsonWriter().write(system, filename)

    @staticmethod
    def load_from_json(filename: str) -> Dict[str, Any]:
        return JsonReader().read(filename)

    @staticmethod
    def save_to_xml(system: BookingSystem, filename: str) -> None:
        XMLWriter().write(system, filename)

    @staticmethod
    def load_from_xml(filename: str) -> ET.Element:
        return XMLReader().read(filename)
