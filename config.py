from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

SECRET_KEY = "lab5-secret-key"
CONTACT_LOG_PATH = BASE_DIR / "contact_submissions.log"
