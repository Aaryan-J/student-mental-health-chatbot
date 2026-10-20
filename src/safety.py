"""Safety layer: a plain-Python crisis keyword check.

This module is intentionally NOT powered by any AI. It is a simple,
case-insensitive phrase check so that self-harm or suicide related messages are
caught reliably and the chatbot can respond with a crisis message and helplines
instead of a normal reply.

Keeping this as explicit code (rather than leaving it to a model) makes the
behaviour predictable and easy to explain.

Notes:
  * Text is normalized the same way as everything else (lower case, apostrophes
    removed, hyphens turned into spaces, whitespace collapsed). So the phrases
    below are written in their "folded" form, for example "self harm" covers
    both "self harm" and "self-harm", and "cant" covers "can't".
  * Matching uses whole-word phrase matching (see nlp._phrase_present) so a
    phrase only fires when it appears as complete words. This keeps it
    deterministic and avoids most accidental matches.
"""

from typing import Final, Tuple

from . import nlp

# Phrases that should always trigger the crisis response.
# Written in folded/normalized form (see module docstring). Kept strictly
# deterministic - no fuzzy matching - because on a safety-critical check it is
# better to be predictable.
CRISIS_KEYWORDS: Final[Tuple[str, ...]] = (
    # Direct mentions.
    "suicide",
    "suicidal",
    "suicidal thoughts",
    "kill myself",
    "killing myself",
    "kill my self",
    "end my life",
    "ending my life",
    "take my life",
    "taking my life",
    "end it all",
    "ending it all",
    "ending everything",
    "end everything",
    "self harm",
    "selfharm",
    "self harming",
    "hurt myself",
    "hurting myself",
    "harm myself",
    "harming myself",
    "cut myself",
    "cutting myself",
    "want to die",
    "wanna die",
    "wanted to die",
    "wish i was dead",
    "wish i were dead",
    "better off dead",
    # Not wanting to live / be here.
    "dont want to live",
    "do not want to live",
    "not want to live",
    "dont want to be here",
    "do not want to be here",
    "no reason to live",
    "nothing to live for",
    "dont deserve to live",
    "do not deserve to live",
    "cant go on living",
    "can not go on living",
    "cannot go on living",
    "cant go on anymore",
    "cannot go on anymore",
    "cant keep going",
    "cannot keep going",
    "cant take it anymore",
    "cannot take it anymore",
    # Disappearing / never waking up.
    "want to disappear forever",
    "disappear forever",
    "sleep and never wake up",
    "never wake up",
    "not wake up",
    # Feeling like a burden worth removing.
    "better off without me",
    "better off if i was gone",
    "better off if i were gone",
    "everyone would be better without me",
    "notice if i was gone",
    "notice if i were gone",
    "notice if i disappeared",
    # Hopelessness that often accompanies ideation.
    "no way out",
    "nothing matters anymore",
)


def is_crisis(text: str) -> bool:
    """Return True if the message contains a crisis phrase.

    Matching is case-insensitive and folded, so "SUICIDE", "Kill Myself" and
    "self-harm" / "self harm" all trigger the check. A phrase only fires when
    it appears as whole words.
    """
    if not text:
        return False

    normalized = nlp.normalize(text)
    return any(
        nlp.phrase_present(keyword, normalized) for keyword in CRISIS_KEYWORDS
    )
