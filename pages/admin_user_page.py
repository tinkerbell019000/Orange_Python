from playwright.async_api import Page
from utils.element_actions import ElementActions
from utils.asserts import AssertData


class AdminUserPage:
    MENU_LINK = "a[href*='view{}Module']"
    BUTTON_BY_TEXT = "//button[normalize-space()='{}']"
    ADD_BUTTON = "//button[normalize-space()='Add']"
    SAVE_BUTTON = "//button[normalize-space()='Save']"
    SEARCH_BUTTON = "//button[normalize-space()='Search']"

    DROPDOWN_BY_LABEL = "//label[text()='{}']/../following-sibling::div//div[contains(@class,'oxd-select-text-input')]"
    DROPDOWN_OPTION = "//div[@role='listbox']//span[text()='{}']"
    INPUT_BY_LABEL = "//label[text()='{}']/../following-sibling::div//input"
    AUTOCOMPLETE_OPTION = "//div[@role='listbox']//div[@role='option'][not(contains(., 'Searching'))]"

    ALL_FIELD_ERRORS = "span.oxd-input-field-error-message"
    ERROR_BY_LABEL = "//label[text()='{}']/../following-sibling::span[contains(@class,'oxd-input-field-error-message')]"
    SUCCESS_TOAST = "div.oxd-toast--success"
    TABLE_CELL_BY_TEXT = "//div[@class='oxd-table-body']//div[@role='cell'][normalize-space()='{}']"

    def __init__(self, page: Page):
        self.page = page
        self.actions = ElementActions(page)
        self.waits = self.actions.waits
        self.asserts = AssertData(page)

    async def open_add_user_form(self):
        await self.actions.click_dynamic(self.MENU_LINK, "Admin")
        await self.actions.wait_and_click(self.ADD_BUTTON)

    async def submit_form(self, payload: dict):
        if "role" in payload:
            await self.actions.select_dynamic_custom_dropdown(self.DROPDOWN_BY_LABEL, self.DROPDOWN_OPTION, "User Role", payload["role"])

        if "employee" in payload:
            emp_input = self.actions.get_dynamic_locator(self.INPUT_BY_LABEL, "Employee Name")
            await self.actions.wait_and_fill(emp_input, payload["employee"])
            if payload.get("pick_emp", False):
                await self.actions.wait_and_click(self.page.locator(self.AUTOCOMPLETE_OPTION).first)

        if "status" in payload:
            await self.actions.select_dynamic_custom_dropdown(self.DROPDOWN_BY_LABEL, self.DROPDOWN_OPTION, "Status", payload["status"])

        if "username" in payload:
            username_input = self.actions.get_dynamic_locator(self.INPUT_BY_LABEL, "Username")
            await self.actions.wait_and_fill(username_input, payload["username"])

        if "password" in payload:
            password_input = self.actions.get_dynamic_locator(self.INPUT_BY_LABEL, "Password")
            await self.actions.wait_and_fill(password_input, payload["password"])

        if "confirm_password" in payload:
            confirm_input = self.actions.get_dynamic_locator(self.INPUT_BY_LABEL, "Confirm Password")
            await self.actions.wait_and_fill(confirm_input, payload["confirm_password"])

        if payload.get("pick_emp"):
            async with self.actions.wait_for_api("admin/users"):
                await self.actions.wait_and_click(self.SAVE_BUTTON)
        else:
            await self.actions.wait_and_click(self.SAVE_BUTTON)

    async def wait_for_success_toast(self):
        await self.waits.wait_for_element_visible(self.SUCCESS_TOAST)

    async def search_user(self, username: str):
        username_input = self.actions.get_dynamic_locator(self.INPUT_BY_LABEL, "Username")
        await self.actions.wait_and_fill(username_input, username)
        async with self.actions.wait_for_api("admin/users"):
            await self.actions.wait_and_click(self.SEARCH_BUTTON)
