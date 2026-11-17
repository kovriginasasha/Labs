from typing import List

from fastapi import APIRouter

from database.connection import bookings, classes
from models.classes import FitClass

class_router = APIRouter(tags=["Classes"])


def free_places(fit_class: dict) -> int:
    booked = sum(1 for b in bookings
                 if b["class_id"] == fit_class["id"] and b["status"] == "active")
    return fit_class["capacity"] - booked


@class_router.get("/", response_model=List[FitClass])
async def retrieve_classes() -> List[FitClass]:
    return [{**c, "free_places": free_places(c)}
            for c in sorted(classes, key=lambda c: c["starts_at"])]
