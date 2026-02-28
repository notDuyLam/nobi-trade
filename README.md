# Nobi Trade 📈

Hệ thống cảnh báo & thống kê đầu tư chứng khoán cá nhân.

## Tính năng

- 📊 **Quản lý danh mục:** Thêm/xóa mã cổ phiếu, theo dõi giá mua, khối lượng
- 🔔 **Cảnh báo Telegram:** Tự động quét giá mỗi 5 phút, gửi cảnh báo khi chạm ngưỡng chốt lời/cắt lỗ
- 📈 **Báo cáo thống kê:** Tổng lời/lỗ, win rate, lịch sử giao dịch chi tiết
- 💰 **Ghi nhận bán:** Tính toán P&L tự động khi bán cổ phiếu

## Tech Stack

- **Backend:** Python, FastAPI, APScheduler
- **Frontend:** Streamlit
- **Database:** SQLite (SQLAlchemy ORM)
- **Data:** vnstock (giá cổ phiếu VN)
- **Notification:** Telegram Bot API

## Quick Start

```bash
# 1. Clone project
git clone <repo-url> && cd nobi-trade

# 2. Tạo virtual environment
python -m venv venv
source venv/bin/activate     # Linux/Mac
# venv\Scripts\activate      # Windows

# 3. Cài đặt dependencies
pip install -r requirements.txt

# 4. Cấu hình
cp .env.example .env
# Sửa .env: điền TELEGRAM_BOT_TOKEN và TELEGRAM_CHAT_ID

# 5. Chạy FastAPI (terminal 1)
uvicorn app.main:app --reload --port 8000

# 6. Chạy Streamlit (terminal 2)
streamlit run streamlit_app/app.py --server.port 8501
```

## Cấu hình `.env`

| Biến | Mô tả | Mặc định |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | Token của Telegram Bot | *(bắt buộc)* |
| `TELEGRAM_CHAT_ID` | Chat ID nhận cảnh báo | *(bắt buộc)* |
| `DATABASE_URL` | SQLite connection string | `sqlite:///./nobi_trade.db` |
| `API_BASE_URL` | URL FastAPI (Streamlit dùng) | `http://localhost:8000` |

## API Documentation

Khi chạy FastAPI, truy cập Swagger docs tại: `http://localhost:8000/docs`

## Deploy lên AWS EC2

```bash
# 1. SSH vào EC2 (Ubuntu)
ssh ubuntu@<ec2-ip>

# 2. Cài Python, clone project, tạo venv, pip install
sudo apt update && sudo apt install -y python3-pip python3-venv
git clone <repo-url> /home/ubuntu/nobi-trade
cd /home/ubuntu/nobi-trade
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Cấu hình .env
cp .env.example .env
nano .env   # điền token + chat ID

# 4. Copy systemd service files
sudo cp scripts/nobi-trade.service /etc/systemd/system/
sudo cp scripts/nobi-trade-streamlit.service /etc/systemd/system/

# 5. Enable & start services
sudo systemctl daemon-reload
sudo systemctl enable nobi-trade nobi-trade-streamlit
sudo systemctl start nobi-trade nobi-trade-streamlit

# 6. Kiểm tra status
sudo systemctl status nobi-trade
sudo systemctl status nobi-trade-streamlit

# 7. Xem logs
journalctl -u nobi-trade -f
journalctl -u nobi-trade-streamlit -f
```

Services sẽ **tự động khởi động lại** khi EC2 reboot nhờ `systemctl enable`.
