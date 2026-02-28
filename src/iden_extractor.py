import logging
import sys

from playwright.sync_api import sync_playwright

from iden.config import load_settings
from iden.workflows.extraction import create_context, run_extraction, save_payload


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> int:
    try:
        logger.info("Loading settings from environment.")
        settings = load_settings()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    with sync_playwright() as playwright:
        context = create_context(playwright, settings, headless=True)
        page = context.new_page()
        try:
            payload = run_extraction(page, settings)
            logger.info("Saving browser storage state: %s", settings.session_path)
            context.storage_state(path=str(settings.session_path))
            save_payload(payload, settings.output_path)
            print(f"Saved {payload['meta']['extracted']} products to {settings.output_path}")
            return 0
        except Exception as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1
        finally:
            context.close()


if __name__ == "__main__":
    raise SystemExit(main())