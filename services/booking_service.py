import uuid

from datetime import date, timedelta

from fastapi import HTTPException

from repositories.trip_repository import TripRepository
from repositories.booking_repository import BookingRepository

from services.trip_service import TripService

from core.utils import serialize_mongo_list
from core.database import bookings_collection


class BookingService:

    @staticmethod
    def create_booking(
            request,
            user_id
    ):

        trip = TripRepository.find_by_id(
            request.tripId
        )

        if not trip:
            raise HTTPException(
                status_code=404,
                detail="Trip not found"
            )

        # Passenger validation
        if request.passengerCount <= 0:
            raise HTTPException(
                status_code=400,
                detail="Passenger count must be greater than 0"
            )

        # Booking allowed only within next 3 days
        trip_date = date.fromisoformat(
            trip["date"]
        )

        if trip_date > (
                date.today()
                + timedelta(days=3)
        ):
            raise HTTPException(
                status_code=400,
                detail="Booking allowed only within next 3 days"
            )

        # Available seat validation
        available = (
            TripService
            .calculate_available_seats(
                trip
            )
        )

        if request.passengerCount > available:
            raise HTTPException(
                status_code=400,
                detail="Not enough seats available"
            )

        total_fare = (
                trip["fare"]
                * request.passengerCount
        )

        booking = {

            "bookingId": str(uuid.uuid4()),

            "tripId": request.tripId,

            "userId": user_id,

            "passengerCount": request.passengerCount,

            "gender": request.gender,

            "note": request.note,

            "totalFare": total_fare,

            "bookingStatus": "PENDING"
        }

        BookingRepository.save(
            booking
        )

        return {

            "bookingId": booking["bookingId"],

            "bookingStatus": booking["bookingStatus"],

            "totalFare": booking["totalFare"]
        }

    @staticmethod
    def get_my_bookings(
            user_id: str
    ):

        bookings = (
            BookingRepository.find_by_user(
                user_id
            )
        )

        return serialize_mongo_list(
            bookings
        )

    @staticmethod
    def get_all_bookings():

        bookings = (
            BookingRepository.get_all_bookings()
        )

        return serialize_mongo_list(
            bookings
        )

    @staticmethod
    def confirm_booking(
            booking_id
    ):

        booking = (
            BookingRepository.find_by_id(
                booking_id
            )
        )

        if not booking:
            raise HTTPException(
                status_code=404,
                detail="Booking not found"
            )

        if booking["bookingStatus"] == "CONFIRMED":
            raise HTTPException(
                status_code=400,
                detail="Booking already confirmed"
            )

        if booking["bookingStatus"] == "REJECTED":
            raise HTTPException(
                status_code=400,
                detail="Rejected booking cannot be confirmed"
            )

        trip = (
            TripRepository.find_by_id(
                booking["tripId"]
            )
        )

        if not trip:
            raise HTTPException(
                status_code=404,
                detail="Trip not found"
            )

        available = (
            TripService
            .calculate_available_seats(
                trip
            )
        )

        if booking["passengerCount"] > available:
            raise HTTPException(
                status_code=400,
                detail="Not enough seats available"
            )

        bookings_collection.update_one(
            {
                "bookingId": booking_id
            },
            {
                "$set": {
                    "bookingStatus": "CONFIRMED"
                }
            }
        )

        return {
            "message": "Booking confirmed successfully"
        }

    @staticmethod
    def reject_booking(
            booking_id
    ):

        booking = (
            BookingRepository.find_by_id(
                booking_id
            )
        )

        if not booking:
            raise HTTPException(
                status_code=404,
                detail="Booking not found"
            )

        if booking["bookingStatus"] == "CONFIRMED":
            raise HTTPException(
                status_code=400,
                detail="Confirmed booking cannot be rejected"
            )

        bookings_collection.update_one(
            {
                "bookingId": booking_id
            },
            {
                "$set": {
                    "bookingStatus": "REJECTED"
                }
            }
        )

        return {
            "message": "Booking rejected successfully"
        }