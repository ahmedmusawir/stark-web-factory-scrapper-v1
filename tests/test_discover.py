"""Pure-logic smoke tests for discover_site.discover — no network, no env."""
from discover_site.discover import is_valid_link, normalize_link

DOMAIN = "example.com"


def test_is_valid_link_rejects_empty_mailto_tel_and_fragments():
    assert not is_valid_link(None, DOMAIN)
    assert not is_valid_link("", DOMAIN)
    assert not is_valid_link("mailto:hi@example.com", DOMAIN)
    assert not is_valid_link("tel:+15551234567", DOMAIN)
    assert not is_valid_link("https://example.com/about#team", DOMAIN)


def test_is_valid_link_accepts_relative_and_same_domain_only():
    assert is_valid_link("/services", DOMAIN)
    assert is_valid_link("https://example.com/services", DOMAIN)
    assert not is_valid_link("https://other.example.com/services", DOMAIN)


def test_normalize_link_strips_fragment_and_query_and_resolves_relative():
    base = "https://example.com/"
    assert normalize_link("/about?utm=x#team", base) == "https://example.com/about"
    assert normalize_link("https://example.com/contact#form", base) == "https://example.com/contact"
