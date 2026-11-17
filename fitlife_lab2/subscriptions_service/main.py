import uvicorn
from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse

from routes.subscriptions import subscription_router
from routes.tariffs import tariff_router

app = FastAPI(title="FitLife: сервис абонементов и оплаты", docs_url=None)

# Register routes
app.include_router(tariff_router, prefix="/tariffs")
app.include_router(subscription_router, prefix="/subscriptions")


@app.get("/docs", include_in_schema=False)
async def custom_docs():
    html = get_swagger_ui_html(openapi_url="/openapi.json", title="FitLife").body.decode()
    css = "<style>.parameter__type, .parameter__in { display: none; }</style>"
    return HTMLResponse(html.replace("</head>", css + "</head>"))


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)