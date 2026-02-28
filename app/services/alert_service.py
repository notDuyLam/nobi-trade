import logging

import requests

from app.config import settings

logger = logging.getLogger(__name__)

TELEGRAM_API_URL = "https://api.telegram.org/bot{token}/sendMessage"


def send_telegram_message(text: str) -> bool:
    """
    Gửi tin nhắn qua Telegram Bot API.

    Returns:
        True nếu gửi thành công, False nếu thất bại.
    """
    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHAT_ID:
        logger.warning("Telegram credentials not configured, skipping alert")
        return False

    url = TELEGRAM_API_URL.format(token=settings.TELEGRAM_BOT_TOKEN)
    payload = {
        "chat_id": settings.TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
    }

    try:
        resp = requests.post(url, json=payload, timeout=10)
        if resp.status_code == 200:
            logger.info("Telegram message sent successfully")
            return True
        else:
            logger.error("Telegram API error: %s %s", resp.status_code, resp.text)
            return False
    except Exception:
        logger.exception("Failed to send Telegram message")
        return False


def format_alert_message(
    symbol: str,
    buy_price: float,
    current_price: float,
    change_pct: float,
    volume: int,
    alert_type: str,
) -> str:
    """Format tin nhắn cảnh báo."""
    if alert_type == "take_profit":
        status = "Chạm ngưỡng CHỐT LỜI ✅"
        emoji = "📈"
    else:
        status = "Chạm ngưỡng CẮT LỖ ❌"
        emoji = "📉"

    return (
        f"🔔 <b>CẢNH BÁO: {symbol}</b>\n"
        f"📊 Trạng thái: {status}\n"
        f"💰 Giá mua: {buy_price:,.0f} VNĐ\n"
        f"💹 Giá hiện tại: {current_price:,.0f} VNĐ\n"
        f"{emoji} Lãi/Lỗ: {change_pct:+.2f}%\n"
        f"📦 Khối lượng: {volume:,}"
    )
