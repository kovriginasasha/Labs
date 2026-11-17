from datetime import datetime
from typing import List

from fastapi import APIRouter, HTTPException, status

from database.connection import bookings, classes, next_id
from models.bookings import Booking, BookingRequest
from routes.classes import free_places
from services.subscriptions_client import (
    SubscriptionServiceUnavailable,
    has_active_subscription,
)

booking_router = APIRouter(tags=["Bookings"])


@booking_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_booking(
    data: BookingRequest,
) -> dict:
    """Вариант использования 2: записаться на тренировку."""
    client_id = data.client_id
    fit_class = next((c for c in classes if c["id"] == data.class_id), None)
    if fit_class is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Class with supplied ID does not exist",
        )

    if any(b for b in bookings if b["class_id"] == data.class_id
           and b["client_id"] == client_id and b["status"] == "active"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Client is already booked on this class",
        )

    if free_places(fit_class) <= 0:  # А1: нет свободных мест
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No free places on this class",
        )

    try:  # проверка абонемента в другом микросервисе - на ДАТУ ЗАНЯТИЯ
        has_subscription = has_active_subscription(client_id, fit_class["starts_at"].date())
    except SubscriptionServiceUnavailable:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Subscription service is unavailable, try again later",
        )
    if not has_subscription:  # А2: абонемента нет, он истёк или истечёт до занятия
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No subscription valid on the class date: buy or renew it first",
        )

    booking = {
        "id": next_id("booking"), "class_id": data.class_id, "client_id": client_id,
        "status": "active", "created_at": datetime.now(),
    }
    bookings.append(booking)
    return {"message": "Booking created successfully", "booking_id": booking["id"]}


@booking_router.get("/my", response_model=List[Booking])
async def retrieve_my_bookings(client_id: int = 1) -> List[Booking]:
    return [b for b in bookings if b["client_id"] == client_id]
