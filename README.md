# Student Mental Health Support Chatbot

A small, friendly console chatbot that supports students with everyday
wellbeing topics: stress management, breathing and relaxation exercises,
study pressure, encouragement, and pointing them to school counselors and
helplines.

The chatbot runs **fully offline**. It does not use any AI model, API key or
internet connection. All replies come from a simple, explainable rule-based
engine written in plain Python, and the crisis safety check is plain Python
code too.

## SDG 3 - Good Health and Well-being

This project links to **United Nations Sustainable Development Goal 3: Good
Health and Well-being**. SDG 3 aims to ensure healthy lives and promote
well-being for all ages. By giving students quick, judgement-free access to
stress-management tips, calm-down exercises and clear pointers to real
support, this small tool tries to make a positive contribution to student
mental health and well-being.

## Features

- Friendly console chat: type a message, read a reply. Type `quit` to exit.
- Topics covered:
  - stress management
  - breathing and relaxation exercises (step-by-step)
  - study-pressure tips
  - encouragement
  - finding a school counselor or helpline
- A **lightweight, offline NLP layer** (see `src/nlp.py`) so the user can rant:
  - text is normalized and split into words, and simple word endings are
    stripped ("stressed" -> "stress")
  - each topic is **scored** and the strongest one wins, instead of taking the
    first keyword that happens to appear
  - small typos are tolerated using fuzzy matching (`rapidfuzz`)
  - if a long message clearly covers more than one topic, the reply
    acknowledges the other theme too
- A **safety layer written in plain Python** (not left to any AI):
  - a case-insensitive keyword check for self-harm or suicide terms
  - it stays strict and deterministic (no fuzzy matching) so it is predictable
  - when triggered, the normal reply is skipped entirely and a crisis message
    with helplines is shown, urging the user to contact a trusted adult **now**
- Helplines are loaded from `config/helplines.json`, so they are easy to edit.
- Runs the same way on **Windows and Linux** with no manual tweaking.

## Limitations and safety disclaimer

- This chatbot is **not a therapist, doctor, or counselor**. It **cannot
  diagnose** any condition or give medical advice.
- It gives **general wellbeing tips only**. It is not a substitute for
  professional help.
- It is **not a trained AI model**. The NLP is a small set of rules: scoring
  keywords with light stemming and fuzzy matching. It understands many rants,
  but unusual phrasings, sarcasm or indirect hints can still be missed.
- Its replies come from fixed, pre-written rules, so they will not always
  perfectly match what the user meant.
- The crisis check is a keyword check. It is deliberately simple and
  predictable, but it cannot catch every possible way of expressing distress.
- **Always tell your users to talk to a trusted adult, school counselor or a
  real helpline.**

## How to run

Just run:

```
python run.py
```

On Windows you may need to use:

```
py run.py
```

On first run, `run.py` will:

1. Check that Python 3.9 or newer is being used.
2. Create a `.venv` virtual environment if one does not exist.
3. Install `requirements.txt` into that `.venv` if needed.
4. Copy `.env.example` to `.env` if `.env` does not exist yet.
5. Re-launch the chatbot using the `.venv` Python.

It needs no API key. On the very first run it needs an internet connection
only to download the small packages in `requirements.txt`.

## How to run the tests

The tests use `pytest`:

```
python -m pytest
```

If you ran `run.py` at least once, the `.venv` already contains `pytest`. To
run the tests using the virtual environment's Python directly:

- Windows: `.venv\Scripts\python -m pytest`
- Linux/macOS: `.venv/bin/python -m pytest`

## Project structure

```
chatbot/
|-- run.py                  # entry point: sets up the venv and launches the bot
|-- requirements.txt        # python-dotenv, rapidfuzz, pytest
|-- .env.example            # optional settings (no secrets, no API key)
|-- .gitignore
|-- LICENSE                 # MIT License
|-- README.md
|-- config/
|   `-- helplines.json      # helplines and the crisis message (EDIT THIS)
|-- src/
|   |-- __init__.py
|   |-- paths.py            # pathlib-based project-root path handling
|   |-- config.py           # loads .env and helplines.json (UTF-8)
|   |-- nlp.py              # lightweight offline NLP: normalize/stem/score
|   |-- safety.py           # plain-Python crisis keyword check
|   |-- responses.py        # local rule-based reply engine
|   `-- chatbot.py          # console loop and topics
`-- tests/
    |-- test_nlp.py         # NLP helper tests
    |-- test_safety.py      # crisis check tests
    `-- test_responses.py   # rule-engine tests
```

## How to replace the helpline numbers

The helplines are placeholders and **must be replaced** before you share this
project with anyone. Open `config/helplines.json` and edit each entry:

```json
{
  "crisis_message": "...",
  "helplines": [
    {
      "region": "Your Country",
      "name": "National Crisis / Suicide Prevention Line",
      "number": "REPLACE-WITH-LOCAL-NUMBER",
      "note": "REPLACE WITH YOUR COUNTRY'S HELPLINE"
    }
  ]
}
```

Replace the `region`, `name`, `number` and `note` values with real helpline
details for your country. You can add or remove entries as needed. Every value
is plain text; keep the file valid JSON (commas between entries, no trailing
comma on the last item).

You can find official helplines through your national health service or the
[IASP crisis centre list](https://www.iasp.info/resources/Crisis_Centres/).

## License

This project is released under the MIT License. See [LICENSE](LICENSE).
