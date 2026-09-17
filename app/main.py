from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes.categories import router as categories_router
from app.api.routes.products import router as products_router
from app.api.routes.purchase_orders import router as purchase_orders_router
from app.api.routes.restocks import router as restocks_router
from app.api.routes.sales import router as sales_router
from app.api.routes.stats import router as stats_router
from app.api.routes.suppliers import router as suppliers_router
from app.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Liquor Management", lifespan=lifespan)

app.include_router(categories_router)
app.include_router(products_router)
app.include_router(purchase_orders_router)
app.include_router(restocks_router)
app.include_router(sales_router)
app.include_router(stats_router)
app.include_router(suppliers_router)

app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/")
def index() -> FileResponse:
    return FileResponse("app/static/index.html")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}