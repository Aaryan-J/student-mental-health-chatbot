"""Local rule-based reply engine with lightweight NLP scoring.

This is the "brain" of the chatbot. It does not use any AI model or network
connection. Instead it scores the user's message against a few support topics
and returns a helpful, pre-written response:

  * stress management
  * breathing / relaxation (step-by-step)
  * study pressure
  * encouragement
  * pointing to a school counselor or helpline

Longer, messier messages (rants) are handled by the helper layer in `nlp.py`:
every topic is scored and the strongest one wins. If more than one topic shows
up clearly, the reply acknowledges the others too.

Everything returned here is plain ASCII text so it displays correctly in the
Windows terminal as well as on Linux.
"""

from typing import Any, Dict, List

from . import nlp

# Each topic has a set of keywords and a reply. The chatbot scores ALL topics
# and picks the strongest, so the order here only breaks ties.
_INTENTS: List[Dict[str, Any]] = [
    {
        "name": "breathing",
        "label": "calming your body down",
        "keywords": (
            "breath", "breathe", "relax", "calm", "grounding",
            "meditation", "meditate", "mindfulness", "panic", "panic attack",
            "breathe in", "breathe out", "slow down", "slow breathing",
            "heart racing", "heart pounding", "cant breathe", "breathless",
            "cant catch my breath", "hyperventilating", "hyperventilate",
            "chest tight", "chest feels tight", "hands are shaking", "shaking",
            "light headed", "lightheaded", "dizzy", "ground myself",
            "calm down", "calm myself",
        ),
        "reply": (
            "Let us try a simple breathing exercise together. It is called "
            "box breathing and it is easy to follow:\n"
            "  1. Sit comfortably and let your shoulders relax.\n"
            "  2. Breathe in slowly through your nose for 4 seconds.\n"
            "  3. Hold your breath gently for 4 seconds.\n"
            "  4. Breathe out slowly through your mouth for 4 seconds.\n"
            "  5. Wait 4 seconds, then repeat the cycle 4 or 5 times.\n"
            "If you feel dizzy, go back to your normal breathing. Doing this "
            "before study or a test can help your body feel calmer."
        ),
    },
    {
        "name": "stress",
        "label": "managing stress",
        "keywords": (
            "stress", "anxious", "anxiety", "worry", "overwhelmed",
            "nervous", "cant cope", "cope", "burned out", "burnt out",
            "freaking out", "stressed out", "under pressure", "on edge",
            "tense", "cant handle", "cannot handle", "breaking point",
            "at my breaking point", "drowning", "piling up", "at my limit",
            "reaching my limit", "losing it", "losing my mind", "spiraling",
            "overthink", "wound up", "cant relax", "no control",
            "everything is too much", "cant sleep", "cannot sleep",
            "trouble sleeping", "cant switch off", "cant switch my brain off",
        ),
        # "pressure" and "too much" are common words, so they only count when
        # the message is clearly about feelings.
        "ambiguous_keywords": ("pressure", "too much"),
        "context_words": (
            "feel", "feeling", "felt", "overwhelmed", "anxious", "stressed",
            "cope", "coping", "cant", "school", "exam", "exams", "study",
            "homework", "handle", "deal", "parents", "family", "friends",
            "everyone",
        ),
        "reply": (
            "It is really normal to feel stressed sometimes, and it does not "
            "mean something is wrong with you. A few things that often help:\n"
            "  - Name what you are feeling, out loud or in writing.\n"
            "  - Break the big thing into one small next step.\n"
            "  - Move your body for a few minutes (a short walk counts).\n"
            "  - Take a slow breathing break (ask me for a breathing exercise).\n"
            "  - Talk to someone you trust about how you feel.\n"
            "You do not have to handle everything at once."
        ),
    },
    {
        "name": "study",
        "label": "study pressure",
        "keywords": (
            "study", "exam", "finals", "test", "quiz", "grades", "marks",
            "homework", "assignment", "revision", "revise", "coursework",
            "school work", "deadline", "behind on", "falling behind",
            "cant focus", "cannot focus", "procrastinate", "no time to study",
            "too much homework", "too many assignments", "failing my exam",
            "failing my finals", "failing my test", "fail my finals",
            "exam stress", "test stress", "study stress",
        ),
        "reply": (
            "Study pressure can feel heavy, so let us make it more manageable:\n"
            "  - Pick ONE subject or task to focus on right now.\n"
            "  - Work in short blocks, for example 25 minutes, then a 5 min break.\n"
            "  - Put your phone in another room while you work.\n"
            "  - Write down the smallest first step, then just do that one.\n"
            "  - Remind yourself: your grades matter, but they do not measure "
            "your worth as a person.\n"
            "You are allowed to do your best without being perfect."
        ),
    },
    {
        "name": "counselor",
        "label": "finding real support",
        "keywords": (
            "counselor", "counsellor", "therapist", "therapy", "help line",
            "helpline", "talk to someone", "speak to someone",
            "talk to a professional", "see someone", "professional",
            "trusted adult", "school nurse", "school counselor",
            "get help", "need help", "help me", "reach out", "get support",
            "who can i talk to", "mental health",
        ),
        # "support" alone is too generic (e.g. "tech support").
        "ambiguous_keywords": ("support",),
        "context_words": (
            "need", "want", "find", "get", "school", "someone", "talk", "help",
            "mental", "emotional",
        ),
        "reply": (
            "Reaching out is a brave and smart thing to do. A school counselor "
            "or a trusted adult can give you real support that a chatbot cannot:\n"
            "  - A school counselor can talk with you privately and confidentially.\n"
            "  - A teacher, parent, or guardian you trust is a good first step too.\n"
            "  - Helplines are free and you do not have to give your name.\n"
            "You can also ask me for a helpline number, or type 'helplines'."
        ),
    },
    {
        "name": "encouragement",
        "label": "how you are feeling",
        "keywords": (
            "sad", "tired", "exhausted", "give up", "giving up",
            "not good enough", "worthless", "hopeless", "discouraged", "fail",
            "failure", "hate myself", "hate my life", "no one cares",
            "nobody likes me",
            "no friends", "cant do this", "unhappy", "alone", "lonely",
            "burden", "a burden", "like a burden", "invisible",
            "not good at anything", "want to cry", "like crying",
            "feel like crying", "scared", "afraid", "trapped", "stuck", "numb",
            "feel numb", "angry", "so angry", "upset", "miserable",
        ),
        # "down" and "empty" are too common on their own (e.g. "shut down the
        # computer" or "the tank is empty"), so require a feeling word nearby.
        "ambiguous_keywords": ("down", "empty"),
        "context_words": (
            "feel", "feeling", "felt", "so", "really", "very", "lately",
            "inside", "know why",
        ),
        "reply": (
            "Thank you for sharing that with me. Feeling this way is hard, and "
            "you are not alone in it. A few gentle reminders:\n"
            "  - You have gotten through difficult days before.\n"
            "  - One bad day or one bad grade does not define you.\n"
            "  - Rest and asking for help are strengths, not weaknesses.\n"
            "  - If it feels like too much, please tell a trusted adult today.\n"
            "I am here to listen, and you matter a great deal."
        ),
    },
]

# Friendly general reply when nothing else matches.
_FALLBACK = (
    "Thanks for telling me that. I am here for you. I can help with stress, "
    "breathing and relaxation exercises, study pressure, and encouragement, "
    "and I can point you to a school counselor or a helpline.\n"
    "Could you tell me a bit more about what is on your mind? For example, "
    "try saying 'I feel stressed about my exams' or 'teach me a breathing "
    "exercise'."
)


def _format_helplines(helplines: Any) -> str:
    """Turn the helpline list into a readable block of text.

    Defensive: if the value is not a list (for example a bad config file), or
    an entry is malformed, we skip the bad parts instead of crashing. All
    values are coerced to text so a number stored as a JSON number still works.
    """
    if not isinstance(helplines, list):
        return ""

    lines = []
    for entry in helplines:
        if not isinstance(entry, dict):
            continue
        region = str(entry.get("region", ""))
        name = str(entry.get("name", ""))
        number = str(entry.get("number", ""))
        note = str(entry.get("note", ""))
        line = "  - {name} ({region}): {number}".format(
            name=name, region=region, number=number
        )
        if note:
            line += "  [{0}]".format(note)
        lines.append(line)
    return "\n".join(lines)


def _intent_by_name(name: str) -> Dict[str, Any]:
    """Look up a topic definition by its name."""
    for intent in _INTENTS:
        if intent["name"] == name:
            return intent
    return _INTENTS[0]


def _build_reply(message: str) -> str:
    """Score the message against every topic and build the best reply.

    The strongest topic decides the main reply. If a second topic is also
    clearly present, we add a short line acknowledging it, so a long rant
    about several things still feels heard.
    """
    scores = nlp.score_topics(message, _INTENTS)
    top_name, top_score = scores[0]

    # Nothing matched with any confidence -> friendly fallback.
    if top_score == 0:
        return _FALLBACK

    reply = _intent_by_name(top_name)["reply"]

    # Acknowledge up to two other themes that are clearly present (at least
    # about a third of the top score), so a long rant still feels heard.
    others = [
        (name, score)
        for name, score in scores[1:]
        if score > 0 and score * 3 >= top_score
    ][:2]
    if others:
        other_labels = [_intent_by_name(name)["label"] for name, _ in others]
        reply += (
            "\n\nI also noticed you mentioned "
            + " and ".join(other_labels)
            + ". We can talk about that too whenever you are ready."
        )

    return reply


def get_reply(message: str, helplines_config: Dict[str, Any]) -> str:
    """Return a local, rule-based reply for the given message.

    The helplines config is used only when the user explicitly asks for
    helplines (for example by typing 'helplines').
    """
    if not message or not message.strip():
        return "I am listening whenever you are ready. What is on your mind?"

    lowered = nlp.normalize(message)

    # Explicit request for helplines -> show the configured numbers.
    if "helpline" in lowered or "help line" in lowered:
        formatted = _format_helplines(helplines_config.get("helplines", []))
        if formatted:
            return (
                "Here are some helplines you can contact. They are free and "
                "confidential:\n" + formatted + "\n"
                "Please also consider telling a trusted adult or your school "
                "counselor."
            )

    return _build_reply(message)


def get_crisis_reply(helplines_config: Dict[str, Any]) -> str:
    """Build the crisis response shown when the safety check triggers.

    This is shown INSTEAD of a normal reply. It urges the user to reach a
    trusted adult immediately and lists the configured helplines.
    """
    message = helplines_config.get(
        "crisis_message",
        "Please reach out to a trusted adult or a helpline right now.",
    )
    formatted = _format_helplines(helplines_config.get("helplines", []))

    parts = [message]
    if formatted:
        parts.append("Helplines you can contact now:")
        parts.append(formatted)
    parts.append(
        "Please talk to a trusted adult - a parent, guardian, teacher, or "
        "school counselor - right now. You deserve support, and you do not "
        "have to go through this alone."
    )
    return "\n".join(parts)
