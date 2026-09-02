from collections import defaultdict
from datetime import date, timedelta

from repositories.trip_repository import TripRepository
from repositories.booking_repository import BookingRepository
from repositories.parcel_repository import ParcelRepository
from repositories.route_repository import RouteRepository


class AdminAnalyticsService:

    # =========================================================
    # MAIN ANALYTICS
    # =========================================================

    @staticmethod
    def get_summary(
        period: str = "today",
        year: int | None = None,
        month: int | None = None
    ):

        # =====================================================
        # DATE RANGE
        # =====================================================

        (
            start_date,
            end_date,
            previous_start,
            previous_end
        ) = AdminAnalyticsService.get_date_range(
            period=period,
            year=year,
            month=month
        )

        # =====================================================
        # LOAD ALL DATA
        #
        # IMPORTANT:
        # Trips, ride bookings and parcels are separate
        # collections.
        # =====================================================

        trips = TripRepository.get_all_trips_for_analytics()

        ride_bookings = (
            BookingRepository
            .get_all_bookings_for_analytics()
        )

        parcels = ParcelRepository.get_all()

        # =====================================================
        # TRIP MAP
        # =====================================================

        trip_map = {}

        for trip in trips:

            trip_id = str(
                trip.get(
                    "tripId",
                    ""
                )
            )

            if trip_id:

                trip_map[trip_id] = trip

        # =====================================================
        # CURRENT PERIOD TRIPS
        # =====================================================

        current_trips = []

        for trip in trips:

            trip_date = (
                AdminAnalyticsService
                .parse_date(
                    trip.get("date")
                )
            )

            if not trip_date:
                continue

            if (
                start_date
                <= trip_date
                <= end_date
            ):

                current_trips.append(
                    trip
                )

        # =====================================================
        # PREVIOUS PERIOD TRIPS
        # =====================================================

        previous_trips = []

        for trip in trips:

            trip_date = (
                AdminAnalyticsService
                .parse_date(
                    trip.get("date")
                )
            )

            if not trip_date:
                continue

            if (
                previous_start
                <= trip_date
                <= previous_end
            ):

                previous_trips.append(
                    trip
                )

        # =====================================================
        # CURRENT RIDE BOOKINGS
        # =====================================================

        current_rides = []

        previous_rides = []

        for booking in ride_bookings:

            trip_id = str(
                booking.get(
                    "tripId",
                    ""
                )
            )

            trip = trip_map.get(
                trip_id
            )

            if not trip:
                continue

            trip_date = (
                AdminAnalyticsService
                .parse_date(
                    trip.get("date")
                )
            )

            if not trip_date:
                continue

            booking_type = str(
                booking.get(
                    "bookingType",
                    "RIDE"
                )
            ).upper()

            # Only RIDE records belong here

            if booking_type != "RIDE":
                continue

            if (
                start_date
                <= trip_date
                <= end_date
            ):

                current_rides.append(
                    booking
                )

            if (
                previous_start
                <= trip_date
                <= previous_end
            ):

                previous_rides.append(
                    booking
                )

        # =====================================================
        # CURRENT PARCELS
        # =====================================================

        current_parcels = []

        previous_parcels = []

        for parcel in parcels:

            parcel_date = (
                AdminAnalyticsService
                .get_parcel_analytics_date(
                    parcel
                )
            )

            if not parcel_date:
                continue

            if (
                start_date
                <= parcel_date
                <= end_date
            ):

                current_parcels.append(
                    parcel
                )

            if (
                previous_start
                <= parcel_date
                <= previous_end
            ):

                previous_parcels.append(
                    parcel
                )

        # =====================================================
        # RIDE BOOKING COUNTS
        # =====================================================

        total_ride_bookings = len(
            current_rides
        )

        confirmed_ride_bookings = 0

        pending_ride_bookings = 0

        rejected_ride_bookings = 0

        ride_revenue = 0.0

        total_passengers = 0

        confirmed_passengers = 0

        for booking in current_rides:

            status = str(
                booking.get(
                    "bookingStatus",
                    ""
                )
            ).upper()

            passengers = AdminAnalyticsService.to_int(
                booking.get(
                    "passengerCount",
                    0
                )
            )

            total_passengers += passengers

            if status == "CONFIRMED":

                confirmed_ride_bookings += 1

                confirmed_passengers += passengers

                ride_revenue += (
                    AdminAnalyticsService.to_float(
                        booking.get(
                            "totalFare",
                            0
                        )
                    )
                )

            elif status == "PENDING":

                pending_ride_bookings += 1

            elif status == "REJECTED":

                rejected_ride_bookings += 1

        # =====================================================
        # PREVIOUS RIDE REVENUE
        # =====================================================

        previous_ride_revenue = 0.0

        previous_confirmed_ride_bookings = 0

        for booking in previous_rides:

            status = str(
                booking.get(
                    "bookingStatus",
                    ""
                )
            ).upper()

            if status != "CONFIRMED":
                continue

            previous_confirmed_ride_bookings += 1

            previous_ride_revenue += (
                AdminAnalyticsService.to_float(
                    booking.get(
                        "totalFare",
                        0
                    )
                )
            )

        # =====================================================
        # PARCEL ANALYTICS
        # =====================================================

        total_parcel_requests = len(
            current_parcels
        )

        confirmed_parcels = 0

        delivered_parcels = 0

        pending_parcels = 0

        rejected_parcels = 0

        parcel_revenue = 0.0

        total_parcel_weight = 0.0

        confirmed_parcel_weight = 0.0

        total_parcel_count = total_parcel_requests

        for parcel in current_parcels:

            status = str(
                parcel.get(
                    "parcelStatus",
                    ""
                )
            ).upper()

            weight = (
                AdminAnalyticsService
                .to_float(
                    parcel.get(
                        "weight",
                        0
                    )
                )
            )

            total_parcel_weight += weight

            # -------------------------------------------------
            # Revenue:
            #
            # CONFIRMED and DELIVERED are completed revenue.
            # -------------------------------------------------

            if status in (
                "CONFIRMED",
                "DELIVERED"
            ):

                confirmed_parcels += 1

                if status == "DELIVERED":

                    delivered_parcels += 1

                confirmed_parcel_weight += weight

                parcel_revenue += (
                    AdminAnalyticsService
                    .to_float(
                        parcel.get(
                            "agreedFare",
                            0
                        )
                    )
                )

            elif status == "PENDING":

                pending_parcels += 1

            elif status == "REJECTED":

                rejected_parcels += 1

        # =====================================================
        # PREVIOUS PARCEL REVENUE
        # =====================================================

        previous_parcel_revenue = 0.0

        previous_confirmed_parcels = 0

        for parcel in previous_parcels:

            status = str(
                parcel.get(
                    "parcelStatus",
                    ""
                )
            ).upper()

            if status not in (
                "CONFIRMED",
                "DELIVERED"
            ):

                continue

            previous_confirmed_parcels += 1

            previous_parcel_revenue += (
                AdminAnalyticsService
                .to_float(
                    parcel.get(
                        "agreedFare",
                        0
                    )
                )
            )

        # =====================================================
        # COMBINED BUSINESS NUMBERS
        # =====================================================

        total_bookings = (
            total_ride_bookings
            + total_parcel_requests
        )

        confirmed_bookings = (
            confirmed_ride_bookings
            + confirmed_parcels
        )

        pending_bookings = (
            pending_ride_bookings
            + pending_parcels
        )

        rejected_bookings = (
            rejected_ride_bookings
            + rejected_parcels
        )

        total_revenue = (
            ride_revenue
            + parcel_revenue
        )

        previous_booking_count = (
            len(previous_rides)
            + len(previous_parcels)
        )

        previous_revenue = (
            previous_ride_revenue
            + previous_parcel_revenue
        )

        # =====================================================
        # CHANGES
        # =====================================================

        revenue_change = (
            AdminAnalyticsService
            .calculate_percentage_change(
                total_revenue,
                previous_revenue
            )
        )

        bookings_change = (
            AdminAnalyticsService
            .calculate_percentage_change(
                total_bookings,
                previous_booking_count
            )
        )

        # =====================================================
        # SEATS
        #
        # ONLY RIDE PASSENGERS
        #
        # PARCELS NEVER CONSUME SEATS
        # =====================================================

        total_seats = 0

        for trip in current_trips:

            total_seats += (
                AdminAnalyticsService.to_int(
                    trip.get(
                        "totalSeats",
                        0
                    )
                )
            )

        booked_seats = confirmed_passengers

        available_seats = max(
            0,
            total_seats - booked_seats
        )

        overbooked_seats = max(
            0,
            booked_seats - total_seats
        )

        seat_utilization = 0.0

        if total_seats > 0:

            seat_utilization = (
                booked_seats
                /
                total_seats
            ) * 100

        # =====================================================
        # AVERAGES
        # =====================================================

        average_booking_value = 0.0

        if confirmed_bookings > 0:

            average_booking_value = (
                total_revenue
                /
                confirmed_bookings
            )

        average_parcel_fare = 0.0

        if confirmed_parcels > 0:

            average_parcel_fare = (
                parcel_revenue
                /
                confirmed_parcels
            )

        average_ride_fare = 0.0

        if confirmed_ride_bookings > 0:

            average_ride_fare = (
                ride_revenue
                /
                confirmed_ride_bookings
            )

        # =====================================================
        # ROUTE ANALYTICS
        # =====================================================

        route_data = defaultdict(
            lambda: {
                "bookings": 0,
                "rideBookings": 0,
                "parcelBookings": 0,
                "passengers": 0,
                "parcels": 0,
                "weight": 0.0,
                "revenue": 0.0,
                "rideRevenue": 0.0,
                "parcelRevenue": 0.0
            }
        )

        # -----------------------------------------------------
        # RIDE ROUTES
        # -----------------------------------------------------

        for booking in current_rides:

            status = str(
                booking.get(
                    "bookingStatus",
                    ""
                )
            ).upper()

            if status != "CONFIRMED":
                continue

            trip_id = str(
                booking.get(
                    "tripId",
                    ""
                )
            )

            trip = trip_map.get(
                trip_id
            )

            if not trip:
                continue

            route = (
                trip.get(
                    "route",
                    "Unknown Route"
                )
                or "Unknown Route"
            )

            fare = (
                AdminAnalyticsService
                .to_float(
                    booking.get(
                        "totalFare",
                        0
                    )
                )
            )

            passengers = (
                AdminAnalyticsService
                .to_int(
                    booking.get(
                        "passengerCount",
                        0
                    )
                )
            )

            route_data[route]["bookings"] += 1

            route_data[route]["rideBookings"] += 1

            route_data[route]["passengers"] += passengers

            route_data[route]["revenue"] += fare

            route_data[route]["rideRevenue"] += fare

        # -----------------------------------------------------
        # PARCEL ROUTES
        # -----------------------------------------------------

        for parcel in current_parcels:

            status = str(
                parcel.get(
                    "parcelStatus",
                    ""
                )
            ).upper()

            if status not in (
                "CONFIRMED",
                "DELIVERED"
            ):

                continue

            route = (
                AdminAnalyticsService
                .get_parcel_route(
                    parcel
                )
            )

            fare = (
                AdminAnalyticsService
                .to_float(
                    parcel.get(
                        "agreedFare",
                        0
                    )
                )
            )

            weight = (
                AdminAnalyticsService
                .to_float(
                    parcel.get(
                        "weight",
                        0
                    )
                )
            )

            route_data[route]["bookings"] += 1

            route_data[route]["parcelBookings"] += 1

            route_data[route]["parcels"] += 1

            route_data[route]["weight"] += weight

            route_data[route]["revenue"] += fare

            route_data[route]["parcelRevenue"] += fare

        # =====================================================
        # ROUTE LIST
        # =====================================================

        route_analytics = []

        for route, data in route_data.items():

            # "travelUnits" means:
            #
            # ride passengers + parcels
            #
            # This gives a consistent activity metric
            # without allowing parcels to affect seats.

            travel_units = (
                data["passengers"]
                +
                data["parcels"]
            )

            route_analytics.append({

                "route":
                    route,

                "bookings":
                    data["bookings"],

                "rideBookings":
                    data["rideBookings"],

                "parcelBookings":
                    data["parcelBookings"],

                "passengers":
                    data["passengers"],

                "parcels":
                    data["parcels"],

                "travelUnits":
                    travel_units,

                "weight":
                    round(
                        data["weight"],
                        2
                    ),

                "revenue":
                    round(
                        data["revenue"],
                        2
                    ),

                "rideRevenue":
                    round(
                        data["rideRevenue"],
                        2
                    ),

                "parcelRevenue":
                    round(
                        data["parcelRevenue"],
                        2
                    )
            })

        # Most travelled = highest travel units

        route_analytics.sort(
            key=lambda item:
                item["travelUnits"],
            reverse=True
        )

        most_travelled_route = None

        if route_analytics:

            most_travelled_route = (
                route_analytics[0]
            )

        least_travelled_route = None

        if route_analytics:

            least_travelled_route = (
                route_analytics[-1]
            )

        # =====================================================
        # PARCEL TYPE ANALYTICS
        # =====================================================

        parcel_type_data = defaultdict(
            lambda: {
                "bookings": 0,
                "parcels": 0,
                "weight": 0.0,
                "revenue": 0.0
            }
        )

        for parcel in current_parcels:

            status = str(
                parcel.get(
                    "parcelStatus",
                    ""
                )
            ).upper()

            if status not in (
                "CONFIRMED",
                "DELIVERED"
            ):

                continue

            parcel_type = (
                parcel.get(
                    "parcelType",
                    ""
                )
                or "Other"
            )

            weight = (
                AdminAnalyticsService
                .to_float(
                    parcel.get(
                        "weight",
                        0
                    )
                )
            )

            fare = (
                AdminAnalyticsService
                .to_float(
                    parcel.get(
                        "agreedFare",
                        0
                    )
                )
            )

            parcel_type_data[
                parcel_type
            ]["bookings"] += 1

            parcel_type_data[
                parcel_type
            ]["parcels"] += 1

            parcel_type_data[
                parcel_type
            ]["weight"] += weight

            parcel_type_data[
                parcel_type
            ]["revenue"] += fare

        parcel_type_analytics = []

        for parcel_type, data in (
            parcel_type_data.items()
        ):

            parcel_type_analytics.append({

                "parcelType":
                    parcel_type,

                "bookings":
                    data["bookings"],

                "parcels":
                    data["parcels"],

                "weight":
                    round(
                        data["weight"],
                        2
                    ),

                "revenue":
                    round(
                        data["revenue"],
                        2
                    )
            })

        parcel_type_analytics.sort(
            key=lambda item:
                item["parcels"],
            reverse=True
        )

        most_booked_parcel_type = None

        if parcel_type_analytics:

            most_booked_parcel_type = (
                parcel_type_analytics[0]
            )

        # =====================================================
        # PARCEL WEIGHT ANALYTICS
        #
        # Based on ACTUAL parcel weight.
        # =====================================================

        weight_categories = {

            "0-1 kg": {
                "parcels": 0,
                "weight": 0.0,
                "revenue": 0.0
            },

            "1-5 kg": {
                "parcels": 0,
                "weight": 0.0,
                "revenue": 0.0
            },

            "5-10 kg": {
                "parcels": 0,
                "weight": 0.0,
                "revenue": 0.0
            },

            "10+ kg": {
                "parcels": 0,
                "weight": 0.0,
                "revenue": 0.0
            }
        }

        for parcel in current_parcels:

            status = str(
                parcel.get(
                    "parcelStatus",
                    ""
                )
            ).upper()

            if status not in (
                "CONFIRMED",
                "DELIVERED"
            ):

                continue

            weight = (
                AdminAnalyticsService
                .to_float(
                    parcel.get(
                        "weight",
                        0
                    )
                )
            )

            fare = (
                AdminAnalyticsService
                .to_float(
                    parcel.get(
                        "agreedFare",
                        0
                    )
                )
            )

            if weight <= 1:

                category = "0-1 kg"

            elif weight <= 5:

                category = "1-5 kg"

            elif weight <= 10:

                category = "5-10 kg"

            else:

                category = "10+ kg"

            weight_categories[
                category
            ]["parcels"] += 1

            weight_categories[
                category
            ]["weight"] += weight

            weight_categories[
                category
            ]["revenue"] += fare

        parcel_weight_analytics = []

        for category, data in (
            weight_categories.items()
        ):

            parcel_weight_analytics.append({

                "category":
                    category,

                "parcels":
                    data["parcels"],

                "weight":
                    round(
                        data["weight"],
                        2
                    ),

                "revenue":
                    round(
                        data["revenue"],
                        2
                    )
            })

        # =====================================================
        # REVENUE TREND
        # =====================================================

        revenue_trend = (
            AdminAnalyticsService
            .build_revenue_trend(
                rides=current_rides,
                parcels=current_parcels,
                trip_map=trip_map,
                start_date=start_date,
                end_date=end_date
            )
        )

        # =====================================================
        # RECENT BOOKINGS
        # =====================================================

        recent_bookings = (
            AdminAnalyticsService
            .build_recent_activity(
                rides=current_rides,
                parcels=current_parcels,
                trip_map=trip_map
            )
        )

        # =====================================================
        # FINAL RESPONSE
        # =====================================================

        return {

            # -------------------------------------------------
            # FILTER
            # -------------------------------------------------

            "period":
                period,

            "year":
                year,

            "month":
                month,

            "startDate":
                start_date.isoformat(),

            "endDate":
                end_date.isoformat(),

            # -------------------------------------------------
            # BUSINESS SUMMARY
            # -------------------------------------------------

            "totalTrips":
                len(current_trips),

            "previousTrips":
                len(previous_trips),

            "totalBookings":
                total_bookings,

            "confirmedBookings":
                confirmed_bookings,

            "pendingBookings":
                pending_bookings,

            "rejectedBookings":
                rejected_bookings,

            "totalRevenue":
                round(
                    total_revenue,
                    2
                ),

            "averageBookingValue":
                round(
                    average_booking_value,
                    2
                ),

            "revenueChange":
                round(
                    revenue_change,
                    1
                ),

            "bookingsChange":
                round(
                    bookings_change,
                    1
                ),

            # -------------------------------------------------
            # RIDE ANALYTICS
            # -------------------------------------------------

            "rideBookings":
                total_ride_bookings,

            "confirmedRideBookings":
                confirmed_ride_bookings,

            "rideRevenue":
                round(
                    ride_revenue,
                    2
                ),

            "averageRideFare":
                round(
                    average_ride_fare,
                    2
                ),

            "totalPassengers":
                total_passengers,

            "confirmedPassengers":
                confirmed_passengers,

            # -------------------------------------------------
            # SEATS
            # -------------------------------------------------

            "totalSeats":
                total_seats,

            "bookedSeats":
                booked_seats,

            "availableSeats":
                available_seats,

            "overbookedSeats":
                overbooked_seats,

            "seatUtilization":
                round(
                    seat_utilization,
                    1
                ),

            # -------------------------------------------------
            # PARCEL ANALYTICS
            # -------------------------------------------------

            "parcelBookings":
                total_parcel_requests,

            "confirmedParcels":
                confirmed_parcels,

            "deliveredParcels":
                delivered_parcels,

            "pendingParcels":
                pending_parcels,

            "rejectedParcels":
                rejected_parcels,

            "parcelRevenue":
                round(
                    parcel_revenue,
                    2
                ),

            "totalParcels":
                total_parcel_count,

            "totalParcelWeight":
                round(
                    total_parcel_weight,
                    2
                ),

            "confirmedParcelWeight":
                round(
                    confirmed_parcel_weight,
                    2
                ),

            "averageParcelFare":
                round(
                    average_parcel_fare,
                    2
                ),

            # -------------------------------------------------
            # BUSINESS MIX
            # -------------------------------------------------

            "businessMix": {

                "rideBookings":
                    total_ride_bookings,

                "parcelBookings":
                    total_parcel_requests,

                "confirmedRideBookings":
                    confirmed_ride_bookings,

                "confirmedParcels":
                    confirmed_parcels,

                "rideRevenue":
                    round(
                        ride_revenue,
                        2
                    ),

                "parcelRevenue":
                    round(
                        parcel_revenue,
                        2
                    ),

                "totalRevenue":
                    round(
                        total_revenue,
                        2
                    )
            },

            # -------------------------------------------------
            # ROUTES
            # -------------------------------------------------

            "mostTravelledRoute":
                most_travelled_route,

            "leastTravelledRoute":
                least_travelled_route,

            "routeAnalytics":
                route_analytics,

            # -------------------------------------------------
            # PARCEL TYPE
            # -------------------------------------------------

            "mostBookedParcelType":
                most_booked_parcel_type,

            "parcelTypeAnalytics":
                parcel_type_analytics,

            "parcelWeightAnalytics":
                parcel_weight_analytics,

            # -------------------------------------------------
            # GRAPH
            # -------------------------------------------------

            "revenueTrend":
                revenue_trend,

            # -------------------------------------------------
            # RECENT ACTIVITY
            # -------------------------------------------------

            "recentBookings":
                recent_bookings
        }

    # =========================================================
    # DATE RANGE
    # =========================================================

    @staticmethod
    def get_date_range(
        period: str,
        year: int | None = None,
        month: int | None = None
    ):

        today = date.today()

        period = (
            str(period)
            .strip()
            .lower()
        )

        # =====================================================
        # TODAY
        # =====================================================

        if period == "today":

            start_date = today

            end_date = today

            previous_start = (
                today
                - timedelta(days=1)
            )

            previous_end = previous_start

        # =====================================================
        # YESTERDAY
        # =====================================================

        elif period == "yesterday":

            start_date = (
                today
                - timedelta(days=1)
            )

            end_date = start_date

            previous_start = (
                today
                - timedelta(days=2)
            )

            previous_end = previous_start

        # =====================================================
        # CURRENT CALENDAR WEEK
        #
        # MONDAY -> SUNDAY
        # =====================================================

        elif period == "week":

            start_date = (
                today
                - timedelta(
                    days=today.weekday()
                )
            )

            end_date = (
                start_date
                + timedelta(days=6)
            )

            previous_start = (
                start_date
                - timedelta(days=7)
            )

            previous_end = (
                start_date
                - timedelta(days=1)
            )

        # =====================================================
        # CALENDAR MONTH
        # =====================================================

        elif period == "month":

            selected_year = (
                year
                if year is not None
                else today.year
            )

            selected_month = (
                month
                if month is not None
                else today.month
            )

            if (
                selected_year < 2000
                or selected_year > today.year
            ):

                raise ValueError(
                    "Invalid year"
                )

            if (
                selected_month < 1
                or selected_month > 12
            ):

                raise ValueError(
                    "Month must be between 1 and 12"
                )

            start_date = date(
                selected_year,
                selected_month,
                1
            )

            current_month_start = date(
                today.year,
                today.month,
                1
            )

            if start_date > current_month_start:

                raise ValueError(
                    "Future months are not allowed"
                )

            if selected_month == 12:

                next_month = date(
                    selected_year + 1,
                    1,
                    1
                )

            else:

                next_month = date(
                    selected_year,
                    selected_month + 1,
                    1
                )

            end_date = (
                next_month
                - timedelta(days=1)
            )

            previous_end = (
                start_date
                - timedelta(days=1)
            )

            previous_start = (
                previous_end.replace(
                    day=1
                )
            )

        else:

            raise ValueError(
                "Invalid period. "
                "Use today, yesterday, week or month."
            )

        return (
            start_date,
            end_date,
            previous_start,
            previous_end
        )

    # =========================================================
    # DATE PARSER
    # =========================================================

    @staticmethod
    def parse_date(value):

        if not value:
            return None

        if isinstance(value, date):

            return value

        try:

            return date.fromisoformat(
                str(value)[:10]
            )

        except Exception:

            return None

    # =========================================================
    # PARCEL ANALYTICS DATE
    #
    # Confirmed/delivered parcel:
    #     actualDate
    #
    # Pending/rejected parcel:
    #     expectedDate
    #
    # This prevents a delivered parcel from being counted
    # against its old request date.
    # =========================================================

    @staticmethod
    def get_parcel_analytics_date(
        parcel
    ):

        status = str(
            parcel.get(
                "parcelStatus",
                ""
            )
        ).upper()

        if status in (
            "CONFIRMED",
            "DELIVERED"
        ):

            actual_date = (
                AdminAnalyticsService
                .parse_date(
                    parcel.get(
                        "actualDate"
                    )
                )
            )

            if actual_date:

                return actual_date

        return (
            AdminAnalyticsService
            .parse_date(
                parcel.get(
                    "expectedDate"
                )
            )
        )

    # =========================================================
    # PARCEL ROUTE
    # =========================================================

    @staticmethod
    def get_parcel_route(
        parcel
    ):

        # First preference:
        # allocated trip route

        trip_id = parcel.get(
            "tripId"
        )

        if trip_id:

            trip = (
                TripRepository
                .find_by_id(
                    trip_id
                )
            )

            if trip:

                route = (
                    trip.get(
                        "route"
                    )
                )

                if route:

                    return route

        # Second preference:
        # parcel route + direction

        route_id = parcel.get(
            "routeId"
        )

        direction = str(
            parcel.get(
                "direction",
                ""
            )
        ).upper()

        if route_id:

            route = (
                RouteRepository
                .find_by_id(
                    route_id
                )
            )

            if route:

                if direction == "UP":

                    return (
                        route.get(
                            "up",
                            "Unknown Route"
                        )
                        or "Unknown Route"
                    )

                if direction == "DOWN":

                    return (
                        route.get(
                            "down",
                            "Unknown Route"
                        )
                        or "Unknown Route"
                    )

                route_name = (
                    route.get(
                        "routeName"
                    )
                )

                if route_name:

                    return route_name

        return "Unknown Route"

    # =========================================================
    # PERCENTAGE CHANGE
    # =========================================================

    @staticmethod
    def calculate_percentage_change(
        current,
        previous
    ):

        current = float(
            current or 0
        )

        previous = float(
            previous or 0
        )

        if previous == 0:

            if current > 0:

                return 100.0

            return 0.0

        return (
            (
                current - previous
            )
            /
            previous
        ) * 100

    # =========================================================
    # REVENUE TREND
    # =========================================================

    @staticmethod
    def build_revenue_trend(
        rides,
        parcels,
        trip_map,
        start_date,
        end_date
    ):

        daily_data = defaultdict(
            lambda: {

                "revenue": 0.0,

                "rideRevenue": 0.0,

                "parcelRevenue": 0.0,

                "bookings": 0,

                "rideBookings": 0,

                "parcelBookings": 0,

                "passengers": 0,

                "parcels": 0,

                "parcelWeight": 0.0
            }
        )

        # =====================================================
        # RIDE REVENUE
        # =====================================================

        for booking in rides:

            status = str(
                booking.get(
                    "bookingStatus",
                    ""
                )
            ).upper()

            if status != "CONFIRMED":
                continue

            trip_id = str(
                booking.get(
                    "tripId",
                    ""
                )
            )

            trip = trip_map.get(
                trip_id
            )

            if not trip:
                continue

            trip_date = (
                AdminAnalyticsService
                .parse_date(
                    trip.get("date")
                )
            )

            if not trip_date:
                continue

            if not (
                start_date
                <= trip_date
                <= end_date
            ):

                continue

            fare = (
                AdminAnalyticsService
                .to_float(
                    booking.get(
                        "totalFare",
                        0
                    )
                )
            )

            passengers = (
                AdminAnalyticsService
                .to_int(
                    booking.get(
                        "passengerCount",
                        0
                    )
                )
            )

            daily_data[
                trip_date
            ]["revenue"] += fare

            daily_data[
                trip_date
            ]["rideRevenue"] += fare

            daily_data[
                trip_date
            ]["bookings"] += 1

            daily_data[
                trip_date
            ]["rideBookings"] += 1

            daily_data[
                trip_date
            ]["passengers"] += passengers

        # =====================================================
        # PARCEL REVENUE
        # =====================================================

        for parcel in parcels:

            status = str(
                parcel.get(
                    "parcelStatus",
                    ""
                )
            ).upper()

            if status not in (
                "CONFIRMED",
                "DELIVERED"
            ):

                continue

            parcel_date = (
                AdminAnalyticsService
                .get_parcel_analytics_date(
                    parcel
                )
            )

            if not parcel_date:
                continue

            if not (
                start_date
                <= parcel_date
                <= end_date
            ):

                continue

            fare = (
                AdminAnalyticsService
                .to_float(
                    parcel.get(
                        "agreedFare",
                        0
                    )
                )
            )

            weight = (
                AdminAnalyticsService
                .to_float(
                    parcel.get(
                        "weight",
                        0
                    )
                )
            )

            daily_data[
                parcel_date
            ]["revenue"] += fare

            daily_data[
                parcel_date
            ]["parcelRevenue"] += fare

            daily_data[
                parcel_date
            ]["bookings"] += 1

            daily_data[
                parcel_date
            ]["parcelBookings"] += 1

            daily_data[
                parcel_date
            ]["parcels"] += 1

            daily_data[
                parcel_date
            ]["parcelWeight"] += weight

        # =====================================================
        # EVERY DATE MUST EXIST
        #
        # This is important for the graph.
        # =====================================================

        result = []

        current_date = start_date

        while current_date <= end_date:

            data = daily_data[
                current_date
            ]

            result.append({

                "date":
                    current_date.isoformat(),

                "label":
                    current_date.strftime(
                        "%d %b"
                    ),

                "revenue":
                    round(
                        data["revenue"],
                        2
                    ),

                "rideRevenue":
                    round(
                        data["rideRevenue"],
                        2
                    ),

                "parcelRevenue":
                    round(
                        data["parcelRevenue"],
                        2
                    ),

                "bookings":
                    data["bookings"],

                "rideBookings":
                    data["rideBookings"],

                "parcelBookings":
                    data["parcelBookings"],

                "passengers":
                    data["passengers"],

                "parcels":
                    data["parcels"],

                "parcelWeight":
                    round(
                        data["parcelWeight"],
                        2
                    )
            })

            current_date += timedelta(
                days=1
            )

        return result

    # =========================================================
    # RECENT ACTIVITY
    # =========================================================

    @staticmethod
    def build_recent_activity(
        rides,
        parcels,
        trip_map
    ):

        result = []

        # =====================================================
        # RIDES
        # =====================================================

        for booking in rides:

            trip_id = str(
                booking.get(
                    "tripId",
                    ""
                )
            )

            trip = trip_map.get(
                trip_id
            )

            if not trip:
                continue

            passengers = (
                AdminAnalyticsService
                .to_int(
                    booking.get(
                        "passengerCount",
                        0
                    )
                )
            )

            result.append({

                "id":
                    booking.get(
                        "bookingId",
                        ""
                    ),

                "bookingId":
                    booking.get(
                        "bookingId",
                        ""
                    ),

                "route":
                    trip.get(
                        "route",
                        "Unknown Route"
                    ),

                "date":
                    trip.get(
                        "date",
                        "-"
                    ),

                "timeSlot":
                    trip.get(
                        "timeSlot",
                        "-"
                    ),

                "bookingType":
                    "RIDE",

                "quantity":
                    passengers,

                "passengers":
                    passengers,

                "parcelType":
                    "",

                "parcelWeight":
                    0,

                "totalFare":
                    AdminAnalyticsService
                    .to_float(
                        booking.get(
                            "totalFare",
                            0
                        )
                    ),

                "status":
                    booking.get(
                        "bookingStatus",
                        ""
                    )
            })

        # =====================================================
        # PARCELS
        # =====================================================

        for parcel in parcels:

            parcel_date = (
                AdminAnalyticsService
                .get_parcel_analytics_date(
                    parcel
                )
            )

            result.append({

                "id":
                    parcel.get(
                        "parcelId",
                        ""
                    ),

                "bookingId":
                    parcel.get(
                        "parcelId",
                        ""
                    ),

                "route":
                    AdminAnalyticsService
                    .get_parcel_route(
                        parcel
                    ),

                "date":
                    (
                        parcel_date.isoformat()
                        if parcel_date
                        else "-"
                    ),

                "timeSlot":
                    parcel.get(
                        "actualTime",
                        "-"
                    )
                    or "-",

                "bookingType":
                    "PARCEL",

                "quantity":
                    1,

                "passengers":
                    0,

                "parcelType":
                    parcel.get(
                        "parcelType",
                        ""
                    ),

                "parcelWeight":
                    AdminAnalyticsService
                    .to_float(
                        parcel.get(
                            "weight",
                            0
                        )
                    ),

                "totalFare":
                    AdminAnalyticsService
                    .to_float(
                        parcel.get(
                            "agreedFare",
                            0
                        )
                    ),

                "status":
                    parcel.get(
                        "parcelStatus",
                        ""
                    )
            })

        # =====================================================
        # SORT
        # =====================================================

        result.sort(
            key=lambda item: (
                item.get(
                    "date",
                    ""
                ),
                item.get(
                    "timeSlot",
                    ""
                )
            ),
            reverse=True
        )

        return result[:10]

    # =========================================================
    # SAFE NUMBER CONVERSION
    # =========================================================

    @staticmethod
    def to_float(value):

        try:

            return float(
                value or 0
            )

        except (
            TypeError,
            ValueError
        ):

            return 0.0

    @staticmethod
    def to_int(value):

        try:

            return int(
                value or 0
            )

        except (
            TypeError,
            ValueError
        ):

            return 0