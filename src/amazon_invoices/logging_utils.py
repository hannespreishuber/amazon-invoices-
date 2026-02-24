from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class InvoiceResult:
    order_id: str
    invoice_url: str
    status: str
    reason: str | None = None
    file_path: str | None = None

    def to_json(self) -> str:
        payload = asdict(self)
        payload["timestamp"] = datetime.now(timezone.utc).isoformat()
        return json.dumps(payload, ensure_ascii=False)


def append_jsonl(log_path: Path, result: InvoiceResult) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(result.to_json() + "\n")
