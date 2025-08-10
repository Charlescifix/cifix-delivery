import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://localhost/cifix_hub")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key")
    ADMIN_PASS: str = os.getenv("ADMIN_PASS", "admin123")
    WEBHOOK_SECRET: str = os.getenv("WEBHOOK_SECRET", "webhook-secret")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    SESSION_COOKIE_NAME: str = "session"
    SESSION_MAX_AGE: int = 86400 * 7  # 7 days

settings = Settings()