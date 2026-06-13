import uuid

from repositories.route_repository import RouteRepository


class RouteService:

    @staticmethod
    def create_route(request):

        route = {

            "routeId":
                str(uuid.uuid4()),

            "routeName":
                request.routeName,

            "up":
                request.up,

            "down":
                request.down,

            "active":
                True
        }

        RouteRepository.create(route)

        return {
            "message":
                "Route created successfully"
        }

    @staticmethod
    def get_routes():

        return RouteRepository.get_all()