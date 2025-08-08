from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv

# Load environment variables from a local .env if present
load_dotenv()


@dataclass(frozen=True)
class DBConfig:
    host: str
    port: int
    user: str
    password: str
    database: str
    sslmode: Optional[str] = None

    @property
    def sqlalchemy_url(self) -> str:
        # psycopg3 driver
        base = f"postgresql+psycopg://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
        if self.sslmode:
            return f"{base}?sslmode={self.sslmode}"
        return base


def load_db_config() -> DBConfig:
    return DBConfig(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "5433")),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres"),
        database=os.getenv("DB_NAME", "fmea_tracker"),
        sslmode=os.getenv("DB_SSLMODE") or None,
    )
