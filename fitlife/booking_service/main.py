from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from database.connection import init_db
from routes.bookings import booking_router
from routes.classes import class_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="FitLife: сервис записи на тренировки", lifespan=lifespan)

# Register routes
app.include_router(class_router, prefix="/classes")
app.include_router(booking_router, prefix="/bookings")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)
