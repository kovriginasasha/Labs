from typing import List

from fastapi import APIRouter

from database.connection import tariffs
from models.tariffs import Tariff

tariff_router = APIRouter(tags=["Tariffs"])


@tariff_router.get("/", response_model=List[Tariff])
async def retrieve_tariffs() -> List[Tariff]:
    return tariffs
