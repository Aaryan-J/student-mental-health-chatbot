"""Central path handling for the project.

All paths are resolved relative to the project root (the folder that contains
run.py), never relative to the current working directory. This keeps the tool
working no matter where it is launched from on Windows or Linux.
"""

from pathlib import Path

# src/paths.py -> parent is "src", parent.parent is the project root.
PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent

# Named locations used across the project.
CONFIG_DIR: Path = PROJECT_ROOT / "config"
HELPLINES_FILE: Path = CONFIG_DIR / "helplines.json"
ENV_FILE: Path = PROJECT_ROOT / ".env"
ENV_EXAMPLE_FILE: Path = PROJECT_ROOT / ".env.example"
REQUIREMENTS_FILE: Path = PROJECT_ROOT / "requirements.txt"
VENV_DIR: Path = PROJECT_ROOT / ".venv"
