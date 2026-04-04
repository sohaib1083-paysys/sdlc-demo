# app/main.py
from fastapi import FastAPI
from health_check import router

app = FastAPI(
    title="Health Check API",
    description="API for checking the health of the application",
    version="1.0.0"
)

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
