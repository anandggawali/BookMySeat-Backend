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

# config_collection = db["configuration"]
#
# rejection_collection = db["reject_reason"]
#
# booking_rules_collection = db["Booking_rules"]