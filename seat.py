from my_exceptions import SeatNotAvailableException
from enum import Enum


class ClassSeat(Enum):
    ECONOMY = "эконом"
    BUSINESS = "бизнес"


class Seat:
    def __init__(self, number: str, seat_class: ClassSeat, price: float):
        self.__number = number
        self.__seat_class = seat_class
        self.__price = price
        self.__is_available = True

    def reserve(self) -> None:
        if not self.__is_available:
            raise SeatNotAvailableException(f"Место {self.number} уже занято")
        self.__is_available = False

    def release(self) -> None:
        self.__is_available = True

    def get_info(self) -> str:
        status = "свободно" if self.__is_available else "занято"
        return f"Место {self.__number} ({self.__seat_class.value}) - {self.__price} руб. ({status})"
