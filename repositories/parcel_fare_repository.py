from core.database import parcel_fares_collection


class ParcelFareRepository:

    # ============================================================
    # CREATE
    # ============================================================

    @staticmethod
    def create(parcel_fare):

        parcel_fares_collection.insert_one(
            parcel_fare
        )

        # Return only our application fields.
        # Never return MongoDB ObjectId.
        return {
            "parcelFareId": parcel_fare["parcelFareId"],
            "routeId": parcel_fare["routeId"],
            "direction": parcel_fare["direction"],
            "weightCategoryId": parcel_fare["weightCategoryId"],
            "minFare": parcel_fare["minFare"],
            "maxFare": parcel_fare["maxFare"],
            "isActive": parcel_fare.get(
                "isActive",
                True
            )
        }

    # ============================================================
    # FIND BY ID
    # ============================================================

    @staticmethod
    def find_by_id(
            parcel_fare_id
    ):

        return parcel_fares_collection.find_one(
            {
                "parcelFareId":
                    parcel_fare_id
            },
            {
                "_id": 0
            }
        )

    # ============================================================
    # FIND BY ROUTE + DIRECTION
    # ============================================================

    @staticmethod
    def find_by_route_and_direction(
            route_id,
            direction
    ):

        return list(
            parcel_fares_collection.find(
                {
                    "routeId":
                        route_id,

                    "direction":
                        direction,

                    "isActive":
                        True
                },
                {
                    "_id": 0
                }
            )
        )

    # ============================================================
    # FIND BY ROUTE + DIRECTION + CATEGORY
    # ============================================================

    @staticmethod
    def find_by_route_direction_and_category(
            route_id,
            direction,
            weight_category_id
    ):

        return parcel_fares_collection.find_one(
            {
                "routeId":
                    route_id,

                "direction":
                    direction,

                "weightCategoryId":
                    weight_category_id,

                "isActive":
                    True
            },
            {
                "_id": 0
            }
        )

    # ============================================================
    # GET ALL
    # ============================================================

    @staticmethod
    def get_all():

        return list(
            parcel_fares_collection.find(
                {},
                {
                    "_id": 0
                }
            )
        )

    # ============================================================
    # UPDATE
    # ============================================================

    @staticmethod
    def update(
            parcel_fare_id,
            data
    ):

        parcel_fares_collection.update_one(
            {
                "parcelFareId":
                    parcel_fare_id
            },
            {
                "$set":
                    data
            }
        )

    # ============================================================
    # DELETE / DEACTIVATE
    # ============================================================

    @staticmethod
    def delete(
            parcel_fare_id
    ):

        parcel_fares_collection.update_one(
            {
                "parcelFareId":
                    parcel_fare_id
            },
            {
                "$set": {
                    "isActive":
                        False
                }
            }
        )