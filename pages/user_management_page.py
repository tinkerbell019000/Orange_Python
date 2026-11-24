from playwright.async_api import Page
from utils.element_actions import ElementActions
from utils.asserts import AssertData


class UserManagementPage:
    MENU_LINK = "a[href*='view{}Module']"
    BUTTON_BY_TEXT = "//button[normalize-space()='{}']"
    DROPDOWN_BY_LABEL = "//label[text()='{}']/../following-sibling::div//div[contains(@class,'oxd-select-text-input')]"
    DROPDOWN_OPTION = "//div[@role='listbox']//span[text()='{}']"
    INPUT_BY_LABEL = "//label[text()='{}']/../following-sibling::div//input"
    AUTOCOMPLETE_FIRST_OPTION = "(//div[@role='listbox']//div[@role='option'][not(contains(., 'Searching'))])[1]"
    CHANGE_PASSWORD_CHECKBOX = "//label[normalize-space()='Yes']/input[@type='checkbox']"
    CHANGE_PASSWORD_SPAN = "//label[normalize-space()='Yes']//span[contains(@class,'oxd-checkbox-input')]"

    ERROR_BY_LABEL = "//label[text()='{}']/../following-sibling::span[contains(@class,'oxd-input-field-error-message')]"
    SUCCESS_TOAST = "div.oxd-toast--success"
    INFO_TOAST = "div.oxd-toast--info"
    NO_RECORDS_TEXT = "//span[normalize-space()='No Records Found']"

    TABLE_ROW_BY_USER = "//div[@class='oxd-table-body']//div[@role='row'][.//div[@role='cell'][normalize-space()='{}']]"
    TABLE_CELL_VALUES = "//div[@class='oxd-table-body']//div[@role='row']//div[@role='cell']"
    EDIT_USER_BTN = "//div[@class='oxd-table-body']//div[@role='row'][.//div[@role='cell'][normalize-space()='{}']]//i[contains(@class,'bi-pencil-fill')]/parent::button"
    DELETE_USER_BTN = "//div[@class='oxd-table-body']//div[@role='row'][.//div[@role='cell'][normalize-space()='{}']]//i[contains(@class,'bi-trash')]/parent::button"
    CONFIRM_DELETE_BTN = "//div[contains(@class,'oxd-dialog-sheet')]//button[normalize-space()='Yes, Delete']"

    def __init__(self, page: Page):
        self.page = page
        self.actions = ElementActions(page)
        self.waits = self.actions.waits
        self.asserts = AssertData(page)

    async def navigate_to_users(self):
        async with self.actions.wait_for_api("admin/users"):
            await self.actions.click_dynamic(self.MENU_LINK, "Admin")

    async def get_any_existing_username(self, exclude: str = "") -> str:
        await self.navigate_to_users()
        users = await self.actions.get_all_texts(self.TABLE_CELL_VALUES)
        return next(u for u in users if u and u != exclude)

    async def create_user(
        self,
        username: str,
        password: str = "Password@123",
        role: str = "ESS",
        status: str = "Enabled",
        employee_hint: str = "a",
    ):
        await self.navigate_to_users()
        await self.actions.click_dynamic(self.BUTTON_BY_TEXT, "Add")
        await self.actions.select_dynamic_custom_dropdown(
            self.DROPDOWN_BY_LABEL, self.DROPDOWN_OPTION, "User Role", role
        )
        await self.actions.select_dynamic_custom_dropdown(
            self.DROPDOWN_BY_LABEL, self.DROPDOWN_OPTION, "Status", status
        )

        emp_input = self.actions.get_dynamic_locator(self.INPUT_BY_LABEL, "Employee Name")
        await self.actions.wait_and_fill(emp_input, employee_hint)
        await self.actions.wait_and_click(self.AUTOCOMPLETE_FIRST_OPTION)

        await self.actions.wait_and_fill(
            self.actions.get_dynamic_locator(self.INPUT_BY_LABEL, "Username"), username
        )
        await self.actions.wait_and_fill(
            self.actions.get_dynamic_locator(self.INPUT_BY_LABEL, "Password"), password
        )
        await self.actions.wait_and_fill(
            self.actions.get_dynamic_locator(self.INPUT_BY_LABEL, "Confirm Password"), password
        )

        async with self.actions.wait_for_api("admin/users"):
            await self.actions.click_dynamic(self.BUTTON_BY_TEXT, "Save")
        await self.waits.wait_for_element_visible(self.SUCCESS_TOAST)

    async def search_user(self, username: str):
        await self.navigate_to_users()
        username_input = self.actions.get_dynamic_locator(self.INPUT_BY_LABEL, "Username")
        await self.actions.wait_and_fill(username_input, username)
        async with self.actions.wait_for_api("admin/users"):
            await self.actions.click_dynamic(self.BUTTON_BY_TEXT, "Search")

    async def _clear_and_fill(self, label: str, value: str):
        locator = self.actions.get_locator(self.INPUT_BY_LABEL, label)
        await self.waits.wait_for_element_visible(locator)
        await locator.fill(value)
        await locator.press("Tab")

    async def edit_user(
        self,
        current_username: str,
        updates: dict,
        expect_success: bool = True,
    ):
        await self.search_user(current_username)
        await self.actions.click_dynamic(self.EDIT_USER_BTN, current_username)

        username_locator = self.actions.get_locator(self.INPUT_BY_LABEL, "Username")
        await self.waits.wait_for_element_visible(username_locator)
        await self.page.wait_for_function(
            "([el, expected]) => el.value === expected",
            arg=[await username_locator.element_handle(), current_username],
            timeout=self.waits.timeout,
        )

        if "role" in updates:
            await self.actions.select_dynamic_custom_dropdown(
                self.DROPDOWN_BY_LABEL, self.DROPDOWN_OPTION, "User Role", updates["role"]
            )

        if "status" in updates:
            await self.actions.select_dynamic_custom_dropdown(
                self.DROPDOWN_BY_LABEL, self.DROPDOWN_OPTION, "Status", updates["status"]
            )

        if "employee" in updates:
            await self._clear_and_fill("Employee Name", updates["employee"])
            if updates.get("pick_emp", False):
                await self.actions.wait_and_click(self.AUTOCOMPLETE_FIRST_OPTION)

        if "username" in updates:
            await self._clear_and_fill("Username", updates["username"])

        if updates.get("change_password"):
            await self.actions.wait_and_click(self.CHANGE_PASSWORD_SPAN)
            if "password" in updates:
                await self._clear_and_fill("Password", updates["password"])
            if "confirm_password" in updates:
                await self._clear_and_fill("Confirm Password", updates["confirm_password"])

        if expect_success:
            async with self.actions.wait_for_api("admin/users"):
                await self.actions.click_dynamic(self.BUTTON_BY_TEXT, "Save")
            await self.waits.wait_for_element_visible(self.SUCCESS_TOAST)
        else:
            await self.actions.click_dynamic(self.BUTTON_BY_TEXT, "Save")

    async def delete_user(self, username: str):
        await self.search_user(username)
        await self.actions.click_dynamic(self.DELETE_USER_BTN, username)
        async with self.actions.wait_for_api("admin/users"):
            await self.actions.wait_and_click(self.CONFIRM_DELETE_BTN)
        await self.waits.wait_for_element_visible(self.SUCCESS_TOAST)

    async def is_delete_disabled_or_protected(self, username: str) -> bool:
        await self.search_user(username)
        delete_locator = self.actions.get_locator(self.DELETE_USER_BTN, username)
        if not await delete_locator.is_visible() or await delete_locator.is_disabled():
            return True
        await self.actions.wait_and_click(delete_locator)
        return not await self.actions.is_visible(self.CONFIRM_DELETE_BTN)
