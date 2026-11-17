"""Хранилище данных в памяти (как список events в практическом занятии №7).
Пакет database оставлен для ЛР3: здесь позже появится подключение к настоящей БД.
При перезапуске сервиса все данные сбрасываются."""
from datetime import datetime, timedelta
from typing import Dict, List

classes: List[dict] = []
bookings: List[dict] = []

_counters: Dict[str, int] = {"class": 0, "booking": 0}


def next_id(name: str) -> int:
    """Автоматическая нумерация записей (аналог AUTOINCREMENT)."""
    _counters[name] += 1
    return _counters[name]


def _seed_classes() -> None:
    base = datetime.now().replace(minute=0, second=0, microsecond=0) + timedelta(days=1)
    demo = [
        ("Йога", "Иванова А.", base, 10),
        ("Силовая тренировка", "Петров С.", base + timedelta(hours=2), 2),  # всего 2 места
        ("Кроссфит", "Сидоров Д.", base + timedelta(hours=4), 8),
        ("Йога (через 60 дней)", "Иванова А.", base + timedelta(days=60), 10),  # после срока месячного абонемента
    ]
    for title, trainer, starts_at, capacity in demo:
        classes.append({"id": next_id("class"), "title": title, "trainer": trainer,
                        "starts_at": starts_at, "capacity": capacity})


_seed_classes()
