from typing import List

from fastapi import APIRouter, HTTPException, status

from database.connection import db, now_iso
from models.bookings import Booking, BookingRequest
from services.subscriptions_client import (
    SubscriptionServiceUnavailable,
    has_active_subscription,
)

booking_router = APIRouter(tags=["Bookings"])


@booking_router.post("/", status_code=status.HTTP_201_CREATED)
def create_booking(data: BookingRequest) -> dict:
    """Вариант использования 2: записаться на тренировку."""
    with db() as conn:
        fit_class = conn.execute(
            "SELECT * FROM classes WHERE id = ?", (data.class_id,)
        ).fetchone()
        if fit_class is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Class with supplied ID does not exist",
            )

        already = conn.execute(
            "SELECT 1 FROM bookings WHERE class_id = ? AND client_id = ? AND status = 'active'",
            (data.class_id, data.client_id),
        ).fetchone()
        if already:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Client is already booked on this class",
            )

        booked = conn.execute(
            "SELECT COUNT(*) FROM bookings WHERE class_id = ? AND status = 'active'",
            (data.class_id,),
        ).fetchone()[0]
        if booked >= fit_class["capacity"]:  # А1: нет свободных мест
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No free places on this class",
            )

        try:  # проверка абонемента в другом микросервисе
            has_subscription = has_active_subscription(data.client_id)
        except SubscriptionServiceUnavailable:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Subscription service is unavailable, try again later",
            )
        if not has_subscription:  # А2: абонемент недействителен
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No active subscription: buy or renew it first",
            )

        cur = conn.execute(
            "INSERT INTO bookings (class_id, client_id, status, created_at)"
            " VALUES (?, ?, 'active', ?)",
            (data.class_id, data.client_id, now_iso()),
        )
    return {"message": "Booking created successfully", "booking_id": cur.lastrowid}


@booking_router.get("/client/{client_id}", response_model=List[Booking])
def retrieve_client_bookings(client_id: int) -> List[Booking]:
    with db() as conn:
        rows = conn.execute(
            "SELECT * FROM bookings WHERE client_id = ? ORDER BY created_at DESC",
            (client_id,),
        ).fetchall()
    return [dict(r) for r in rows]
