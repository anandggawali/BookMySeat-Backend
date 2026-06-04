import uuid

from core.database import users_collection
from core.security import hash_password

admin = {
    "userId": str(uuid.uuid4()),
    "name": "Super Admin",
    "phoneNo": "9999999999",
    "password": hash_password("admin123"),
    "role": "ADMIN"
}

users_collection.insert_one(admin)

print("Admin Created")