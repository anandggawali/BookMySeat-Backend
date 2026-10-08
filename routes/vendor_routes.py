from fastapi import APIRouter, Depends

from dependencies.auth_dependency import get_current_vendor
from services.shared_ride_service import SharedRideService


router = APIRouter(
    prefix="/api/vendor",
    tags=["Vendor"]
)


# =========================================================
# VENDOR TEST
# =========================================================

@router.get("/test")
def vendor_test(
        current_user=Depends(
            get_current_vendor
        )
):

    return {

        "message":
            "Vendor access working",

        "userId":
            current_user["userId"],

        "role":
            current_user["role"]
    }


# =========================================================
# VENDOR - ACCEPTED SHARED RIDES
# =========================================================

@router.get("/shared-rides")
def get_shared_rides(

        current_user=Depends(
            get_current_vendor
        )

):

    return (
        SharedRideService
        .get_vendor_shared_rides(
            current_user["userId"]
        )
    )
