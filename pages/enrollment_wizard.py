"""
Simple enrollment wizard that handles adding a dependent.
Note: Full benefit shopping steps are skipped since the demo site
is unstable and the focus is on the object model.
"""

import random
from faker import Faker
from .base_page import BasePage
from datetime import datetime
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException
import time

fake = Faker()


class EnrollmentWizard(BasePage):
    # UI element locators
    _START_ENROLL = (BasePage.By.PARTIAL_LINK_TEXT, "Hire Enrollment")
    _GET_STARTED  = (BasePage.By.XPATH, "//a[@id='enrollmentStepOne']")
    _NEXT_FAMILY  = (BasePage.By.XPATH, "//span[contains(text(),'Next: Review My Family')]")
    _ADD_FAMILY   = (BasePage.By.XPATH, "//a[@href='/subscriber/family/new']")
    _DEP_FIRST    = (BasePage.By.ID, "first_name")
    _DEP_LAST     = (BasePage.By.ID, "last_name")
    _DEP_GENDER   = (BasePage.By.ID, "gender")
    _DEP_BIRTH    = (BasePage.By.ID, "birthdate")
    _REL_DD       = (BasePage.By.XPATH, "//span[contains(@class,'filter-option')]")
    _REL_OPT_DOM  = (BasePage.By.XPATH, "//span[text()='Domestic Partner']")
    _SAVE_DEP     = (BasePage.By.ID, "submit_form")

    # ---------------- flow helpers ---------------- #
    def _open_family_review(self):
        # Start the enrollment process
        self._click(self._START_ENROLL)

        # Get the Get Started button and wait for it to be ready
        get_started = self.wait.until(EC.presence_of_element_located(self._GET_STARTED))

        # Let any loading overlays clear
        time.sleep(1)

        # Make sure the button is visible
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", get_started)
        time.sleep(0.5)

        # Try clicking normally first, fall back to JS click if needed
        try:
            get_started.click()
        except ElementClickInterceptedException:
            self.driver.execute_script("arguments[0].click();", get_started)

        self._click(self._NEXT_FAMILY)

    def _add_domestic_partner(self, employee_age: int):
        self._click(self._ADD_FAMILY)

        # Generate random but valid dependent data
        gender = random.choice(["Male", "Female"])
        first  = fake.first_name_female() if gender == "Female" else fake.first_name_male()
        last   = fake.last_name()
        min_a  = max(employee_age - 2, 18)
        max_a  = max(employee_age + 2, 18)
        bd     = fake.date_of_birth(minimum_age=min_a, maximum_age=max_a).strftime("%m/%d/%Y")

        # Fill out the dependent form
        self._type(self._DEP_FIRST, first)
        self._type(self._DEP_LAST,  last)
        self._select(self._DEP_GENDER, gender)
        self._type(self._DEP_BIRTH,  bd)

        # Set relationship to Domestic Partner
        self._click(self._REL_DD)
        self._click(self._REL_OPT_DOM)
        self._click(self._SAVE_DEP)

    # ---------------- public api ---------------- #
    def add_single_domestic_partner(self, employee_birthdate: str):
        self._open_family_review()
        emp_age = (datetime.today() - datetime.strptime(employee_birthdate, "%m/%d/%Y")).days // 365
        self._add_domestic_partner(emp_age)
        return self
