from datetime import datetime

from pydantic import BaseModel


class FitClass(BaseModel):
    id: int
    title: str
    trainer: str
    starts_at: datetime
    capacity: int
    free_places: int

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1, "title": "Йога", "trainer": "Иванова А.",
                "starts_at": "2026-11-10T10:00:00", "capacity": 10, "free_places": 10,
            }
        }
    }
