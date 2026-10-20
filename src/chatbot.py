"""Console chat interface and program entry logic.

This module wires together configuration, the safety check and the local
rule-based response engine, and runs a simple input/print loop.

Run it with:  python -m src.chatbot
(Type 'quit' or 'exit' to leave.)
"""

import sys
from typing import Any, Dict

from . import config, responses, safety

# ASCII-only banner so it renders correctly in the Windows terminal.
BANNER = (
    "========================================================\n"
    "  School Support Bot - a friendly student wellbeing chat\n"
    "========================================================\n"
)

DISCLAIMER = (
    "I am a support chatbot, not a therapist or a doctor. I cannot diagnose\n"
    "any condition or give medical advice. If you are in danger or in crisis,\n"
    "please contact a trusted adult or a helpline right away. You can type\n"
    "'helplines' at any time to see helpline numbers.\n"
)

HELP = (
    "You can talk to me about:\n"
    "  - stress management\n"
    "  - breathing and relaxation exercises\n"
    "  - study pressure and exams\n"
    "  - encouragement when you feel low\n"
    "  - finding a school counselor or helpline\n"
    "Type 'help' to see this again, or 'quit' to exit."
)


def _print(message: str = "") -> None:
    """Print a line of ASCII text, safely flushing the buffer."""
    print(message, flush=True)


def main() -> int:
    """Run the chatbot loop. Returns a process exit code."""
    # Load .env (optional settings) and the helplines config.
    config.load_env()
    bot_name = config.get_bot_name()
    helplines_config: Dict[str, Any] = config.load_helplines()

    _print(BANNER)
    _print("Hi, I am {0}. I am glad you are here.".format(bot_name))
    _print(DISCLAIMER)
    _print(HELP)
    _print("")

    while True:
        try:
            user_input = input("You: ")
        except (EOFError, KeyboardInterrupt):
            # Ctrl+C or closed input stream: exit cleanly.
            _print("")
            _print("{0}: Take care of yourself. Goodbye.".format(bot_name))
            return 0

        message = user_input.strip()
        if not message:
            _print("{0}: I am listening whenever you are ready.".format(bot_name))
            continue

        lowered = message.lower()

        if lowered in ("quit", "exit"):
            _print("{0}: Take care of yourself. Goodbye.".format(bot_name))
            return 0

        if lowered in ("help", "?", "commands"):
            _print("{0}: {1}".format(bot_name, HELP))
            continue

        # SAFETY FIRST: a plain-Python crisis check runs before any reply.
        # This is not left to the AI/model; it is explicit code.
        if safety.is_crisis(message):
            _print("")
            _print("{0}: {1}".format(
                bot_name, responses.get_crisis_reply(helplines_config)
            ))
            _print("")
            continue

        # Normal path: local rule-based reply (no network, no API key).
        reply = responses.get_reply(message, helplines_config)
        _print("{0}: {1}".format(bot_name, reply))
        _print("")


if __name__ == "__main__":
    sys.exit(main())
