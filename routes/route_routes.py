from fastapi import APIRouter

from schemas.route_schema import (
    CreateRouteRequest
)

from services.route_service import (
    RouteService
)

router = APIRouter(
    prefix="/api/routes",
    tags=["Routes"]
)


@router.get("")
def get_routes():

    return RouteService.get_routes()


@router.post("")
def create_route(
        request: CreateRouteRequest
):

    return RouteService.create_route(
        request
    )