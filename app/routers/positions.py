from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Position
from app.schemas import HistoryResponse, PositionCreate, PositionResponse, SellRequest
from app.services.trade_service import sell_position

router = APIRouter(prefix="/api/positions", tags=["Positions"])


@router.post("/", response_model=PositionResponse, status_code=201)
def create_position(payload: PositionCreate, db: Session = Depends(get_db)):
    """Thêm mã cổ phiếu mới vào danh mục."""
    position = Position(
        symbol=payload.symbol.upper().strip(),
        buy_price=payload.buy_price,
        volume=payload.volume,
        take_profit_pct=payload.take_profit_pct,
        stop_loss_pct=payload.stop_loss_pct,
    )
    db.add(position)
    db.commit()
    db.refresh(position)
    return position


@router.get("/", response_model=list[PositionResponse])
def list_positions(db: Session = Depends(get_db)):
    """Lấy danh sách tất cả cổ phiếu đang giữ."""
    return db.query(Position).order_by(Position.created_at.desc()).all()


@router.get("/{position_id}", response_model=PositionResponse)
def get_position(position_id: int, db: Session = Depends(get_db)):
    """Lấy chi tiết 1 position."""
    position = db.query(Position).filter(Position.id == position_id).first()
    if not position:
        raise HTTPException(status_code=404, detail="Position not found")
    return position


@router.patch("/{position_id}/toggle-alert", response_model=PositionResponse)
def toggle_alert(position_id: int, db: Session = Depends(get_db)):
    """Bật/tắt cảnh báo cho position."""
    position = db.query(Position).filter(Position.id == position_id).first()
    if not position:
        raise HTTPException(status_code=404, detail="Position not found")
    position.is_paused_alert = not position.is_paused_alert
    db.commit()
    db.refresh(position)
    return position


@router.delete("/{position_id}", status_code=204)
def delete_position(position_id: int, db: Session = Depends(get_db)):
    """Xóa position."""
    position = db.query(Position).filter(Position.id == position_id).first()
    if not position:
        raise HTTPException(status_code=404, detail="Position not found")
    db.delete(position)
    db.commit()


@router.post("/{position_id}/sell", response_model=HistoryResponse)
def sell(position_id: int, payload: SellRequest, db: Session = Depends(get_db)):
    """Bán position: tính lời/lỗ, chuyển sang history."""
    try:
        history = sell_position(db, position_id, payload.sell_price)
        return history
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
