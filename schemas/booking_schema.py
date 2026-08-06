from pydantic import BaseModel
from typing import Optional

class CreateBookingRequest(BaseModel):
    tripId: str
    passengerCount: int = 0
    gender: str = ""
    note: str = ""

    # Booking type
    bookingType: str = "RIDE"

    # Parcel details
    parcelCount: int = 0
    parcelType: str = ""
    parcelWeight: str = ""


class BookingResponse(BaseModel):
    bookingId: str
    bookingStatus: str
    totalFare: float


class ConfirmBookingResponse(BaseModel):
    message: str

class RejectBookingRequest(BaseModel):
    reason: Optional[str] = None