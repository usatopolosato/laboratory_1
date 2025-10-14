from seat import Seat
from datetime import datetime
from typing import List


class Trip:
    def __init__(self, base_price: float, seats: List[Seat]):
        self.base_price = base_price
        self._seats = seats
        self._creation_date = datetime.now()

    @property
    def creation_date(self) -> datetime:
        return self._creation_date

    @property
    def total_seats(self) -> int:
        return len(self._seats)

    @property
    def available_seats(self) -> List[Seat]:
        return [seat for seat in self._seats if seat.is_available]

    @property
    def revenue(self) -> float:
        return sum(seat.price for seat in self._seats if not seat.is_available)
