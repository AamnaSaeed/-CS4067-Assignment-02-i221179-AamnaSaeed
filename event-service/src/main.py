from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
import os
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

class Event(BaseModel):
    name: str
    date: str
    location: str

class EventAvailabilityResponse(BaseModel):
    event_id: int
    available: bool

@app.post("/events")
def create_event(event: Event):
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO events (name, date, location) VALUES (%s, %s, %s)", 
                       (event.name, event.date, event.location))
        conn.commit()
        return {"message": "Event created successfully"}
    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@app.get("/events")
def get_events():
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM events")
        events = cursor.fetchall()
        return [{"id": event[0], "name": event[1], "date": event[2], "location": event[3]} for event in events]
    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

# New endpoint to check event availability
@app.get("/events/{event_id}/availability")
def check_event_availability(event_id: int):
    cursor = conn.cursor()
    try:
        # Check if the event exists and has available tickets
        cursor.execute("SELECT * FROM events WHERE id = %s", (event_id,))
        event = cursor.fetchone()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")

        # Mock logic to check availability (e.g., assume all events are available)
        available = True  # Replace with actual logic to check availability

        return {"event_id": event_id, "available": available}
    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")