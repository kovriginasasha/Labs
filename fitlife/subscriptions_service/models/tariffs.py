from pydantic import BaseModel


class Tariff(BaseModel):
    id: int
    name: str
    price: float
    duration_days: int

    model_config = {
        "json_schema_extra": {
            "example": {"id": 1, "name": "Месяц", "price": 2500, "duration_days": 30}
        }
    }
