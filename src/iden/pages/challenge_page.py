import re

from .base_page import BasePage


class ChallengePage(BasePage):
    def open(self, base_url: str) -> None:
        target = base_url.rstrip("/") + "/challenge"
        self.logger.info("Opening challenge page: %s", target)
        self.page.goto(target, wait_until="domcontentloaded")
        assert "/challenge" in self.page.url, f"Expected challenge page, got '{self.page.url}'"

    def launch_if_needed(self) -> None:
        self.logger.info("Checking if 'Launch Challenge' click is required.")
        if self.page.locator("button:has-text('Launch Challenge')").count() > 0:
            self.logger.info("Clicking 'Launch Challenge'.")
            self.page.get_by_role("button", name="Launch Challenge").click()

        step_selector = self.wait_for_any(
            [
                "text=Select Data Source",
                "text=Product Inventory",
                "button:has-text('View Products')",
            ]
        )
        self.logger.info("Challenge state after launch step: %s", step_selector)
        assert step_selector in {
            "text=Select Data Source",
            "text=Product Inventory",
            "button:has-text('View Products')",
        }, "Launch Challenge step did not reach expected wizard state."

    def complete_wizard(self) -> None:
        if self.page.locator("text=Product Inventory").count() > 0:
            self.logger.info("Product inventory already visible. Wizard skipped.")
            assert self.page.locator("text=Product Inventory").count() > 0, (
                "Expected Product Inventory to be visible when skipping wizard."
            )
            return

        steps = [
            {"title": "Select Data Source", "option": "button:has-text('Local Database')"},
            {"title": "Choose Category", "option": "button:has-text('All Products')"},
            {"title": "Select View Type", "option": "button:has-text('Table View')"},
            {"title": "View Products", "option": "button:has-text('View Products')"},
        ]

        for step in steps:
            if self.page.locator("text=Product Inventory").count() > 0:
                self.logger.info("Reached product inventory during wizard at step '%s'.", step["title"])
                return
            if self.page.locator(f"text={step['title']}").count() == 0:
                self.logger.info("Step '%s' not visible; likely auto-advanced.", step["title"])
                continue

            self.logger.info("Executing step: %s", step["title"])
            option_clicked = self.click_if_visible(step["option"])
            next_clicked = self.click_if_visible("button:has-text('Next')")
            assert option_clicked or next_clicked, (
                f"Assertion failed: could not perform action for step '{step['title']}'."
            )
            if not option_clicked and not next_clicked:
                raise RuntimeError(f"Could not progress wizard at step '{step['title']}'.")

            self.page.wait_for_timeout(250)

        if self.page.locator("button:has-text('View Products')").count() > 0:
            self.logger.info("Clicking final 'View Products' button.")
            self.page.get_by_role("button", name="View Products").click()

        self.page.locator("text=Product Inventory").first.wait_for(
            state="visible", timeout=self.timeout_ms
        )
        assert self.page.locator("text=Product Inventory").count() > 0, (
            "Expected Product Inventory after completing wizard."
        )
        self.logger.info("Product inventory is visible.")

    def read_counts(self) -> dict[str, int | None]:
        count_loc = self.page.locator("text=/Showing\\s+\\d+\\s+of\\s+\\d+\\s+products/")
        if count_loc.count() == 0:
            return {"showing": None, "total": None}

        text = count_loc.first.inner_text()
        match = re.search(r"Showing\s+(\d+)\s+of\s+(\d+)\s+products", text)
        if not match:
            return {"showing": None, "total": None}
        return {"showing": int(match.group(1)), "total": int(match.group(2))}

    def extract_all_products(self, max_scroll_rounds: int, idle_rounds_before_stop: int) -> dict[str, object]:
        assert self.page.locator("text=Product Inventory").count() > 0, (
            "Extraction started before Product Inventory became visible."
        )
        self.logger.info("Starting product extraction.")
        stale_rounds = 0
        last_showing = self.read_counts()["showing"] or 0

        for round_index in range(max_scroll_rounds):
            counts = self.read_counts()
            showing = counts["showing"] or 0
            total = counts["total"]

            if round_index % 25 == 0:
                self.logger.info(
                    "Scroll round=%s showing=%s total=%s stale_rounds=%s",
                    round_index,
                    showing,
                    total,
                    stale_rounds,
                )

            if total is not None and showing >= total:
                self.logger.info("Reached reported total products (%s).", total)
                break

            self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            self.page.wait_for_timeout(500)

            counts_after = self.read_counts()
            showing_after = counts_after["showing"] or 0
            if showing_after > last_showing:
                last_showing = showing_after
                stale_rounds = 0
            else:
                stale_rounds += 1
                if stale_rounds >= idle_rounds_before_stop:
                    self.logger.info("Stopping scroll due to stale rounds threshold: %s", stale_rounds)
                    break

        self.logger.info("Collecting product card data from DOM.")
        products = self.page.evaluate(
            """() => {
              const cards = Array.from(document.querySelectorAll('main div')).filter((el) => {
                const h3 = el.querySelector('h3');
                const p = Array.from(el.querySelectorAll('p')).find((x) => (x.textContent || '').includes('ID:'));
                return !!h3 && !!p;
              });

              const seen = new Set();
              const items = [];

              for (const card of cards) {
                const name = (card.querySelector('h3')?.textContent || '').trim();
                if (!name) continue;

                const category = (card.querySelector('h3 + div')?.textContent || '').trim();
                const idText = (Array.from(card.querySelectorAll('p')).find((x) => (x.textContent || '').includes('ID:'))?.textContent || '').trim();
                const idMatch = idText.match(/ID:\\s*(\\d+)/);
                const id = idMatch ? Number(idMatch[1]) : null;
                if (id === null || seen.has(id)) continue;
                seen.add(id);

                const specs = {};
                const dts = Array.from(card.querySelectorAll('dt'));
                const dds = Array.from(card.querySelectorAll('dd'));
                const n = Math.min(dts.length, dds.length);
                for (let i = 0; i < n; i++) {
                  const key = (dts[i].textContent || '').replace(':', '').trim().toLowerCase().replace(/\\s+/g, '_');
                  specs[key] = (dds[i].textContent || '').trim();
                }

                const updatedText =
                  (Array.from(card.querySelectorAll('*')).find((x) => ((x.textContent || '').trim().startsWith('Updated:')))?.textContent || '').trim();
                const updatedMatch = updatedText.match(/Updated:\\s*(.+)$/);
                const cost = specs['cost'] || '';
                const costMatch = cost.match(/\\$([\\d,]+(?:\\.\\d{1,2})?)/);

                items.push({
                  id,
                  name,
                  category,
                  manufacturer: specs['manufacturer'] || null,
                  cost,
                  cost_value: costMatch ? Number(costMatch[1].replace(/,/g, '')) : null,
                  shade: specs['shade'] || null,
                  weight_kg: specs['weight_(kg)'] || null,
                  guarantee: specs['guarantee'] || null,
                  updated: updatedMatch ? updatedMatch[1].trim() : null,
                  raw_specifications: specs
                });
              }

              items.sort((a, b) => a.id - b.id);
              return items;
            }"""
        )

        counts = self.read_counts()
        assert isinstance(products, list), "Expected extracted products payload to be a list."
        self.logger.info(
            "Extraction complete. extracted=%s showing_last_seen=%s total_reported=%s",
            len(products),
            counts["showing"],
            counts["total"],
        )
        return {
            "meta": {
                "source": self.page.url,
                "showing_last_seen": counts["showing"],
                "total_reported": counts["total"],
                "extracted": len(products),
            },
            "products": products,
        }