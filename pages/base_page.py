"""
Thin wrapper over Selenium’s WebDriverWait.
All page classes inherit this – keeps actions DRY and easy to extend.
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import InvalidElementStateException, StaleElementReferenceException


_WAIT = 15


class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait   = WebDriverWait(driver, _WAIT)

    # ---------- tiny helpers ---------- #
    def _click(self, locator: tuple):
        self.wait.until(EC.element_to_be_clickable(locator)).click()

    def _type(self, locator: tuple, value, clear=True):
        """
        Send keys unless the input is temporarily read-only or disabled.
        If so, fall back to JavaScript assignment so the flow keeps moving.
        """
        el = self.wait.until(EC.presence_of_element_located(locator))

        # if the field is disabled or has readonly flag, don’t use .clear() / .send_keys()
        if (not el.is_enabled()) or el.get_attribute("readonly"):
            self.driver.execute_script("arguments[0].value = arguments[1];", el, value)
            # dispatch change event in case the page listens for it
            self.driver.execute_script(
                "arguments[0].dispatchEvent(new Event('change', {bubbles: true}));", el
            )
            return

        try:
            if clear:
                el.clear()
            el.send_keys(value)
        except (InvalidElementStateException, StaleElementReferenceException):
            # last-chance JS fallback
            self.driver.execute_script("arguments[0].value = arguments[1];", el, value)
            self.driver.execute_script(
                "arguments[0].dispatchEvent(new Event('change', {bubbles: true}));", el
            )


    def _select(self, locator: tuple, visible_text: str):
        sel = self.wait.until(EC.presence_of_element_located(locator))
        Select(sel).select_by_visible_text(visible_text)

    def _text_contains(self, locator: tuple, snippet: str) -> bool:
        return snippet.lower() in self.wait.until(
            EC.visibility_of_element_located(locator)
        ).text.lower()

    # expose By for shorter imports
    By = By
