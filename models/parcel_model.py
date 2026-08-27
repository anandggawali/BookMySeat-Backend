from pydantic import BaseModel
from typing import Optional


class ParcelCreate(BaseModel):

    parcelFareId: Optional[str] = None

    weightCategoryId: str

    expectedDate: str

    parcelType: str

    weight: float

    note: str = ""
    contactPersonName: str
    contactPersonPhone: str

class ParcelAllocateRequest(BaseModel):

    tripId: str

    agreedFare: float


class ParcelRejectRequest(BaseModel):

    reason: str


class Parcel(BaseModel):

    parcelId: str

    userId: str

    parcelFareId: Optional[str] = None

    weightCategoryId: str

    tripId: Optional[str] = None

    expectedDate: str

    actualDate: Optional[str] = None

    actualTime: Optional[str] = None

    parcelType: str

    weight: float

    note: Optional[str] = None

    agreedFare: Optional[float] = None

    rejectionReason: Optional[str] = None

    parcelStatus: str = "PENDING"

    createdAt: str

    updatedAt: Optional[str] = None
    contactPersonName: str
    contactPersonPhone: str

class ParcelRescheduleRequest(BaseModel):

    tripId: str
    agreedFare: float