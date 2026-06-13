from core.database import trips_collection


class TripRepository:

    @staticmethod
    def save(trip: dict):
        return trips_collection.insert_one(trip)

    @staticmethod
    def get_all_trips():
        return list(
            trips_collection.find(
                {"status": "OPEN"}
            )
        )
    @staticmethod
    def find_by_id(trip_id: str):
        return trips_collection.find_one(
            {"tripId": trip_id}
        )

    @staticmethod
    def search(route: str, trip_date):
        return list(
            trips_collection.find({
                "route": route,
                "date": str(trip_date)
            })
        )