from pydantic import BaseModel


class Route(BaseModel):
    routeId: str
    routeName: str
    up: str
    down: str
    active: bool = True

class CreateRouteRequest(BaseModel):
        routeName: str
        up: str
        down: str

class RouteResponse(BaseModel):
        routeId: str
        routeName: str
        up: str
        down: str
        active: bool