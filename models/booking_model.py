from pydantic import BaseModel


class Booking(BaseModel):
    bookingId: str
    tripId: str
    userId: str
    passengerCount: int
    gender: str
    note: str | None = None
    totalFare: float
    bookingStatus: str

class BookingRequest(BaseModel):
        tripId: str
        passengerCount: int
        gender: str
        note: str = ""