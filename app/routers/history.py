from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import History
from app.schemas import AnalyticsResponse, HistoryResponse

router = APIRouter(prefix="/api", tags=["History & Analytics"], redirect_slashes=False)

PERIOD_MAP = {
    "1m": timedelta(days=30),
    "3m": timedelta(days=90),
    "6m": timedelta(days=180),
    "1y": timedelta(days=365),
}


def _apply_filters(query, period: str, symbol: str | None):
    """Apply period and symbol filters to a history query."""
    if period != "all" and period in PERIOD_MAP:
        cutoff = datetime.now(timezone.utc) - PERIOD_MAP[period]
        query = query.filter(History.sold_at >= cutoff)
    if symbol:
        query = query.filter(History.symbol == symbol.upper().strip())
    return query


@router.get("/history", response_model=list[HistoryResponse])
def list_history(
    period: str = Query(default="1m", pattern="^(1m|3m|6m|1y|all)$"),
    symbol: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    """Lấy lịch sử giao dịch theo bộ lọc."""
    query = db.query(History)
    query = _apply_filters(query, period, symbol)
    return query.order_by(History.sold_at.desc()).all()


@router.get("/analytics", response_model=AnalyticsResponse)
def get_analytics(
    period: str = Query(default="1m", pattern="^(1m|3m|6m|1y|all)$"),
    symbol: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    """Thống kê tổng lời/lỗ và win rate."""
    query = db.query(History)
    query = _apply_filters(query, period, symbol)
    records = query.all()

    total_profit_loss = sum(r.profit_loss_value for r in records)
    winning = [r for r in records if r.profit_loss_value > 0]
    losing = [r for r in records if r.profit_loss_value <= 0]
    total = len(records)
    win_rate = (len(winning) / total * 100) if total > 0 else 0.0

    return AnalyticsResponse(
        total_profit_loss=round(total_profit_loss, 0),
        total_trades=total,
        winning_trades=len(winning),
        losing_trades=len(losing),
        win_rate=round(win_rate, 2),
    )


@router.delete("/history/{history_id}", status_code=204)
def delete_history(history_id: int, db: Session = Depends(get_db)):
    """Xóa 1 record lịch sử giao dịch."""
    record = db.query(History).filter(History.id == history_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="History record not found")
    db.delete(record)
    db.commit()

