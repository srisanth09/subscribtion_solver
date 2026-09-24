from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import engine, Base, SessionLocal
from app.data.seed_data import seed_initial_data
from app.routes import audit, subscriptions, guardrails, savings, audit_logs, transactions, emails, prompt, merchants

# Create all database tables
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: seed database with initial transactions and emails
    db = SessionLocal()
    try:
        seed_initial_data(db, settings.DEFAULT_USER_ID)
    finally:
        db.close()
    yield

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Agentic AI Subscription & Recurring-Spend Guardian Engine. Detects waste, checks guardrails, acts autonomously, and escalates when ambiguous.",
    lifespan=lifespan
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(audit.router)
app.include_router(prompt.router)
app.include_router(subscriptions.router)
app.include_router(guardrails.router)
app.include_router(savings.router)
app.include_router(audit_logs.router)
app.include_router(transactions.router)
app.include_router(emails.router)
app.include_router(merchants.router)


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "llm_provider": settings.LLM_PROVIDER,
        "database": settings.DATABASE_URL
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
