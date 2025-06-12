import os
from dotenv import load_dotenv
from .base_page import BasePage

load_dotenv()  # pulls vars from .env if present


class LoginPage(BasePage):
    URL = "https://partner-dev-benefits.plansource.com"

    _UNAME = (BasePage.By.ID, "user_name")
    _PWD   = (BasePage.By.ID, "password")
    _SUBMIT= (BasePage.By.ID, "logon_submit")

    def open(self):
        self.driver.get(self.URL)
        return self

    def login(self, user: str | None = None, pwd: str | None = None):
        user = user or os.getenv("PS_USER")
        pwd  = pwd  or os.getenv("PS_PASS")
        if not (user and pwd):
            raise RuntimeError("PS_USER / PS_PASS not set")
        self._type(self._UNAME, user)
        self._type(self._PWD,  pwd)
        self._click(self._SUBMIT)
        from .home_page import HomePage
        return HomePage(self.driver)
