from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
import os
import requests
from dotenv import load_dotenv
from passlib.context import CryptContext  # For password hashing

load_dotenv()

app = FastAPI()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Database connection
try:
    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
    )
except psycopg2.OperationalError as e:
    raise Exception(f"Failed to connect to the database: {e}")

# URLs for other services
EVENT_SERVICE_URL = "http://localhost:8001"  # Event Service URL
BOOKING_SERVICE_URL = "http://localhost:8002"  # Booking Service URL

class User(BaseModel):
    name: str
    email: str
    password: str

class BookingRequest(BaseModel):
    user_id: int
    event_id: int
    tickets: int

@app.post("/register")
def register(user: User):
    cursor = conn.cursor()
    try:
        # Hash the password before storing it
        hashed_password = pwd_context.hash(user.password)
        
        # Insert the user into the database
        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
            (user.name, user.email, hashed_password)
        )
        conn.commit()
        return {"message": "User registered successfully"}
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        raise HTTPException(status_code=400, detail="Email already exists")
    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        cursor.close()

@app.post("/login")
def login(user: User):
    cursor = conn.cursor()
    try:
        # Fetch the user from the database
        cursor.execute("SELECT id, password FROM users WHERE email = %s", (user.email,))
        db_user = cursor.fetchone()
        
        # Verify the password
        if not db_user or not pwd_context.verify(user.password, db_user[1]):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        return {"message": "Login successful", "user_id": db_user[0]}
    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        cursor.close()

@app.get("/users/{user_id}")
def get_user(user_id: int):
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, name, email FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return {"user_id": user[0], "name": user[1], "email": user[2]}
    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        cursor.close()

@app.get("/events")
def get_events():
    try:
        response = requests.get(f"{EVENT_SERVICE_URL}/events")
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail="Failed to fetch events")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error connecting to Event Service: {e}")

@app.post("/bookings")
def create_booking(booking: BookingRequest):
    try:
        response = requests.post(
            f"{BOOKING_SERVICE_URL}/bookings",
            json={"user_id": booking.user_id, "event_id": booking.event_id, "tickets": booking.tickets}
        )
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail="Failed to create booking")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error connecting to Booking Service: {e}")