from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ── Position ──────────────────────────────────────────────


class PositionCreate(BaseModel):
    symbol: str = Field(..., max_length=10, examples=["VNM"])
    buy_price: float = Field(..., gt=0, examples=[80000])
    volume: int = Field(..., gt=0, examples=[100])
    take_profit_pct: float = Field(..., gt=0, examples=[5.0])
    stop_loss_pct: float = Field(..., gt=0, examples=[3.0])


class PositionResponse(BaseModel):
    id: int
    symbol: str
    buy_price: float
    volume: int
    take_profit_pct: float
    stop_loss_pct: float
    is_paused_alert: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class SellRequest(BaseModel):
    sell_price: float = Field(..., gt=0, examples=[85000])


# ── History ───────────────────────────────────────────────


class HistoryResponse(BaseModel):
    id: int
    symbol: str
    buy_price: float
    sell_price: float
    volume: int
    profit_loss_value: float
    profit_loss_pct: float
    sold_at: datetime

    model_config = {"from_attributes": True}


# ── Analytics ─────────────────────────────────────────────


class AnalyticsResponse(BaseModel):
    total_profit_loss: float  # Tổng lời/lỗ VNĐ
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float  # %


# ── Query params ──────────────────────────────────────────


class HistoryFilter(BaseModel):
    period: str = Field(default="1m", pattern="^(1m|3m|6m|1y|all)$")
    symbol: Optional[str] = None
