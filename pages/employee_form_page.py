"""
Employee creation screen.
Fields dictionary keeps locators tidy and lets us loop through them.
"""

import random
from datetime import datetime, timedelta
from faker import Faker
from .base_page import BasePage

fake = Faker()


class EmployeeFormPage(BasePage):
    # field-to-locator map
    _F = {
        "password":        (BasePage.By.ID, "password"),
        "first_name":      (BasePage.By.ID, "first_name"),
        "last_name":       (BasePage.By.ID, "last_name"),
        "ssn":             (BasePage.By.ID, "ssn_text"),
        "address":         (BasePage.By.ID, "address_1"),
        "city":            (BasePage.By.ID, "city"),
        "state":           (BasePage.By.ID, "stateTypeahead"),
        "zip":             (BasePage.By.ID, "zip_code"),
        "country":         (BasePage.By.ID, "countryTypeahead"),
        "birthdate":       (BasePage.By.ID, "birthdate"),
        "gender":          (BasePage.By.ID, "gender"),
        "marital_status":  (BasePage.By.ID, "marital_status"),
        "hire_date":       (BasePage.By.ID, "hire_date"),
        "benefits_start":  (BasePage.By.ID, "benefits_start_date"),
        "employment_level":(BasePage.By.ID, "employment_level"),
        "location":        (BasePage.By.ID, "location"),
        "current_salary":  (BasePage.By.ID, "current_salary"),
        "benefit_salary":  (BasePage.By.ID, "benefit_salary"),
        "payroll_id":      (BasePage.By.ID, "org_payroll_id"),
    }
    _SAVE = (BasePage.By.ID, "btn_save")

    # ---------------- data factory ---------------- #
    def _fake_employee(self) -> dict:
        bd = fake.date_of_birth(minimum_age=18, maximum_age=60)
        return {
            "password": fake.password(length=10, special_chars=True, digits=True,
                                      upper_case=True, lower_case=True),
            "first_name": fake.first_name(),
            "last_name":  fake.last_name(),
            "ssn": fake.ssn().replace("-", "")[:9],
            "address": fake.street_address(),
            "city": fake.city(),
            "state": fake.state(),
            "zip": fake.zipcode_in_state(state_abbr=fake.state_abbr()),
            "country": "United States",
            "birthdate": bd.strftime("%m/%d/%Y"),
            "gender": random.choice(["Male", "Female"]),
            "marital_status": random.choice(["Single", "Married"]),
            "hire_date": (datetime.today() - timedelta(days=2)).strftime("%m/%d/%Y"),
            "benefits_start": (datetime.today() - timedelta(days=2)).strftime("%m/%d/%Y"),
            "employment_level": random.choice(["F", "P"]),
            "location": random.choice(["SCA", "NCA", "NONCA"]),
            "current_salary": str(random.randint(50_000, 150_000)),
            "benefit_salary": str(random.randint(40_000, 130_000)),
            "payroll_id": random.choice(["Semi-monthly", "Monthly", "Bi-weekly"]),
        }

    # ---------------- public api ---------------- #
    def create_employee(self, data: dict | None = None):
        """
        Fills the form, hits Save, and hands back the Enrollment wizard page plus data
        so tests can piggy-back on birthdate/age.
        """
        data = data or self._fake_employee()
        for key, locator in self._F.items():
            self._type(locator, data[key])
        self._click(self._SAVE)

        from .enrollment_wizard import EnrollmentWizard
        return EnrollmentWizard(self.driver), data
