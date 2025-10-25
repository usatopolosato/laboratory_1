from my_exceptions import *
from trip import *
from transports import *


# Статусы бронирования - как этапы заказа
class BookingStatus(Enum):
    CONFIRMED = "подтверждено"    # Заказ подтвержден
    PENDING = "ожидает"           # Заказ ожидает оплаты
    CANCELLED = "отменено"        # Заказ отменен
    COMPLETED = "завершено"       # Поездка завершена


# Класс для работы с оплатой
class Payment:
    def __init__(self, payment_id: str, amount: float, payment_method: str):
        self.__payment_id = payment_id        # Уникальный номер платежа
        self.__amount = amount                # Сумма оплаты
        self.__payment_method = payment_method  # Способ оплаты (карта, наличные)
        self.__payment_date = datetime.now()  # Дата платежа
        self.__is_paid = False                # Статус оплаты

    # Методы для получения информации (только чтение)
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

    # Обработка платежа - проверяем хватает ли денег
    def process_payment(self, balance: float) -> None:
        if balance < self.__amount:
            raise NoMoneyException(
                f"Недостаточно средств. Требуется: {self.__amount}, доступно: {balance}"
            )
        self.__is_paid = True  # Если денег хватает - помечаем как оплачено

    # Краткая информация о платеже
    def get_info(self) -> str:
        status = "оплачено" if self.__is_paid else "не оплачено"
        return (f"Оплата {self.__payment_id}: {self.__amount} руб. "
                f"({self.__payment_method}) - {status}")


# Класс бронирования - основной заказ
class Booking:
    def __init__(self, booking_id: str, trip: Trip, seat: Seat):
        self.__booking_id = booking_id        # Номер бронирования
        self.__trip = trip                    # Поездка
        self.__seat = seat                    # Выбранное место
        self.__booking_date = datetime.now()  # Дата бронирования
        self.__status = BookingStatus.PENDING  # Статус - изначально "ожидает"
        self.__payment: Optional[Payment] = None  # Платеж (пока нет)

    # Методы для получения информации
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

    # Расчет общей цены (просто цена места)
    def calculate_total_price(self) -> float:
        return self.__seat.price

    # Добавление платежа к бронированию
    def add_payment(self, payment: Payment) -> None:
        self.__payment = payment

    # Подтверждение бронирования - только если оплачено
    def confirm_booking(self) -> None:
        if self.__payment and self.__payment.is_paid:
            self.__status = BookingStatus.CONFIRMED  # Меняем статус
            self.__seat.reserve()  # Занимаем место
        else:
            raise MyException("Невозможно подтвердить бронирование без оплаты")

    # Отмена бронирования
    def cancel_booking(self) -> None:
        self.__status = BookingStatus.CANCELLED  # Статус "отменено"
        self.__seat.release()  # Освобождаем место
        # Здесь могла бы быть логика возврата денег
        if self.__payment:
            pass

    # Краткая информация о бронировании
    def get_info(self) -> str:
        return (f"Бронирование {self.__booking_id} |"
                f"Статус: {self.__status.value} | Место: {self.__seat.number}")
