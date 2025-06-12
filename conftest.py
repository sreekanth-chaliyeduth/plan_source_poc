"""
Central driver fixture.
Runs Chrome in 'headless=new' mode (Chrome ≥115) for faster CI,
but can be overridden with  --headed  when debugging locally.
"""

import os
import time
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def _build_driver(headless: bool = True):
    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(options=opts)


def _kill_stale_chrome():
    """
    Partner-dev leaves zombie Chrome processes if the test crashes.
    A quick pre-clean keeps CI machines healthy.
    """
    os.system("pkill -f 'Google Chrome' || true")
    time.sleep(2)


def pytest_addoption(parser):
    parser.addoption("--headed", action="store_true",
                     help="Run browser in headed mode for debugging")


@pytest.fixture(scope="session")
def driver(pytestconfig):
    _kill_stale_chrome()
    drv = _build_driver(headless=not pytestconfig.getoption("--headed"))
    yield drv
    drv.quit()
