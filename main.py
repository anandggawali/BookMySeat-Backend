from fastapi import FastAPI
import core.firebase

from routes.auth_routes import router as auth_router
from routes.trip_routes import router as trip_router
from routes.booking_routes import router as booking_router
from routes.admin_routes import router as admin_router
from routes.user_routes import router as user_router
from routes.route_routes import router as route_router
from routes.test_routes import router as test_router
from routes.notification_routes import router as notification_router
from routes.config_routes import router as configuration_router

app = FastAPI(
    title="Book My Seat API",
    version="1.0.0"
)

app.include_router(auth_router)
app.include_router(trip_router)
app.include_router(booking_router)
app.include_router(admin_router)
app.include_router(user_router)
app.include_router(route_router)
app.include_router(test_router)
app.include_router(notification_router)
app.include_router(configuration_router)
# app.include_router(
#     user_router,
#     prefix="/api/users",
#     tags=["Users"]
# )

from core.database import db

@app.get("/db-test")
def db_test():
    db.command("ping")
    return {"message": "MongoDB Connected"}
@app.get("/")
def home():
    return {
        "message": "Book My Seat Backend Running"
    }