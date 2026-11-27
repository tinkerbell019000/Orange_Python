import re
from typing import Union
from playwright.async_api import Locator, Page, expect
from utils.element_actions import ElementActions
from utils.logger import get_logger

logger = get_logger(__name__)

class AssertData:
    def __init__(self, page: Page):
        self.page = page
        self.actions = ElementActions(page)

    def _format_target(self, selector: Union[str, Locator], *args) -> str:
        return (self.actions.get_dynamic_locator(selector, *args) if isinstance(selector, str) else str(selector))

    async def assert_page_title(self, title: str) -> None:
        logger.info(f"Asserting page title: {title}")
        await expect(self.page).to_have_title(title)

    async def assert_text(self, selector: Union[str, Locator], expected_text: str, *args) -> None:
        logger.info(f"Asserting exact text '{expected_text}' on {self._format_target(selector, *args)}")
        await expect(self.actions.get_locator(selector, *args).first).to_have_text(expected_text)

    async def assert_dynamic_contains_text(
        self, selector_template: Union[str, Locator], expected_text: str, *args) -> None:
        logger.info(f"Asserting contains text '{expected_text}' on {self._format_target(selector_template, *args)}")
        await expect(self.actions.get_locator(selector_template, *args).first).to_contain_text(expected_text)

    async def assert_element_visible(self, selector: Union[str, Locator], *args) -> None:
        logger.info(f"Asserting visible: {self._format_target(selector, *args)}")
        await expect(self.actions.get_locator(selector, *args).first).to_be_visible()

    async def assert_element_enabled(self, selector: Union[str, Locator], *args) -> None:
        logger.info(f"Asserting enabled: {self._format_target(selector, *args)}")
        await expect(self.actions.get_locator(selector, *args).first).to_be_enabled()

    async def assert_element_disabled(self, selector: Union[str, Locator], *args) -> None:
        logger.info(f"Asserting disabled: {self._format_target(selector, *args)}")
        await expect(self.actions.get_locator(selector, *args).first).to_be_disabled()

    async def assert_element_count(self, selector: Union[str, Locator], expected_count: int, *args) -> None:
        logger.info(f"Asserting count {expected_count} for: {self._format_target(selector, *args)}")
        await expect(self.actions.get_locator(selector, *args)).to_have_count(expected_count)

    async def assert_list_sorted(self, items: list[str], descending: bool = False) -> None:
        logger.info(f"Asserting {len(items)} items sorted (descending={descending})")
        assert items, "Expected non-empty list for sort verification"
        expected = sorted(items, key=lambda s: s.lower(), reverse=descending)
        assert items == expected, f"Sort mismatch.\nActual:   {items}\nExpected: {expected}"

