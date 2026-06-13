from pydantic import BaseModel
from datetime import date


class Trip(BaseModel):
    tripId: str
    route: str
    date: date
    timeSlot: str
    fare: float
    totalSeats: int
    status: str

