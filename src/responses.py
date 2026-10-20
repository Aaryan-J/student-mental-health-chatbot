"""Local rule-based reply engine.

This is the "brain" of the chatbot. It does not use any AI model or network
connection. Instead it matches keywords in the user's message to one of a few
support topics and returns a helpful, pre-written response:

  * stress management
  * breathing / relaxation (step-by-step)
  * study pressure
  * encouragement
  * pointing to a school counselor or helpline

Everything returned here is plain ASCII text so it displays correctly in the
Windows terminal as well as on Linux.
"""

from typing import Any, Dict, List

# Each topic has a set of keywords and a reply. Order matters: the first topic
# whose keywords appear in the message is used.
_INTENTS: List[Dict[str, Any]] = [
    {
        "name": "breathing",
        "keywords": (
            "breathing", "breathe", "breath", "relax", "calm",
            "grounding", "panic", "meditation", "quiet",
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
        "keywords": (
            "stress", "stressed", "anxious", "anxiety", "worried",
            "overwhelmed", "pressure", "nervous", "panic attack",
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
        "keywords": (
            "study", "studying", "exam", "exams", "test", "tests",
            "grades", "marks", "homework", "assignment", "revision",
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
        "keywords": (
            "counselor", "counsellor", "therapist", "help line", "helpline",
            "talk to someone", "support", "professional", "trusted adult",
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
        "keywords": (
            "sad", "down", "lonely", "alone", "tired", "give up",
            "not good enough", "worthless", "hopeless", "discouraged",
            "fail", "failed", "failing",
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


def _format_helplines(helplines: List[Dict[str, Any]]) -> str:
    """Turn the helpline list into a readable block of text."""
    lines = []
    for entry in helplines:
        region = entry.get("region", "")
        name = entry.get("name", "")
        number = entry.get("number", "")
        note = entry.get("note", "")
        line = "  - {name} ({region}): {number}".format(
            name=name, region=region, number=number
        )
        if note:
            line += "  [{0}]".format(note)
        lines.append(line)
    return "\n".join(lines)


def get_reply(message: str, helplines_config: Dict[str, Any]) -> str:
    """Return a local, rule-based reply for the given message.

    The helplines config is used only when the user explicitly asks for
    helplines (for example by typing 'helplines').
    """
    if not message or not message.strip():
        return "I am listening whenever you are ready. What is on your mind?"

    lowered = message.lower()

    # Explicit request for helplines -> show the configured numbers.
    if "helpline" in lowered or "help line" in lowered:
        helplines = helplines_config.get("helplines", [])
        if helplines:
            return (
                "Here are some helplines you can contact. They are free and "
                "confidential:\n" + _format_helplines(helplines) + "\n"
                "Please also consider telling a trusted adult or your school "
                "counselor."
            )

    # Match the first topic whose keywords appear in the message.
    for intent in _INTENTS:
        if any(keyword in lowered for keyword in intent["keywords"]):
            return intent["reply"]

    return _FALLBACK


def get_crisis_reply(helplines_config: Dict[str, Any]) -> str:
    """Build the crisis response shown when the safety check triggers.

    This is shown INSTEAD of a normal reply. It urges the user to reach a
    trusted adult immediately and lists the configured helplines.
    """
    message = helplines_config.get(
        "crisis_message",
        "Please reach out to a trusted adult or a helpline right now.",
    )
    helplines = helplines_config.get("helplines", [])

    parts = [message]
    if helplines:
        parts.append("Helplines you can contact now:")
        parts.append(_format_helplines(helplines))
    parts.append(
        "Please talk to a trusted adult - a parent, guardian, teacher, or "
        "school counselor - right now. You deserve support, and you do not "
        "have to go through this alone."
    )
    return "\n".join(parts)
