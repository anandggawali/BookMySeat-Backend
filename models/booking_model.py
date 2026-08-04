from pydantic import BaseModel


class Booking(BaseModel):
    bookingId: str
    tripId: str
    userId: str

    # Ride Details
    passengerCount: int = 0
    gender: str = ""

    # Parcel Details
    bookingType: str = "RIDE"      # RIDE / PARCEL
    parcelCount: int = 0
    parcelType: str = ""
    parcelWeight: float = 0.0

    # Common
    note: str | None = None
    totalFare: float
    bookingStatus: str


class BookingRequest(BaseModel):
    tripId: str

    # Ride Details
    passengerCount: int = 0
    gender: str = ""

    # Parcel Details
    bookingType: str = "RIDE"
    parcelCount: int = 0
    parcelType: str = ""
    parcelWeight: float = 0.0

    # Common
    note: str = ""