import uvicorn
from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse

from routes.bookings import booking_router
from routes.classes import class_router

app = FastAPI(title="FitLife: сервис записи на тренировки", docs_url=None)

# Register routes
app.include_router(class_router, prefix="/classes")
app.include_router(booking_router, prefix="/bookings")


@app.get("/docs", include_in_schema=False)
async def custom_docs():
    html = get_swagger_ui_html(openapi_url="/openapi.json", title="FitLife").body.decode()
    css = "<style>.parameter__type, .parameter__in { display: none; }</style>"
    return HTMLResponse(html.replace("</head>", css + "</head>"))


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)