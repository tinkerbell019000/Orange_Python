from contextlib import suppress
import pytest
import pytest_asyncio

from config.config import Config
from pages.user_management_page import UserManagementPage
from utils.test_data import (
    ADD_USER_NEGATIVE_VALIDATIONS,
    EDIT_USER_NEGATIVE_VALIDATIONS,
    get_user_lookup_payload,
    get_valid_add_user_payload,
    get_valid_edit_user_payload,
    unique_username,
)

pytestmark = pytest.mark.asyncio

@pytest_asyncio.fixture(scope="module")
async def shared_test_user(logged_in_session,user_management_page: UserManagementPage,) -> dict:

    payload = get_valid_add_user_payload(unique_username("shared"))
    await user_management_page.create_user(payload, expect_success=True)
    try:
        yield payload
    finally:
        with suppress(Exception):
            await user_management_page.delete_user(payload)


@pytest_asyncio.fixture
async def disposable_user(logged_in_session,user_management_page: UserManagementPage,) -> dict:
    payload = get_valid_add_user_payload(unique_username("disp"))
    state = {"username": payload["username"]}
    await user_management_page.create_user(payload, expect_success=True)
    try:
        yield state
    finally:
        if state.get("username"):
            with suppress(Exception):
                await user_management_page.delete_user(state)

@pytest.mark.smoke
@pytest.mark.regression
async def test_add_user_valid_positive(logged_in_session,user_management_page: UserManagementPage,):
    payload = get_valid_add_user_payload()
    try:
        await user_management_page.create_user(payload, expect_success=True)
        await user_management_page.search_user(payload)
        await user_management_page.asserts.assert_element_visible(user_management_page.TABLE_ROW_BY_USER,payload["username"],)
    finally:
        with suppress(Exception):
            await user_management_page.delete_user(payload)


@pytest.mark.regression
@pytest.mark.parametrize("overrides, error_label, expected_error",ADD_USER_NEGATIVE_VALIDATIONS,)
async def test_add_user_all_field_validations_negative(logged_in_session,user_management_page: UserManagementPage,overrides: dict,error_label: str,expected_error: str,):
    payload = {**get_valid_add_user_payload(), **overrides}
    await user_management_page.create_user(payload, expect_success=False)
    await user_management_page.asserts.assert_dynamic_contains_text(user_management_page.ERROR_BY_LABEL,expected_error,error_label,)

@pytest.mark.smoke
@pytest.mark.regression
async def test_search_user_valid_positive(shared_test_user: dict,user_management_page: UserManagementPage,):
    await user_management_page.search_user(shared_test_user)
    await user_management_page.asserts.assert_element_visible(user_management_page.TABLE_ROW_BY_USER,shared_test_user["username"],)


@pytest.mark.regression
async def test_search_user_non_existent_negative(logged_in_session,user_management_page: UserManagementPage,):
    ghost_payload = get_user_lookup_payload(unique_username("ghost"))
    await user_management_page.search_user(ghost_payload)
    await user_management_page.asserts.assert_element_visible(user_management_page.NO_RECORDS_TEXT)

@pytest.mark.smoke
@pytest.mark.regression
async def test_edit_user_valid_positive(disposable_user: dict,user_management_page: UserManagementPage,):
    edit_payload = get_valid_edit_user_payload(current_username=disposable_user["username"])
    await user_management_page.edit_user(edit_payload, expect_success=True)
    disposable_user["username"] = edit_payload["username"]

    await user_management_page.search_user(disposable_user)
    await user_management_page.asserts.assert_element_visible(user_management_page.TABLE_ROW_BY_USER,disposable_user["username"],)


@pytest.mark.regression
@pytest.mark.parametrize("updates, error_label, expected_error",EDIT_USER_NEGATIVE_VALIDATIONS,)
async def test_edit_user_all_field_validations_negative(shared_test_user: dict,user_management_page: UserManagementPage,updates: dict,error_label: str,expected_error: str,):
    payload = {
        "current_username": shared_test_user["username"],
        **updates,
    }
    await user_management_page.edit_user(payload, expect_success=False)
    await user_management_page.asserts.assert_dynamic_contains_text(
        user_management_page.ERROR_BY_LABEL,
        expected_error,
        error_label,
    )

@pytest.mark.smoke
@pytest.mark.regression
async def test_delete_existing_user_positive(disposable_user: dict,user_management_page: UserManagementPage,):
    target_payload = get_user_lookup_payload(disposable_user["username"])
    await user_management_page.delete_user(target_payload)
    disposable_user["username"] = None
    await user_management_page.search_user(target_payload)
    await user_management_page.asserts.assert_element_visible(user_management_page.NO_RECORDS_TEXT)


@pytest.mark.regression
async def test_delete_logged_in_user_invalid_negative(logged_in_session,user_management_page: UserManagementPage,):
    admin_payload = get_user_lookup_payload(Config.USERNAME)
    is_protected = await user_management_page.is_delete_disabled_or_protected(admin_payload)
    assert is_protected, (f"Expected logged-in user '{Config.USERNAME}' to be protected from deletion.")
