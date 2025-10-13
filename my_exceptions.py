class SeatNotAvailableException(Exception):
    def __repr__(self):
        return "Место недоступно"
