"""A small, offline NLP helper layer.

This is NOT a trained AI model. It is a lightweight, explainable toolkit that
helps the chatbot understand longer, messier messages (rants) by:

  * normalizing text (lower case, collapsed whitespace),
  * splitting it into word tokens,
  * reducing words to a simple stem so "stressed", "stressing" and "stress"
    all count as the same word,
  * counting how strongly a message matches each topic's keywords, including
    tolerance for small typos using rapidfuzz.

Everything here runs locally with no network access.
"""

import re
from typing import Dict, Iterable, List, Set, Tuple

from rapidfuzz import fuzz

# Words are sequences of letters, digits and apostrophes.
_TOKEN_RE = re.compile(r"[a-z0-9']+")

# Minimum similarity (0-100) for two words to be treated as the same word.
# Kept fairly high so only close typos match, not unrelated words.
FUZZY_THRESHOLD = 90

# Only words at least this long are fuzzy-matched, to avoid short-word noise.
FUZZY_MIN_LENGTH = 5


def normalize(text: str) -> str:
    """Lower-case the text and collapse whitespace.

    Apostrophes and other punctuation are kept in place (only leading and
    trailing whitespace is removed), which lets multi-word phrases match as
    written. Use tokenize() when you want clean words.
    """
    return re.sub(r"\s+", " ", (text or "").lower()).strip()


def tokenize(text: str) -> List[str]:
    """Return a list of clean word tokens from the text."""
    return _TOKEN_RE.findall(normalize(text))


def stem(word: str) -> str:
    """Reduce a word to a rough stem by stripping common suffixes.

    This is intentionally simple (no external stemmer), but it is designed to
    be *consistent*: it strips at most one suffix, longest first, and never
    strips a trailing "s" that would leave a too-short stem. That keeps
    related forms together, for example:

        "stressed"  -> "stress"
        "stressing" -> "stress"
        "stress"    -> "stress"   (unchanged)
        "studies"   -> "studi"
        "study"     -> "study"
    """
    word = word or ""
    for suffix in ("ing", "edly", "ed", "s"):
        if word.endswith(suffix) and len(word) - len(suffix) >= 3:
            # Guard: a single trailing "s" is usually a plural, but "--ss"
            # (as in "stress") is part of the word, so never strip that.
            if suffix == "s" and word.endswith("ss"):
                continue
            return word[: -len(suffix)]
    return word


def _phrase_present(needle: str, haystack: str) -> bool:
    """Return True if a multi-word phrase appears in the normalized text."""
    return needle in haystack


def match_keyword(
    keyword: str, text_norm: str, tokens: List[str], token_stems: Set[str]
) -> int:
    """Return 1 if one keyword matches the message, otherwise 0.

    A keyword can be:
      * a multi-word phrase (matched against the whole normalized text), or
      * a single word (matched against tokens by exact form, by stem, or by a
        close fuzzy match for small typos).
    """
    keyword = keyword.lower().strip()
    if not keyword:
        return 0

    # Multi-word phrases are matched as a substring of the normalized text.
    if " " in keyword:
        return 1 if _phrase_present(keyword, text_norm) else 0

    # Exact token match, or either the keyword or the token stems to the other.
    # Comparing both directions makes the match robust to which word carries
    # the suffix (e.g. keyword "stress" vs token "stressed").
    if keyword in tokens or stem(keyword) in token_stems:
        return 1

    # Fuzzy match for small typos, e.g. "stessed" -> "stressed".
    if len(keyword) >= FUZZY_MIN_LENGTH:
        key_stem = stem(keyword)
        for token in tokens:
            if len(token) < FUZZY_MIN_LENGTH:
                continue
            if (
                fuzz.ratio(token, keyword) >= FUZZY_THRESHOLD
                or fuzz.ratio(stem(token), key_stem) >= FUZZY_THRESHOLD
            ):
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

    Some topics also list ``ambiguous_keywords``. Those are common words that
    are only meaningful in context (for example "down" or "alone"). They are
    counted ONLY when the message also contains one of the topic's
    ``context_words`` (for example "feel" or "sad"). This stops ordinary
    sentences like "shut down the computer" from being misread.
    """
    text_norm = normalize(text)
    tokens = tokenize(text)
    token_stems = {stem(t) for t in tokens}

    results: List[Tuple[str, int]] = []
    for topic in topics:
        # Plain keywords always count.
        score = 0
        for keyword in topic.get("keywords", ()):
            if match_keyword(keyword, text_norm, tokens, token_stems):
                score += _keyword_weight(keyword)

        # Ambiguous keywords need a context word somewhere in the message.
        ambiguous = topic.get("ambiguous_keywords", ())
        if ambiguous:
            context = topic.get("context_words", ())
            context_present = any(
                match_keyword(word, text_norm, tokens, token_stems) for word in context
            )
            if context_present:
                for keyword in ambiguous:
                    if match_keyword(keyword, text_norm, tokens, token_stems):
                        score += _keyword_weight(keyword)

        results.append((topic["name"], score))

    # Sort by score descending; Python's sort is stable so ties keep the
    # original topic order.
    results.sort(key=lambda item: item[1], reverse=True)
    return results
