from sqlalchemy.orm import Session

from app.models import History, Position


def sell_position(db: Session, position_id: int, sell_price: float) -> History:
    """
    Bán position: tính lời/lỗ, tạo history, xóa position.

    Returns:
        History record vừa tạo.
    Raises:
        ValueError nếu position không tồn tại.
    """
    position = db.query(Position).filter(Position.id == position_id).first()
    if not position:
        raise ValueError(f"Position {position_id} not found")

    profit_loss_value = (sell_price - position.buy_price) * position.volume
    profit_loss_pct = ((sell_price - position.buy_price) / position.buy_price) * 100

    history = History(
        symbol=position.symbol,
        buy_price=position.buy_price,
        sell_price=sell_price,
        volume=position.volume,
        profit_loss_value=profit_loss_value,
        profit_loss_pct=round(profit_loss_pct, 2),
    )
    db.add(history)
    db.delete(position)
    db.commit()
    db.refresh(history)
    return history
