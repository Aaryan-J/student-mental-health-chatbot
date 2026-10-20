"""Tests for the local rule-based reply engine (src/responses.py)."""

import pytest

from src.responses import get_crisis_reply, get_reply

HELPLINES_CONFIG = {
    "crisis_message": "Please reach out for help now.",
    "helplines": [
        {
            "region": "Testland",
            "name": "Test Crisis Line",
            "number": "REPLACE-WITH-LOCAL-NUMBER",
            "note": "REPLACE WITH YOUR COUNTRY'S HELPLINE",
        }
    ],
}


def test_breathing_request_returns_step_by_step():
    reply = get_reply("Can you teach me a breathing exercise?", HELPLINES_CONFIG)
    assert "1." in reply
    assert "Breathe in" in reply


def test_stress_message_returns_stress_reply():
    reply = get_reply("I'm stressed about my exam", HELPLINES_CONFIG)
    assert "normal to feel stressed" in reply.lower()


def test_study_pressure_returns_study_reply():
    reply = get_reply("I have so much homework and revision to do", HELPLINES_CONFIG)
    assert "study" in reply.lower() or "focus" in reply.lower()


def test_counselor_request_returns_counselor_reply():
    reply = get_reply("Can I talk to someone?", HELPLINES_CONFIG)
    assert "counselor" in reply.lower()


def test_helpline_request_lists_numbers():
    reply = get_reply("show me helplines", HELPLINES_CONFIG)
    assert "Test Crisis Line" in reply


def test_unknown_message_returns_fallback():
    reply = get_reply("the weather is nice today", HELPLINES_CONFIG)
    assert "what is on your mind" in reply.lower()


def test_empty_message_is_handled():
    reply = get_reply("   ", HELPLINES_CONFIG)
    assert reply  # non-empty, no crash


def test_crisis_reply_includes_helplines_and_trusted_adult():
    reply = get_crisis_reply(HELPLINES_CONFIG)
    assert "Test Crisis Line" in reply
    assert "trusted adult" in reply.lower()


def test_rant_about_exams_and_stress_returns_reply():
    rant = (
        "honestly I am so stressed right now, I have three exams this week and "
        "I barely slept, I do not know where to even start with revision"
    )
    reply = get_reply(rant, HELPLINES_CONFIG)
    # Should pick one of the clearly present topics, not the fallback.
    assert reply != get_reply("the weather is nice today", HELPLINES_CONFIG)
    assert ("stress" in reply.lower()) or ("study" in reply.lower())


def test_multi_topic_rant_acknowledges_other_theme():
    rant = "I am so stressed about my exam tomorrow and I feel so alone lately"
    reply = get_reply(rant, HELPLINES_CONFIG)
    assert "also noticed" in reply.lower()


def test_typos_are_still_understood():
    reply = get_reply("I am stessed about my exms", HELPLINES_CONFIG)
    # Match the stress reply exactly, not the fallback (which also mentions
    # the word "stress").
    assert "normal to feel stressed" in reply.lower()


def test_burned_out_and_overwhelmed_matches_stress():
    reply = get_reply("I feel so burned out and overwhelmed with homework", HELPLINES_CONFIG)
    assert "normal to feel stressed" in reply.lower()


def test_word_forms_all_match_stress_topic():
    # Regression: "stress", "stressed" and "stressing" must all give the
    # stress reply, not the fallback.
    for phrase in ("I have so much stress", "I am stressed", "I am stressing out"):
        reply = get_reply(phrase, HELPLINES_CONFIG)
        assert "normal to feel stressed" in reply.lower(), phrase


def test_ambiguous_words_do_not_trigger_encouragement():
    # Regression: these are ordinary sentences, not signs of distress.
    for phrase in (
        "shut down the computer",
        "my phone is down",
        "the tank is empty",
        "that is too much work",
        "i am down for it",
    ):
        reply = get_reply(phrase, HELPLINES_CONFIG)
        assert "thank you for sharing" not in reply.lower(), phrase


def test_feeling_words_still_trigger_encouragement():
    for phrase in ("i feel so alone", "i have been feeling down lately", "i am lonely"):
        reply = get_reply(phrase, HELPLINES_CONFIG)
        assert "thank you for sharing" in reply.lower(), phrase

