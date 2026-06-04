from pydantic import BaseModel
from datetime import date


class CreateTripRequest(BaseModel):
    route: str
    date: date
    timeSlot: str
    fare: float
    totalSeats: int


class SearchTripRequest(BaseModel):
    route: str
    date: date


class TripResponse(BaseModel):
    tripId: str
    route: str
    date: date
    timeSlot: str
    fare: float
    totalSeats: int
    availableSeats: int
    status: str