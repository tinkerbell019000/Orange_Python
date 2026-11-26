import asyncio
import os
import re
import pytest
import pytest_asyncio
from playwright.async_api import async_playwright
from config.config import Config
from pages.login_page import LoginPage
from pages.select_side_menu_page import SideMenuPage
from pages.admin_user_page import AdminUserPage
from pages.user_table_page import UserTablePage
from pages.user_management_page import UserManagementPage

HEADLESS = os.getenv("HEADLESS", str(getattr(Config, "HEADLESS", False))).lower() == "true"

BROWSER_CONFIGS = {
    "chrome": {
        "type": "chromium",
        "kwargs": {
            "headless": HEADLESS,
            "slow_mo": 0 if HEADLESS else 300,
            "args": ["--no-sandbox", "--disable-dev-shm-usage", "--start-maximized"],
        },
    },
    "edge": {
        "type": "chromium",
        "kwargs": {
            "channel": "msedge",
            "headless": HEADLESS,
            "slow_mo": 0 if HEADLESS else 300,
            "args": ["--no-sandbox", "--disable-dev-shm-usage", "--start-maximized"],
        },
    },
    "firefox": {"type": "firefox", "kwargs": {"headless": HEADLESS, "slow_mo": 0 if HEADLESS else 300}},
    "webkit": {"type": "webkit", "kwargs": {"headless": HEADLESS, "slow_mo": 0 if HEADLESS else 300}},
}


@pytest_asyncio.fixture(scope="session")
async def page():
    requested = os.getenv("BROWSER", getattr(Config, "BROWSER", "chrome")).lower()
    candidates = [requested, "chrome"] if requested != "chrome" else ["chrome"]

    async with async_playwright() as p:
        browser = None
        for name in candidates:
            if cfg := BROWSER_CONFIGS.get(name):
                try:
                    browser = await getattr(p, cfg["type"]).launch(**cfg["kwargs"])
                    break
                except Exception:
                    continue
        if not browser:
            raise RuntimeError("No supported browser could be launched.")

        is_chromium = browser.browser_type.name == "chromium"
        context = await browser.new_context(
            no_viewport=False if HEADLESS else is_chromium,
            viewport={"width": 1920, "height": 1080} if (HEADLESS or not is_chromium) else None,
        )
        page = await context.new_page()
        yield page
        await page.close()
        await context.close()
        await browser.close()


@pytest.fixture(scope="session")
def login_page(page): return LoginPage(page)

@pytest.fixture(scope="session")
def select_side_menu_page(page): return SideMenuPage(page)

@pytest.fixture(scope="session")
def admin_user_page(page): return AdminUserPage(page)

@pytest.fixture(scope="session")
def user_table_page(page): return UserTablePage(page)

@pytest.fixture(scope="session")
def user_management_page(page): return UserManagementPage(page)

@pytest_asyncio.fixture(scope="session")
async def logged_in_session(login_page: LoginPage):
    await login_page.login_to_orangehrm()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    extras = getattr(report, "extras", [])

    if report.when == "call" and report.failed:
        if page := item.funcargs.get("page"):
            os.makedirs("reports/screenshots", exist_ok=True)
            safe_name = re.sub(r"[^\w\-]", "_", item.name)
            screenshot_path = f"reports/screenshots/{safe_name}.png"
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.ensure_future(page.screenshot(path=screenshot_path))
            else:
                loop.run_until_complete(page.screenshot(path=screenshot_path))
            if pytest_html := item.config.pluginmanager.getplugin("html"):
                extras.append(pytest_html.extras.image(screenshot_path))
    report.extras = extras
