from typing import List

from fastapi import APIRouter

from database.connection import db
from models.classes import FitClass

class_router = APIRouter(tags=["Classes"])


@class_router.get("/", response_model=List[FitClass])
def retrieve_classes() -> List[FitClass]:
    with db() as conn:
        rows = conn.execute(
            "SELECT c.*, c.capacity - COUNT(b.id) AS free_places"
            " FROM classes c"
            " LEFT JOIN bookings b ON b.class_id = c.id AND b.status = 'active'"
            " GROUP BY c.id ORDER BY c.starts_at"
        ).fetchall()
    return [dict(r) for r in rows]
