"""Shared constants: thresholds and the exact Excel column headers."""

CONFIDENCE_THRESHOLD = 0.90  # confidence strictly below this is shown in red
PREVIEW_ROWS = 10

# Languages the detector may choose from, as ISO 639-1 codes (at least two, e.g. ("fi", "en", "sv")).
# None = all 75 languages Lingua supports. A shorter list is clearly more accurate and more
# confident on short segments, but any language outside the list can only be reported as one of them.
CANDIDATE_LANGUAGES: tuple[str, ...] | None = None

COL_NUMBER = "Segment number"
COL_ID = "Segment ID"
COL_SOURCE = "Source"
COL_TARGET = "Target"
COL_BOTH_EN = "Is both source and target English (Yes or No)"
COL_SRC_LANG = "Source language"
COL_TGT_LANG = "Target language"
COL_CONF = "Confidence level"

RESULT_COLUMNS = [
    COL_NUMBER, COL_ID, COL_SOURCE, COL_TARGET,
    COL_BOTH_EN, COL_SRC_LANG, COL_TGT_LANG, COL_CONF,
]
