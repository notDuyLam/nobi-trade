from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String

from app.database import Base


class Position(Base):
    """Danh mục cổ phiếu đang giữ."""

    __tablename__ = "positions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    symbol = Column(String(10), nullable=False, index=True)
    buy_price = Column(Float, nullable=False)
    volume = Column(Integer, nullable=False)
    take_profit_pct = Column(Float, nullable=False)
    stop_loss_pct = Column(Float, nullable=False)  # Lưu dương, VD: 5.0 = cắt lỗ -5%
    is_paused_alert = Column(Boolean, default=False, nullable=False)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )


class History(Base):
    """Lịch sử giao dịch đã bán."""

    __tablename__ = "history"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    symbol = Column(String(10), nullable=False, index=True)
    buy_price = Column(Float, nullable=False)
    sell_price = Column(Float, nullable=False)
    volume = Column(Integer, nullable=False)
    profit_loss_value = Column(Float, nullable=False)  # Lời/lỗ VNĐ
    profit_loss_pct = Column(Float, nullable=False)  # % lời/lỗ
    sold_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
