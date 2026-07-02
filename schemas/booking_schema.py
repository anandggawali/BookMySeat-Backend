from pydantic import BaseModel
from typing import Optional

class CreateBookingRequest(BaseModel):
    tripId: str
    passengerCount: int
    gender: str
    note: Optional[str] = None


class BookingResponse(BaseModel):
    bookingId: str
    bookingStatus: str
    totalFare: float


class ConfirmBookingResponse(BaseModel):
    message: str

class RejectBookingRequest(BaseModel):
    reason: Optional[str] = None