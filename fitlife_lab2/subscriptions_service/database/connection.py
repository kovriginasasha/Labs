"""Хранилище данных в памяти (как списки events/users в практическом занятии №7).
Пакет database оставлен для ЛР3: здесь позже появится подключение к настоящей БД.
При перезапуске сервиса все данные сбрасываются."""
from datetime import date, timedelta
from typing import Dict, List

tariffs: List[dict] = [
    {"id": 1, "name": "Месяц", "price": 2500, "duration_days": 30},
    {"id": 2, "name": "Квартал", "price": 6500, "duration_days": 90},
    {"id": 3, "name": "Год", "price": 21000, "duration_days": 365},
]
subscriptions: List[dict] = []
payments: List[dict] = []

_counters: Dict[str, int] = {"subscription": 0, "payment": 0}


def next_id(name: str) -> int:
    """Автоматическая нумерация записей (аналог AUTOINCREMENT)."""
    _counters[name] += 1
    return _counters[name]


def _seed_demo_data() -> None:
    """Демо: у клиента 99 абонемент уже просрочен (срок закончился 10 дней назад),
    но статус ещё 'active' - как будто проверка сроков давно не запускалась."""
    today = date.today()
    sub_id = next_id("subscription")
    subscriptions.append({
        "id": sub_id, "client_id": 99, "tariff_id": 1,
        "start_date": today - timedelta(days=40),
        "end_date": today - timedelta(days=10),
        "status": "active",
    })
    payments.append({
        "id": next_id("payment"), "client_id": 99, "tariff_id": 1,
        "subscription_id": sub_id, "amount": 2500, "status": "approved",
    })


_seed_demo_data()
