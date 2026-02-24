# Amazon Invoice Downloader (Playwright + Python)

Automates Amazon sign-in, opens order history, filters for likely business-payment orders, attempts invoice PDF downloads, and writes structured results logs.

## Features

- Playwright automation with Chromium.
- Login flow with optional OTP submission.
- Order-history traversal with pagination.
- Invoice PDF download attempts for business-like orders.
- JSONL result logging per processed order/invoice.
- Self-healing selector fallback: if a fallback selector works, it is promoted for subsequent steps in the same run.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
python -m playwright install chromium
cp .env.example .env
```

Fill credentials in `.env`.

## Run

```bash
python -m amazon_invoices
```

## Output

- PDFs are written to `downloads/` by default.
- Log file is `logs/results.jsonl` by default.

Example JSONL entry:

```json
{"order_id":"123-1234567-1234567","invoice_url":"https://...","status":"downloaded","file_path":"/abs/path/downloads/123-...-1.pdf","timestamp":"2026-01-01T00:00:00+00:00"}
```

## Notes

- Amazon flows vary by account, region, localization, and anti-bot checks.
- You may need to adjust selectors in `src/amazon_invoices/selectors.py`.
- Use this tool only in compliance with Amazon terms and your local policies.
