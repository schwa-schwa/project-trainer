from pathlib import Path
from dotenv import load_dotenv

# core/common/config.py → core/common → core → backend
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
PROJECT_DIR = BACKEND_DIR.parent


def load_config():
    """Load environment variables from the .env file

    Searches for .env in:
    1. Backend directory (backend/.env)
    2. Project root (project_trainer/.env)
    """
    backend_env = BACKEND_DIR / ".env"
    if backend_env.exists():
        load_dotenv(backend_env)
        return

    project_env = PROJECT_DIR / ".env"
    if project_env.exists():
        load_dotenv(project_env)


def get_project_root() -> Path:
    """Return the absolute path to the backend directory"""
    return BACKEND_DIR


def get_data_dir() -> Path:
    """Return the absolute path to the data directory"""
    return BACKEND_DIR / "data"
