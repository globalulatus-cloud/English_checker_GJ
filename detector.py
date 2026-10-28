"""Language detection for a single piece of text (Lingua)."""
import re
from dataclasses import dataclass
from functools import lru_cache

from lingua import IsoCode639_1, LanguageDetectorBuilder

import settings as cfg

ENGLISH = "English"
NUMBER = "Number"
SYMBOLS = "Symbols"
CODE = "Code / ID"
EMPTY = "Empty"
UNDETERMINED = "Undetermined"

# Pieces that are not language: tags, {1}-style placeholders, [BU-HCS]-style codes,
# *FIELD: markers, the word "null", URLs, e-mails and part numbers (tokens mixing
# letters and digits, e.g. M1239104).
_NOISE = re.compile(
    r"<[^>]+>"
    r"|\{[^}]*\}"
    r"|\[[^\s\]]*\]"
    r"|\*\w+:?"
    r"|\bnull\b"
    r"|(?:https?://|www\.)\S+"
    r"|\S+@\S+\.\S+"
    r"|\b(?=\w*\d)(?=\w*[^\W\d_])\w+\b"
)


@dataclass(frozen=True)
class Detection:
    language: str
    confidence: float | None  # None when the text is not language (number, symbols...)


@lru_cache(maxsize=1)
def _detector():
    if cfg.CANDIDATE_LANGUAGES is None:
        return LanguageDetectorBuilder.from_all_languages().build()
    try:
        codes = [getattr(IsoCode639_1, code.upper()) for code in cfg.CANDIDATE_LANGUAGES]
    except AttributeError as exc:
        raise ValueError(f"Unknown ISO 639-1 code in settings.CANDIDATE_LANGUAGES: {exc}") from exc
    return LanguageDetectorBuilder.from_iso_codes_639_1(*codes).build()


def _non_language_label(original: str) -> str:
    if not original.strip():
        return EMPTY
    if any(ch.isalpha() for ch in original):
        return CODE  # had letters, but only codes/IDs/tags
    if any(ch.isdigit() for ch in original):
        return NUMBER
    return SYMBOLS


@lru_cache(maxsize=8192)
def detect_language(text: str) -> Detection:
    cleaned = _NOISE.sub(" ", text)
    if not any(ch.isalpha() for ch in cleaned):
        return Detection(_non_language_label(text), None)

    top = _detector().compute_language_confidence_values(cleaned)[0]
    if top.value == 0:
        return Detection(UNDETERMINED, 0.0)
    return Detection(top.language.name.replace("_", " ").title(), top.value)
