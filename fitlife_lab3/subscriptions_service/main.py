from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from database.connection import conn
from routes.subscriptions import subscription_router
from routes.tariffs import tariff_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    conn()  # при запуске создаём БД и таблицы
    yield


app = FastAPI(title="FitLife: сервис абонементов и оплаты", lifespan=lifespan)

# Register routes
app.include_router(tariff_router, prefix="/tariffs")
app.include_router(subscription_router, prefix="/subscriptions")


@app.get("/", include_in_schema=False)
async def home():
    return RedirectResponse(url="/tariffs/")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
