from abc import ABC, abstractmethod
from services import Booking
from typing import List
import re


class Person(ABC):
    EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    PHONE_PATTERN = r'^[+]?[7-8][ (-]?\d{3}[) -]?\d{3}[ -]?\d{2}[ -]?\d{2}$'
    PASSPORT_PATTERN = r'^[0-9]{4}[\s]?[0-9]{6}$'
    NAME_PATTERN = r'^[A-Za-zА-Яа-яЁё\s\-]+$'

    def __init__(self, name: str, email: str, phone: str):
        self._name = name
        self._email = email
        self._phone = phone
        self._validate_contact_info()

    def _validate_contact_info(self) -> None:
        self._validate_name()
        self._validate_email()
        self._validate_phone()

    def _validate_name(self) -> None:
        if not re.match(self.NAME_PATTERN, self._name):
            raise ValueError(
                f"Некорректное имя: '{self._name}'. "
                f"Имя должно содержать только буквы, пробелы и дефисы"
            )

    def _validate_email(self) -> None:
        if not re.match(self.EMAIL_PATTERN, self._email):
            raise ValueError(
                f"Некорректный email адрес: '{self._email}'. "
                f"Пример правильного формата: user@example.com"
            )

    def _validate_phone(self) -> None:
        normalized_phone = re.sub(r'[\s\-()]', '', self._phone)

        if not re.match(self.PHONE_PATTERN, self._phone):
            raise ValueError(
                f"Некорректный номер телефона: '{self._phone}'. "
            )

        if normalized_phone.startswith('8') and len(normalized_phone) == 11:
            self._phone = '+7' + normalized_phone[1:]

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if not re.match(self.NAME_PATTERN, value):
            raise ValueError(f"Некорректное имя: '{value}'")
        self._name = value

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, value: str) -> None:
        if not re.match(self.EMAIL_PATTERN, value):
            raise ValueError(f"Некорректный email: '{value}'")
        self._email = value

    @property
    def phone(self) -> str:
        return self._phone

    @phone.setter
    def phone(self, value: str) -> None:
        if not re.match(self.PHONE_PATTERN, value):
            raise ValueError(f"Некорректный номер телефона: '{value}'")
        normalized_phone = re.sub(r'[\s\-()]', '', value)
        if normalized_phone.startswith('8') and len(normalized_phone) == 11:
            self._phone = '+7' + normalized_phone[1:]
        else:
            self._phone = value

    @abstractmethod
    def get_info(self) -> str:
        pass


class Passenger(Person):
    def __init__(self, name: str, email: str, phone: str, passport: str):
        super().__init__(name, email, phone)
        self.__passport = passport
        self.__bookings: List[Booking] = []
        self._validate_passport()

    def _validate_passport(self) -> None:
        password = re.sub(r'[\s]', '', self.__passport)
        if not re.match(self.PASSPORT_PATTERN, self.__passport):
            raise ValueError(
                f"Некорректный номер паспорта: '{self.__passport}'. "
                f"Паспорт должен содержать ровно 10 цифр"
            )

    @property
    def passport(self) -> str:
        return self.__passport

    @property
    def bookings(self) -> List[Booking]:
        return self.__bookings.copy()

    def add_booking(self, booking: Booking) -> None:
        self.__bookings.append(booking)

    def get_info(self) -> str:
        return f"Пассажир: {self.name}, Паспорт: {self.passport}"
