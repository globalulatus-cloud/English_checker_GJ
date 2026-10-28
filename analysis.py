"""Turn parsed segments into the result table."""
from collections.abc import Callable

import pandas as pd

import settings as cfg
from detector import CODE, ENGLISH, SYMBOLS, detect_language
from mxliff_parser import Segment


BOTH_SAME = "Both same"
EN_NOT_MATCHING = "English not matching"
EN_MATCH_NA = ""  # not applicable: source and target aren't both English


def analyse(
    segments: list[Segment],
    on_progress: Callable[[int, int], None] | None = None,
) -> pd.DataFrame:
    """Detect source/target language per segment.

    Confidence is the lower of the two detections, i.e. how sure we are about the
    source-vs-target comparison. It is left empty (NaN) when either side is not
    language (number, symbols, code, empty). Identical symbol-only or code-only
    source/target pairs are labelled "Both same" in both language columns.
    """
    total = len(segments)
    rows = []
    for index, seg in enumerate(segments, start=1):
        src = detect_language(seg.source)
        tgt = detect_language(seg.target)
        both_english = src.language == ENGLISH and tgt.language == ENGLISH
        src_lang, tgt_lang = src.language, tgt.language
        if (src_lang == tgt_lang and src_lang in (SYMBOLS, CODE)
                and seg.source.strip() == seg.target.strip()):
            src_lang = tgt_lang = BOTH_SAME
        if both_english:
            en_match = BOTH_SAME if seg.source.strip() == seg.target.strip() else EN_NOT_MATCHING
        else:
            en_match = EN_MATCH_NA
        if src.confidence is None or tgt.confidence is None:
            confidence = float("nan")
        else:
            confidence = min(src.confidence, tgt.confidence)

        rows.append({
            cfg.COL_NUMBER: seg.number,
            cfg.COL_ID: seg.segment_id,
            cfg.COL_SOURCE: seg.source,
            cfg.COL_TARGET: seg.target,
            cfg.COL_BOTH_EN: "Yes" if both_english else "No",
            cfg.COL_EN_MATCH: en_match,
            cfg.COL_SRC_LANG: src_lang,
            cfg.COL_TGT_LANG: tgt_lang,
            cfg.COL_CONF: confidence,
        })
        if on_progress and (index % 10 == 0 or index == total):
            on_progress(index, total)
    return pd.DataFrame(rows, columns=cfg.RESULT_COLUMNS)
