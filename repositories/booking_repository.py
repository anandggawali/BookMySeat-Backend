from core.database import bookings_collection
from core.utils import serialize_mongo_list

class BookingRepository:

    @staticmethod
    def save(booking: dict):
        return bookings_collection.insert_one(
            booking
        )

    @staticmethod
    def find_by_user(user_id: str):
        return list(
            bookings_collection.find(
                {"userId": user_id}
            )
        )

    @staticmethod
    def find_by_id(booking_id: str):
        return bookings_collection.find_one(
            {"bookingId": booking_id}
        )

    @staticmethod
    def get_all_bookings():
        return list(
            bookings_collection.find()
        )



    @staticmethod
    def get_my_bookings(user_id):
        bookings = BookingRepository.find_by_user(
            user_id
        )

        return serialize_mongo_list(bookings)

    @staticmethod
    def get_confirmed_bookings(trip_id: str):
        return list(
            bookings_collection.find({
                "tripId": trip_id,
                "bookingStatus": "CONFIRMED"
            })
        )

    @staticmethod
    def get_bookings_by_trip(trip_id):
        return list(
            bookings_collection.find({
                "tripId": trip_id
            })
        )