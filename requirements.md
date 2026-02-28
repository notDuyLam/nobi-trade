# Yêu Cầu Dự Án: Hệ Thống Cảnh Báo & Thống Kê Đầu Tư Chứng Khoán Cá Nhân
Bạn là một Expert Full-stack Python Developer. Nhiệm vụ của bạn là viết code hoàn chỉnh cho hệ thống theo dõi, cảnh báo giá cổ phiếu Việt Nam và báo cáo thống kê lời/lỗ.

## 1. Tech Stack
- **Backend:** Python, FastAPI, APScheduler (để chạy job định kỳ).
- **Frontend:** Streamlit.
- **Database:** SQLite (dùng SQLAlchemy ORM hoặc sqlite3 thuần).
- **Data Source:** Thư viện `vnstock` (Lấy giá realtime/intraday).
- **Notification:** Telegram Bot API.
- **Môi trường Deploy:** AWS EC2 (Ubuntu), quản lý process bằng `systemd` hoặc `pm2`, web server `uvicorn`.

## 2. Thiết Kế Database (SQLite)
Cần thiết kế 2 bảng chính:
- **Bảng `positions` (Danh mục đang giữ):** `id`, `symbol`, `buy_price`, `volume`, `take_profit_pct`, `stop_loss_pct`, `is_paused_alert` (boolean, default False), `created_at`.
- **Bảng `history` (Lịch sử giao dịch):** `id`, `symbol`, `buy_price`, `sell_price`, `volume`, `profit_loss_value` (VNĐ), `profit_loss_pct` (%), `sold_at`.

## 3. Core Features & Logic Xử Lý
### A. Backend (FastAPI + APScheduler)
1. **Cronjob quét giá:** - Lặp 5 phút/lần.
   - **Chỉ chạy trong giờ hành chính sàn VN (Giờ VN - UTC+7):** Thứ 2 - Thứ 6, từ 09:00 - 11:30 và 13:00 - 14:45.
2. **Logic Cảnh báo (Telegram):**
   - Lấy danh sách cổ phiếu từ bảng `positions`. Bỏ qua các mã có `is_paused_alert == True`.
   - Dùng `vnstock` lấy giá khớp lệnh hiện tại.
   - Tính % Lãi/Lỗ: `((Current_Price - Buy_Price) / Buy_Price) * 100`.
   - Nếu `% Lãi >= take_profit_pct` HOẶC `% Lỗ <= stop_loss_pct`: Bắn tin nhắn qua Telegram.
   - Nội dung tin nhắn cần rõ ràng: Mã, Giá Mua, Giá Hiện Tại, % Lãi/Lỗ, Trạng thái (Chạm ngưỡng chốt lời/Cắt lỗ).

### B. Frontend (Streamlit)
Giao diện có 2 Tabs chính:

**Tab 1: Quản lý danh mục (Active Positions)**
- Form thêm mã mới: Nhập `Mã CP`, `Giá mua`, `Khối lượng`, `% Chốt lời`, `% Cắt lỗ`.
- Bảng hiển thị danh mục đang giữ. Mỗi dòng có các Action (Nút bấm):
  - **Tạm dừng/Bật thông báo:** Cập nhật trường `is_paused_alert`.
  - **Đã Bán:** Mở modal/input nhập "Giá Bán Thực Tế". Khi xác nhận: 
    -> Xóa/Đổi trạng thái mã này ở bảng `positions`.
    -> Tính toán số tiền Lời/Lỗ và % Lời/Lỗ.
    -> Lưu vào bảng `history`.

**Tab 2: Báo cáo & Lịch sử (Analytics & History)**
- **Filter (Bộ lọc):** - Lọc theo khoảng thời gian (1 tháng, 3 tháng, 6 tháng, 1 năm, Tất cả). Mặc định là 1 tháng gần nhất.
  - Lọc theo mã cổ phiếu (Tất cả hoặc chọn 1 mã).
- **Dashboard (Metrics):** Hiển thị Tổng Lãi/Lỗ (VNĐ), Tỷ lệ Thắng/Thua (Win rate).
- **Data Table:** Hiển thị chi tiết bảng `history` theo bộ lọc.

### 4. Yêu Cầu Code & Phân phối
- Cấu trúc project rõ ràng (phân tách router, model, service, UI).
- Có file `requirements.txt`.
- Viết sẵn một đoạn script hoặc hướng dẫn ngắn gọn cách setup tự động chạy lại tool khi server AWS EC2 bị reboot (dùng systemd service).
- Handle các exception khi `vnstock` bị lỗi kết nối hoặc trả về data rỗng để không bị crash hệ thống.

Hãy bắt đầu bằng việc cung cấp cấu trúc thư mục project và code cho phần Database + Backend (FastAPI + Scheduler) trước.