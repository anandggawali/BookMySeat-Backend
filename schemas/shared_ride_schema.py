from pydantic import BaseModel


class ShareBookingRequest(BaseModel):

    bookingId: str
    vendorId: str
    note: str = ""
