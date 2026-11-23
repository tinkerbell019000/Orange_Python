import pytest
from pages.login_page import LoginPage


@pytest.mark.regression
@pytest.mark.smoke
async def test_login(login_page: LoginPage):
    await login_page.login_to_orangehrm()
    await login_page.actions.waits.wait_for_element_visible(login_page.SIDE_MENU)
