import pytest
import pytest_asyncio
from pages.admin_user_page import AdminUserPage
from utils.test_data import (
    ADD_USER_NEGATIVE_VALIDATIONS,
    get_valid_add_user_payload,
    unique_username,
)


@pytest_asyncio.fixture(autouse=True)
async def setup_add_user(logged_in_session, admin_user_page: AdminUserPage):
    await admin_user_page.open_add_user_form()


@pytest.mark.regression
async def test_validate_error_messages_when_all_fields_empty(admin_user_page: AdminUserPage):
    await admin_user_page.submit_form({})
    await admin_user_page.asserts.assert_element_count(admin_user_page.ALL_FIELD_ERRORS, 6)


@pytest.mark.regression
@pytest.mark.parametrize("payload, error_label, expected_msg", ADD_USER_NEGATIVE_VALIDATIONS)
async def test_validate_error_message_with_invalid_user_inputs(
    admin_user_page: AdminUserPage,
    payload: dict,
    error_label: str,
    expected_msg: str,
):
    await admin_user_page.submit_form(payload)
    await admin_user_page.asserts.assert_dynamic_contains_text(admin_user_page.ERROR_BY_LABEL, expected_msg, error_label)


@pytest.mark.smoke
@pytest.mark.regression
async def test_create_new_user(admin_user_page: AdminUserPage):
    username = unique_username()
    payload = get_valid_add_user_payload(username)

    await admin_user_page.submit_form(payload)
    await admin_user_page.wait_for_success_toast()
    await admin_user_page.search_user(username)
    await admin_user_page.asserts.assert_element_visible(admin_user_page.actions.get_dynamic_locator(admin_user_page.TABLE_CELL_BY_TEXT, username))
