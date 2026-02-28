import json
import logging
from pathlib import Path
from typing import Any

from playwright.sync_api import BrowserContext, Page

from iden.config import Settings
from iden.pages.challenge_page import ChallengePage
from iden.pages.login_page import LoginPage

logger = logging.getLogger(__name__)


def create_context(playwright: Any, settings: Settings, headless: bool = True) -> BrowserContext:
    logger.info("Launching browser (headless=%s)", headless)
    browser = playwright.chromium.launch(headless=headless)
    if settings.session_path.exists():
        logger.info("Using existing storage state: %s", settings.session_path)
        context = browser.new_context(storage_state=str(settings.session_path))
    else:
        logger.info("No session file found. Starting fresh browser context.")
        context = browser.new_context()
    context.set_default_timeout(settings.timeout_ms)
    return context


def run_extraction(page: Page, settings: Settings) -> dict[str, Any]:
    logger.info("Starting extraction workflow.")
    login_page = LoginPage(page, settings.timeout_ms)
    login_page.login_if_needed(settings.base_url, settings.email, settings.password)

    challenge_page = ChallengePage(page, settings.timeout_ms)
    challenge_page.open(settings.base_url)
    challenge_page.launch_if_needed()
    challenge_page.complete_wizard()

    payload = challenge_page.extract_all_products(
        max_scroll_rounds=settings.max_scroll_rounds,
        idle_rounds_before_stop=settings.idle_rounds_before_stop,
    )
    assert payload.get("meta", {}).get("extracted", 0) > 0, (
        "Expected at least one product to be extracted."
    )
    logger.info("Extraction workflow finished successfully.")
    return payload


def save_payload(payload: dict[str, Any], output_path: Path) -> None:
    logger.info("Writing payload to JSON: %s", output_path)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")