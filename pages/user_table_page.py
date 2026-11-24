from playwright.async_api import Page
from utils.element_actions import ElementActions
from utils.asserts import AssertData


class UserTablePage:
    MENU_LINK = "a[href*='view{}Module']"
    SORT_HEADER = "//div[@role='columnheader'][contains(.,'{}')]//div[@class='oxd-table-header-sort']"
    SORT_OPTION = "//div[@role='columnheader'][contains(.,'{}')]//div[contains(@class,'oxd-table-header-sort-dropdown')]//span[text()='{}']"
    COLUMN_CELLS = "//div[@class='oxd-table-body']//div[@role='row']//div[@role='cell'][{}]"

    def __init__(self, page: Page):
        self.actions = ElementActions(page)
        self.asserts = AssertData(page)

    async def open_users_table(self):
        await self.actions.click_dynamic(self.MENU_LINK, "Admin")
        await self.actions.get_all_texts(self.COLUMN_CELLS, 2)

    async def sort_and_verify_column(self, column_name: str, column_index: int, order: str):
        async wi
        th self.actions.wait_for_api("admin/users"):
            await self.actions.select_dynamic_custom_dropdown(
                self.SORT_HEADER, self.SORT_OPTION, column_name, order
            )
        values = await self.actions.get_all_texts(self.COLUMN_CELLS, column_index)
        await self.asserts.assert_list_sorted(values, descending=(order == "Descending"))
