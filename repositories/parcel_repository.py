from core.database import parcels_collection


class ParcelRepository:

    @staticmethod
    def create(parcel):

        parcels_collection.insert_one(parcel)

        return parcel

    @staticmethod
    def find_by_id(parcel_id):

        return parcels_collection.find_one(
            {
                "parcelId": parcel_id
            }
        )

    @staticmethod
    def find_by_user(user_id):

        return list(
            parcels_collection.find(
                {
                    "userId": user_id
                },
                {
                    "_id": 0
                }
            )
        )

    @staticmethod
    def get_all():

        return list(
            parcels_collection.find(
                {},
                {
                    "_id": 0
                }
            )
        )

    @staticmethod
    def update(
            parcel_id,
            data
    ):

        parcels_collection.update_one(
            {
                "parcelId": parcel_id
            },
            {
                "$set": data
            }
        )

    @staticmethod
    def delete(
            parcel_id
    ):

        parcels_collection.delete_one(
            {
                "parcelId": parcel_id
            }
        )