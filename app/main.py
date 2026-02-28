import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routers import history, positions
from app.scheduler import start_scheduler

# ── Logging ───────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("nobi_trade.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)


# ── App ───────────────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup & shutdown events."""
    logger.info("Starting Nobi Trade API...")
    init_db()
    logger.info("Database initialized")
    scheduler = start_scheduler()
    yield
    scheduler.shutdown()
    logger.info("Nobi Trade API stopped")


app = FastAPI(
    title="Nobi Trade API",
    description="Hệ thống cảnh báo & thống kê đầu tư chứng khoán cá nhân",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — cho phép Streamlit (hoặc frontend khác) gọi API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(positions.router)
app.include_router(history.router)


@app.get("/")
def root():
    return {"message": "Nobi Trade API is running"}
