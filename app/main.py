from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import init_db
from app.routers import history, positions


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup & shutdown events."""
    init_db()
    yield


app = FastAPI(
    title="Nobi Trade API",
    description="Hệ thống cảnh báo & thống kê đầu tư chứng khoán cá nhân",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(positions.router)
app.include_router(history.router)


@app.get("/")
def root():
    return {"message": "Nobi Trade API is running"}
