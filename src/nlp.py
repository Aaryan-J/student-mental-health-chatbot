"""A small, offline NLP helper layer.

This is NOT a trained AI model. It is a lightweight, explainable toolkit that
helps the chatbot understand longer, messier messages (rants) by:

  * normalizing text (lower case, no punctuation),
  * splitting it into word tokens,
  * reducing words to a simple stem so "stressed", "stressing" and "stress"
    all count as the same word,
  * counting how strongly a message matches each topic's keywords, including
    tolerance for small typos using rapidfuzz.

Everything here runs locally with no network access.
"""

import re
from typing import Dict, Iterable, List, Tuple

from rapidfuzz import fuzz

# Words are sequences of letters, digits and apostrophes.
_TOKEN_RE = re.compile(r"[a-z0-9']+")

# Minimum similarity (0-100) for two words to be treated as the same word.
FUZZY_THRESHOLD = 88


def normalize(text: str) -> str:
    """Lower-case the text and collapse whitespace.

    Punctuation is left in place for phrase matching; use tokenize() when you
    want clean words.
    """
    return re.sub(r"\s+", " ", (text or "").lower()).strip()


def tokenize(text: str) -> List[str]:
    """Return a list of clean word tokens from the text."""
    return _TOKEN_RE.findall(normalize(text))


def stem(word: str) -> str:
    """Reduce a word to a rough stem by stripping common suffixes.

    This is intentionally simple (no external stemmer), just enough to unify
    related forms like "stressed" -> "stress" and "studying" -> "study".
    """
    for suffix in ("ing", "edly", "ed", "es", "s"):
        if len(word) > len(suffix) + 2 and word.endswith(suffix):
            return word[: -len(suffix)]
    return word


def _phrase_present(needle: str, haystack: str) -> bool:
    """Return True if a multi-word phrase appears in the normalized text."""
    return needle in haystack


def match_keyword(keyword: str, text_norm: str, tokens: List[str], stems: List[str]) -> int:
    """Count how well one keyword matches, returning 0 or more hits.

    A keyword can be:
      * a multi-word phrase (matched against the whole normalized text), or
      * a single word (matched against tokens, with stem + fuzzy tolerance).
    """
    keyword = keyword.lower().strip()
    if not keyword:
        return 0

    # Multi-word phrases are matched as a substring of the normalized text.
    if " " in keyword:
        return 1 if _phrase_present(keyword, text_norm) else 0

    key_stem = stem(keyword)

    # Exact token or stem match.
    if keyword in tokens or key_stem in stems:
        return 1

    # Fuzzy match for small typos, e.g. "stessed" -> "stressed".
    for token in tokens:
        if len(token) >= 4 and fuzz.ratio(token, keyword) >= FUZZY_THRESHOLD:
            return 1
    return 0


def _keyword_weight(keyword: str) -> int:
    """Give more specific keywords (longer / multi-word) a higher weight."""
    if " " in keyword:
        return 3
    return 2 if len(keyword) >= 7 else 1


def score_topics(
    text: str, topics: Iterable[Dict]
) -> List[Tuple[str, int]]:
    """Score each topic against the text and return (name, score) sorted desc.

    A topic's score is the sum of the weights of the keywords that matched.
    Longer, multi-word keywords count more than short single words, so a
    message that clearly mentions "panic attack" ranks above one that only
    brushed past a short word by accident.
    """
    text_norm = normalize(text)
    tokens = tokenize(text)
    stems = [stem(t) for t in tokens]

    results: List[Tuple[str, int]] = []
    for topic in topics:
        score = 0
        for keyword in topic["keywords"]:
            if match_keyword(keyword, text_norm, tokens, stems):
                score += _keyword_weight(keyword)
        results.append((topic["name"], score))

    # Sort by score descending; Python's sort is stable so ties keep the
    # original topic order.
    results.sort(key=lambda item: item[1], reverse=True)
    return results
