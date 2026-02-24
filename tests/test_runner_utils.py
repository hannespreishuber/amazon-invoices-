from amazon_invoices.utils import extract_order_id, is_business_order, safe_name


def test_extract_order_id_prefers_standard_amazon_format():
    text = "Order # 123-1234567-1234567 placed Jan 1"
    assert extract_order_id(text) == "123-1234567-1234567"


def test_is_business_order_detects_keywords():
    assert is_business_order("Paid with Business Prime card") is True
    assert is_business_order("Paid with personal Visa") is False


def test_safe_name_replaces_invalid_characters():
    assert safe_name("123/ABC:invoice") == "123_ABC_invoice"
