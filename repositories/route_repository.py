from core.database import routes_collection


class RouteRepository:

    @staticmethod
    def create(route):

        routes_collection.insert_one(
            route
        )

    @staticmethod
    def get_all():

        return list(
            routes_collection.find(
                {},
                {"_id": 0}
            )
        )

    @staticmethod
    def find_by_id(route_id):

        return routes_collection.find_one(
            {
                "routeId": route_id
            },
            {
                "_id": 0
            }
        )