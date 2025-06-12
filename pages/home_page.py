from .base_page import BasePage


class HomePage(BasePage):
    _ADD_EMP = (BasePage.By.LINK_TEXT, "Add a New Employee")

    def go_to_add_employee(self):
        self._click(self._ADD_EMP)
        from .employee_form_page import EmployeeFormPage
        return EmployeeFormPage(self.driver)
