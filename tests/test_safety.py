"""Tests for the crisis safety check (src/safety.py).

These tests confirm that:
  * crisis phrases trigger the check in any letter case, and
  * ordinary messages that mention stress or exams do NOT trigger it.
"""

import pytest

from src.safety import is_crisis


@pytest.mark.parametrize(
    "message",
    [
        "I want to kill myself",
        "I have been thinking about suicide",
        "sometimes I self harm",
        "I want to end my life",
        "I just want to die",
        "I do not want to live anymore",
    ],
)
def test_crisis_phrases_trigger(message):
    assert is_crisis(message) is True


@pytest.mark.parametrize(
    "message",
    [
        "SUICIDE",
        "I want to KILL MYSELF",
        "Kill Myself",
        "I WANT TO DIE",
        "Self Harm",
        "End My Life",
    ],
)
def test_crisis_check_is_case_insensitive(message):
    # The same phrases in different casing must still trigger.
    assert is_crisis(message) is True


@pytest.mark.parametrize(
    "message",
    [
        "I'm stressed about my exam",
        "I feel anxious about my grades",
        "Can you teach me a breathing exercise?",
        "School is really hard right now",
        "I am worried about my test tomorrow",
        "Where can I find a school counselor?",
        "I feel sad and tired",
        "I keep failing my homework",
        "",
    ],
)
def test_normal_messages_do_not_trigger(message):
    assert is_crisis(message) is False
