"""Read segments (source/target pairs) out of an MXLIFF / XLIFF 1.2 file."""
from dataclasses import dataclass

from defusedxml import ElementTree as ET
from defusedxml.common import DefusedXmlException

# Inline elements whose content is markup, not translatable text.
_CODE_TAGS = frozenset({"ph", "bpt", "ept", "it", "x", "bx", "ex"})


class MxliffError(ValueError):
    """Raised when an uploaded file cannot be read as MXLIFF."""


@dataclass(frozen=True)
class Segment:
    number: int      # running number across the whole file, starting at 1
    segment_id: str  # the trans-unit id exactly as stored in the file
    source: str
    target: str


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _text(element) -> str:
    """Visible text of an element, skipping the content of inline code tags."""
    if element is None:
        return ""
    parts = [element.text or ""]
    for child in element:
        if _local(child.tag) not in _CODE_TAGS:
            parts.append(_text(child))
        parts.append(child.tail or "")
    return "".join(parts)


def _child(element, name: str):
    return next((c for c in element if _local(c.tag) == name), None)


def parse_mxliff(data: bytes) -> list[Segment]:
    """Return every segment in document order. Works for joined (multi-<file>) files."""
    try:
        root = ET.fromstring(data)
    except (ET.ParseError, DefusedXmlException) as exc:
        raise MxliffError(f"This is not a readable XML/MXLIFF file ({exc}).") from exc

    segments: list[Segment] = []
    for unit in root.iter():
        if _local(unit.tag) != "trans-unit":
            continue
        source = _child(unit, "source")
        if source is None:
            continue
        segments.append(
            Segment(
                number=len(segments) + 1,
                segment_id=unit.get("id", ""),
                source=_text(source),
                target=_text(_child(unit, "target")),
            )
        )
    if not segments:
        raise MxliffError("No <trans-unit> segments were found in this file.")
    return segments
