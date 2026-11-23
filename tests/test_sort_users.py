import pytest
import pytest_asyncio
from pages.user_table_page import UserTablePage


@pytest_asyncio.fixture(autouse=True)
async def setup_users_table(logged_in_session, user_table_page: UserTablePage):
    await user_table_page.open_users_table()


@pytest.mark.regression
@pytest.mark.parametrize("order", ["Ascending", "Descending"])
async def test_sort_username_column(user_table_page: UserTablePage, order: str):
    await user_table_page.sort_and_verify_column("Username", column_index=2, order=order)
