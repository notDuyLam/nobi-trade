# Nobi Trade

Hệ thống cảnh báo & thống kê đầu tư chứng khoán cá nhân.

## Quick Start

```bash
# 1. Tạo virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 2. Cài đặt dependencies
pip install -r requirements.txt

# 3. Tạo file .env từ template
cp .env.example .env
# Sửa file .env: điền TELEGRAM_BOT_TOKEN và TELEGRAM_CHAT_ID

# 4. Chạy FastAPI
uvicorn app.main:app --reload --port 8000

# 5. Chạy Streamlit (terminal khác)
streamlit run streamlit_app/app.py --server.port 8501
```
