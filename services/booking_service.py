import uuid

from datetime import date, timedelta

from fastapi import HTTPException

from repositories.trip_repository import TripRepository
from repositories.booking_repository import BookingRepository
from repositories.user_repository import UserRepository

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
        user = UserRepository.find_by_id(user_id)
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

            "mobileNumber":
                user.get("phoneNo", "")
                if user else "",

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

    # @staticmethod
    # def get_my_bookings(
    #         user_id: str
    # ):
    #
    #     bookings = (
    #         BookingRepository.find_by_user(
    #             user_id
    #         )
    #     )
    #
    #     return serialize_mongo_list(
    #         bookings
    #     )
    @staticmethod
    def get_my_bookings(user_id):

        bookings = BookingRepository.find_by_user(user_id)

        response = []

        for booking in bookings:
            trip = TripRepository.find_by_id(
                booking["tripId"]
            )

            response.append({

                "bookingId": booking["bookingId"],

                "tripId": booking["tripId"],

                "route":
                    trip["route"]
                    if trip else "Trip Deleted",

                "date":
                    trip["date"]
                    if trip else "-",

                "timeSlot":
                    trip["timeSlot"]
                    if trip else "-",

                "fare":
                    booking.get("totalFare", 0),

                "passengerCount":
                    booking["passengerCount"],

                "gender":
                    booking["gender"],

                "bookingStatus":
                    booking["bookingStatus"]
            })

        return response

    @staticmethod
    def get_all_bookings():

        bookings = BookingRepository.get_all_bookings()

        response = []

        for booking in bookings:
            trip = TripRepository.find_by_id(
                booking.get("tripId")
            )

            user = UserRepository.find_by_id(
                booking.get("userId")
            )

            response.append({

                "bookingId": booking.get("bookingId"),

                "userName":
                    user.get("name", "Unknown User")
                    if user else "Unknown User",

                "mobileNumber":
                    user.get("phoneNo", "")
                    if user else "",

                "tripId": booking.get("tripId"),

                "route":
                    trip.get("route", "")
                    if trip else "",

                "date":
                    trip.get("date", "")
                    if trip else "",

                "timeSlot":
                    trip.get("timeSlot", "")
                    if trip else "",

                "fare":
                    booking.get("totalFare", 0),

                "note":
                    booking.get("note", 0),

                "passengerCount":
                    booking.get("passengerCount", 0),

                "gender":
                    booking.get("gender", ""),

                "bookingStatus":
                    booking.get("bookingStatus", "")
            })

        return response

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