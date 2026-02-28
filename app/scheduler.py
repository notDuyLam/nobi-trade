import logging
from datetime import datetime

import pytz
from apscheduler.schedulers.background import BackgroundScheduler

from app.database import SessionLocal
from app.models import Position
from app.services.alert_service import format_alert_message, send_telegram_message
from app.services.price_service import get_current_prices

logger = logging.getLogger(__name__)

VN_TZ = pytz.timezone("Asia/Ho_Chi_Minh")


def is_trading_hours() -> bool:
    """Kiểm tra có đang trong giờ giao dịch sàn VN không."""
    now = datetime.now(VN_TZ)
    weekday = now.weekday()  # 0=Mon, 6=Sun

    # Chỉ T2-T6
    if weekday > 4:
        return False

    current_time = now.time()
    morning = (now.replace(hour=9, minute=0).time(), now.replace(hour=11, minute=30).time())
    afternoon = (now.replace(hour=13, minute=0).time(), now.replace(hour=14, minute=45).time())

    return (morning[0] <= current_time <= morning[1]) or (
        afternoon[0] <= current_time <= afternoon[1]
    )


def check_prices_and_alert():
    """Job: quét giá và gửi cảnh báo nếu chạm ngưỡng."""
    if not is_trading_hours():
        logger.debug("Outside trading hours, skipping price check")
        return

    logger.info("Running price check job...")
    db = SessionLocal()

    try:
        # Lấy positions chưa tạm dừng cảnh báo
        positions = (
            db.query(Position).filter(Position.is_paused_alert == False).all()  # noqa: E712
        )
        if not positions:
            logger.info("No active positions to check")
            return

        symbols = list(set(p.symbol for p in positions))
        prices = get_current_prices(symbols)

        for pos in positions:
            current_price = prices.get(pos.symbol)
            if current_price is None:
                logger.warning("Could not get price for %s, skipping", pos.symbol)
                continue

            change_pct = ((current_price - pos.buy_price) / pos.buy_price) * 100

            if change_pct >= pos.take_profit_pct:
                msg = format_alert_message(
                    symbol=pos.symbol,
                    buy_price=pos.buy_price,
                    current_price=current_price,
                    change_pct=change_pct,
                    volume=pos.volume,
                    alert_type="take_profit",
                )
                send_telegram_message(msg)
                logger.info("Take profit alert sent for %s (%.2f%%)", pos.symbol, change_pct)

            elif change_pct <= -pos.stop_loss_pct:
                msg = format_alert_message(
                    symbol=pos.symbol,
                    buy_price=pos.buy_price,
                    current_price=current_price,
                    change_pct=change_pct,
                    volume=pos.volume,
                    alert_type="stop_loss",
                )
                send_telegram_message(msg)
                logger.info("Stop loss alert sent for %s (%.2f%%)", pos.symbol, change_pct)
    except Exception:
        logger.exception("Error in price check job")
    finally:
        db.close()


def start_scheduler():
    """Khởi tạo và bắt đầu APScheduler."""
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        check_prices_and_alert,
        "interval",
        minutes=5,
        id="price_check_job",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Scheduler started — price check every 5 minutes")
    return scheduler
