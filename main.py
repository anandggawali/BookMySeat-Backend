from fastapi import FastAPI

from routes.auth_routes import router as auth_router
from routes.trip_routes import router as trip_router
from routes.booking_routes import router as booking_router
from routes.admin_routes import router as admin_router
from routes.user_routes import router as user_router
from routes.route_routes import router as route_router

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