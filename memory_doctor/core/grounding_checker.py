"""Local, heuristic checks for generated memory summaries.

These checks identify review candidates; they do not prove semantic entailment.
"""

from __future__ import annotations

import re

MAX_TEXT_CHARS = 100_000

_WORD_RE = re.compile(r"\b[\w’'-]+\b", re.UNICODE)
_PERSON_RE = re.compile(
    r"\b(?:Dr\.?|Doctor|Prof\.?|Professor|Mr\.?|Mrs\.?|Ms\.?|Mx\.?)\s+"
    r"[A-Z][A-Za-zÀ-ÖØ-öø-ÿ'’-]*(?:\s+[A-Z][A-Za-zÀ-ÖØ-öø-ÿ'’-]*){0,2}"
)
_ORG_RE = re.compile(
    r"\b(?:[A-Z][A-Za-z0-9&.'’-]*\s+){0,4}"
    r"(?:Team|Group|Labs?|Institute|Department|Division|Committee|Engine|"
    r"Foundation|University|Corporation|Corp\.?|LLC|Ltd\.?)\b"
)
_PROJECT_RE = re.compile(r"\bProject\s+[A-Z][A-Za-z0-9_-]*\b")
_MONTHS = (
    "January|February|March|April|May|June|July|August|September|October|"
    "November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec"
)
_DATE_RE = re.compile(
    rf"\b(?:{_MONTHS})\.?\s+(?:\d{{1,2}}(?:st|nd|rd|th)?(?:,?\s+\d{{4}})?|\d{{4}})"
    rf"|\b\d{{4}}-\d{{2}}-\d{{2}}\b"
    rf"|\b\d{{1,2}}/\d{{1,2}}/\d{{2,4}}\b",
    re.IGNORECASE,
)
_NUMBER_RE = re.compile(r"(?<![\w])\d[\d,]*(?:\.\d+)?(?![\w])")
_NUMBER_WORDS = {
    "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4",
    "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9",
    "ten": "10", "eleven": "11", "twelve": "12", "thirteen": "13",
    "fourteen": "14", "fifteen": "15", "sixteen": "16",
    "seventeen": "17", "eighteen": "18", "nineteen": "19", "twenty": "20",
}


def _normalise(value: str) -> str:
    """Normalize whitespace and punctuation for conservative phrase matching."""
    return " ".join(re.findall(r"[\w]+", value.casefold(), flags=re.UNICODE))


def _count_words(text: str) -> int:
    return len(_WORD_RE.findall(text))


def _unique_matches(pattern: re.Pattern[str], text: str) -> list[str]:
    found: dict[str, str] = {}
    for match in pattern.finditer(text):
        value = match.group(0).strip().lstrip(".,;:")
        value = re.sub(r"^(?:The|A|An)\s+", "", value)
        key = _normalise(value)
        if key:
            found.setdefault(key, value)
    return list(found.values())


def _number_keys(text: str) -> set[str]:
    """Collect digit and small number-word forms, excluding date spans."""
    date_spans = [match.span() for match in _DATE_RE.finditer(text)]

    def inside_date(start: int, end: int) -> bool:
        return any(start < date_end and end > date_start for date_start, date_end in date_spans)

    values: set[str] = set()
    for match in _NUMBER_RE.finditer(text):
        if not inside_date(*match.span()):
            values.add(match.group(0).replace(",", ""))

    for match in _WORD_RE.finditer(text.casefold()):
        if match.group(0) in _NUMBER_WORDS:
            values.add(_NUMBER_WORDS[match.group(0)])
    return values


def analyze_summary(
    source: str,
    summary: str,
    required_phrases: str | list[str] | tuple[str, ...] = "",
) -> dict:
    """Compare a source and summary using transparent local heuristics.

    Args:
        source: Original source text.
        summary: Generated memory summary.
        required_phrases: Optional newline-delimited or iterable list of exact
            phrases that should remain in the summary.

    Returns a JSON-serializable dictionary. It deliberately avoids a single
    groundedness score because lexical heuristics cannot establish truth.
    """
    if not isinstance(source, str) or not source.strip():
        raise ValueError("Source text is required.")
    if not isinstance(summary, str) or not summary.strip():
        raise ValueError("Summary text is required.")
    if len(source) > MAX_TEXT_CHARS or len(summary) > MAX_TEXT_CHARS:
        raise ValueError(f"Source and summary must each be under {MAX_TEXT_CHARS:,} characters.")

    if isinstance(required_phrases, str):
        phrases = [line.strip() for line in required_phrases.splitlines() if line.strip()]
    else:
        phrases = [str(item).strip() for item in required_phrases if str(item).strip()]

    source_norm = _normalise(source)
    summary_norm = _normalise(summary)

    source_words = _count_words(source)
    summary_words = _count_words(summary)
    ratio = round(summary_words / source_words, 2) if source_words else None

    source_entities = {
        _normalise(value)
        for pattern in (_PERSON_RE, _ORG_RE, _PROJECT_RE)
        for value in _unique_matches(pattern, source)
    }
    summary_entities: list[dict[str, str]] = []
    for kind, pattern in (
        ("Person-like name", _PERSON_RE),
        ("Team / organization-like phrase", _ORG_RE),
        ("Project name", _PROJECT_RE),
    ):
        for value in _unique_matches(pattern, summary):
            summary_entities.append({"type": kind, "value": value})

    unsupported_entities = [
        item for item in summary_entities
        if _normalise(item["value"]) not in source_entities
        and _normalise(item["value"]) not in source_norm
    ]

    source_dates = {_normalise(value) for value in _unique_matches(_DATE_RE, source)}
    summary_dates = _unique_matches(_DATE_RE, summary)
    unsupported_dates = [
        value for value in summary_dates
        if _normalise(value) not in source_dates
        and _normalise(value) not in source_norm
    ]

    source_numbers = _number_keys(source)
    unsupported_numbers = sorted(_number_keys(summary) - source_numbers)

    missing_phrases = [
        phrase for phrase in phrases
        if _normalise(phrase) not in summary_norm
    ]

    findings: list[dict[str, str]] = []
    if summary_words > source_words:
        findings.append({
            "severity": "Review",
            "check": "Length",
            "finding": "Summary is longer than its source",
            "detail": (
                f"Source: {source_words} words; summary: {summary_words} words "
                f"({ratio:.2f}× the source length)."
            ),
        })

    for item in unsupported_entities:
        findings.append({
            "severity": "Review",
            "check": "Entity grounding",
            "finding": f"Candidate not found in source: {item['value']}",
            "detail": f"Detected as {item['type'].lower()}; verify against the original source.",
        })

    for value in unsupported_dates:
        findings.append({
            "severity": "Review",
            "check": "Date grounding",
            "finding": f"Date candidate not found in source: {value}",
            "detail": "Confirm that the date is supported by source evidence.",
        })

    for value in unsupported_numbers:
        findings.append({
            "severity": "Review",
            "check": "Number grounding",
            "finding": f"Number candidate not found in source: {value}",
            "detail": "Confirm that this quantity is supported by source evidence.",
        })

    for phrase in missing_phrases:
        findings.append({
            "severity": "Review",
            "check": "Required phrase",
            "finding": f"Required phrase not found: {phrase}",
            "detail": "Exact phrase matching is used; a valid paraphrase may also be flagged.",
        })

    return {
        "status": "Review recommended" if findings else "No heuristic flags",
        "source_word_count": source_words,
        "summary_word_count": summary_words,
        "length_ratio": ratio,
        "expanded": summary_words > source_words,
        "unsupported_entities": unsupported_entities,
        "unsupported_dates": unsupported_dates,
        "unsupported_numbers": unsupported_numbers,
        "missing_required_phrases": missing_phrases,
        "findings": findings,
        "limitations": [
            "Checks are lexical heuristics, not semantic entailment or a truth guarantee.",
            "Named-entity detection uses conservative patterns and may miss names or flag valid paraphrases.",
            "Required phrases use exact normalized matching; semantic equivalents may be marked missing.",
            "A lack of flags does not prove that a summary is fully grounded.",
        ],
    }
