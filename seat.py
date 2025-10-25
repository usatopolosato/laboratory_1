from my_exceptions import SeatNotAvailableException
from enum import Enum


# Типы мест в транспорте
class ClassSeat(Enum):
    ECONOMY = "эконом"    # Эконом класс
    BUSINESS = "бизнес"   # Бизнес класс


# Класс Seat - представляет одно место в транспорте
class Seat:
    def __init__(self, number: str, seat_class: ClassSeat, price: float):
        self.__number = number          # Номер места
        self.__seat_class = seat_class  # Класс места
        self.__price = price            # Цена места
        self.__is_available = True      # Свободно ли место (изначально да)

    # Свойства только для чтения - данные места нельзя менять напрямую
    @property
    def number(self) -> str:
        return self.__number           # Получить номер места

    @property
    def seat_class(self) -> ClassSeat:
        return self.__seat_class       # Получить класс места

    @property
    def price(self) -> float:
        return self.__price            # Получить цену

    @property
    def is_available(self) -> bool:
        return self.__is_available     # Проверить свободно ли место

    def reserve(self) -> None:
        # Забронировать место
        if not self.__is_available:
            # Если место уже занято - бросаем исключение
            raise SeatNotAvailableException(f"Место {self.number} уже занято")
        self.__is_available = False   # Помечаем как занятое

    def release(self) -> None:
        # Освободить место (при отмене бронирования)
        self.__is_available = True    # Помечаем как свободное

    def get_info(self) -> str:
        # Получить информацию о месте в читаемом виде
        status = "свободно" if self.__is_available else "занято"
        return f"Место {self.__number} ({self.__seat_class.value}) - {self.__price} руб. ({status})"
