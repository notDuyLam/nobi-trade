from fastapi import FastAPI

app = FastAPI(
    title="Nobi Trade API",
    description="Hệ thống cảnh báo & thống kê đầu tư chứng khoán cá nhân",
    version="1.0.0",
)


@app.get("/")
def root():
    return {"message": "Nobi Trade API is running"}
