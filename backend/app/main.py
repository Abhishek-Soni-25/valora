
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router

app = FastAPI(
    title="Valora DCF Valuation API",
    description="A transparent discounted cash flow valuation calculator.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://valora-wim3.onrender.com/",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

app.include_router(router)


@app.get("/")
def root():
    return {
        "application": "Valora",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
