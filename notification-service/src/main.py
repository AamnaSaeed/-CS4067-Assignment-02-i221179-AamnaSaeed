from fastapi import FastAPI
from pydantic import BaseModel
import pika
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

class Notification(BaseModel):
    booking_id: int
    user_email: str
    status: str

@app.post("/notifications")
def send_notification(notification: Notification):
    # Simulate sending an email/SMS
    print(f"Sending notification to {notification.user_email}: Booking {notification.booking_id} is {notification.status}")
    return {"message": "Notification sent successfully"}