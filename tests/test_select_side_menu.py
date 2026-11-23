import pytest
from pages.select_side_menu_page import SideMenuPage

@pytest.mark.regression
@pytest.mark.smoke
async def test_select_side_menu(logged_in_session, select_side_menu_page: SideMenuPage):
    await select_side_menu_page.select_menu_option("Admin")