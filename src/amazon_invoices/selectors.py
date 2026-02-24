from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class SelectorPlan:
    name: str
    candidates: tuple[str, ...]


class SelectorResolver:
    """Find elements using primary and fallback selectors.

    If the primary selector fails but a fallback works, the fallback is promoted
    to the front of the list for future calls in this run.
    """

    def __init__(self, plans: Iterable[SelectorPlan]) -> None:
        self._plans = {p.name: list(p.candidates) for p in plans}

    def find_first_visible(self, page, name: str, timeout_ms: int) -> str:
        selectors = self._plans[name]
        for idx, selector in enumerate(selectors):
            loc = page.locator(selector).first
            try:
                if loc.is_visible(timeout=timeout_ms):
                    if idx > 0:
                        selectors.insert(0, selectors.pop(idx))
                    return selector
            except Exception:
                continue
        raise LookupError(f"No selector matched for {name}: {selectors}")


DEFAULT_PLANS = [
    SelectorPlan("sign_in_email", ("#ap_email", "input[name='email']", "input[type='email']")),
    SelectorPlan("continue_button", ("#continue", "input[type='submit']", "button:has-text('Continue')")),
    SelectorPlan("sign_in_password", ("#ap_password", "input[name='password']", "input[type='password']")),
    SelectorPlan("sign_in_submit", ("#signInSubmit", "input#signInSubmit", "button:has-text('Sign in')")),
    SelectorPlan("otp_input", ("input[name='otpCode']", "input#auth-mfa-otpcode", "input[type='tel']")),
    SelectorPlan("otp_submit", ("#auth-signin-button", "input[type='submit']", "button:has-text('Submit code')")),
    SelectorPlan(
        "order_cards",
        (
            "div.order-card",
            "div[data-component='order-card']",
            "div.order",
        ),
    ),
    SelectorPlan(
        "invoice_links",
        (
            "a:has-text('Invoice')",
            "a:has-text('View invoice')",
            "a[href*='invoice']",
        ),
    ),
    SelectorPlan(
        "business_payment_badge",
        (
            "text=/Business Prime|Business.*card|Corporate/i",
            "span:has-text('Business')",
            "div:has-text('Business')",
        ),
    ),
    SelectorPlan(
        "next_page",
        (
            "ul.a-pagination li.a-last a",
            "a:has-text('Next')",
            "a[aria-label='Go to next page']",
        ),
    ),
]
