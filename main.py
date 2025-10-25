from datetime import timedelta
import os
from seat import *
from action import *
from my_exceptions import *
from jobwf import *


def test_booking_system():
    """Комплексное тестирование системы бронирования"""
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ СИСТЕМЫ БРОНИРОВАНИЯ")
    print("=" * 60)
    system = BookingSystem()

    try:
        # 1. Тестирование создания пассажиров
        print("\n1. ТЕСТИРОВАНИЕ СОЗДАНИЯ ПАССАЖИРОВ")
        print("-" * 40)

        # Успешное создание
        passenger1 = system.create_passenger(
            "Иван Иванов",
            "ivan@mail.ru",
            "+79161234567",
            "1234567890"
        )
        print(f"Пассажир создан: {passenger1.get_info()}")

        passenger2 = system.create_passenger(
            "Анна Петрова",
            "anna@yandex.ru",
            "8-916-987-65-43",
            "0987654321"
        )
        print(f"Пассажир создан: {passenger2.get_info()}")

        # Тест ошибок валидации
        print("\nТест ошибок валидации:")
        try:
            system.create_passenger(" -", "test@mail.ru", "+79161111111", "1111111111")
        except ValueError as e:
            print(f"Корректно отловлена ошибка имени: {e}")

        try:
            system.create_passenger("Иван", "invalid-email", "+79161111111", "1111111111")
        except ValueError as e:
            print(f"Корректно отловлена ошибка email: {e}")

        try:
            system.create_passenger("Иван", "test@mail.ru", "123", "1111111111")
        except ValueError as e:
            print(f"Корректно отловлена ошибка телефона: {e}")

        try:
            system.create_passenger("Иван", "test@mail.ru", "+79161111111", "123")
        except ValueError as e:
            print(f"Корректно отловлена ошибка паспорта: {e}")

        # 2. Тестирование создания транспорта и мест
        print("\n2. ТЕСТИРОВАНИЕ ТРАНСПОРТА И МЕСТ")
        print("-" * 40)

        # Создаем автобус
        bus = system.create_transport(
            TransportType.BUS,
            model="Mercedes Tourismo",
            capacity=5,  # Маленькая вместимость для тестирования
            has_wifi=True,
            has_usb_charging=True
        )
        print(f"Автобус создан: {bus.get_transport_info()}")

        # Добавляем места в автобус
        seats_data = [
            ("01", ClassSeat.ECONOMY, 1000.0),
            ("02", ClassSeat.ECONOMY, 1000.0),
            ("03", ClassSeat.BUSINESS, 2000.0),
            ("04", ClassSeat.BUSINESS, 2000.0),
            ("05", ClassSeat.ECONOMY, 1000.0),
        ]

        for number, seat_class, price in seats_data:
            seat = Seat(number, seat_class, price)
            bus.add_seat(seat)
        print(f"Добавлено {len(seats_data)} мест в автобус")

        # 3. Тестирование маршрутов и рейсов
        print("\n3. ТЕСТИРОВАНИЕ МАРШРУТОВ И РЕЙСОВ")
        print("-" * 40)

        # Создаем маршрут
        departure_time = datetime(2024, 1, 20, 10, 0)
        arrival_time = departure_time + timedelta(hours=8)

        route = system.create_route(
            "Москва",
            "Санкт-Петербург",
            departure_time,
            arrival_time
        )
        print(f"Маршрут создан: {route.get_info()}")
        print(f"Продолжительность: {route.get_duration()}")

        # Создаем рейс
        trip = system.create_trip(route, bus)
        print(f"Рейс создан: {trip.get_info()}")

        # 4. Тестирование бронирований
        print("\n4.ТЕСТИРОВАНИЕ БРОНИРОВАНИЙ")
        print("-" * 40)

        # Успешное бронирование
        booking1 = system.create_booking(passenger1, trip, "01")
        passenger1.add_booking(booking1)
        print(f"Бронирование создано: {booking1.get_info()}")

        # Создаем и обрабатываем оплату
        payment1 = Payment("PAY_001", booking1.calculate_total_price(), "карта")
        payment1.process_payment(5000.0)  # Успешная оплата
        booking1.add_payment(payment1)
        booking1.confirm_booking()
        print(f"Бронирование подтверждено: {booking1.get_info()}")
        print(f"Оплата: {payment1.get_info()}")

        # Второе бронирование
        booking2 = system.create_booking(passenger2, trip, "03")
        payment2 = Payment("PAY_002", booking2.calculate_total_price(), "карта")
        payment2.process_payment(5000.0)
        booking2.add_payment(payment2)
        booking2.confirm_booking()
        print(f"Бронирование создано: {booking2.get_info()}")

        # Тест ошибок бронирования
        print("\nТест ошибок бронирования:")
        try:
            system.create_booking(passenger1, trip, "01")  # Место уже занято
        except SeatNotAvailableException as e:
            print(f"Корректно отловлена ошибка занятого места: {e}")

        try:
            system.create_booking(passenger1, trip, "99")  # Несуществующее место
        except SeatNotAvailableException as e:
            print(f"Корректно отловлена ошибка несуществующего места: {e}")

        # 5. Тестирование поиска и управления бронированиями
        print("\n5. ТЕСТИРОВАНИЕ ПОИСКА БРОНИРОВАНИЙ")
        print("-" * 40)

        # Поиск бронирования по ID
        found_booking = system.find_booking_by_id(booking1.booking_id)
        print(f"Бронирование найдено по ID: {found_booking.get_info()}")

        # Получение бронирований пассажира
        passenger_bookings = system.get_passenger_bookings(passenger1.passport)
        print(f"Бронирования пассажира {passenger1.name}: {len(passenger_bookings)}")

        # Тест ошибки поиска
        try:
            system.find_booking_by_id("NON_EXISTENT")
        except BookingNotFoundException as e:
            print(f"Корректно отловлена ошибка поиска: {e}")

        # 6. Тестирование отмены бронирования
        print("\n6. ТЕСТИРОВАНИЕ ОТМЕНЫ БРОНИРОВАНИЯ")
        print("-" * 40)

        system.cancel_booking(booking2)
        print(f"Бронирование отменено: {booking2.get_info()}")

        # Проверяем, что место освободилось
        available_seats = trip.get_available_seats()
        print(f"Доступные места после отмены: {len(available_seats)}")
        for seat in available_seats:
            print(f"   - {seat.get_info()}")

        # 7. Тестирование статистики
        print("\n7. ТЕСТИРОВАНИЕ СТАТИСТИКИ")
        print("-" * 40)

        print(f"Общая выручка рейса: {trip.revenue} руб.")
        print(f"Всего пассажиров в системе: {len(system.passengers)}")
        print(f"Всего бронирований в системе: {len(system.bookings)} [{system.bookings.keys()}]")
        print(f"Всего транспорта в системе: {len(system.transports)}")

        return system

    except Exception as e:
        print(f"❌ Критическая ошибка при тестировании: {e}")
        return None


def test_file_operations(system: BookingSystem):
    """Тестирование работы с файлами"""
    print("\n" + "=" * 60)
    print("ТЕСТИРОВАНИЕ РАБОТЫ С ФАЙЛАМИ")
    print("=" * 60)

    # Создаем сериализаторы
    json_writer = JsonWriter()
    json_reader = JsonReader()
    xml_writer = XMLWriter()
    xml_reader = XMLReader()

    try:
        # 1. Тестирование JSON
        print("\n1. ТЕСТИРОВАНИЕ JSON СЕРИАЛИЗАЦИИ")
        print("-" * 40)

        # Запись в JSON
        json_filename = "test_bookings.json"
        json_writer.write(system, json_filename)
        print(f"Данные записаны в JSON файл: {json_filename}")

        # Чтение из JSON
        json_data = json_reader.read(json_filename)
        print(json_data)

        # 2. Тестирование XML
        print("\n2. ТЕСТИРОВАНИЕ XML СЕРИАЛИЗАЦИИ")
        print("-" * 40)

        # Запись в XML
        xml_filename = "test_bookings.xml"
        xml_writer.write(system, xml_filename)
        print(f"Данные записаны в XML файл: {xml_filename}")

        # Чтение из XML
        xml_data = xml_reader.read(xml_filename)
        print(f"Данные прочитаны из XML файла")
        print(xml_data)

        # 3. Тестирование ошибок файловых операций
        print("\n3. ТЕСТИРОВАНИЕ ОШИБОК ФАЙЛОВЫХ ОПЕРАЦИЙ")
        print("-" * 40)

        # Тест ошибки чтения несуществующего JSON файла
        try:
            json_reader.read("non_existent.json")
        except MyException as e:
            print(f"Корректно отловлена ошибка чтения JSON: {e}")

        # Тест ошибки чтения несуществующего XML файла
        try:
            xml_reader.read("non_existent.xml")
        except MyException as e:
            print(f"Корректно отловлена ошибка чтения XML: {e}")

        # Тест ошибки чтения некорректного JSON
        with open("corrupted.json", "w") as f:
            f.write("{invalid json}")

        try:
            json_reader.read("corrupted.json")
        except MyException as e:
            print(f"Корректно отловлена ошибка парсинга JSON: {e}")

        # Очистка тестовых файлов
        if os.path.exists("corrupted.json"):
            os.remove("corrupted.json")

        # 4. Тестирование обратной совместимости через DataSerializer
        print("\n4. ТЕСТИРОВАНИЕ ОБРАТНОЙ СОВМЕСТИМОСТИ")
        print("-" * 40)

        serializer = DataSerializer()

        # Сохранение через статические методы
        serializer.save_to_json(system, "compat_bookings.json")
        serializer.save_to_xml(system, "compat_bookings.xml")
        print("Данные сохранены через методы обратной совместимости")

        # Загрузка через статические методы
        compat_json_data = serializer.load_from_json("compat_bookings.json")
        compat_xml_data = serializer.load_from_xml("compat_bookings.xml")
        print("Данные загружены через методы обратной совместимости")

        print(f"   JSON: {len(compat_json_data.passengers)} пассажиров")
        print(f"   XML: {len(compat_xml_data.passengers)} пассажиров")

        # 5. Показ содержимого файлов
        print("\n5. СОДЕРЖИМОЕ ФАЙЛОВ")
        print("-" * 40)

        print("JSON файл (первые 700 символов):")
        with open(json_filename, 'r', encoding='utf-8') as f:
            content = f.read(700)
            print(f"   {content}...")

        print("\nXML файл (первые 700 символов):")
        with open(xml_filename, 'r', encoding='utf-8') as f:
            content = f.read(700)
            print(f"   {content}...")

    except Exception as e:
        print(f"❌ Ошибка при тестировании файловых операций: {e}")


def test_error_scenarios():
    """Тестирование различных сценариев ошибок"""
    print("\n" + "=" * 60)
    print("ТЕСТИРОВАНИЕ СЦЕНАРИЕВ ОШИБОК")
    print("=" * 60)

    system = BookingSystem()

    try:
        # 1. Ошибка недостатка средств
        print("\n1. ТЕСТИРОВАНИЕ ОШИБКИ НЕДОСТАТКА СРЕДСТВ")
        print("-" * 40)

        # Создаем тестовые данные
        passenger = system.create_passenger("Тест", "test@test.ru", "+79161111111",
                                            "1111111111")
        bus = system.create_transport(TransportType.BUS, model="Test", capacity=2, has_wifi=True,
                                      has_usb_charging=True)

        # Добавляем место
        seat = Seat("01", ClassSeat.ECONOMY, 1000.0)
        bus.add_seat(seat)

        # Создаем маршрут и рейс
        route = system.create_route("А", "Б", datetime.now(), datetime.now() + timedelta(hours=1))
        trip = system.create_trip(route, bus)

        # Создаем бронирование
        booking = system.create_booking(passenger, trip, "01")

        # Пытаемся оплатить с недостаточными средствами
        payment = Payment("TEST_PAY", booking.calculate_total_price(), "карта")

        try:
            payment.process_payment(500.0)  # Недостаточно средств
        except NoMoneyException as e:
            print(f"Корректно отловлена ошибка недостатка средств: {e}")

        # 2. Ошибка подтверждения без оплаты
        print("\n2. ТЕСТИРОВАНИЕ ОШИБКИ ПОДТВЕРЖДЕНИЯ БЕЗ ОПЛАТЫ")
        print("-" * 40)

        try:
            booking.confirm_booking()  # Без оплаты
        except MyException as e:
            print(f"Корректно отловлена ошибка подтверждения без оплаты: {e}")

        # 3. Ошибка двойного бронирования
        print("\n3. ТЕСТИРОВАНИЕ ОШИБКИ ДВОЙНОГО БРОНИРОВАНИЯ")
        print("-" * 40)

        # Успешно бронируем и оплачиваем
        payment.process_payment(2000.0)
        booking.add_payment(payment)
        booking.confirm_booking()
        print(f"Первое бронирование подтверждено")

        # Пытаемся забронировать то же место повторно
        passenger2 = system.create_passenger("ТестДва", "test2@test.ru",
                                             "+79162222222", "2222222222")

        try:
            system.create_booking(passenger2, trip, "01")
        except SeatNotAvailableException as e:
            print(f"Корректно отловлена ошибка двойного бронирования: {e}")

    except Exception as e:
        print(f"❌ Неожиданная ошибка при тестировании сценариев: {e}")


def cleanup_test_files():
    """Очистка тестовых файлов"""
    test_files = [
        "test_bookings.json", "test_bookings.xml",
        "compat_bookings.json", "compat_bookings.xml"
    ]

    print("\n" + "=" * 60)
    print("ОЧИСТКА ТЕСТОВЫХ ФАЙЛОВ")
    print("=" * 60)

    for file in test_files:
        if os.path.exists(file):
            os.remove(file)
            print(f"Удален файл: {file}")
        else:
            print(f"ℹФайл не найден: {file}")


def main():
    """Главная функция тестирования"""
    try:
        # Тестирование системы бронирования
        system = test_booking_system()

        if system:
            # Тестирование работы с файлами
            test_file_operations(system)

            # Тестирование сценариев ошибок
            test_error_scenarios()

            print("\n" + "=" * 60)
            print("ВСЕ ТЕСТЫ УСПЕШНО ЗАВЕРШЕНЫ!")
            print("=" * 60)

            # Очистка тестовых файлов
            cleanup_test_files()

        else:
            print("\nТестирование системы бронирования завершилось с ошибками")

    except Exception as e:
        print(f"\nКритическая ошибка в основном потоке тестирования: {e}")


if __name__ == "__main__":
    main()
