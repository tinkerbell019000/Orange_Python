import pytest
import pytest_asyncio
from config.config import Config
from pages.user_management_page import UserManagementPage
from utils.test_data import EDIT_USER_NEGATIVE_VALIDATIONS, unique_username


@pytest_asyncio.fixture(scope="module")
async def shared_test_user(logged_in_session, user_management_page: UserManagementPage):
    username = unique_username("edneg")
    await user_management_page.create_user(username=username)
    yield username
    await user_management_page.delete_user(username)

@pytest.mark.smoke
@pytest.mark.regression
async def test_search_user_valid_positive(
    shared_test_user: str,
    user_management_page: UserManagementPage,
):
    await user_management_page.search_user(shared_test_user)
    await user_management_page.asserts.assert_element_visible(
        user_management_page.actions.get_dynamic_locator(
            user_management_page.TABLE_ROW_BY_USER, shared_test_user
        )
    )

@pytest.mark.regression
async def test_search_user_non_existent_negative(
    logged_in_session,
    user_management_page: UserManagementPage,
):
    ghost_user = unique_username("ghost")
    await user_management_page.search_user(ghost_user)
    await user_management_page.asserts.assert_element_visible(user_management_page.NO_RECORDS_TEXT)

@pytest.mark.regression
@pytest.mark.parametrize("updates, error_label, expected_error", EDIT_USER_NEGATIVE_VALIDATIONS)
async def test_edit_user_all_field_validations_negative(
    shared_test_user: str,
    user_management_page: UserManagementPage,
    updates: dict,
    error_label: str,
    expected_error: str,
):
    payload = dict(updates)
    if payload.get("username") == "EXISTING_USER":
        payload["username"] = await user_management_page.get_any_existing_username(
            exclude=shared_test_user
        )

    await user_management_page.edit_user(
        current_username=shared_test_user,
        updates=payload,
        expect_success=False,
    )
    await user_management_page.asserts.assert_dynamic_contains_text(
        user_management_page.ERROR_BY_LABEL, expected_error, error_label
    )

@pytest.mark.smoke
@pytest.mark.regression
async def test_edit_user_positive(
    logged_in_session,
    user_management_page: UserManagementPage,
):
    original_username = unique_username("edit_orig")
    updated_username = unique_username("edit_new")

    await user_management_page.create_user(
        username=original_username, role="ESS", status="Enabled"
    )
    try:
        await user_management_page.edit_user(
            current_username=original_username,
            updates={
                "role": "Admin",
                "status": "Disabled",
                "username": updated_username,
                "change_password": True,
                "password": "NewPassword@123",
                "confirm_password": "NewPassword@123",
            },
            expect_success=True,
        )
        await user_management_page.search_user(updated_username)
        await user_management_page.asserts.assert_element_visible(
            user_management_page.actions.get_dynamic_locator(
                user_management_page.TABLE_ROW_BY_USER, updated_username
            )
        )
    finally:
        await user_management_page.delete_user(updated_username)

@pytest.mark.smoke
@pytest.mark.regression
async def test_delete_user_valid_positive(
    logged_in_session,
    user_management_page: UserManagementPage,
):
    username = unique_username("del_ok")
    await user_management_page.create_user(username=username)

    await user_management_page.delete_user(username)
    await user_management_page.search_user(username)
    await user_management_page.asserts.assert_element_visible(user_management_page.NO_RECORDS_TEXT)


@pytest.mark.regression
async def test_delete_logged_in_user_invalid_negative(
    logged_in_session,
    user_management_page: UserManagementPage,
):
    is_protected = await user_management_page.is_delete_disabled_or_protected(Config.USERNAME)
    assert is_protected, f"Expected logged-in user '{Config.USERNAME}' to be protected from deletion."
