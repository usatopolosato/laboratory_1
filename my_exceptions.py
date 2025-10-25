# Базовое исключение для нашей системы - родитель для всех наших ошибок
class MyException(Exception):
    pass


# Исключение когда место уже занято или недоступно
class SeatNotAvailableException(MyException):
    pass
# Используется когда пытаются забронировать место, которое уже занято


# Исключение когда не хватает денег для оплаты
class NoMoneyException(MyException):
    pass
# Используется в Payment.process_payment() когда баланс меньше суммы оплаты


# Исключение когда бронирование не найдено
class BookingNotFoundException(Exception):
    pass
# Используется когда ищут бронирование по ID которого нет в системе
