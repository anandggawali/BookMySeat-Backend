from pymongo import MongoClient

from core.config import settings


client = MongoClient(
    settings.MONGO_URI,
    serverSelectionTimeoutMS=5000
)

db = client[settings.DATABASE_NAME]


users_collection = db["users"]

trips_collection = db["trips"]

bookings_collection = db["bookings"]

routes_collection = db["routes"]

notifications_collection = db["notifications"]

weight_categories_collection = db["weight_categories"]

parcel_fares_collection = db["parcel_fares"]

parcels_collection = db["parcels"]
# config_collection = db["configuration"]
#
# rejection_collection = db["reject_reason"]
#
# booking_rules_collection = db["Booking_rules"]