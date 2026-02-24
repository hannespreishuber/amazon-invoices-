from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class AppConfig:
    amazon_email: str
    amazon_password: str
    otp_code: str | None
    headless: bool
    orders_url: str
    download_dir: Path
    log_path: Path
    timeout_ms: int
    max_orders: int

    @classmethod
    def from_env(cls) -> "AppConfig":
        load_dotenv()
        email = os.getenv("AMAZON_EMAIL", "").strip()
        password = os.getenv("AMAZON_PASSWORD", "").strip()
        if not email or not password:
            raise ValueError("AMAZON_EMAIL and AMAZON_PASSWORD must be set.")

        download_dir = Path(os.getenv("DOWNLOAD_DIR", "downloads")).resolve()
        log_path = Path(os.getenv("RESULT_LOG_PATH", "logs/results.jsonl")).resolve()
        return cls(
            amazon_email=email,
            amazon_password=password,
            otp_code=os.getenv("AMAZON_OTP_CODE"),
            headless=os.getenv("HEADLESS", "true").lower() not in {"0", "false", "no"},
            orders_url=os.getenv("ORDERS_URL", "https://www.amazon.com/gp/css/order-history"),
            download_dir=download_dir,
            log_path=log_path,
            timeout_ms=int(os.getenv("TIMEOUT_MS", "25000")),
            max_orders=int(os.getenv("MAX_ORDERS", "100")),
        )
