import httpx
import pandas as pd
import streamlit as st

# ── Config ────────────────────────────────────────────────

st.set_page_config(
    page_title="Nobi Trade",
    page_icon="📈",
    layout="wide",
)

# API base URL — đổi khi deploy
import os
from dotenv import load_dotenv

load_dotenv()
API_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


# ── Helper ────────────────────────────────────────────────


def api_get(path: str, params: dict | None = None):
    try:
        r = httpx.get(f"{API_URL}{path}", params=params, timeout=10, follow_redirects=True)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"Lỗi kết nối API: {e}")
        return None


def api_post(path: str, json: dict | None = None):
    try:
        r = httpx.post(f"{API_URL}{path}", json=json, timeout=10, follow_redirects=True)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"Lỗi kết nối API: {e}")
        return None


def api_patch(path: str):
    try:
        r = httpx.patch(f"{API_URL}{path}", timeout=10, follow_redirects=True)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"Lỗi kết nối API: {e}")
        return None


def api_delete(path: str):
    try:
        r = httpx.delete(f"{API_URL}{path}", timeout=10, follow_redirects=True)
        if r.status_code == 204:
            return True
        r.raise_for_status()
        return True
    except Exception as e:
        st.error(f"Lỗi kết nối API: {e}")
        return False


# ── Sidebar ───────────────────────────────────────────────

st.sidebar.title("📈 Nobi Trade")
st.sidebar.markdown("Hệ thống cảnh báo & thống kê đầu tư chứng khoán cá nhân")

st.sidebar.divider()
if st.sidebar.button("🧪 Test gửi Telegram", use_container_width=True):
    result = api_post("/api/test-notification")
    if result and result.get("status") == "ok":
        st.sidebar.success("✅ Đã gửi! Kiểm tra Telegram.")
    else:
        msg = result.get("message", "Không kết nối được API") if result else "Không kết nối được API"
        st.sidebar.error(f"❌ {msg}")

# ── Tabs ──────────────────────────────────────────────────

tab1, tab2 = st.tabs(["📊 Quản lý danh mục", "📈 Báo cáo & Lịch sử"])

# ══════════════════════════════════════════════════════════
# TAB 1: Quản lý danh mục
# ══════════════════════════════════════════════════════════

with tab1:
    st.header("Quản lý danh mục đầu tư")

    # ── Form thêm mã mới ──
    with st.expander("➕ Thêm mã cổ phiếu mới", expanded=False):
        with st.form("add_position_form", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                symbol = st.text_input("Mã CP", placeholder="VNM", max_chars=10)
                buy_price = st.number_input("Giá mua (VNĐ)", min_value=0.0, step=100.0, format="%.0f")
            with col2:
                volume = st.number_input("Khối lượng", min_value=1, step=100, value=100)
                take_profit_pct = st.number_input("% Chốt lời", min_value=0.1, step=0.5, value=5.0)
            with col3:
                stop_loss_pct = st.number_input("% Cắt lỗ", min_value=0.1, step=0.5, value=3.0)

            submitted = st.form_submit_button("Thêm vào danh mục", use_container_width=True)
            if submitted:
                if not symbol.strip():
                    st.warning("Vui lòng nhập mã cổ phiếu")
                elif buy_price <= 0:
                    st.warning("Giá mua phải lớn hơn 0")
                else:
                    result = api_post("/api/positions", json={
                        "symbol": symbol.strip().upper(),
                        "buy_price": buy_price,
                        "volume": volume,
                        "take_profit_pct": take_profit_pct,
                        "stop_loss_pct": stop_loss_pct,
                    })
                    if result:
                        st.success(f"✅ Đã thêm {symbol.upper()} vào danh mục!")
                        st.rerun()

    # ── Bảng danh mục ──
    st.subheader("Danh mục đang giữ")
    positions = api_get("/api/positions")

    if positions and len(positions) > 0:
        for pos in positions:
            with st.container(border=True):
                col1, col2, col3, col4 = st.columns([2, 2, 2, 2])

                with col1:
                    alert_icon = "🔕" if pos["is_paused_alert"] else "🔔"
                    st.markdown(f"### {alert_icon} {pos['symbol']}")
                    st.caption(f"ID: {pos['id']} | Ngày mua: {pos['created_at'][:10]}")

                with col2:
                    st.metric("Giá mua", f"{pos['buy_price']:,.0f} ₫")
                    st.metric("Khối lượng", f"{pos['volume']:,}")

                with col3:
                    st.metric("% Chốt lời", f"+{pos['take_profit_pct']}%")
                    st.metric("% Cắt lỗ", f"-{pos['stop_loss_pct']}%")

                with col4:
                    # Toggle alert
                    alert_label = "🔔 Bật cảnh báo" if pos["is_paused_alert"] else "🔕 Tắt cảnh báo"
                    if st.button(alert_label, key=f"toggle_{pos['id']}", use_container_width=True):
                        api_patch(f"/api/positions/{pos['id']}/toggle-alert")
                        st.rerun()

                    # Sell
                    sell_price = st.number_input(
                        "💲 Nhập giá bán (VNĐ)",
                        min_value=0.0,
                        step=100.0,
                        format="%.0f",
                        key=f"sell_price_{pos['id']}",
                    )
                    if st.button("💰 Đã bán", key=f"sell_{pos['id']}", use_container_width=True):
                        if sell_price > 0:
                            result = api_post(
                                f"/api/positions/{pos['id']}/sell",
                                json={"sell_price": sell_price},
                            )
                            if result:
                                pnl = result["profit_loss_value"]
                                pnl_pct = result["profit_loss_pct"]
                                emoji = "🟢" if pnl >= 0 else "🔴"
                                st.success(
                                    f"{emoji} Đã bán {pos['symbol']}! "
                                    f"Lời/Lỗ: {pnl:,.0f} ₫ ({pnl_pct:+.2f}%)"
                                )
                                st.rerun()
                        else:
                            st.warning("Vui lòng nhập giá bán")

                    # Delete
                    if st.button("🗑️ Xóa", key=f"del_{pos['id']}", use_container_width=True, type="secondary"):
                        api_delete(f"/api/positions/{pos['id']}")
                        st.rerun()
    else:
        st.info("Chưa có mã nào trong danh mục. Hãy thêm mã cổ phiếu mới! ☝️")


# ══════════════════════════════════════════════════════════
# TAB 2: Báo cáo & Lịch sử
# ══════════════════════════════════════════════════════════

with tab2:
    st.header("Báo cáo & Lịch sử giao dịch")

    # ── Bộ lọc ──
    filter_col1, filter_col2 = st.columns(2)

    with filter_col1:
        period_options = {
            "1 tháng": "1m",
            "3 tháng": "3m",
            "6 tháng": "6m",
            "1 năm": "1y",
            "Tất cả": "all",
        }
        period_label = st.selectbox("Khoảng thời gian", list(period_options.keys()), index=0)
        period = period_options[period_label]

    with filter_col2:
        symbol_filter = st.text_input("Lọc theo mã CP (để trống = tất cả)", placeholder="VNM")
        symbol_filter = symbol_filter.strip().upper() if symbol_filter.strip() else None

    # ── Dashboard metrics ──
    params = {"period": period}
    if symbol_filter:
        params["symbol"] = symbol_filter

    analytics = api_get("/api/analytics", params=params)

    if analytics:
        m1, m2, m3, m4 = st.columns(4)

        total_pnl = analytics["total_profit_loss"]
        pnl_color = "normal" if total_pnl >= 0 else "inverse"

        m1.metric("💰 Tổng Lãi/Lỗ", f"{total_pnl:,.0f} ₫")
        m2.metric("📊 Tổng giao dịch", analytics["total_trades"])
        m3.metric("✅ Thắng / ❌ Thua", f"{analytics['winning_trades']} / {analytics['losing_trades']}")
        m4.metric("🎯 Win Rate", f"{analytics['win_rate']:.1f}%")

    # ── Bảng lịch sử ──
    st.subheader("Chi tiết lịch sử giao dịch")
    history = api_get("/api/history", params=params)

    if history and len(history) > 0:
        for record in history:
            pnl = record["profit_loss_value"]
            pnl_pct = record["profit_loss_pct"]
            emoji = "🟢" if pnl >= 0 else "🔴"

            with st.container(border=True):
                col1, col2, col3, col4 = st.columns([2, 3, 3, 1])

                with col1:
                    st.markdown(f"**{emoji} {record['symbol']}**")
                    sold_date = pd.to_datetime(record["sold_at"]).strftime("%Y-%m-%d %H:%M")
                    st.caption(sold_date)

                with col2:
                    st.markdown(f"Mua: **{record['buy_price']:,.0f}** → Bán: **{record['sell_price']:,.0f}** | KL: {record['volume']:,}")

                with col3:
                    st.markdown(f"Lời/Lỗ: **{pnl:+,.0f} ₫** ({pnl_pct:+.2f}%)")

                with col4:
                    if st.button("🗑️", key=f"del_history_{record['id']}", help="Xóa record này"):
                        api_delete(f"/api/history/{record['id']}")
                        st.rerun()
    else:
        st.info("Chưa có lịch sử giao dịch nào trong khoảng thời gian này.")
