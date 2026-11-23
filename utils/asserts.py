import re
from playwright.async_api import Page, expect
from utils.element_actions import ElementActions
from utils.logger import get_logger

logger = get_logger(__name__)


class AssertData:
    def __init__(self, page: Page):
        self.page = page
        self.actions = ElementActions(page)

    async def assert_page_title(self, title: str):
        logger.info(f"Asserting page title: {title}")
        await expect(self.page).to_have_title(title)

    async def assert_text(self, selector: str, expected_text: str, *args):
        logger.info(f"Asserting exact text '{expected_text}'")
        await expect(self.actions.get_locator(selector, *args).first).to_have_text(expected_text)

    async def assert_dynamic_contains_text(self, selector_template: str, expected_text: str, *args):
        logger.info(f"Asserting contains text '{expected_text}'")
        await expect(self.actions.get_locator(selector_template, *args).first).to_contain_text(expected_text)

    async def assert_element_visible(self, selector: str, *args):
        logger.info(f"Asserting visible: {self.actions.get_dynamic_locator(selector, *args)}")
        await expect(self.actions.get_locator(selector, *args).first).to_be_visible()

    async def assert_element_enabled(self, selector: str, *args):
        logger.info(f"Asserting enabled: {self.actions.get_dynamic_locator(selector, *args)}")
        await expect(self.actions.get_locator(selector, *args).first).to_be_enabled()

    async def assert_element_disabled(self, selector: str, *args):
        logger.info(f"Asserting disabled: {self.actions.get_dynamic_locator(selector, *args)}")
        await expect(self.actions.get_locator(selector, *args).first).to_be_disabled()

    async def assert_element_count(self, selector: str, expected_count: int, *args):
        logger.info(f"Asserting count {expected_count} for: {self.actions.get_dynamic_locator(selector, *args)}")
        await expect(self.actions.get_locator(selector, *args)).to_have_count(expected_count)

    async def assert_list_sorted(self, items: list[str], descending: bool = False):
        logger.info(f"Asserting {len(items)} items sorted (descending={descending})")
        assert items, "Expected non-empty list for sort verification"
        sort_key = lambda s: (re.sub(r"[^a-z0-9]", "", s.lower()), s.lower())
        expected = sorted(items, key=sort_key, reverse=descending)
        assert items == expected, f"Sort mismatch.\nActual:   {items}\nExpected: {expected}"
