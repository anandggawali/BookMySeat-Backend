from fastapi import APIRouter

from services.trip_service import TripService

from schemas.trip_schema import SearchTripRequest

router = APIRouter(
    prefix="/api/trips",
    tags=["Trips"]
)


@router.post("/search")
def search_trips(
        request: SearchTripRequest
):

    return TripService.search_trips(
        request.route,
        request.date
    )