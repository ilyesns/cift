from dataclasses import dataclass

from app.domain.i18n import (
    is_rtl,
    locale_from_accept_language,
    normalize_locale,
    pick_translation,
)


@dataclass
class Tr:
    locale: str
    title: str


def test_exact_locale_wins():
    items = [Tr("it", "Ciao"), Tr("ar", "مرحبا")]
    assert pick_translation(items, "ar").title == "مرحبا"


def test_arabic_falls_back_to_italian():
    items = [Tr("en", "Hello"), Tr("it", "Ciao")]
    assert pick_translation(items, "ar").title == "Ciao"


def test_english_falls_back_to_italian_before_arabic():
    items = [Tr("ar", "مرحبا"), Tr("it", "Ciao")]
    assert pick_translation(items, "en").title == "Ciao"


def test_unknown_locale_uses_italian_order():
    items = [Tr("en", "Hello"), Tr("it", "Ciao")]
    assert pick_translation(items, "fr").title == "Ciao"


def test_no_translations_returns_none():
    assert pick_translation([], "it") is None


def test_normalize_locale():
    assert normalize_locale("ar-TN") == "ar"
    assert normalize_locale("EN_gb") == "en"
    assert normalize_locale("fr") == "it"
    assert normalize_locale(None) == "it"


def test_accept_language_header():
    assert locale_from_accept_language("fr-FR,en;q=0.8,it;q=0.5") == "en"
    assert locale_from_accept_language("ar-TN,ar;q=0.9") == "ar"
    assert locale_from_accept_language("de-DE") == "it"
    assert locale_from_accept_language(None) == "it"


def test_only_arabic_is_rtl():
    assert is_rtl("ar")
    assert not is_rtl("it")
    assert not is_rtl("en")
