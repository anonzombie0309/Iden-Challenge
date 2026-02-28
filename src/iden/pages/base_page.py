import logging
import time

from playwright.sync_api import Page, TimeoutError


class BasePage:
    def __init__(self, page: Page, timeout_ms: int) -> None:
        self.page = page
        self.timeout_ms = timeout_ms
        self.logger = logging.getLogger(self.__class__.__name__)

    def wait_for_any(self, selectors: list[str], timeout_ms: int | None = None) -> str:
        timeout = timeout_ms or self.timeout_ms
        self.logger.info("Waiting for one of selectors: %s", selectors)
        end_time = time.time() + timeout / 1000
        while time.time() < end_time:
            for selector in selectors:
                loc = self.page.locator(selector)
                if loc.count() > 0 and loc.first.is_visible():
                    self.logger.info("Matched selector: %s", selector)
                    return selector
            self.page.wait_for_timeout(200)
        raise TimeoutError(f"None of the selectors became visible: {selectors}")

    def click_if_visible(self, selector: str) -> bool:
        loc = self.page.locator(selector)
        if loc.count() > 0 and loc.first.is_visible():
            self.logger.info("Clicking visible selector: %s", selector)
            loc.first.click()
            return True
        self.logger.info("Selector not visible, skipping click: %s", selector)
        return False