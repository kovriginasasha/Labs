from datetime import date, timedelta
from typing import List, Optional

from fastapi import APIRouter, HTTPException, status

from database.connection import next_id, payments, subscriptions, tariffs
from models.subscriptions import PurchaseRequest, Subscription
from services.payment_gateway import charge

subscription_router = APIRouter(tags=["Subscriptions"])


def is_valid(sub: dict, on_date: date) -> bool:
    """Абонемент действует на дату, если он не закрыт и дата попадает в срок.
    Срок проверяется по датам, поэтому просроченный абонемент не сработает,
    даже если статус ещё не успели сменить на expired."""
    return sub["status"] == "active" and sub["start_date"] <= on_date <= sub["end_date"]


@subscription_router.post("/buy", status_code=status.HTTP_201_CREATED)
async def buy_subscription(data: PurchaseRequest) -> dict:
    """Вариант использования 1: оформить и оплатить абонемент."""
    client_id = data.client_id
    tariff = next((t for t in tariffs if t["id"] == data.tariff_id), None)
    if tariff is None:  # А1: тариф не выбран / не существует
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tariff with supplied ID does not exist",
        )

    if not charge(tariff["price"], data.card_token):  # А2: платёж отклонён
        payments.append({
            "id": next_id("payment"), "client_id": client_id, "tariff_id": tariff["id"],
            "subscription_id": None, "amount": tariff["price"], "status": "declined",
        })
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Payment declined, subscription not activated",
        )

    start = date.today()
    end = start + timedelta(days=tariff["duration_days"])  # срок действия по тарифу
    sub = {
        "id": next_id("subscription"), "client_id": client_id, "tariff_id": tariff["id"],
        "start_date": start, "end_date": end, "status": "active",
    }
    subscriptions.append(sub)
    payments.append({
        "id": next_id("payment"), "client_id": client_id, "tariff_id": tariff["id"],
        "subscription_id": sub["id"], "amount": tariff["price"], "status": "approved",
    })
    return {
        "message": "Payment processed, subscription activated",
        "subscription_id": sub["id"],
        "valid_until": end.isoformat(),
    }


@subscription_router.get("/active", response_model=Subscription)
async def retrieve_active_subscription(
    client_id: int = 1,  # номер клиента
    on_date: Optional[date] = None,  # на какую дату проверить (по умолчанию сегодня)
) -> Subscription:
    """Действующий абонемент клиента на дату. Им пользуется сервис записи:
    он передаёт дату занятия, чтобы абонемент не истёк раньше тренировки."""
    check_date = on_date or date.today()
    valid = [s for s in subscriptions if s["client_id"] == client_id and is_valid(s, check_date)]
    if not valid:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client has no active subscription on " + check_date.isoformat(),
        )
    return max(valid, key=lambda s: s["end_date"])


@subscription_router.get("/my", response_model=List[Subscription])
async def retrieve_client_subscriptions(
    client_id: int = 1,  # номер клиента
) -> List[Subscription]:
    """Все абонементы клиента (история), в том числе истёкшие."""
    return [s for s in subscriptions if s["client_id"] == client_id]


@subscription_router.post("/expire")
async def run_expiration() -> dict:
    """Закрывает абонементы, срок которых вышел: статус active -> expired."""
    today = date.today()
    expired = [s for s in subscriptions if s["status"] == "active" and s["end_date"] < today]
    for s in expired:
        s["status"] = "expired"
    return {"message": "Expiration completed", "expired": len(expired),
            "subscription_ids": [s["id"] for s in expired]}
