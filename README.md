# BookMySeat Backend

FastAPI + MongoDB Atlas backend for intercity shared cab seat booking.

## Features

- User Registration
- User Login (JWT)
- Role Based Access (Admin / Member)
- Trip Creation
- Trip Search
- Seat Booking
- Booking Confirmation
- Dynamic Seat Availability

## Tech Stack

- FastAPI
- MongoDB Atlas
- JWT Authentication
- Python
- Oracle Cloud (Deployment)

## Run

```bash
pip install -r requirements.txt

uvicorn main:app --reload
```

Open:

http://127.0.0.1:8000/docs