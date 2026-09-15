from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    DATABASE_URL: str = "sqlite:///./inventory.db"
    STOCK_LOW_THRESHOLD: int = 5


settings = Settings()