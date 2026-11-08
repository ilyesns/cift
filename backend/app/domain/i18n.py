"""Locale rules.

Content is stored as <entity> + <entity>_translations (one row per locale).
When the visitor's language is missing we fall back in a fixed order.
Italian comes first in every fallback because every piece of content must have it.
"""

from collections.abc import Iterable
from typing import Protocol

SUPPORTED: tuple[str, ...] = ("it", "ar", "en")
DEFAULT = "it"
RTL = frozenset({"ar"})

FALLBACK_ORDER: dict[str, tuple[str, ...]] = {
    "it": ("it", "en", "ar"),
    "ar": ("ar", "it", "en"),
    "en": ("en", "it", "ar"),
}


class HasLocale(Protocol):
    locale: str


def normalize_locale(value: str | None) -> str:
    """'ar-TN' -> 'ar'; anything unsupported -> the default."""
    if not value:
        return DEFAULT
    base = value.strip().lower().replace("_", "-").split("-")[0]
    return base if base in SUPPORTED else DEFAULT


def locale_from_accept_language(header: str | None) -> str:
    """First supported language in an Accept-Language header."""
    if not header:
        return DEFAULT
    for part in header.split(","):
        base = part.split(";")[0].strip().lower().split("-")[0]
        if base in SUPPORTED:
            return base
    return DEFAULT


def pick_translation[T: HasLocale](translations: Iterable[T], locale: str) -> T | None:
    """Best translation for `locale`, following FALLBACK_ORDER."""
    by_locale = {t.locale: t for t in translations}
    for candidate in FALLBACK_ORDER[normalize_locale(locale)]:
        if candidate in by_locale:
            return by_locale[candidate]
    return None


def is_rtl(locale: str) -> bool:
    return normalize_locale(locale) in RTL
