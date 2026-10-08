from fastapi import APIRouter
from fastapi import Depends

from typing import Optional

from fastapi import HTTPException, Query


from services.admin_analytics_service import (
    AdminAnalyticsService
)

from dependencies.auth_dependency import get_current_user
from schemas.booking_schema import RejectBookingRequest

from schemas.trip_schema import CreateTripRequest

from services.trip_service import TripService
from services.booking_service import BookingService
from schemas.shared_ride_schema import ShareBookingRequest
from services.shared_ride_service import SharedRideService
from repositories.user_repository import UserRepository

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

@router.get("/vendors")
def get_vendors(
        current_user=Depends(get_current_user)
):

    validate_admin(current_user)

    return UserRepository.get_vendors()

@router.post("/shared-rides")
def share_booking(
        request: ShareBookingRequest,
        current_user=Depends(get_current_user)
):

    validate_admin(current_user)

    return SharedRideService.share_booking(
        request,
        current_user["userId"]
    )

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


@router.get(
    "/analytics/summary"
)
def get_admin_analytics(

    period: str = Query(
        default="today"
    ),

    year: Optional[int] = Query(
        default=None
    ),

    month: Optional[int] = Query(
        default=None
    )
):

    try:

        return (
            AdminAnalyticsService
            .get_summary(
                period=period,
                year=year,
                month=month
            )
        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:

        print(
            "================================="
        )

        print(
            "ADMIN ANALYTICS ERROR"
        )

        print(
            str(error)
        )

        print(
            "================================="
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to load admin analytics"
        )
