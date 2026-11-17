from pydantic import BaseModel


class BookingRequest(BaseModel):
    client_id: int
    class_id: int

    model_config = {"json_schema_extra": {"example": {"client_id": 1, "class_id": 1}}}


class Booking(BaseModel):
    id: int
    class_id: int
    client_id: int
    status: str
    created_at: str
