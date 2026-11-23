from contextlib import asynccontextmanager
from playwright.async_api import Page, Locator
from utils.waits import Waits
from utils.logger import get_logger

logger = get_logger(__name__)


class ElementActions:
    def __init__(self, page: Page):
        self.page = page
        self.waits = Waits(page)

    @staticmethod
    def get_dynamic_locator(selector_template: str, *args) -> str:
        return selector_template.format(*args) if args else selector_template

    def get_locator(self, selector_template: str, *args) -> Locator:
        return self.page.locator(self.get_dynamic_locator(selector_template, *args))

    def _first(self, action: str, selector_template: str, *args) -> Locator:
        selector = self.get_dynamic_locator(selector_template, *args)
        logger.info(f"{action}: {selector}")
        return self.page.locator(selector).first

    async def wait_and_click(self, selector: str, *args):
        await self._first("Clicking", selector, *args).click()

    async def wait_and_fill(self, selector: str, value: str, *args):
        await self._first("Filling", selector, *args).fill(value)

    async def hover_element(self, selector: str, *args):
        await self._first("Hovering", selector, *args).hover()
        click_dynamic = wait_and_click
        fill_dynamic = wait_and_fill

    async def is_visible(self, selector: str, *args) -> bool:
        return await self.get_locator(selector, *args).first.is_visible()

    async def select_dropdown_by_value(self, selector: str, value: str, *args):
        await self._first(f"Selecting [{value}]", selector, *args).select_option(value=value)

    async def select_custom_dropdown_option(self, dropdown_selector: str, option_selector: str):
        await self.wait_and_click(dropdown_selector)
        await self.wait_and_click(option_selector)

    async def select_dynamic_custom_dropdown(self, dropdown_template: str, option_template: str, *args):
        await self.wait_and_click(dropdown_template, *args)
        await self.wait_and_click(option_template, *args)

    async def get_all_texts(self, selector_template: str, *args) -> list[str]:
        locator = self.get_locator(selector_template, *args)
        await locator.first.wait_for(state="visible")
        cleaned = [t.strip() for t in await locator.all_inner_texts() if t.strip()]
        logger.info(f"Extracted {len(cleaned)} items")
        return cleaned

    @asynccontextmanager
    async def wait_for_api(self, url_substring: str, status: int = 200):
        async with self.page.expect_response(lambda r: url_substring in r.url and r.status == status):
            yield

    async def set_checkbox_state(self, selector: str, check: bool = True, *args):
        locator = self.get_locator(selector, *args).first
        if await locator.is_checked() != check:
            logger.info(f"Toggling checkbox: {self.get_dynamic_locator(selector, *args)}")
            await locator.click()

    async def get_element_count(self, selector: str, *args) -> int:
        resolved = self.get_dynamic_locator(selector, *args)
        count = await self.page.locator(resolved).count()
        logger.info(f"Count for {resolved}: {count}")
        return count
