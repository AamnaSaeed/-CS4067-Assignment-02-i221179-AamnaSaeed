from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
import os
import requests  # For making HTTP requests to other services
import pika  # For RabbitMQ communication
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

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

# RabbitMQ configuration
RABBITMQ_HOST = "localhost"
RABBITMQ_QUEUE = "booking_confirmation"

class Booking(BaseModel):
    user_id: int
    event_id: int
    tickets: int

# Function to check event availability
def check_event_availability(event_id: int):
    try:
        response = requests.get(f"{EVENT_SERVICE_URL}/events/{event_id}/availability")
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail="Failed to check event availability")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error connecting to Event Service: {e}")

# Function to publish booking confirmation to RabbitMQ
def publish_booking_confirmation(booking_id: int, user_email: str, status: str):
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
        channel = connection.channel()
        channel.queue_declare(queue=RABBITMQ_QUEUE)
        message = {
            "booking_id": booking_id,
            "user_email": user_email,
            "status": status
        }
        channel.basic_publish(exchange='', routing_key=RABBITMQ_QUEUE, body=str(message))
        connection.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error publishing to RabbitMQ: {e}")

@app.post("/bookings")
def create_booking(booking: Booking):
    cursor = conn.cursor()

    # Step 1: Check event availability
    availability = check_event_availability(booking.event_id)
    if not availability.get("available", False):
        raise HTTPException(status_code=400, detail="Event is not available")

    # Step 2: Mock payment processing (since there's no Payment Gateway)
    # Assume payment is always successful for simplicity
    payment_successful = True
    if not payment_successful:
        raise HTTPException(status_code=400, detail="Payment failed")

    # Step 3: Create the booking
    try:
        cursor.execute(
            "INSERT INTO bookings (user_id, event_id, tickets, status) VALUES (%s, %s, %s, %s)",
            (booking.user_id, booking.event_id, booking.tickets, "CONFIRMED")
        )
        conn.commit()
        booking_id = cursor.lastrowid  # Get the ID of the newly created booking

        # Step 4: Publish booking confirmation to RabbitMQ
        user_email = "user@example.com"  # Replace with actual user email (fetch from User Service if needed)
        publish_booking_confirmation(booking_id, user_email, "CONFIRMED")

        return {"message": "Booking created successfully", "booking_id": booking_id}
    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@app.get("/bookings/{booking_id}")
def get_booking(booking_id: int):
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM bookings WHERE id = %s", (booking_id,))
        booking = cursor.fetchone()
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        return {
            "booking_id": booking[0],
            "user_id": booking[1],
            "event_id": booking[2],
            "tickets": booking[3],
            "status": booking[4]
        }
    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")