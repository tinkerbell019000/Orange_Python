from playwright.async_api import Page
from utils.element_actions import ElementActions
from utils.asserts import AssertData


class AdminUserPage:
    MENU_LINK = "a[href*='view{}Module']"
    BUTTON_BY_TEXT = "//button[normalize-space()='{}']"
    DROPDOWN_BY_LABEL = "//label[text()='{}']/../following-sibling::div//div[contains(@class,'oxd-select-text-input')]"
    DROPDOWN_OPTION = "//div[@role='listbox']//span[text()='{}']"
    INPUT_BY_LABEL = "//label[text()='{}']/../following-sibling::div//input"
    ERROR_BY_LABEL = "//label[text()='{}']/../following-sibling::span[contains(@class,'oxd-input-field-error-message')]"
    TABLE_CELL_BY_TEXT = "//div[@class='oxd-table-body']//div[@role='row']//div[@role='cell'][normalize-space()='{}']"

    AUTOCOMPLETE_OPTION = "(//div[@role='listbox']//div[@role='option'][not(contains(., 'Searching'))])[1]"

    SUCCESS_TOAST = "div.oxd-toast--success"
    ALL_FIELD_ERRORS = "span.oxd-input-field-error-message"

    def __init__(self, page: Page):
        self.page = page
        self.actions = ElementActions(page)
        self.asserts = AssertData(page)

    async def open_add_user_form(self):
        await self.actions.click_dynamic(self.MENU_LINK, "Admin")
        await self.actions.click_dynamic(self.BUTTON_BY_TEXT, "Add")
        await self.actions.waits.wait_for_element_visible(
            self.actions.get_dynamic_locator(self.BUTTON_BY_TEXT, "Save")
        )

    async def submit_form(self, data: dict):
        for label, key in (("User Role", "role"), ("Status", "status")):
            if data.get(key):
                await self.actions.select_custom_dropdown_option(
                    self.actions.get_dynamic_locator(self.DROPDOWN_BY_LABEL, label),
                    self.actions.get_dynamic_locator(self.DROPDOWN_OPTION, data[key]),
                )

        if data.get("employee"):
            await self.actions.wait_and_fill(
                self.actions.get_dynamic_locator(self.INPUT_BY_LABEL, "Employee Name"),
                data["employee"],
            )
            if data.get("pick_emp", True):
                await self.actions.wait_and_click(self.AUTOCOMPLETE_OPTION)

        for label, key in (("Username", "username"), ("Password", "password"), ("Confirm Password", "confirm_password")):
            if data.get(key):
                await self.actions.wait_and_fill(
                    self.actions.get_dynamic_locator(self.INPUT_BY_LABEL, label),
                    data[key],
                )

        await self.actions.click_dynamic(self.BUTTON_BY_TEXT, "Save")

    async def search_user(self, username: str):
        await self.actions.wait_and_fill(
            self.actions.get_dynamic_locator(self.INPUT_BY_LABEL, "Username"),
            username,
        )
        await self.actions.click_dynamic(self.BUTTON_BY_TEXT, "Search")
