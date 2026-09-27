import os


class Settings:
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-only-secret-change-me-in-production-please")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./coco_nutricare.db")
    CORS_ORIGINS: list[str] = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")]
    WHO_WFA_BOYS_CSV: str | None = os.getenv("WHO_WFA_BOYS_CSV")
    WHO_WFA_GIRLS_CSV: str | None = os.getenv("WHO_WFA_GIRLS_CSV")


settings = Settings()
