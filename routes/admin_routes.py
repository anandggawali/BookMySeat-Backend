from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from dependencies.auth_dependency import get_current_user
from schemas.booking_schema import RejectBookingRequest

from schemas.trip_schema import CreateTripRequest

from services.trip_service import TripService
from services.booking_service import BookingService

router = APIRouter(
    prefix="/api/admin",
    tags=["Admin"]
)


def validate_admin(user):

    if user["role"] != "ADMIN":

        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )


@router.post("/trips")
def create_trip(
        request: CreateTripRequest,
        current_user=Depends(get_current_user)
):

    validate_admin(current_user)

    return TripService.create_trip(
        request
    )

@router.get("/bookings")
def get_all_bookings(
        current_user=Depends(get_current_user)
):

    validate_admin(current_user)

    return BookingService.get_all_bookings()

@router.put(
    "/bookings/{booking_id}/confirm"
)
def confirm_booking(
        booking_id: str,
        current_user=Depends(get_current_user)
):

    validate_admin(current_user)

    return BookingService.confirm_booking(
        booking_id
    )


@router.put(
    "/bookings/{booking_id}/reject"
)
def reject_booking(
        booking_id: str,
        request: RejectBookingRequest,
        current_user=Depends(get_current_user)
):

    validate_admin(current_user)

    return BookingService.reject_booking(
        booking_id,
        request.reason
    )