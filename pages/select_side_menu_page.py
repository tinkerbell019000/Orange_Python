from playwright.async_api import Page
from utils.element_actions import ElementActions


class SideMenuPage:
    MENU_OPTION = "ul.oxd-main-menu a.oxd-main-menu-item:has(span:text-is('{}'))"

    def __init__(self, page: Page):
        self.page = page
        self.actions = ElementActions(page)

    async def select_menu_option(self, option_name: str):
        await self.actions.click_dynamic(self.MENU_OPTION, option_name)
