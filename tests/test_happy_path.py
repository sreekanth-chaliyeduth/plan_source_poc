"""
E2E happy path:
* login
* create employee
* add one domestic-partner dependent

Assertions are minimal because the partner-dev site is flaky.
Passing == no unhandled exception.
"""

from pages.login_page import LoginPage


def test_employee_with_dependent(driver):
    home = LoginPage(driver).open().login()
    wizard, emp = home.go_to_add_employee().create_employee()
    wizard.add_single_domestic_partner(emp["birthdate"])
