import uuid
import pytest
from pages.user_management_page import UserManagementPage
from utils.test_data import EDIT_USERNAME_VALIDATIONS, unique_username

_unique_username = unique_username

@pytest.mark.regression
@pytest.mark.parametrize("invalid_username, expected_error", EDIT_USERNAME_VALIDATIONS)
async def test_edit_user_invalid_username_negative(
    logged_in_session,
    user_management_page: UserManagementPage,
    invalid_username: str,
    expected_error: str,
):
    username = _unique_username("edneg")
    await user_management_page.create_user(username=username)
    try:
        await user_management_page.edit_user(
            current_username=username,
            new_username=invalid_username,
            expect_success=False,
        )
        await user_management_page.asserts.assert_dynamic_contains_text(
            user_management_page.ERROR_BY_LABEL, expected_error, "Username"
        )
    finally:
        await user_management_page.delete_user(username)
