import uuid

from fastapi import APIRouter, Depends

from core.database import weight_categories_collection
from models.weight_category_model import (
    WeightCategoryCreate
)

from models.parcel_fare_model import (
    ParcelFareCreate
)

from models.parcel_model import (
    ParcelCreate,
    ParcelAllocateRequest,
    ParcelRejectRequest, ParcelRescheduleRequest
)

from services.parcel_service import ParcelService

from dependencies.auth_dependency import get_current_user


router = APIRouter(
    prefix="/api/parcels",
    tags=["Parcels"]
)


# ============================================================
# WEIGHT CATEGORIES
# ============================================================

@router.post("/weight-categories")
def create_weight_category(
    request: WeightCategoryCreate,
    current_user=Depends(get_current_user)
):
    weight_category = {
        "weightCategoryId": str(uuid.uuid4()),
        "categoryName": request.categoryName,
        "minWeight": request.minWeight,
        "maxWeight": request.maxWeight,
        "isActive": True
    }

    weight_categories_collection.insert_one(weight_category)

    return weight_category

@router.get(
    "/weight-categories"
)
def get_weight_categories():

    return ParcelService.get_weight_categories()


# ============================================================
# PARCEL FARES
# ============================================================

@router.post(
    "/fares"
)
def create_parcel_fare(
        request: ParcelFareCreate,
        current_user=Depends(
            get_current_user
        )
):

    return ParcelService.create_parcel_fare(
        request
    )


@router.get("/fares/route/{route_id}/{direction}")
def get_parcel_fares_by_route(
        route_id: str,
        direction: str
):
    return ParcelService.get_parcel_fares_by_route(
        route_id,
        direction
    )


# ============================================================
# USER - CREATE PARCEL
# ============================================================

@router.post("")
def create_parcel(
        request: ParcelCreate,
        current_user=Depends(
            get_current_user
        )
):

    return ParcelService.create_parcel(

        request,

        current_user["userId"]
    )


# ============================================================
# USER - MY PARCELS
# ============================================================

@router.get("/my")
def get_my_parcels(

        current_user=Depends(
            get_current_user
        )
):

    return ParcelService.get_my_parcels(

        current_user["userId"]
    )


# ============================================================
# ADMIN - ALL PARCELS
# ============================================================

@router.get("/admin/all")
def get_all_parcels(

        current_user=Depends(
            get_current_user
        )
):

    return ParcelService.get_all_parcels()


# ============================================================
# ADMIN - ALLOCATE TRIP
# ============================================================

@router.put(
    "/admin/{parcel_id}/allocate"
)
def allocate_parcel(

        parcel_id: str,

        request: ParcelAllocateRequest,

        current_user=Depends(
            get_current_user
        )
):

    return ParcelService.allocate_parcel(

        parcel_id,

        request
    )


# ============================================================
# ADMIN - REJECT
# ============================================================

@router.put(
    "/admin/{parcel_id}/reject"
)
def reject_parcel(

        parcel_id: str,

        request: ParcelRejectRequest,

        current_user=Depends(
            get_current_user
        )
):

    return ParcelService.reject_parcel(

        parcel_id,

        request
    )


# ============================================================
# ADMIN - DELIVERED
# ============================================================

@router.put(
    "/admin/{parcel_id}/delivered"
)
def mark_delivered( 

        parcel_id: str,

        current_user=Depends(
            get_current_user
        )
):
   return ParcelService.mark_delivered(

        parcel_id
    )

# ============================================================
# ADMIN - RESCHEDULE CONFIRMED PARCEL
# ============================================================

@router.put(
    "/admin/{parcel_id}/reschedule"
)
def reschedule_parcel(

    parcel_id: str,

    request: ParcelRescheduleRequest,

    current_user=Depends(
        get_current_user
    )

):

    return ParcelService.reschedule_parcel(

        parcel_id,

        request

    )