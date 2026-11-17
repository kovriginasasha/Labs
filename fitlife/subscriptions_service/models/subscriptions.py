from datetime import date

from pydantic import BaseModel


class PurchaseRequest(BaseModel):
    client_id: int
    tariff_id: int
    card_token: str

    model_config = {
        "json_schema_extra": {
            "example": {"client_id": 1, "tariff_id": 1, "card_token": "tok_visa_4242"}
        }
    }


class Subscription(BaseModel):
    id: int
    client_id: int
    tariff_id: int
    start_date: date
    end_date: date
    status: str
