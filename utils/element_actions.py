from typing import Union
from playwright.async_api import Page, Locator
from utils.waits import Waits
from utils.logger import get_logger
from contextlib import asynccontextmanager

logger = get_logger(__name__)


class ElementActions:
    def __init__(self, page: Page):
        self.page = page
        self.waits = Waits(page)

    def get_locator(self, selector: Union[str, Locator], *args) -> Locator:
        if isinstance(selector, str):
            formatted = selector.format(*args) if args else selector
            return self.page.locator(formatted)
        return selector

    def get_dynamic_locator(self, selector_template: str, *args) -> str:
        return selector_template.format(*args)

    async def wait_and_click(self, selector: Union[str, Locator]):
        locator = await self.waits.wait_for_element_clickable(selector)
        logger.info(f"Clicking element: {selector}")
        await locator.click(no_wait_after=True)
        

    async def click_dynamic(self, selector_template: str, *args):
        selector = self.get_dynamic_locator(selector_template, *args)
        await self.wait_and_click(selector)

    async def wait_and_fill(self, selector: Union[str, Locator], value: str):
        locator = await self.waits.wait_for_element_visible(selector)
        logger.info(f"Filling element: {selector}")
        await locator.fill(value)

    async def get_text(self, selector: Union[str, Locator], *args) -> str:
        locator = self.get_locator(selector, *args)
        await self.waits.wait_for_element_visible(locator)
        text = (await locator.inner_text()).strip()
        logger.info(f"Retrieved text [{text}] from: {selector}")
        return text

    async def get_all_texts(self, selector: Union[str, Locator], *args) -> list[str]:
        locator = self.get_locator(selector, *args)
        await self.waits.wait_for_element_visible(locator.first)
        texts = [text.strip() for text in await locator.all_inner_texts()]
        logger.info(f"Retrieved {len(texts)} texts from: {selector}")
        return texts


    async def is_visible(self, selector: Union[str, Locator]) -> bool:
        return await self.get_locator(selector).is_visible()

    async def hover_element(self, selector: Union[str, Locator]):
        locator = await self.waits.wait_for_element_visible(selector)
        logger.info(f"Hovering mouse: {selector}")
        await locator.hover()

    async def select_dropdown_by_value(self, selector: Union[str, Locator], value: str):
        locator = await self.waits.wait_for_element_visible(selector)
        logger.info(f"Select dropdown value [{value}] element: {selector}")
        await locator.select_option(value=value)

    async def select_custom_dropdown_option(self, dropdown_click_selector: Union[str, Locator], option_text_selector: Union[str, Locator]):
        logger.info(f"menu: {dropdown_click_selector}")
        await self.wait_and_click(dropdown_click_selector)
        locator = await self.waits.wait_for_element_visible(option_text_selector)
        logger.info(f"Select option list: {option_text_selector}")
        await locator.click()

    async def set_checkbox_state(self, selector: Union[str, Locator], check: bool = True):
        locator = await self.waits.wait_for_element_visible(selector)
        is_checked = await locator.is_checked()
        if is_checked != check:
            logger.info(f"Toggle checkbox: {selector}")
            await locator.click()

    async def get_element_count(self, selector: Union[str, Locator]) -> int:
        count = await self.get_locator(selector).count()
        logger.info(f"Found match counts: {count}: {selector}")
        return count

    @asynccontextmanager
    async def wait_for_api(self, url_substring: str, status_code: int = 200):
        logger.info(f"Waiting for API response containing: {url_substring}")
        async with self.page.expect_response(
            lambda res: url_substring in res.url and res.status == status_code,
            timeout=self.waits.timeout
        ) as response_info:
            yield response_info
        await response_info.value

    async def select_dynamic_custom_dropdown(
        self,
        dropdown_click_template: str,
        option_text_template: str,
        dropdown_arg: str,
        option_arg: str,
    ):
        dropdown_selector = self.get_dynamic_locator(dropdown_click_template, dropdown_arg)
        option_selector = (
            self.get_dynamic_locator(option_text_template, dropdown_arg, option_arg)
            if option_text_template.count("{}") == 2
            else self.get_dynamic_locator(option_text_template, option_arg)
        )
        logger.info(f"Opening dynamic custom dropdown: {dropdown_selector}")
        await self.wait_and_click(dropdown_selector)
        logger.info(f"Selecting dynamic option: {option_selector}")
        await self.wait_and_click(option_selector)

