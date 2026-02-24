from __future__ import annotations

from pathlib import Path

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

from .config import AppConfig
from .logging_utils import InvoiceResult, append_jsonl
from .selectors import DEFAULT_PLANS, SelectorResolver
from .utils import extract_order_id, is_business_order, safe_name


def _login(page, cfg: AppConfig, resolver: SelectorResolver) -> None:
    page.goto("https://www.amazon.com/ap/signin", wait_until="domcontentloaded")
    email_selector = resolver.find_first_visible(page, "sign_in_email", cfg.timeout_ms)
    page.fill(email_selector, cfg.amazon_email)

    continue_selector = resolver.find_first_visible(page, "continue_button", cfg.timeout_ms)
    page.click(continue_selector)

    password_selector = resolver.find_first_visible(page, "sign_in_password", cfg.timeout_ms)
    page.fill(password_selector, cfg.amazon_password)

    submit_selector = resolver.find_first_visible(page, "sign_in_submit", cfg.timeout_ms)
    page.click(submit_selector)

    if cfg.otp_code:
        try:
            otp_selector = resolver.find_first_visible(page, "otp_input", 5000)
            page.fill(otp_selector, cfg.otp_code)
            otp_submit = resolver.find_first_visible(page, "otp_submit", 5000)
            page.click(otp_submit)
        except LookupError:
            pass


def _download_invoice(context, page, invoice_link: str, target_path: Path, timeout_ms: int) -> bool:
    page.goto(invoice_link, wait_until="domcontentloaded")
    if page.url.lower().endswith(".pdf"):
        response = page.request.get(page.url, timeout=timeout_ms)
        if response.ok:
            target_path.write_bytes(response.body())
            return True
    try:
        with context.expect_page(timeout=timeout_ms) as popup_info:
            page.locator(f"a[href='{invoice_link}']").click(timeout=3000)
        popup = popup_info.value
        popup.wait_for_load_state("domcontentloaded")
        if popup.url.lower().endswith(".pdf"):
            response = popup.request.get(popup.url, timeout=timeout_ms)
            if response.ok:
                target_path.write_bytes(response.body())
                popup.close()
                return True
        popup.close()
    except Exception:
        pass
    return False


def run() -> None:
    cfg = AppConfig.from_env()
    cfg.download_dir.mkdir(parents=True, exist_ok=True)
    resolver = SelectorResolver(DEFAULT_PLANS)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=cfg.headless)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()
        page.set_default_timeout(cfg.timeout_ms)

        _login(page, cfg, resolver)
        page.goto(cfg.orders_url, wait_until="domcontentloaded")

        processed_orders = 0
        while processed_orders < cfg.max_orders:
            order_selector = resolver.find_first_visible(page, "order_cards", cfg.timeout_ms)
            cards = page.locator(order_selector).all()
            if not cards:
                break

            for card in cards:
                if processed_orders >= cfg.max_orders:
                    break

                card_text = card.inner_text(timeout=cfg.timeout_ms)
                order_id = extract_order_id(card_text)
                processed_orders += 1

                if not is_business_order(card_text):
                    append_jsonl(
                        cfg.log_path,
                        InvoiceResult(order_id=order_id, invoice_url="", status="skipped", reason="non-business payment"),
                    )
                    continue

                invoice_selector = resolver.find_first_visible(page, "invoice_links", 5000)
                links = card.locator(invoice_selector).all()
                if not links:
                    append_jsonl(
                        cfg.log_path,
                        InvoiceResult(order_id=order_id, invoice_url="", status="skipped", reason="no invoice link"),
                    )
                    continue

                for idx, link in enumerate(links, start=1):
                    invoice_url = link.get_attribute("href") or ""
                    if invoice_url.startswith("/"):
                        invoice_url = f"https://www.amazon.com{invoice_url}"
                    target = cfg.download_dir / f"{safe_name(order_id)}-{idx}.pdf"
                    ok = _download_invoice(context, page, invoice_url, target, cfg.timeout_ms)
                    if ok:
                        append_jsonl(
                            cfg.log_path,
                            InvoiceResult(
                                order_id=order_id,
                                invoice_url=invoice_url,
                                status="downloaded",
                                file_path=str(target),
                            ),
                        )
                    else:
                        append_jsonl(
                            cfg.log_path,
                            InvoiceResult(
                                order_id=order_id,
                                invoice_url=invoice_url,
                                status="failed",
                                reason="invoice retrieval failed",
                            ),
                        )

            try:
                next_selector = resolver.find_first_visible(page, "next_page", 2500)
                page.click(next_selector)
                page.wait_for_load_state("domcontentloaded")
            except (LookupError, PlaywrightTimeoutError):
                break

        context.close()
        browser.close()
