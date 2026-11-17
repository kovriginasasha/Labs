from datetime import date, timedelta

from fastapi import APIRouter, HTTPException, status

from database.connection import db, now_iso
from models.subscriptions import PurchaseRequest, Subscription
from services.payment_gateway import charge

subscription_router = APIRouter(tags=["Subscriptions"])


@subscription_router.post("/buy", status_code=status.HTTP_201_CREATED)
def buy_subscription(data: PurchaseRequest) -> dict:
    """Вариант использования 1: оформить и оплатить абонемент."""
    declined = False
    with db() as conn:
        tariff = conn.execute(
            "SELECT * FROM tariffs WHERE id = ?", (data.tariff_id,)
        ).fetchone()
        if tariff is None:  # А1: тариф не выбран / не существует
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tariff with supplied ID does not exist",
            )

        if not charge(tariff["price"], data.card_token):  # А2: платёж отклонён
            declined = True
            conn.execute(
                "INSERT INTO payments (client_id, tariff_id, amount, status, created_at)"
                " VALUES (?, ?, ?, 'declined', ?)",
                (data.client_id, tariff["id"], tariff["price"], now_iso()),
            )
        else:
            start = date.today()
            end = start + timedelta(days=tariff["duration_days"])
            cur = conn.execute(
                "INSERT INTO subscriptions (client_id, tariff_id, start_date, end_date, status)"
                " VALUES (?, ?, ?, ?, 'active')",
                (data.client_id, tariff["id"], start.isoformat(), end.isoformat()),
            )
            sub_id = cur.lastrowid
            conn.execute(
                "INSERT INTO payments (client_id, tariff_id, subscription_id, amount, status, created_at)"
                " VALUES (?, ?, ?, ?, 'approved', ?)",
                (data.client_id, tariff["id"], sub_id, tariff["price"], now_iso()),
            )

    if declined:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Payment declined, subscription not activated",
        )
    return {
        "message": "Payment processed, subscription activated",
        "subscription_id": sub_id,
        "valid_until": end.isoformat(),
    }


@subscription_router.get("/client/{client_id}/active", response_model=Subscription)
def retrieve_active_subscription(client_id: int) -> Subscription:
    """Нужен сервису записи: есть ли у клиента действующий абонемент."""
    with db() as conn:
        row = conn.execute(
            "SELECT * FROM subscriptions"
            " WHERE client_id = ? AND status = 'active' AND end_date >= ?"
            " ORDER BY end_date DESC LIMIT 1",
            (client_id, date.today().isoformat()),
        ).fetchone()
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client has no active subscription",
        )
    return dict(row)
