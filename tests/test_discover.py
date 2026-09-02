"""Pure-logic smoke tests for discover_site.discover — no network, no env."""
from discover_site.discover import is_valid_link, normalize_link

DOMAIN = "cyberizegroup.com"


def test_is_valid_link_rejects_empty_mailto_tel_and_fragments():
    assert not is_valid_link(None, DOMAIN)
    assert not is_valid_link("", DOMAIN)
    assert not is_valid_link("mailto:hi@cyberizegroup.com", DOMAIN)
    assert not is_valid_link("tel:+15551234567", DOMAIN)
    assert not is_valid_link("https://cyberizegroup.com/about#team", DOMAIN)


def test_is_valid_link_accepts_relative_and_same_domain_only():
    assert is_valid_link("/services", DOMAIN)
    assert is_valid_link("https://cyberizegroup.com/services", DOMAIN)
    assert not is_valid_link("https://other.example.com/services", DOMAIN)


def test_normalize_link_strips_fragment_and_query_and_resolves_relative():
    base = "https://cyberizegroup.com/"
    assert normalize_link("/about?utm=x#team", base) == "https://cyberizegroup.com/about"
    assert normalize_link("https://cyberizegroup.com/contact#form", base) == "https://cyberizegroup.com/contact"
