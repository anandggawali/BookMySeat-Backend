from typing import List, Optional

from pydantic import BaseModel


class RevenuePoint(BaseModel):

    label: str

    revenue: float

    bookings: int


class RouteAnalytics(BaseModel):

    route: str

    bookings: int

    revenue: float


class RecentBookingAnalytics(BaseModel):

    bookingId: str

    route: str

    date: str

    timeSlot: str

    userName: str

    bookingType: str

    quantity: int

    totalFare: float

    status: str


class AdminAnalyticsResponse(BaseModel):

    period: str

    totalTrips: int

    totalBookings: int

    confirmedBookings: int
    pendingBookings: int
    rejectedBookings: int

    totalSeats: int
    bookedSeats: int

    seatUtilization: float

    totalRevenue: float
    averageFare: float

    revenueChange: float
    bookingsChange: float

    mostTravelledRoute: Optional[RouteAnalytics] = None

    leastTravelledRoute: Optional[RouteAnalytics] = None

    revenueTrend: List[RevenuePoint] = []

    recentBookings: List[RecentBookingAnalytics] = []