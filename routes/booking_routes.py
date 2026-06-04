from fastapi import APIRouter
from fastapi import Depends

from schemas.booking_schema import CreateBookingRequest

from services.booking_service import BookingService

from dependencies.auth_dependency import get_current_user

router = APIRouter(
    prefix="/api/bookings",
    tags=["Bookings"]
)


@router.post("")
def create_booking(
        request: CreateBookingRequest,
        current_user=Depends(get_current_user)
):

    return BookingService.create_booking(
        request,
        current_user["userId"]
    )

@router.get("/my")
def my_bookings(
        current_user=Depends(get_current_user)
):

    return BookingService.get_my_bookings(
        current_user["userId"]
    )