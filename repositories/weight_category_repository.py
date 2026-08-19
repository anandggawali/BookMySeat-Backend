from core.database import weight_categories_collection


class WeightCategoryRepository:

    @staticmethod
    def create(category):

        weight_categories_collection.insert_one(category)

        return category

    @staticmethod
    def find_by_id(weight_category_id):

        return weight_categories_collection.find_one(
            {
                "weightCategoryId": weight_category_id
            }
        )

    @staticmethod
    def get_all():

        return list(
            weight_categories_collection.find(
                {
                    "isActive": True
                },
                {
                    "_id": 0
                }
            )
        )

    @staticmethod
    def get_all_admin():

        return list(
            weight_categories_collection.find(
                {},
                {
                    "_id": 0
                }
            )
        )

    @staticmethod
    def update(
            weight_category_id,
            data
    ):

        weight_categories_collection.update_one(
            {
                "weightCategoryId":
                    weight_category_id
            },
            {
                "$set": data
            }
        )

    @staticmethod
    def delete(
            weight_category_id
    ):

        weight_categories_collection.update_one(
            {
                "weightCategoryId":
                    weight_category_id
            },
            {
                "$set": {
                    "isActive": False
                }
            }
        )