from pydantic import BaseModel


class CreateBookingRequest(BaseModel):
    tripId: str
    passengerCount: int
    gender: str
    note: str | None = None


class BookingResponse(BaseModel):
    bookingId: str
    bookingStatus: str
    totalFare: float


class ConfirmBookingResponse(BaseModel):
    message: str