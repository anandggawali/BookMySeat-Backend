from pydantic import BaseModel


# ============================================================
# CREATE PARCEL FARE
# ============================================================

class ParcelFareCreate(BaseModel):

    routeId: str

    direction: str

    weightCategoryId: str

    minFare: float

    maxFare: float


# ============================================================
# PARCEL FARE RESPONSE
# ============================================================

class ParcelFare(BaseModel):

    parcelFareId: str

    routeId: str

    direction: str

    weightCategoryId: str

    minFare: float

    maxFare: float

    isActive: bool = True