from .base_page import BasePage


class SubmitPage(BasePage):
    def open(self, base_url: str) -> None:
        self.page.goto(base_url.rstrip("/") + "/submit-script", wait_until="domcontentloaded")

    def submit_repository(self, repo_url: str) -> None:
        url_input = self.page.get_by_role("textbox", name="GitHub Repository URL")
        submit_button = self.page.get_by_role("button", name="Submit Repository")

        url_input.wait_for(state="visible", timeout=self.timeout_ms)
        url_input.fill(repo_url)
        submit_button.click()

        self.wait_for_any(
            [
                "text=Repository submitted",
                "text=already submitted",
                "text=Submission",
            ]
        )
