from __future__ import annotations

import re


def safe_name(raw: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.-]", "_", raw)
    return cleaned.strip("_") or "invoice"


def is_business_order(card_text: str) -> bool:
    lowered = card_text.lower()
    keywords = ["business", "corporate", "commercial"]
    return any(k in lowered for k in keywords)


def extract_order_id(card_text: str) -> str:
    match = re.search(r"order\s*#?\s*([0-9-]{8,})", card_text, re.IGNORECASE)
    if match:
        return match.group(1)
    match = re.search(r"([0-9]{3}-[0-9]{7}-[0-9]{7})", card_text)
    return match.group(1) if match else "unknown-order"
