from typing import Union
from playwright.async_api import Locator, Page
from config.config import Config
from utils.logger import get_logger


class Waits:
    def __init__(self, page: Page):
        self.page = page
        self.log = get_logger(self.__class__.__name__)
        self.timeout = Config.DEFAULT_TIMEOUT

    async def static_wait(self, timeInSeconds: float) -> None:
        await self.page.wait_for_timeout(timeInSeconds * 1000)

    async def wait_for_page_load(self) -> None:
        await self.page.wait_for_load_state("load", timeout=self.timeout)

    async def wait_for_dom_content_loaded(self) -> None:
        await self.page.wait_for_load_state("domcontentloaded", timeout=self.timeout)

    async def wait_for_element_visible(self, locator_value: Union[str, Locator]) -> Locator:
        locator = (self.page.locator(locator_value) if isinstance(locator_value, str) else locator_value)
        await locator.wait_for(state="visible", timeout=self.timeout)
        return locator

    async def wait_for_element_hidden(self, locator_value: Union[str, Locator]) -> Locator:
        locator = (self.page.locator(locator_value) if isinstance(locator_value, str) else locator_value)
        await locator.wait_for(state="hidden", timeout=self.timeout)
        return locator

    async def wait_for_element_clickable(self, locator_value: Union[str, Locator]) -> Locator:
        locator = (self.page.locator(locator_value) if isinstance(locator_value, str) else locator_value)
        await locator.wait_for(state="visible", timeout=self.timeout)
        await locator.click(trial=True, timeout=self.timeout)
        return locator

    async def wait_for_url(self, url_pattern: str) -> None:
        await self.page.wait_for_url(url_pattern, timeout=self.timeout)
