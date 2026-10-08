import uuid
from datetime import datetime

from fastapi import HTTPException

from repositories.booking_repository import BookingRepository
from repositories.user_repository import UserRepository
from repositories.shared_ride_repository import SharedRideRepository
from repositories.trip_repository import TripRepository


class SharedRideService:

    # =========================================================
    # ADMIN - SHARE BOOKING
    # =========================================================

    @staticmethod
    def share_booking(
            request,
            admin_id: str
    ):

        booking = BookingRepository.find_by_id(
            request.bookingId
        )

        if not booking:

            raise HTTPException(
                status_code=404,
                detail="Booking not found"
            )

        # -----------------------------------------------------
        # ONLY RIDE BOOKINGS CAN BE SHARED
        # -----------------------------------------------------

        if booking.get("bookingType") != "RIDE":

            raise HTTPException(
                status_code=400,
                detail="Only ride bookings can be shared"
            )

        # -----------------------------------------------------
        # BOOKING MUST STILL BE PENDING
        # -----------------------------------------------------

        if booking.get("bookingStatus") != "PENDING":

            raise HTTPException(
                status_code=400,
                detail="Only pending bookings can be shared"
            )

        # -----------------------------------------------------
        # FIND TRIP
        # -----------------------------------------------------

        trip = TripRepository.find_by_id(
            booking["tripId"]
        )

        if not trip:

            raise HTTPException(
                status_code=404,
                detail="Trip not found"
            )

        # -----------------------------------------------------
        # FIND VENDOR
        # -----------------------------------------------------

        vendor = UserRepository.find_by_id(
            request.vendorId
        )

        if not vendor:

            raise HTTPException(
                status_code=404,
                detail="Vendor not found"
            )

        # -----------------------------------------------------
        # VERIFY VENDOR ROLE
        # -----------------------------------------------------

        if vendor.get("role") != "VENDOR":

            raise HTTPException(
                status_code=400,
                detail="Selected user is not a vendor"
            )

        # -----------------------------------------------------
        # PREVENT ACTIVE DUPLICATE SHARE
        # -----------------------------------------------------

        existing = (
            SharedRideRepository.find_by_booking_id(
                request.bookingId
            )
        )

        if existing and existing.get("status") in (
            "PENDING",
            "ACCEPTED"
        ):

            raise HTTPException(
                status_code=400,
                detail="Booking already has an active shared ride"
            )

        # -----------------------------------------------------
        # CREATE SHARED RIDE
        # -----------------------------------------------------

        shared_ride_id = str(
            uuid.uuid4()
        )

        now = datetime.utcnow()

        shared_ride = {

            "sharedRideId":
                shared_ride_id,

            "bookingId":
                booking["bookingId"],

            "tripId":
                booking["tripId"],

            "sharedByAdminId":
                admin_id,

            "sharedToVendorId":
                request.vendorId,

            # Admin has already accepted the sharing decision
            "status":
                "ACCEPTED",

            "sharedAt":
                now,

            "acceptedAt":
                now,

            "rejectedAt":
                None,

            "note":
                request.note
        }

        SharedRideRepository.save(
            shared_ride
        )

        # -----------------------------------------------------
        # CONFIRM BOOKING + MARK AS SHARED
        # -----------------------------------------------------

        from core.database import bookings_collection

        bookings_collection.update_one(

            {
                "bookingId":
                    booking["bookingId"]
            },

            {
                "$set": {

                    "bookingStatus":
                        "CONFIRMED",

                    "fulfillmentType":
                        "SHARED",

                    "sharedRideId":
                        shared_ride_id
                }
            }
        )

        # -----------------------------------------------------
        # CUSTOMER NOTIFICATION
        #
        # Customer only sees normal confirmation.
        # -----------------------------------------------------

        try:

            from services.app_notification_service import (
                AppNotificationService
            )

            AppNotificationService.create_notification(

                user_id=
                    booking["userId"],

                title=
                    "Booking Confirmed",

                body=(
                    "Your booking has been confirmed.\n"
                    f"{trip.get('route', '')}\n"
                    f"{trip.get('date', '')} • "
                    f"{trip.get('timeSlot', '')}\n"
                    f"Passengers: "
                    f"{booking.get('passengerCount', 0)}\n"
                    f"Fare: ₹"
                    f"{booking.get('totalFare', 0)}"
                ),

                type=
                    "BOOKING_CONFIRMED",

                click_action=
                    "OPEN_BOOKING",

                color=
                    "#4CAF50"
            )

        except Exception as e:

            print(
                "Customer confirmation notification failed:",
                repr(e)
            )

        # -----------------------------------------------------
        # VENDOR NOTIFICATION
        #
        # Informational only.
        # Vendor does not accept/reject.
        # -----------------------------------------------------

        try:

            from services.app_notification_service import (
                AppNotificationService
            )

            customer = UserRepository.find_by_id(
                booking.get("userId")
            )

            customer_name = (

                customer.get(
                    "name",
                    "Customer"
                )

                if customer

                else "Customer"
            )

            AppNotificationService.create_notification(

                user_id=
                    request.vendorId,

                title=
                    "Shared Ride Assigned",

                body=(
                    "A shared ride has been assigned to you.\n"
                    f"{trip.get('route', '')}\n"
                    f"{trip.get('date', '')} • "
                    f"{trip.get('timeSlot', '')}\n"
                    f"Customer: "
                    f"{customer_name}\n"
                    f"Passengers: "
                    f"{booking.get('passengerCount', 0)}"
                ),

                type=
                    "SHARED_RIDE_ASSIGNED",

                click_action=
                    "VENDOR_SHARED_RIDES",

                color=
                    "#2962FF"
            )

        except Exception as e:

            print(
                "Vendor shared ride notification failed:",
                repr(e)
            )

        # -----------------------------------------------------
        # RESPONSE
        # -----------------------------------------------------

        return {

            "message":
                "Booking shared and confirmed successfully",

            "sharedRideId":
                shared_ride_id,

            "bookingId":
                booking["bookingId"],

            "vendorId":
                request.vendorId,

            "status":
                "ACCEPTED",

            "bookingStatus":
                "CONFIRMED",

            "fulfillmentType":
                "SHARED"
        }

    # =========================================================
    # VENDOR - GET ACCEPTED SHARED RIDES
    # =========================================================

    @staticmethod
    def get_vendor_shared_rides(
            vendor_id: str
    ):

        shared_rides = (
            SharedRideRepository.find_accepted_by_vendor(
                vendor_id
            )
        )

        response = []

        for shared_ride in shared_rides:

            booking = BookingRepository.find_by_id(
                shared_ride["bookingId"]
            )

            if not booking:
                continue

            trip = TripRepository.find_by_id(
                shared_ride["tripId"]
            )

            user = UserRepository.find_by_id(
                booking.get("userId")
            )

            response.append({

                "sharedRideId":
                    shared_ride["sharedRideId"],

                "bookingId":
                    shared_ride["bookingId"],

                "tripId":
                    shared_ride["tripId"],

                "status":
                    shared_ride.get(
                        "status",
                        "ACCEPTED"
                    ),

                "route":
                    trip.get("route", "")
                    if trip
                    else "",

                "date":
                    trip.get("date", "")
                    if trip
                    else "",

                "timeSlot":
                    trip.get("timeSlot", "")
                    if trip
                    else "",

                "customerName":
                    user.get("name", "")
                    if user
                    else "",

                "customerPhone":
                    (
                        user.get(
                            "phoneNo",
                            ""
                        )

                        if user

                        else booking.get(
                            "mobileNumber",
                            ""
                        )
                    ),

                "passengerCount":
                    booking.get(
                        "passengerCount",
                        0
                    ),

                "gender":
                    booking.get(
                        "gender",
                        ""
                    ),

                "bookingType":
                    booking.get(
                        "bookingType",
                        "RIDE"
                    ),

                "totalFare":
                    booking.get(
                        "totalFare",
                        0
                    ),

                "note":
                    booking.get(
                        "note",
                        ""
                    ),

                "sharedNote":
                    shared_ride.get(
                        "note",
                        ""
                    ),

                "sharedAt":
                    shared_ride.get(
                        "sharedAt"
                    ),

                "acceptedAt":
                    shared_ride.get(
                        "acceptedAt"
                    )
            })

        return response
