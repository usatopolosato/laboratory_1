from my_exceptions import *
from trip import *
from transports import *


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
    def __init__(self, booking_id: str, trip: Trip, seat: Seat):
        self.__booking_id = booking_id
        self.__trip = trip
        self.__seat = seat
        self.__booking_date = datetime.now()
        self.__status = BookingStatus.PENDING
        self.__payment: Optional[Payment] = None

    @property
    def booking_id(self) -> str:
        return self.__booking_id

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
        else:
            raise MyException("Невозможно подтвердить бронирование без оплаты")

    def cancel_booking(self) -> None:
        self.__status = BookingStatus.CANCELLED
        self.__seat.release()
        if self.__payment:
            pass

    def get_info(self) -> str:
        return (f"Бронирование {self.__booking_id} |"
                f"Статус: {self.__status.value} | Место: {self.__seat.number}")
