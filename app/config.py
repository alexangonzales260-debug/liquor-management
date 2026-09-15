from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    DATABASE_URL: str = "sqlite:///./inventory.db"


settings = Settings()