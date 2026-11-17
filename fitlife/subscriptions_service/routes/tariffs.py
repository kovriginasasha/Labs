from typing import List

from fastapi import APIRouter

from database.connection import db
from models.tariffs import Tariff

tariff_router = APIRouter(tags=["Tariffs"])


@tariff_router.get("/", response_model=List[Tariff])
def retrieve_tariffs() -> List[Tariff]:
    with db() as conn:
        rows = conn.execute("SELECT * FROM tariffs ORDER BY price").fetchall()
    return [dict(r) for r in rows]
