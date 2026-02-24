from amazon_invoices.selectors import SelectorPlan, SelectorResolver


class FakeLocator:
    def __init__(self, visible: bool):
        self._visible = visible

    @property
    def first(self):
        return self

    def is_visible(self, timeout: int):
        return self._visible


class FakePage:
    def __init__(self, visibility):
        self.visibility = visibility

    def locator(self, selector):
        return FakeLocator(self.visibility.get(selector, False))


def test_selector_fallback_promotes_working_candidate():
    resolver = SelectorResolver([SelectorPlan("x", ("#a", "#b", "#c"))])
    page = FakePage({"#b": True})

    selected = resolver.find_first_visible(page, "x", timeout_ms=10)
    assert selected == "#b"

    selected_again = resolver.find_first_visible(page, "x", timeout_ms=10)
    assert selected_again == "#b"
