from .base_page import BasePage


class LoginPage(BasePage):
    def open(self, base_url: str) -> None:
        self.logger.info("Opening base URL: %s", base_url)
        self.page.goto(base_url, wait_until="domcontentloaded")
        assert self.page.url.startswith(base_url.rstrip("/")), (
            f"Expected to be on base URL '{base_url}', got '{self.page.url}'"
        )

    def is_logged_in(self) -> bool:
        return (
            self.page.locator("button:has-text('Sign out')").count() > 0
            or self.page.locator("text=Launch Challenge").count() > 0
            or "/instructions" in self.page.url
            or "/challenge" in self.page.url
        )

    def login_if_needed(self, base_url: str, email: str, password: str) -> None:
        self.open(base_url)
        if self.is_logged_in():
            self.logger.info("Existing session detected. Skipping login.")
            assert self.is_logged_in(), "Expected existing session to be valid."
            return

        self.logger.info("No valid session found. Performing login for %s", email)
        email_input = self.page.get_by_role("textbox", name="Email")
        password_input = self.page.get_by_role("textbox", name="Password")
        sign_in_button = self.page.get_by_role("button", name="Sign in")

        email_input.wait_for(state="visible", timeout=self.timeout_ms)
        assert email_input.is_visible(), "Email input is not visible on login page."
        assert password_input.is_visible(), "Password input is not visible on login page."
        assert sign_in_button.is_visible(), "Sign in button is not visible on login page."

        email_input.fill(email)
        password_input.fill(password)
        sign_in_button.click()

        post_login_selector = self.wait_for_any(
            [
                "text=Launch Challenge",
                "button:has-text('Sign out')",
                "text=Iden Challenge Instructions",
            ]
        )
        assert post_login_selector in {
            "text=Launch Challenge",
            "button:has-text('Sign out')",
            "text=Iden Challenge Instructions",
        }, "Post-login verification failed."
        assert self.is_logged_in(), "Expected user to be logged in after sign in."
        self.logger.info("Login completed successfully.")