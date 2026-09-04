import uuid

from datetime import date, timedelta

from fastapi import HTTPException

from repositories.trip_repository import TripRepository
from repositories.booking_repository import BookingRepository
from repositories.user_repository import UserRepository
from services.app_notification_service import AppNotificationService
from services.notification_service import NotificationService

from services.trip_service import TripService

from core.utils import serialize_mongo_list
from core.database import bookings_collection


class BookingService:

    @staticmethod
    def create_booking(
            request,
            user_id
    ):

        print("========== CREATE BOOKING START ==========")
        print("User ID:", user_id)
        print("Trip ID:", request.tripId)
        print("Booking Type:", request.bookingType)
        print("Passenger Count:", request.passengerCount)
        print("Parcel Count:", request.parcelCount)

        # -------------------------------------------------
        # GET TRIP
        # -------------------------------------------------

        trip = TripRepository.find_by_id(
            request.tripId
        )

        if not trip:
            raise HTTPException(
                status_code=404,
                detail="Trip not found"
            )

        # -------------------------------------------------
        # GET USER
        # -------------------------------------------------

        user = UserRepository.find_by_id(
            user_id
        )

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        # -------------------------------------------------
        # NORMALIZE BOOKING TYPE
        # -------------------------------------------------

        booking_type = (
                request.bookingType or "RIDE"
        ).strip().upper()

        # -------------------------------------------------
        # RIDE VALIDATION
        # -------------------------------------------------

        if booking_type == "RIDE":

            if request.passengerCount <= 0:
                raise HTTPException(
                    status_code=400,
                    detail="Passenger count must be greater than 0"
                )

        # -------------------------------------------------
        # PARCEL VALIDATION
        # -------------------------------------------------

        elif booking_type == "PARCEL":

            if request.parcelCount <= 0:
                raise HTTPException(
                    status_code=400,
                    detail="Parcel count must be greater than 0"
                )

        else:

            raise HTTPException(
                status_code=400,
                detail="Invalid booking type"
            )

        # -------------------------------------------------
        # DATE VALIDATION
        # -------------------------------------------------

        try:

            trip_date = date.fromisoformat(
                trip["date"]
            )

        except Exception:

            raise HTTPException(
                status_code=500,
                detail="Invalid trip date format"
            )

        if trip_date > (
                date.today()
                + timedelta(days=3)
        ):
            raise HTTPException(
                status_code=400,
                detail="Booking allowed only within next 3 days"
            )

        # -------------------------------------------------
        # AVAILABLE SEATS
        # -------------------------------------------------

        try:

            available = TripService.calculate_available_seats(
                trip
            )

        except Exception as e:

            print(
                "ERROR calculating available seats:",
                repr(e)
            )

            # Fallback so booking creation does not crash
            available = trip.get(
                "totalSeats",
                0
            )

        # -------------------------------------------------
        # QUANTITY
        # -------------------------------------------------

        if booking_type == "RIDE":

            quantity = request.passengerCount

        else:

            quantity = request.parcelCount

        # -------------------------------------------------
        # FARE
        # -------------------------------------------------

        try:

            fare = float(
                trip.get("fare", 0)
            )

        except Exception:

            raise HTTPException(
                status_code=500,
                detail="Invalid trip fare"
            )

        total_fare = fare * quantity

        # -------------------------------------------------
        # BOOKING ID
        # -------------------------------------------------

        booking_id = str(
            uuid.uuid4()
        )

        # -------------------------------------------------
        # SAFE USER DATA
        # -------------------------------------------------

        mobile_number = user.get(
            "phoneNo",
            ""
        )

        user_name = user.get(
            "name",
            "User"
        )

        # -------------------------------------------------
        # CREATE BOOKING
        # -------------------------------------------------

        booking = {

            "bookingId": booking_id,

            "tripId": request.tripId,

            "userId": user_id,

            "mobileNumber": mobile_number,

            "bookingType": booking_type,

            # Ride
            "passengerCount":
                request.passengerCount
                if booking_type == "RIDE"
                else 0,

            "gender":
                request.gender
                if booking_type == "RIDE"
                else "",

            # Parcel
            "parcelCount":
                request.parcelCount
                if booking_type == "PARCEL"
                else 0,

            "parcelType":
                request.parcelType
                if booking_type == "PARCEL"
                else "",

            "parcelWeight":
                request.parcelWeight
                if booking_type == "PARCEL"
                else "",

            # Common
            "note":
                request.note or "",

            "totalFare":
                total_fare,

            "availableSeatsAtBooking":
                available,

            "bookingStatus":
                "PENDING",

            "isOverBooking":
                available < quantity
                if booking_type == "RIDE"
                else False
        }

        # -------------------------------------------------
        # SAVE BOOKING
        # -------------------------------------------------

        try:

            result = BookingRepository.save(
                booking
            )

            print(
                "BOOKING SAVED SUCCESSFULLY:",
                booking_id
            )

        except Exception as e:

            print(
                "========== BOOKING DATABASE ERROR =========="
            )
            print(
                repr(e)
            )

            raise HTTPException(
                status_code=500,
                detail="Unable to save booking"
            )

        # -------------------------------------------------
        # ADMIN NOTIFICATION
        #
        # IMPORTANT:
        # Notification failure must NOT make
        # booking creation return HTTP 500.
        # -------------------------------------------------

        try:

            admins = UserRepository.get_admins()

            print(
                "ADMIN COUNT:",
                len(admins)
            )

            for admin in admins:

                try:

                    if booking_type == "RIDE":

                        notification_body = (
                            f"{user_name}\n"
                            f"{trip.get('route', '')}\n"
                            f"{trip.get('date', '')} • "
                            f"{trip.get('timeSlot', '')}\n"
                            f"Passengers: "
                            f"{request.passengerCount}"
                        )

                    else:

                        notification_body = (
                            f"{user_name}\n"
                            f"{trip.get('route', '')}\n"
                            f"{trip.get('date', '')} • "
                            f"{trip.get('timeSlot', '')}\n"
                            f"Parcels: "
                            f"{request.parcelCount}"
                        )

                    AppNotificationService.create_notification(

                        user_id=admin["userId"],

                        title="New Booking Request",

                        body=notification_body,

                        type="BOOKING",

                        click_action="MANAGE_BOOKINGS",

                        color="#2962FF"
                    )

                    print(
                        "Admin notification sent:",
                        admin.get("userId")
                    )

                except Exception as notification_error:

                    print(
                        "ADMIN NOTIFICATION ERROR:",
                        repr(notification_error)
                    )

                    # DO NOT raise here

        except Exception as notification_error:

            print(
                "NOTIFICATION SYSTEM ERROR:",
                repr(notification_error)
            )

            # DO NOT raise here

        # -------------------------------------------------
        # SUCCESS
        # -------------------------------------------------

        print(
            "========== CREATE BOOKING SUCCESS =========="
        )

        return {

            "bookingId":
                booking["bookingId"],

            "bookingStatus":
                booking["bookingStatus"],

            "totalFare":
                booking["totalFare"]
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
                "bookingType":
                    booking.get("bookingType", "RIDE"),

                # Ride
                "passengerCount":
                    booking.get("passengerCount", 0),

                "gender":
                    booking.get("gender", ""),

                # Parcel
                "parcelCount":
                    booking.get("parcelCount", 0),

                "parcelType":
                    booking.get("parcelType", ""),

                "parcelWeight":
                    booking.get("parcelWeight", 0),

                "bookingStatus":
                    booking["bookingStatus"],

                "rejectionReason":
                    booking.get("rejectionReason", "")
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

            total_seats = trip.get("totalSeats", 0) if trip else 0

            booked_passengers = 0

            if trip:
                trip_bookings = BookingRepository.get_bookings_by_trip(
                    booking.get("tripId")
                )

                booked_passengers = sum(
                    b.get("passengerCount", 0)
                    if b.get("bookingType", "RIDE") == "RIDE"
                    else b.get("parcelCount", 0)
                    for b in trip_bookings
                )

            over_booked = max(
                0,
                booked_passengers - total_seats
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
                    booking.get("note", ""),

                "bookingType":
                    booking.get("bookingType", "RIDE"),

                # Ride
                "passengerCount":
                    booking.get("passengerCount", 0),

                "gender":
                    booking.get("gender", ""),

                # Parcel
                "parcelCount":
                    booking.get("parcelCount", 0),

                "parcelType":
                    booking.get("parcelType", ""),

                "parcelWeight":
                    booking.get("parcelWeight", 0),

                "bookingStatus":
                    booking.get("bookingStatus", ""),

                "rejectionReason":
                    booking.get("rejectionReason", ""),

                "totalSeats": total_seats,

                "bookedPassengers": booked_passengers,

                "availableSeats": total_seats - booked_passengers,

                "overBookedSeats": over_booked,

                "isOverBooked": over_booked > 0
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
        user = UserRepository.find_by_id(booking["userId"])

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

        # available = (
        #     TripService
        #     .calculate_available_seats(
        #         trip
        #     )
        # )
        #
        # if booking["passengerCount"] > available:
        #     raise HTTPException(
        #         status_code=400,
        #         detail="Not enough seats available"
        #     )

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
        print("========== CALLING APP NOTIFICATION ==========")
        print("User:", booking["userId"])
        print("Trip:", trip["route"])
        from services.app_notification_service import AppNotificationService
        AppNotificationService.create_notification(

            user_id=booking["userId"],

            title="Booking Confirmed",

            body=f"Your booking for {trip['route']} on {trip['date']} at {trip['timeSlot']} has been confirmed.",

            type="BOOKING_CONFIRMED",

            click_action="OPEN_BOOKING",

            color="#4CAF50"

        )

        return {
            "message": "Booking confirmed successfully"
        }

    @staticmethod
    def reject_booking(
            booking_id,
            reason
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
        user = UserRepository.find_by_id(
            booking["userId"]
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
                    "bookingStatus": "REJECTED",
                    "rejectionReason": reason
                }
            }
        )
        trip = TripRepository.find_by_id(
            booking["tripId"]
        )

        AppNotificationService.create_notification(

            user_id=booking["userId"],

            title="Booking Rejected",

            body=f"Your booking for {trip['route']} has been rejected.\nReason: {reason}",

            type="BOOKING_REJECTED",

            click_action="OPEN_BOOKING",

            color="#F44336"

        )

        return {
            "message": "Booking rejected successfully"
        }