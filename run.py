"""Entry point for the Student Mental Health Support Chatbot.

Running `python run.py` (or `py run.py` on Windows) will:

  1. Check that Python 3.9 or newer is being used.
  2. Create a ".venv" virtual environment if one does not already exist.
  3. Install the packages in requirements.txt into that environment if needed.
  4. Copy ".env.example" to ".env" if ".env" does not exist yet.
  5. Re-launch the chatbot using the virtual environment's own Python.

The script uses only ASCII output and only cross-platform Python so it works
the same on Windows and Linux, with no manual tweaking.
"""

import os
import platform
import subprocess
import sys
import venv
from pathlib import Path

# The project root is the folder that contains this file. All paths are
# resolved from here, never from the current working directory.
PROJECT_ROOT = Path(__file__).resolve().parent

VENV_DIR = PROJECT_ROOT / ".venv"
REQUIREMENTS_FILE = PROJECT_ROOT / "requirements.txt"
ENV_FILE = PROJECT_ROOT / ".env"
ENV_EXAMPLE_FILE = PROJECT_ROOT / ".env.example"

# The packages we check for inside the virtual environment. "pytest" is
# included so `python -m pytest` works for the project's tests; the chatbot
# itself only needs "dotenv" and "rapidfuzz" at runtime.
REQUIRED_IMPORTS = ["dotenv", "rapidfuzz", "pytest"]

MIN_PYTHON = (3, 9)


def fail(message: str) -> None:
    """Print an error message to stderr and exit."""
    print("ERROR: " + message, file=sys.stderr, flush=True)
    sys.exit(1)


def check_python_version() -> None:
    """Ensure we are running on Python 3.9 or newer."""
    if sys.version_info < MIN_PYTHON:
        current = ".".join(str(part) for part in sys.version_info[:3])
        fail(
            "Python {0} or newer is required, but you are running {1}.\n"
            "Please install a newer version from https://www.python.org/downloads/".format(
                ".".join(str(p) for p in MIN_PYTHON), current
            )
        )


def venv_python_path() -> Path:
    """Return the path to the Python executable inside the .venv.

    Windows keeps the executable in Scripts\\python.exe while Linux and macOS
    use bin/python.
    """
    if platform.system() == "Windows":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def is_running_in_venv() -> bool:
    """Return True if the current interpreter is the .venv interpreter."""
    try:
        return Path(sys.executable).resolve() == venv_python_path().resolve()
    except OSError:
        return False


def create_venv() -> None:
    """Create the .venv virtual environment using the current interpreter."""
    if VENV_DIR.exists():
        return
    print("Creating virtual environment (.venv)...", flush=True)
    try:
        venv.EnvBuilder(with_pip=True).create(str(VENV_DIR))
    except Exception as exc:  # noqa: BLE001 - report any creation failure
        fail("Could not create the virtual environment: {0}".format(exc))


def dependencies_installed(python_exe: Path) -> bool:
    """Check whether the required packages can be imported inside the venv."""
    check_code = ";".join("import " + name for name in REQUIRED_IMPORTS)
    result = subprocess.run(
        [str(python_exe), "-c", check_code],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return result.returncode == 0


def install_requirements(python_exe: Path) -> None:
    """Install requirements.txt into the virtual environment."""
    if not REQUIREMENTS_FILE.exists():
        return
    print("Installing requirements into .venv ...", flush=True)
    result = subprocess.run(
        [
            str(python_exe),
            "-m",
            "pip",
            "install",
            "--disable-pip-version-check",
            "-r",
            str(REQUIREMENTS_FILE),
        ]
    )
    if result.returncode != 0:
        fail(
            "Could not install the requirements. Check your internet "
            "connection and try again."
        )


def ensure_env_file() -> None:
    """Copy .env.example to .env if .env does not exist yet."""
    if ENV_FILE.exists():
        return
    if not ENV_EXAMPLE_FILE.exists():
        return
    try:
        content = ENV_EXAMPLE_FILE.read_text(encoding="utf-8")
        ENV_FILE.write_text(content, encoding="utf-8")
        print(
            "Created .env from .env.example. You can edit .env if you like "
            "(it is optional - the chatbot needs no API key).",
            flush=True,
        )
    except OSError as exc:
        # Not fatal: the chatbot works without a .env file.
        print("Note: could not create .env ({0}). Continuing anyway.".format(exc))


def relaunch_in_venv() -> None:
    """Re-run the chatbot using the .venv interpreter."""
    python_exe = venv_python_path()
    if not python_exe.exists():
        fail("The virtual environment Python was not found at: {0}".format(python_exe))

    # Run "python -m src.chatbot" from the project root so imports work.
    result = subprocess.run(
        [str(python_exe), "-m", "src.chatbot"],
        cwd=str(PROJECT_ROOT),
    )
    sys.exit(result.returncode)


def main() -> None:
    check_python_version()

    # If we are already inside the .venv, go straight to running the bot.
    if is_running_in_venv():
        from src.chatbot import main as chatbot_main

        sys.exit(chatbot_main())

    create_venv()

    python_exe = venv_python_path()
    if not python_exe.exists():
        fail("The virtual environment Python was not found at: {0}".format(python_exe))

    if not dependencies_installed(python_exe):
        install_requirements(python_exe)

    ensure_env_file()

    print("Starting the chatbot...\n", flush=True)
    relaunch_in_venv()


if __name__ == "__main__":
    main()
