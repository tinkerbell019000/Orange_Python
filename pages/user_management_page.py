from playwright.async_api import Page
from utils.element_actions import ElementActions
from utils.asserts import AssertData


class UserManagementPage:
    MENU_LINK = "a[href*='view{}Module']"
    BUTTON_BY_TEXT = "//button[normalize-space()='{}']"

    FIELD_CONTAINER = "//label[normalize-space()='{}']/ancestor::div[contains(@class,'oxd-input-group')]"
    DROPDOWN_BY_LABEL = f"{FIELD_CONTAINER}//div[contains(@class,'oxd-select-text-input')]"
    INPUT_BY_LABEL = f"{FIELD_CONTAINER}//input"
    ERROR_BY_LABEL = f"{FIELD_CONTAINER}//span[contains(@class,'oxd-input-field-error-message')]"

    DROPDOWN_OPTION = "//div[@role='listbox']//span[normalize-space()='{}']"
    AUTOCOMPLETE_OPTION = "//div[@role='listbox']//div[@role='option'][not(contains(., 'Searching'))]"
    CHANGE_PASSWORD_SPAN = "//label[normalize-space()='Yes']//span[contains(@class,'oxd-checkbox-input')]"

    SUCCESS_TOAST = "div.oxd-toast--success"
    NO_RECORDS_TEXT = "//span[normalize-space()='No Records Found']"

    TABLE_ROW_BY_USER = "//div[@class='oxd-table-body']//div[@role='row'][.//div[@role='cell'][2][normalize-space()='{}']]"
    TABLE_USERNAME_CELLS = "//div[@class='oxd-table-body']//div[@role='row']//div[@role='cell'][2]"
    ROW_ACTION_BTN = f"{TABLE_ROW_BY_USER}//button[.//i[contains(@class,'{{}}')]]"
    CONFIRM_DELETE_BTN = "//div[contains(@class,'oxd-dialog-sheet')]//button[normalize-space()='Yes, Delete']"

    FIELD_HANDLERS = {
        "role": ("User Role", "_select_dropdown"),
        "status": ("Status", "_select_dropdown"),
        "employee": ("Employee Name", "_fill_employee"),
        "username": ("Username", "_clear_and_fill"),
        "change_password": ("Change Password", "_toggle_change_password"),
        "password": ("Password", "_clear_and_fill"),
        "confirm_password": ("Confirm Password", "_clear_and_fill"),
    }

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
        users = await self.actions.get_all_texts(self.TABLE_USERNAME_CELLS)
        return next(u for u in users if u and u != exclude)

    async def _select_dropdown(self, label: str, value: str, **_):
        await self.actions.select_dynamic_custom_dropdown(self.DROPDOWN_BY_LABEL, self.DROPDOWN_OPTION, label, value)

    async def _clear_and_fill(self, label: str, value: str, blur: bool = True, **_):
        locator = self.actions.get_locator(self.INPUT_BY_LABEL, label)
        await self.waits.wait_for_element_visible(locator)
        await locator.fill(value)
        if blur:
            await locator.press("Tab")

    async def _fill_employee(self, label: str, value: str, payload: dict):
        await self._clear_and_fill(label, value, blur=False)
        if payload.get("pick_emp"):
            first_option = self.page.locator(self.AUTOCOMPLETE_OPTION).first
            await self.waits.wait_for_element_visible(first_option)
            await self.actions.wait_and_click(first_option)

    async def _toggle_change_password(self, _label: str, enabled: bool, **_):
        if enabled:
            await self.actions.wait_and_click(self.CHANGE_PASSWORD_SPAN)

    async def _fill_user_form(self, payload: dict):
        for key, (label, handler_name) in self.FIELD_HANDLERS.items():
            if key in payload:
                await getattr(self, handler_name)(label, payload[key], payload=payload)

    async def _submit_form(self, expect_success: bool):
        if expect_success:
            await self.page.wait_for_load_state("networkidle")
            async with self.actions.wait_for_api("admin/users"):
                await self.actions.click_dynamic(self.BUTTON_BY_TEXT, "Save")
            await self.waits.wait_for_element_visible(self.SUCCESS_TOAST)
        else:
            await self.actions.click_dynamic(self.BUTTON_BY_TEXT, "Save")

    async def create_user(self, payload: dict, expect_success: bool = True):
        await self.navigate_to_users()
        await self.actions.click_dynamic(self.BUTTON_BY_TEXT, "Add")
        await self._fill_user_form(payload)
        await self._submit_form(expect_success)

    async def search_user(self, username: str):
        await self.navigate_to_users()
        await self._clear_and_fill("Username", username)
        async with self.actions.wait_for_api("admin/users"):
            await self.actions.click_dynamic(self.BUTTON_BY_TEXT, "Search")

    async def edit_user(self, current_username: str, payload: dict, expect_success: bool = True):
        await self.search_user(current_username)
        await self.actions.click_dynamic(self.ROW_ACTION_BTN, current_username, "bi-pencil-fill")

        username_locator = self.actions.get_locator(self.INPUT_BY_LABEL, "Username")
        await self.waits.wait_for_element_visible(username_locator)
        await self.page.wait_for_function("([el, expected]) => el.value === expected",arg=[await username_locator.element_handle(), current_username],timeout=self.waits.timeout,)

        await self._fill_user_form(payload)
        await self._submit_form(expect_success)

    async def delete_user(self, username: str):
        await self.search_user(username)
        await self.actions.click_dynamic(self.ROW_ACTION_BTN, username, "bi-trash")
        async with self.actions.wait_for_api("admin/users"):
            await self.actions.wait_and_click(self.CONFIRM_DELETE_BTN)
        await self.waits.wait_for_element_visible(self.SUCCESS_TOAST)

    async def is_delete_disabled_or_protected(self, username: str) -> bool:
        await self.search_user(username)
        delete_locator = self.actions.get_locator(self.ROW_ACTION_BTN, username, "bi-trash")
        if not await delete_locator.is_visible() or await delete_locator.is_disabled():
            return True
        await self.actions.wait_and_click(delete_locator)
        return not await self.actions.is_visible(self.CONFIRM_DELETE_BTN)
