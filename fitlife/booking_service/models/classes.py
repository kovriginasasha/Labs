from pydantic import BaseModel


class FitClass(BaseModel):
    id: int
    title: str
    trainer: str
    starts_at: str
    capacity: int
    free_places: int

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1, "title": "Йога", "trainer": "Иванова А.",
                "starts_at": "2026-10-20T10:00", "capacity": 10, "free_places": 10,
            }
        }
    }
