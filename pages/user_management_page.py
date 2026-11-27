import importlib
from playwright.async_api import Page
from utils.element_actions import ElementActions
from utils.logger import get_logger
from utils.waits import Waits

try:
    AssertData = importlib.import_module("utils.assert").AssertData
except ModuleNotFoundError:
    AssertData = importlib.import_module("utils.asserts").AssertData
logger = get_logger(__name__)

class UserManagementPage:
    USERS_API_ENDPOINT = "/api/v2/admin/users"
    MENU_ITEM_BY_NAME = "//aside//a[contains(@class,'oxd-main-menu-item')][.//span[normalize-space()='{}']]"
    BUTTON_BY_TEXT = "//button[normalize-space()='{}']"
    INPUT_BY_LABEL = "//div[contains(@class,'oxd-input-group')][.//label[normalize-space()='{}']]//input"
    DROPDOWN_BY_LABEL = "//div[contains(@class,'oxd-input-group')][.//label[normalize-space()='{}']]//div[contains(@class,'oxd-select-text-input')]"
    DROPDOWN_OPTION_BY_TEXT = "//div[@role='listbox']//div[@role='option'][.//span[normalize-space()='{}']]"
    AUTOCOMPLETE_OPTION = "//div[@role='listbox']//div[@role='option'][not(contains(.,'Searching')) and not(contains(.,'No Records'))]"

    CHECKBOX_ICON_BY_LABEL = "//div[contains(@class,'oxd-input-group')][.//label[normalize-space()='{}']]//i[contains(@class,'oxd-checkbox-input-icon')]"
    ERROR_BY_LABEL = "//div[contains(@class,'oxd-input-group')][.//label[normalize-space()='{}']]//span[contains(@class,'oxd-input-field-error-message')]"

    TABLE_ROW_BY_USER = "//div[@role='table']//div[@role='row'][.//div[@role='cell'][normalize-space()='{}']]"
    ROW_ACTION_BY_USER = "//div[@role='table']//div[@role='row'][.//div[@role='cell'][normalize-space()='{}']]//button[.//i[contains(@class,'{}')]]"

    NO_RECORDS_TEXT = "//div[contains(@class,'orangehrm-paper-container')]//span[normalize-space()='No Records Found']"
    SUCCESS_TOAST = "//div[contains(@class,'oxd-toast-container')]//div[contains(@class,'oxd-toast--success')]"
    LOADING_SPINNER = "//div[contains(@class,'oxd-form-loader')]"
    ERROR_TOAST = "//div[contains(@class,'oxd-toast-container')]//div[contains(@class,'oxd-toast--error') or contains(@class,'oxd-toast--warn')]"
    EDIT_ICON_CLASS = "bi-pencil-fill"
    DELETE_ICON_CLASS = "bi-trash"

    DROPDOWN_FIELDS = (("role", "User Role"), ("status", "Status"))
    TEXT_FIELDS = (
        ("username", "Username"),
        ("password", "Password"),
        ("confirm_password", "Confirm Password"),
    )

    def __init__(self, page: Page):
        self.page = page
        self.actions = ElementActions(page)
        self.waits = Waits(page)
        self.asserts = AssertData(page)

    async def _fill_labeled_input(self, label: str, value: str) -> None:
        selector = self.actions.get_dynamic_locator(self.INPUT_BY_LABEL, label)
        await self.actions.wait_and_fill(selector, value)

    async def _click_button(self, button_text: str) -> None:
        await self.actions.click_dynamic(self.BUTTON_BY_TEXT, button_text)

    async def navigate_to_user_management(self) -> None:
        if "admin/viewSystemUsers" not in self.page.url:
            base_host = self.page.url.split("/web/")[0]
            await self.page.goto(f"{base_host}/web/index.php/admin/viewSystemUsers")
        await self.waits.wait_for_element_hidden(self.LOADING_SPINNER)

    async def _fill_user_form(self, payload: dict) -> None:
        for key, label in self.DROPDOWN_FIELDS:
            if payload.get(key):
                await self.actions.select_dynamic_custom_dropdown(dropdown_click_template=self.DROPDOWN_BY_LABEL,option_text_template=self.DROPDOWN_OPTION_BY_TEXT,dropdown_arg=label,option_arg=payload[key],)

        if "employee" in payload:
            await self._fill_labeled_input("Employee Name", payload["employee"])
            if payload.get("pick_emp", False):
                first_option = self.actions.get_locator(self.AUTOCOMPLETE_OPTION).first
                await self.actions.wait_and_click(first_option)

        if payload.get("change_password", False):
            await self.actions.click_dynamic(self.CHECKBOX_ICON_BY_LABEL, "Change Password ?")

        for key, label in self.TEXT_FIELDS:
            if key in payload:
                await self._fill_labeled_input(label, payload[key])

    async def search_user(self, payload: dict) -> None:
        username = payload["username"]
        logger.info(f"Searching user: {username}")
        await self.navigate_to_user_management()
        await self._click_button("Reset")
        await self.waits.wait_for_element_hidden(self.LOADING_SPINNER)
        await self._fill_labeled_input("Username", username)
        async with self.actions.wait_for_api(self.USERS_API_ENDPOINT, status_code=200):
            await self._click_button("Search")
        await self.waits.wait_for_element_hidden(self.LOADING_SPINNER)
    
    async def _submit_user_form(self, expect_success: bool) -> None:
        if not expect_success:
            await self.page.keyboard.press("Tab")
            await self._click_button("Save")
            return
        async with self.actions.wait_for_api(self.USERS_API_ENDPOINT, status_code=200):
            await self._click_button("Save")
        await self.waits.wait_for_element_visible(self.SUCCESS_TOAST)
        await self.waits.wait_for_element_hidden(self.LOADING_SPINNER)

    async def create_user(self, payload: dict, expect_success: bool = True) -> None:
        logger.info(f"Creating user: {payload.get('username')} (expect_success={expect_success})")
        await self.navigate_to_user_management()
        await self._click_button("Add")
        await self.waits.wait_for_url("**/admin/saveSystemUser")
        await self.waits.wait_for_element_hidden(self.LOADING_SPINNER)
        await self._fill_user_form(payload)
        await self._submit_user_form(expect_success)

    async def edit_user(self, payload: dict, expect_success: bool = True) -> None:
        current_username = payload["current_username"]
        logger.info(f"Editing user: {current_username} (expect_success={expect_success})")
        await self.search_user({"username": current_username})
        async with self.actions.wait_for_api(self.USERS_API_ENDPOINT, status_code=200):
            await self.actions.click_dynamic(self.ROW_ACTION_BY_USER, current_username, self.EDIT_ICON_CLASS)
        await self.waits.wait_for_url("**/admin/saveSystemUser/**")
        await self.waits.wait_for_element_hidden(self.LOADING_SPINNER)
        await self._fill_user_form(payload)
        await self._submit_user_form(expect_success)

    async def delete_user(self, payload: dict) -> None:
        username = payload["username"]
        logger.info(f"Deleting user: {username}")
        await self.search_user({"username": username})
        await self.actions.click_dynamic(
            self.ROW_ACTION_BY_USER, username, self.DELETE_ICON_CLASS
        )
        await self.actions.click_dynamic(self.BUTTON_BY_TEXT, "Yes, Delete")
        await self.waits.wait_for_element_visible(self.SUCCESS_TOAST)
        await self.waits.wait_for_element_hidden(self.LOADING_SPINNER)

    async def is_delete_disabled_or_protected(self, payload: dict) -> bool:
        username = payload["username"]
        logger.info(f"Checking delete protection for user: {username}")

        await self.search_user({"username": username})
        delete_btn = self.actions.get_locator(self.ROW_ACTION_BY_USER, username, self.DELETE_ICON_CLASS)

        if (await delete_btn.count() == 0 or not await delete_btn.is_visible() or await delete_btn.is_disabled() or "disabled" in ((await delete_btn.get_attribute("class")) or "").lower()):
            return True

        await self.actions.wait_and_click(delete_btn)
        try:
            await self.actions.get_locator(self.ERROR_TOAST).wait_for(state="visible", timeout=5000)
            return True
        except Exception:
            return False
