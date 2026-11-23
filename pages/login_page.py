from playwright.async_api import Page
from config.config import Config
from utils.element_actions import ElementActions
from utils.waits import Waits

class LoginPage:
    USERNAME_INPUT = "input[name='username']"
    PASSWORD_INPUT = "input[name='password']"
    LOGIN_BUTTON = "button[type='submit']"
    SIDE_MENU = "ul.oxd-main-menu"

    def __init__(self, page: Page):
        self.page = page
        self.actions = ElementActions(page)
        self.waits = self.actions.waits

    async def login_to_orangehrm(self):
        if await self.actions.is_visible(self.SIDE_MENU):
            return

        await self.page.goto(Config.BASE_URL)
        await self.actions.wait_and_fill(self.USERNAME_INPUT, Config.USERNAME)
        await self.actions.wait_and_fill(self.PASSWORD_INPUT, Config.PASSWORD)
        await self.actions.wait_and_click(self.LOGIN_BUTTON)
        await self.actions.waits.wait_for_element_visible(self.SIDE_MENU)
