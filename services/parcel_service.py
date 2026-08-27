import uuid

from datetime import date, datetime

from fastapi import HTTPException

from repositories.parcel_repository import ParcelRepository
from repositories.parcel_fare_repository import ParcelFareRepository
from repositories.route_repository import RouteRepository
from repositories.weight_category_repository import WeightCategoryRepository
from repositories.trip_repository import TripRepository
from repositories.user_repository import UserRepository

from models.weight_category_model import WeightCategoryCreate
from models.parcel_fare_model import ParcelFareCreate
from models.parcel_model import (
    ParcelCreate,
    ParcelAllocateRequest,
    ParcelRejectRequest, ParcelRescheduleRequest
)


class ParcelService:

    # ============================================================
    # WEIGHT CATEGORY
    # ============================================================

    @staticmethod
    def create_weight_category(
            request: WeightCategoryCreate
    ):

        if request.minWeight < 0:
            raise HTTPException(
                status_code=400,
                detail="Minimum weight cannot be negative"
            )

        if (
                request.maxWeight is not None
                and request.maxWeight <= request.minWeight
        ):
            raise HTTPException(
                status_code=400,
                detail="Maximum weight must be greater than minimum weight"
            )

        category = {

            "weightCategoryId":
                str(uuid.uuid4()),

            "categoryName":
                request.categoryName.strip(),

            "minWeight":
                request.minWeight,

            "maxWeight":
                request.maxWeight,

            "isActive":
                True
        }

        return WeightCategoryRepository.create(
            category
        )

    @staticmethod
    def get_weight_categories():

        return WeightCategoryRepository.get_all()

    @staticmethod
    def get_all_weight_categories_admin():

        return WeightCategoryRepository.get_all_admin()

    # ============================================================
    # PARCEL FARE
    #
    # Fare belongs to:
    #
    # routeId
    # direction (UP / DOWN)
    # weightCategoryId
    #
    # NOT tripId
    # ============================================================

    @staticmethod
    def create_parcel_fare(
            request: ParcelFareCreate
    ):

        # --------------------------------------------------------
        # Find Route
        # --------------------------------------------------------

        route = RouteRepository.find_by_id(
            request.routeId
        )

        if not route:
            raise HTTPException(
                status_code=404,
                detail="Route not found"
            )

        if not route.get(
                "active",
                True
        ):
            raise HTTPException(
                status_code=400,
                detail="Route is inactive"
            )

        # --------------------------------------------------------
        # Validate Direction
        # --------------------------------------------------------

        direction = request.direction.upper()

        if direction not in [
            "UP",
            "DOWN"
        ]:
            raise HTTPException(
                status_code=400,
                detail="Direction must be UP or DOWN"
            )

        # --------------------------------------------------------
        # Get actual route string
        #
        # UP:
        # Pune(kharadi)-Rahuri-ShriRampur
        #
        # DOWN:
        # ShriRampur-Rahuri-Pune(kharadi)
        # --------------------------------------------------------

        if direction == "UP":

            route_value = route.get(
                "up"
            )

        else:

            route_value = route.get(
                "down"
            )

        if not route_value:
            raise HTTPException(
                status_code=400,
                detail=f"{direction} route is not configured"
            )

        # --------------------------------------------------------
        # Find Weight Category
        # --------------------------------------------------------

        category = (
            WeightCategoryRepository.find_by_id(
                request.weightCategoryId
            )
        )

        if not category:

            raise HTTPException(
                status_code=404,
                detail="Weight category not found"
            )

        if not category.get(
                "isActive",
                True
        ):

            raise HTTPException(
                status_code=400,
                detail="Weight category is inactive"
            )

        # --------------------------------------------------------
        # Validate Fare
        # --------------------------------------------------------

        if request.minFare <= 0:

            raise HTTPException(
                status_code=400,
                detail="Minimum fare must be greater than 0"
            )

        if request.maxFare < request.minFare:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Maximum fare must be greater than "
                    "or equal to minimum fare"
                )
            )

        # --------------------------------------------------------
        # Check Duplicate
        #
        # One fare configuration for:
        #
        # route + direction + weight category
        # --------------------------------------------------------

        existing = (
            ParcelFareRepository
            .find_by_route_direction_and_category(
                request.routeId,
                direction,
                request.weightCategoryId
            )
        )

        if existing:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Parcel fare already exists for "
                    "this route, direction and weight category"
                )
            )

        # --------------------------------------------------------
        # Create Parcel Fare
        # --------------------------------------------------------

        parcel_fare = {

            "parcelFareId":
                str(uuid.uuid4()),

            "routeId":
                request.routeId,

            "direction":
                direction,

            "weightCategoryId":
                request.weightCategoryId,

            "minFare":
                request.minFare,

            "maxFare":
                request.maxFare,

            "isActive":
                True
        }

        return ParcelFareRepository.create(
            parcel_fare
        )

    # ============================================================
    # GET PARCEL FARES BY ROUTE + DIRECTION
    # ============================================================

    @staticmethod
    def get_parcel_fares_by_route(
            route_id,
            direction
    ):

        # --------------------------------------------------------
        # Find Route
        # --------------------------------------------------------

        route = RouteRepository.find_by_id(
            route_id
        )

        if not route:

            raise HTTPException(
                status_code=404,
                detail="Route not found"
            )

        if not route.get(
                "active",
                True
        ):

            raise HTTPException(
                status_code=400,
                detail="Route is inactive"
            )

        # --------------------------------------------------------
        # Validate Direction
        # --------------------------------------------------------

        direction = direction.upper()

        if direction not in [
            "UP",
            "DOWN"
        ]:

            raise HTTPException(
                status_code=400,
                detail="Direction must be UP or DOWN"
            )

        # --------------------------------------------------------
        # Get actual route
        # --------------------------------------------------------

        if direction == "UP":

            route_value = route.get(
                "up"
            )

        else:

            route_value = route.get(
                "down"
            )

        if not route_value:

            raise HTTPException(
                status_code=404,
                detail=(
                    f"{direction} route is not configured"
                )
            )

        # --------------------------------------------------------
        # Get Parcel Fares
        # --------------------------------------------------------

        fares = (
            ParcelFareRepository
            .find_by_route_and_direction(
                route_id,
                direction
            )
        )

        response = []

        for fare in fares:

            category = (
                WeightCategoryRepository
                .find_by_id(
                    fare["weightCategoryId"]
                )
            )

            if not category:
                continue

            response.append({

                "parcelFareId":
                    fare["parcelFareId"],

                "routeId":
                    fare["routeId"],

                "direction":
                    fare["direction"],

                # Actual route string
                "route":
                    route_value,

                "routeName":
                    route.get(
                        "routeName",
                        ""
                    ),

                # Weight category
                "weightCategoryId":
                    fare["weightCategoryId"],

                "categoryName":
                    category.get(
                        "categoryName",
                        ""
                    ),

                "minWeight":
                    category.get(
                        "minWeight",
                        0
                    ),

                "maxWeight":
                    category.get(
                        "maxWeight"
                    ),

                # Fare
                "minFare":
                    fare["minFare"],

                "maxFare":
                    fare["maxFare"],

                "isActive":
                    fare.get(
                        "isActive",
                        True
                    )
            })

        return response

    # ============================================================
    # CREATE PARCEL
    # ============================================================

    @staticmethod
    def create_parcel(
            request: ParcelCreate,
            user_id
    ):

        user = UserRepository.find_by_id(
            user_id
        )

        if not user:

            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        # --------------------------------------------------------
        # Weight Category
        # --------------------------------------------------------

        category = (
            WeightCategoryRepository
            .find_by_id(
                request.weightCategoryId
            )
        )

        if not category:

            raise HTTPException(
                status_code=404,
                detail="Weight category not found"
            )

        if not category.get(
                "isActive",
                True
        ):

            raise HTTPException(
                status_code=400,
                detail="Weight category is inactive"
            )

        # --------------------------------------------------------
        # Validate Weight
        # --------------------------------------------------------

        if request.weight <= 0:

            raise HTTPException(
                status_code=400,
                detail="Parcel weight must be greater than 0"
            )

        min_weight = category.get(
            "minWeight",
            0
        )

        max_weight = category.get(
            "maxWeight"
        )

        if request.weight < min_weight:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Parcel weight is below "
                    "selected weight category"
                )
            )

        if (
                max_weight is not None
                and request.weight > max_weight
        ):

            raise HTTPException(
                status_code=400,
                detail=(
                    "Parcel weight exceeds "
                    "selected weight category"
                )
            )

        # --------------------------------------------------------
        # Expected Date
        # --------------------------------------------------------

        try:

            expected_date = date.fromisoformat(
                request.expectedDate
            )

        except ValueError:

            raise HTTPException(
                status_code=400,
                detail="Invalid expected date"
            )

        if expected_date < date.today():

            raise HTTPException(
                status_code=400,
                detail="Expected date cannot be in the past"
            )

        # --------------------------------------------------------
        # Parcel Fare
        # --------------------------------------------------------

        parcel_fare = None

        if request.parcelFareId:

            parcel_fare = (
                ParcelFareRepository
                .find_by_id(
                    request.parcelFareId
                )
            )

            if not parcel_fare:

                raise HTTPException(
                    status_code=404,
                    detail="Parcel fare not found"
                )

            if not parcel_fare.get(
                    "isActive",
                    True
            ):

                raise HTTPException(
                    status_code=400,
                    detail="Parcel fare is inactive"
                )

            if (
                    parcel_fare["weightCategoryId"]
                    != request.weightCategoryId
            ):

                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Parcel fare does not match "
                        "weight category"
                    )
                )
        if not request.contactPersonPhone.isdigit():
            raise HTTPException(
                status_code=400,
                detail="Contact phone number must contain only digits"
            )

        if len(request.contactPersonPhone) != 10:
            raise HTTPException(
                status_code=400,
                detail="Contact phone number must be 10 digits"
            )
        # --------------------------------------------------------
        # Create Parcel
        # --------------------------------------------------------

        now = datetime.utcnow().isoformat()

        parcel = {

            "parcelId":
                str(uuid.uuid4()),

            "userId":
                user_id,

            "parcelFareId":
                request.parcelFareId,

            "weightCategoryId":
                request.weightCategoryId,

            # Direction will be determined from
            # selected parcel fare
            "routeId":
                parcel_fare.get(
                    "routeId"
                )
                if parcel_fare
                else None,

            "direction":
                parcel_fare.get(
                    "direction"
                )
                if parcel_fare
                else None,

            # Trip allocated later by admin
            "tripId":
                None,

            "expectedDate":
                request.expectedDate,

            "actualDate":
                None,

            "actualTime":
                None,

            "parcelType":
                request.parcelType.strip(),

            "weight":
                request.weight,

            "note":
                request.note,

            "agreedFare":
                None,

            "rejectionReason":
                None,

            "parcelStatus":
                "PENDING",

            "createdAt":
                now,

            "updatedAt":
                now
        }

        ParcelRepository.create(
            parcel
        )

        # --------------------------------------------------------
        # Notify Admins
        # --------------------------------------------------------

        try:

            admins = UserRepository.get_admins()

            from services.app_notification_service import (
                AppNotificationService
            )

            for admin in admins:

                AppNotificationService.create_notification(

                    user_id=admin["userId"],

                    title="New Parcel Request",

                    body=(
                        f"{user.get('name', 'User')}\n"
                        f"Parcel: {request.parcelType}\n"
                        f"Weight: {request.weight} KG\n"
                        f"Expected Date: "
                        f"{request.expectedDate}"
                    ),

                    type="PARCEL",

                    click_action="MANAGE_PARCELS",

                    color="#2962FF"
                )

        except Exception as e:

            print(
                "Parcel notification failed:",
                str(e)
            )

        return {

            "parcelId":
                parcel["parcelId"],

            "parcelStatus":
                parcel["parcelStatus"],

            "message":
                "Parcel request created successfully"
        }

    # ============================================================
    # USER - MY PARCELS
    # ============================================================

    @staticmethod
    def get_my_parcels(
            user_id
    ):

        parcels = (
            ParcelRepository
            .find_by_user(
                user_id
            )
        )

        response = []

        for parcel in parcels:

            trip = None

            if parcel.get("tripId"):

                trip = (
                    TripRepository
                    .find_by_id(
                        parcel["tripId"]
                    )
                )

            category = (
                WeightCategoryRepository
                .find_by_id(
                    parcel["weightCategoryId"]
                )
            )

            route = None

            if parcel.get("routeId"):

                route = (
                    RouteRepository
                    .find_by_id(
                        parcel["routeId"]
                    )
                )

            direction = parcel.get(
                "direction"
            )

            route_value = ""

            if route and direction:

                route_value = route.get(
                    "up"
                    if direction == "UP"
                    else "down",
                    ""
                )

            response.append({

                "parcelId":
                    parcel["parcelId"],

                "parcelType":
                    parcel.get(
                        "parcelType",
                        ""
                    ),

                "weight":
                    parcel.get(
                        "weight",
                        0
                    ),

                "categoryName":
                    category.get(
                        "categoryName",
                        ""
                    )
                    if category else "",

                "expectedDate":
                    parcel.get(
                        "expectedDate",
                        ""
                    ),

                "actualDate":
                    parcel.get(
                        "actualDate"
                    ),

                "actualTime":
                    parcel.get(
                        "actualTime"
                    ),

                "routeId":
                    parcel.get(
                        "routeId"
                    ),

                "direction":
                    direction,

                "route":
                    route_value,

                "tripId":
                    parcel.get(
                        "tripId"
                    ),

                "agreedFare":
                    parcel.get(
                        "agreedFare"
                    ),

                "parcelStatus":
                    parcel.get(
                        "parcelStatus",
                        ""
                    ),

                "rejectionReason":
                    parcel.get(
                        "rejectionReason",
                        ""
                    )
            })

        return response

    # ============================================================
    # ADMIN - ALL PARCELS
    # ============================================================

    @staticmethod
    def get_all_parcels():

        parcels = ParcelRepository.get_all()

        response = []

        for parcel in parcels:

            user = (
                UserRepository
                .find_by_id(
                    parcel.get("userId")
                )
            )

            trip = None

            if parcel.get("tripId"):

                trip = (
                    TripRepository
                    .find_by_id(
                        parcel["tripId"]
                    )
                )

            category = (
                WeightCategoryRepository
                .find_by_id(
                    parcel.get(
                        "weightCategoryId"
                    )
                )
            )

            route = None

            if parcel.get("routeId"):

                route = (
                    RouteRepository
                    .find_by_id(
                        parcel["routeId"]
                    )
                )

            direction = parcel.get(
                "direction"
            )

            route_value = ""

            if route and direction:

                route_value = route.get(
                    "up"
                    if direction == "UP"
                    else "down",
                    ""
                )

            response.append({

                "parcelId":
                    parcel.get(
                        "parcelId"
                    ),

                "userId":
                    parcel.get(
                        "userId"
                    ),

                "userName":
                    user.get(
                        "name",
                        "Unknown User"
                    )
                    if user else
                    "Unknown User",

                "mobileNumber":
                    user.get(
                        "phoneNo",
                        ""
                    )
                    if user else "",

                "parcelType":
                    parcel.get(
                        "parcelType",
                        ""
                    ),

                "weight":
                    parcel.get(
                        "weight",
                        0
                    ),

                "categoryName":
                    category.get(
                        "categoryName",
                        ""
                    )
                    if category else "",

                "expectedDate":
                    parcel.get(
                        "expectedDate",
                        ""
                    ),

                "routeId":
                    parcel.get(
                        "routeId"
                    ),

                "direction":
                    direction,

                "route":
                    route_value,

                "tripId":
                    parcel.get(
                        "tripId"
                    ),

                "actualDate":
                    parcel.get(
                        "actualDate"
                    ),

                "actualTime":
                    parcel.get(
                        "actualTime"
                    ),

                "agreedFare":
                    parcel.get(
                        "agreedFare"
                    ),

                "parcelStatus":
                    parcel.get(
                        "parcelStatus",
                        ""
                    ),

                "note":
                    parcel.get(
                        "note",
                        ""
                    ),

                "rejectionReason":
                    parcel.get(
                        "rejectionReason",
                        ""
                    )
            })

        return response

    # ============================================================
    # ADMIN - ALLOCATE TRIP + FARE
    # ============================================================

    @staticmethod
    def allocate_parcel(
            parcel_id,
            request: ParcelAllocateRequest
    ):

        parcel = (
            ParcelRepository
            .find_by_id(
                parcel_id
            )
        )

        if not parcel:

            raise HTTPException(
                status_code=404,
                detail="Parcel not found"
            )

        if parcel["parcelStatus"] == "DELIVERED":

            raise HTTPException(
                status_code=400,
                detail="Delivered parcel cannot be modified"
            )

        if parcel["parcelStatus"] == "REJECTED":

            raise HTTPException(
                status_code=400,
                detail="Rejected parcel cannot be allocated"
            )

        # --------------------------------------------------------
        # Find Trip
        # --------------------------------------------------------

        trip = (
            TripRepository
            .find_by_id(
                request.tripId
            )
        )

        if not trip:

            raise HTTPException(
                status_code=404,
                detail="Trip not found"
            )

        # --------------------------------------------------------
        # Validate Trip Against Parcel Route
        # --------------------------------------------------------

        if parcel.get("routeId"):

            trip_route_id = trip.get(
                "routeId"
            )

            if trip_route_id:

                if trip_route_id != parcel["routeId"]:

                    raise HTTPException(
                        status_code=400,
                        detail=(
                            "Selected trip does not belong "
                            "to parcel route"
                        )
                    )

        # --------------------------------------------------------
        # Validate Trip Direction
        # --------------------------------------------------------

        if parcel.get("direction"):

            trip_direction = trip.get(
                "direction"
            )

            if trip_direction:

                if (
                        trip_direction.upper()
                        != parcel["direction"].upper()
                ):

                    raise HTTPException(
                        status_code=400,
                        detail=(
                            "Selected trip direction does not "
                            "match parcel direction"
                        )
                    )

        # --------------------------------------------------------
        # Check Parcel Fare
        # --------------------------------------------------------

        parcel_fare = None

        if parcel.get(
                "parcelFareId"
        ):

            parcel_fare = (
                ParcelFareRepository
                .find_by_id(
                    parcel["parcelFareId"]
                )
            )

        if parcel_fare:

            if (
                    parcel_fare["routeId"]
                    != parcel.get("routeId")
            ):

                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Parcel fare does not match "
                        "parcel route"
                    )
                )

            if (
                    parcel_fare["direction"]
                    != parcel.get("direction")
            ):

                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Parcel fare does not match "
                        "parcel direction"
                    )
                )



        # --------------------------------------------------------
        # Allocate Trip
        # --------------------------------------------------------

        now = datetime.utcnow().isoformat()

        update_data = {

            "tripId":
                request.tripId,

            "actualDate":
                trip["date"],

            "actualTime":
                trip["timeSlot"],

            "agreedFare":
                request.agreedFare,

            "parcelStatus":
                "CONFIRMED",

            "rejectionReason":
                None,

            "updatedAt":
                now
        }

        ParcelRepository.update(
            parcel_id,
            update_data
        )

        # --------------------------------------------------------
        # Notify User
        # --------------------------------------------------------

        try:

            from services.app_notification_service import (
                AppNotificationService
            )

            AppNotificationService.create_notification(

                user_id=parcel["userId"],

                title="Parcel Confirmed",

                body=(
                    f"Your parcel has been confirmed.\n"
                    f"{trip.get('route', '')}\n"
                    f"{trip['date']} • "
                    f"{trip['timeSlot']}\n"
                    f"Fare: ₹{request.agreedFare}"
                ),

                type="PARCEL_CONFIRMED",

                click_action="OPEN_PARCEL",

                color="#4CAF50"
            )

        except Exception as e:

            print(
                "Parcel confirmation notification failed:",
                str(e)
            )

        return {

            "message":
                "Parcel confirmed successfully",

            "parcelId":
                parcel_id,

            "tripId":
                request.tripId,

            "actualDate":
                trip["date"],

            "actualTime":
                trip["timeSlot"],

            "agreedFare":
                request.agreedFare,

            "parcelStatus":
                "CONFIRMED"
        }

    # ============================================================
    # ADMIN - REJECT PARCEL
    # ============================================================

    @staticmethod
    def reject_parcel(
            parcel_id,
            request: ParcelRejectRequest
    ):

        parcel = (
            ParcelRepository
            .find_by_id(
                parcel_id
            )
        )

        if not parcel:

            raise HTTPException(
                status_code=404,
                detail="Parcel not found"
            )

        if parcel["parcelStatus"] == "CONFIRMED":

            raise HTTPException(
                status_code=400,
                detail="Confirmed parcel cannot be rejected"
            )

        now = datetime.utcnow().isoformat()

        ParcelRepository.update(

            parcel_id,

            {

                "parcelStatus":
                    "REJECTED",

                "rejectionReason":
                    request.reason,

                "updatedAt":
                    now
            }
        )

        try:

            from services.app_notification_service import (
                AppNotificationService
            )

            AppNotificationService.create_notification(

                user_id=parcel["userId"],

                title="Parcel Rejected",

                body=(
                    "Your parcel request has been rejected.\n"
                    f"Reason: {request.reason}"
                ),

                type="PARCEL_REJECTED",

                click_action="OPEN_PARCEL",

                color="#F44336"
            )

        except Exception as e:

            print(
                "Parcel rejection notification failed:",
                str(e)
            )

        return {

            "message":
                "Parcel rejected successfully"
        }

    # ============================================================
    # MARK DELIVERED
    # ============================================================

    @staticmethod
    def mark_delivered(
            parcel_id
    ):

        parcel = (
            ParcelRepository
            .find_by_id(
                parcel_id
            )
        )

        if not parcel:
            raise HTTPException(
                status_code=404,
                detail="Parcel not found"
            )

        if parcel["parcelStatus"] != "CONFIRMED":
            raise HTTPException(
                status_code=400,
                detail=(
                    "Only confirmed parcels can "
                    "be marked delivered"
                )
            )

        # --------------------------------------------------------
        # Update Parcel
        # --------------------------------------------------------

        now = datetime.utcnow()

        ParcelRepository.update(

            parcel_id,

            {

                "parcelStatus":
                    "DELIVERED",

                "updatedAt":
                    now.isoformat()
            }
        )

        # --------------------------------------------------------
        # Notify User
        # --------------------------------------------------------

        try:

            from services.app_notification_service import (
                AppNotificationService
            )

            AppNotificationService.create_notification(

                user_id=parcel["userId"],

                title="Parcel Delivered",

                body=(
                    "Your parcel has been delivered successfully."
                ),

                type="PARCEL_DELIVERED",

                click_action="OPEN_PARCEL",

                color="#4CAF50"
            )

        except Exception as e:

            print(
                "Parcel delivery notification failed:",
                str(e)
            )

        # --------------------------------------------------------
        # Response
        # --------------------------------------------------------

        return {

            "message":
                "Parcel marked as delivered",

            "parcelId":
                parcel_id,

            "parcelStatus":
                "DELIVERED"
        }

    @staticmethod
    def reschedule_parcel(
            parcel_id: str,
            request: ParcelRescheduleRequest
    ):

        parcel = ParcelRepository.find_by_id(parcel_id)

        if not parcel:
            raise HTTPException(
                status_code=404,
                detail="Parcel not found"
            )

        # ------------------------------------------------------------
        # Only confirmed parcels can be rescheduled
        # ------------------------------------------------------------

        if parcel.get("parcelStatus") != "CONFIRMED":
            raise HTTPException(
                status_code=400,
                detail="Only confirmed parcels can be rescheduled"
            )

        # ------------------------------------------------------------
        # Get trip
        # ------------------------------------------------------------

        trip = TripRepository.find_by_id(
            request.tripId
        )

        if not trip:
            raise HTTPException(
                status_code=404,
                detail="Trip not found"
            )

        # ------------------------------------------------------------
        # Validate route
        # ------------------------------------------------------------

        parcel_route_id = parcel.get("routeId")

        trip_route_id = trip.get("routeId")

        if (
                parcel_route_id
                and trip_route_id
                and parcel_route_id != trip_route_id
        ):
            raise HTTPException(
                status_code=400,
                detail="Selected trip does not belong to parcel route"
            )

        # ------------------------------------------------------------
        # Update trip and fare
        # ------------------------------------------------------------

        update_data = {

            "tripId": request.tripId,

            "actualDate": trip.get("date"),

            "actualTime": trip.get("timeSlot"),

            "agreedFare": request.agreedFare,

            "updatedAt": datetime.utcnow().isoformat()
        }

        ParcelRepository.update(
            parcel_id,
            update_data
        )

        return {

            "parcelId": parcel_id,

            "parcelStatus": "CONFIRMED",

            "tripId": request.tripId,

            "agreedFare": request.agreedFare,

            "actualDate": trip.get("date"),

            "actualTime": trip.get("timeSlot"),

            "message": "Parcel rescheduled successfully"
        }