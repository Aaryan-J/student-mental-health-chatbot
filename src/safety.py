"""Safety layer: a plain-Python crisis keyword check.

This module is intentionally NOT powered by any AI. It is a simple,
case-insensitive substring check so that self-harm or suicide related messages
are caught reliably and the chatbot can respond with a crisis message and
helplines instead of a normal reply.

Keeping this as explicit code (rather than leaving it to a model) makes the
behaviour predictable and easy to explain.
"""

from typing import Final, Tuple

from . import nlp

# Phrases that should always trigger the crisis response.
# All matching is done in lower case, so the words below are lower case too.
# This list stays deliberately strict (exact normalized phrases plus a few
# safe variant spellings) - we do NOT use fuzzy matching here, because on a
# safety-critical check it is better to be predictable.
CRISIS_KEYWORDS: Final[Tuple[str, ...]] = (
    "suicide",
    "suicidal",
    "kill myself",
    "kill my self",
    "killing myself",
    "self harm",
    "self-harm",
    "selfharm",
    "end my life",
    "ending my life",
    "take my life",
    "want to die",
    "wanna die",
    "wanted to die",
    "dont want to live",
    "don't want to live",
    "do not want to live",
    "not want to live",
)


def is_crisis(text: str) -> bool:
    """Return True if the message contains a crisis keyword.

    Matching is case-insensitive and ignores repeated whitespace, so
    "SUICIDE", "Kill Myself" and "i want to die" all trigger the check.
    Hyphenated and spaced forms ("self harm" / "self-harm") are both covered.
    """
    if not text:
        return False

    normalized = nlp.normalize(text)
    return any(keyword in normalized for keyword in CRISIS_KEYWORDS)
