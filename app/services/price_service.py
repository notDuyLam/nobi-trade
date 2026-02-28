import logging

from vnstock import Vnstock

logger = logging.getLogger(__name__)


def get_current_prices(symbols: list[str]) -> dict[str, float | None]:
    """
    Lấy giá khớp lệnh hiện tại cho danh sách mã CP.

    Returns:
        Dict mapping symbol -> giá hiện tại (None nếu không lấy được).
    """
    prices: dict[str, float | None] = {}

    for symbol in symbols:
        try:
            stock = Vnstock().stock(symbol=symbol, source="VCI")
            df = stock.quote.history(start="2025-01-01", end="2030-12-31", interval="1D")
            if df is not None and not df.empty:
                # Lấy giá đóng cửa ngày gần nhất
                prices[symbol] = float(df.iloc[-1]["close"])
            else:
                logger.warning("No price data for %s", symbol)
                prices[symbol] = None
        except Exception:
            logger.exception("Error fetching price for %s", symbol)
            prices[symbol] = None

    return prices
