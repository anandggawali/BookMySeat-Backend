from core.database import shared_rides_collection


class SharedRideRepository:

    @staticmethod
    def save(shared_ride: dict):

        return shared_rides_collection.insert_one(
            shared_ride
        )

    @staticmethod
    def find_by_id(
            shared_ride_id: str
    ):

        return shared_rides_collection.find_one(

            {
                "sharedRideId":
                    shared_ride_id
            }

        )

    @staticmethod
    def find_by_booking_id(
            booking_id: str
    ):

        return shared_rides_collection.find_one(

            {
                "bookingId":
                    booking_id
            }

        )

    @staticmethod
    def find_pending_by_vendor(
            vendor_id: str
    ):

        return list(

            shared_rides_collection.find(

                {
                    "sharedToVendorId":
                        vendor_id,

                    "status":
                        "PENDING"
                }

            )

        )

    @staticmethod
    def find_by_vendor(
            vendor_id: str
    ):

        return list(

            shared_rides_collection.find(

                {
                    "sharedToVendorId":
                        vendor_id
                }

            )

        )

    @staticmethod
    def find_accepted_by_vendor(
            vendor_id: str
    ):

        return list(

            shared_rides_collection.find(

                {
                    "sharedToVendorId":
                        vendor_id,

                    "status":
                        "ACCEPTED"
                }

            )

        )

    @staticmethod
    def update_status(
            shared_ride_id: str,
            status: str,
            update_data: dict = None
    ):

        update_fields = {

            "status":
                status
        }

        if update_data:

            update_fields.update(
                update_data
            )

        return shared_rides_collection.update_one(

            {
                "sharedRideId":
                    shared_ride_id
            },

            {
                "$set":
                    update_fields
            }

        )
