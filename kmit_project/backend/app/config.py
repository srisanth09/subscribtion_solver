import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    APP_NAME: str = "Subscription & Recurring-Spend Guardian Agent"
    APP_VERSION: str = "1.0.0"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./guardian.db")
    
    # Default User Guardrails (as required in hackathon specification)
    DEFAULT_USER_ID: str = "u_301"
    DEFAULT_AUTO_ACTION_LIMIT: float = 20.0  # $20 or ₹2,000 depending on currency
    CURRENCY_SYMBOL: str = "₹"  # Supports ₹ or $
    
    # Protected categories that MUST NEVER be auto-cancelled
    DEFAULT_PROTECTED_CATEGORIES: list[str] = [
        "insurance",
        "loan_payment",
        "healthcare",
        "utility",
        "education",
        "tax"
    ]
    
    # AI / LLM Configuration
    # Supports "LOCAL" (zero-latency, 100% offline rule+NLP agent) or "OPENAI", "GEMINI"
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "LOCAL")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Agent Confidence & Waste thresholds
    MIN_AUTO_CANCEL_WASTE_SCORE: int = 70
    MIN_AUTO_CANCEL_CONFIDENCE: float = 0.85
    AMBIGUOUS_CONFIDENCE_THRESHOLD: float = 0.70

settings = Settings()
