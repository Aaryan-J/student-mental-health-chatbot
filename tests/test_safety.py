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
        # Expanded ideation phrases.
        "I wish I was dead",
        "I want to end it all",
        "I am better off dead",
        "I do not deserve to live",
        "there is no reason to live",
        "I want to hurt myself",
        "I keep cutting myself",
        "I do not want to be here anymore",
        "I cannot go on anymore",
        "I want to sleep and never wake up",
        "everyone would be better without me",
        "I have suicidal thoughts",
        "I have no way out",
        "nothing to live for",
        "I cannot take it anymore",
        "I want to disappear forever",
        "I am thinking about ending everything",
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
        "I am so tired I could sleep forever",
        "this game is killing me",
        "I killed it on the test",
        "the battery is dead",
        "better off without my old phone",
        "cutting it close on the deadline",
        "I want to disappear from social media",
        "I want to be dead honest with you",
        "",
    ],
)
def test_normal_messages_do_not_trigger(message):
    assert is_crisis(message) is False


@pytest.mark.parametrize(
    "message",
    [
        "I want to self-harm",
        "self harm",
        "I don't want to live",
        "I can't go on anymore",
        "I wish I were dead",
        "I am better-off dead",
    ],
)
def test_hyphen_and_apostrophe_variants_trigger(message):
    # Hyphens and apostrophes must not hide a crisis phrase.
    assert is_crisis(message) is True
