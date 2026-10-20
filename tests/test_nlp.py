"""Tests for the lightweight NLP helpers (src/nlp.py)."""

from src import nlp


def test_normalize_lowercases_and_collapses_spaces():
    assert nlp.normalize("  I'm  SO   Stressed!  ") == "i'm so stressed!"


def test_tokenize_splits_into_words():
    assert nlp.tokenize("I am stressed, really!") == ["i", "am", "stressed", "really"]


def test_stem_unifies_word_forms():
    assert nlp.stem("stressed") == "stress"
    assert nlp.stem("stressing") == "stress"
    assert nlp.stem("exams") == "exam"


def test_stem_is_consistent_for_same_root():
    # Regression: "stress", "stressed" and "stressing" must all reduce to the
    # SAME stem. Previously "stress" became "stres" while the others became
    # "stress", which broke matching.
    assert nlp.stem("stress") == nlp.stem("stressed") == nlp.stem("stressing")


def test_stem_does_not_strip_double_s():
    # Words ending in "--ss" keep that ending; it is part of the word, not
    # a plural "s".
    assert nlp.stem("stress") == "stress"
    assert nlp.stem("class") == "class"


def test_stem_keeps_short_words():
    assert nlp.stem("sad") == "sad"
    assert nlp.stem("is") == "is"


def _topics():
    return [
        {"name": "stress", "label": "managing stress", "keywords": ("stress", "stressed")},
        {"name": "study", "label": "study pressure", "keywords": ("exam", "homework")},
    ]


def test_score_topics_ranks_strongest():
    scores = nlp.score_topics("I am so stressed about my exam", _topics())
    assert scores[0][0] == "stress"
    names = [name for name, _ in scores]
    assert "study" in names


def test_score_topics_handles_typos():
    scores = nlp.score_topics("I am stessed today", _topics())
    assert scores[0][0] == "stress"
    assert scores[0][1] > 0


def test_score_topics_no_match_returns_zeros():
    scores = nlp.score_topics("the weather is nice", _topics())
    assert all(score == 0 for _, score in scores)


def _topics_with_context():
    return [
        {
            "name": "encouragement",
            "label": "how you are feeling",
            "keywords": ("sad", "alone", "lonely"),
            "ambiguous_keywords": ("down", "empty"),
            "context_words": ("feel", "feeling", "so", "lately"),
        }
    ]


def test_ambiguous_keyword_needs_context():
    # "down" alone (as in "shut down the computer") must NOT match.
    scores = nlp.score_topics("shut down the computer", _topics_with_context())
    assert scores[0][1] == 0


def test_ambiguous_keyword_matches_with_context():
    # "down" with a feeling word nearby SHOULD match.
    scores = nlp.score_topics("i feel so down lately", _topics_with_context())
    assert scores[0][1] > 0


def test_plain_keyword_matches_without_context():
    # Words like "alone" are specific enough on their own.
    scores = nlp.score_topics("i am alone", _topics_with_context())
    assert scores[0][1] > 0
