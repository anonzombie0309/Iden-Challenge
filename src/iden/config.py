from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv


DEFAULT_BASE_URL = "https://hiring.idenhq.com/"


@dataclass(frozen=True)
class Settings:
    base_url: str
    email: str
    password: str
    session_path: Path
    output_path: Path
    timeout_ms: int
    max_scroll_rounds: int
    idle_rounds_before_stop: int
    submit_repo_url: str | None


def load_settings() -> Settings:
    load_dotenv()

    base_url = os.getenv("IDEN_BASE_URL", DEFAULT_BASE_URL).strip()
    email = os.getenv("IDEN_EMAIL", "bandooniaviral@gmail.com").strip()
    password = os.getenv("IDEN_PASSWORD", "").strip()
    submit_repo_url = os.getenv("IDEN_SUBMIT_REPO_URL", "").strip() or None

    if not password:
        raise ValueError("IDEN_PASSWORD is missing. Set it in .env.")

    session_path = Path("automation/state/session.json")
    output_path = Path("automation/data/products.json")
    session_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    return Settings(
        base_url=base_url,
        email=email,
        password=password,
        session_path=session_path,
        output_path=output_path,
        timeout_ms=int(os.getenv("IDEN_TIMEOUT_MS", "20000")),
        max_scroll_rounds=int(os.getenv("IDEN_MAX_SCROLL_ROUNDS", "500")),
        idle_rounds_before_stop=int(os.getenv("IDEN_IDLE_ROUNDS_BEFORE_STOP", "8")),
        submit_repo_url=submit_repo_url,
    )
