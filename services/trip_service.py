import uuid

from datetime import date, timedelta

from fastapi import HTTPException

from repositories.trip_repository import TripRepository
from repositories.booking_repository import BookingRepository


class TripService:

    @staticmethod
    def create_trip(request):

        today = date.today()
        max_date = today + timedelta(days=7)

        # Validate trip date
        if request.date < today:
            raise HTTPException(
                status_code=400,
                detail="Past date not allowed"
            )

        if request.date > max_date:
            raise HTTPException(
                status_code=400,
                detail="Trips can be created only within next 7 days"
            )

        # Validate fare
        if request.fare <= 0:
            raise HTTPException(
                status_code=400,
                detail="Fare must be greater than 0"
            )

        # Validate seats
        if request.totalSeats <= 0:
            raise HTTPException(
                status_code=400,
                detail="Total seats must be greater than 0"
            )

        trip = {
            "tripId": str(uuid.uuid4()),
            "route": request.route,
            "date": str(request.date),
            "timeSlot": request.timeSlot,
            "fare": request.fare,
            "totalSeats": request.totalSeats,
            "status": "OPEN"
        }

        TripRepository.save(trip)

        return {
            "message": "Trip created successfully",
            "tripId": trip["tripId"]
        }

    @staticmethod
    def calculate_available_seats(trip):

        confirmed_bookings = (
            BookingRepository.get_confirmed_bookings(
                trip["tripId"]
            )
        )

        confirmed_seats = sum(
            booking["passengerCount"]
            for booking in confirmed_bookings
        )

        available_seats = (
            trip["totalSeats"]
            - confirmed_seats
        )

        return max(0, available_seats)

    @staticmethod
    def search_trips(route, trip_date):

        trips = TripRepository.search(
            route,
            trip_date
        )

        response = []

        for trip in trips:

            available_seats = (
                TripService.calculate_available_seats(
                    trip
                )
            )

            response.append({

                "tripId": trip["tripId"],

                "route": trip["route"],

                "date": trip["date"],

                "timeSlot": trip["timeSlot"],

                "fare": trip["fare"],

                "totalSeats": trip["totalSeats"],

                "availableSeats": available_seats,

                "status": trip["status"]
            })

        return response

    @staticmethod
    def get_trip_by_id(trip_id):

        trip = TripRepository.find_by_id(
            trip_id
        )

        if not trip:
            raise HTTPException(
                status_code=404,
                detail="Trip not found"
            )

        available_seats = (
            TripService.calculate_available_seats(
                trip
            )
        )

        return {

            "tripId": trip["tripId"],

            "route": trip["route"],

            "date": trip["date"],

            "timeSlot": trip["timeSlot"],

            "fare": trip["fare"],

            "totalSeats": trip["totalSeats"],

            "availableSeats": available_seats,

            "status": trip["status"]
        }