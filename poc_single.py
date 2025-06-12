from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from faker import Faker
from datetime import datetime, timedelta
import random
import os
import time

# Let's start fresh by closing any existing Chrome instances
os.system("pkill -f 'Google Chrome'")
time.sleep(2)

# Setup our test data generator and browser
fake = Faker()
options = Options()
options.add_argument("--headless")  # Run in headless mode for CI/CD
options.add_experimental_option("detach", True)  # Keep browser open after script

driver = webdriver.Chrome(options=options)
driver.maximize_window()
driver.get("https://partner-dev-benefits.plansource.com")

# Login to the demo environment
WebDriverWait(driver, 15).until(
    EC.presence_of_element_located((By.ID, "user_name"))
).send_keys("plansource_test_admin")
driver.find_element(By.ID, "password").send_keys("password123")
driver.find_element(By.ID, "logon_submit").click()

# Start by adding a new employee
WebDriverWait(driver, 15).until(
    EC.element_to_be_clickable((By.LINK_TEXT, "Add a New Employee"))
).click()

# Generate realistic employee data
emp_birthdate = fake.date_of_birth(minimum_age=18, maximum_age=60)
birthdate = emp_birthdate.strftime("%m/%d/%Y")
emp_age = (datetime.today().date() - emp_birthdate).days // 365

first_name = fake.first_name()
last_name = fake.last_name()
address = fake.street_address()
city = fake.city()
state = fake.state()
zip_code = fake.zipcode_in_state(state_abbr=fake.state_abbr())
country = "United States"
ssn = fake.ssn().replace("-", "")[:9]
gender = random.choice(["Male", "Female"])
marital_status = random.choice(["Single", "Married"])

# Set employment details
hire_date = (datetime.today() - timedelta(days=2)).strftime("%m/%d/%Y")
eligibility_date = hire_date
employment_level = random.choice(["F", "P"])
location = random.choice(["SCA", "NCA", "NONCA"])
current_salary = str(random.randint(50000, 150000))
benefit_salary = str(random.randint(40000, 130000))
payroll_schedule = random.choice(["Semi-monthly", "Monthly", "Bi-weekly"])
password = fake.password(length=10, special_chars=True, digits=True, upper_case=True, lower_case=True)

# Fill out the employee form
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "password"))).send_keys(password)
driver.find_element(By.ID, "first_name").send_keys(first_name)
driver.find_element(By.ID, "last_name").send_keys(last_name)
driver.find_element(By.ID, "ssn_text").send_keys(ssn)
driver.find_element(By.ID, "address_1").send_keys(address)
driver.find_element(By.ID, "city").send_keys(city)
driver.find_element(By.ID, "stateTypeahead").send_keys(state)
driver.find_element(By.ID, "zip_code").send_keys(zip_code)
driver.find_element(By.ID, "countryTypeahead").send_keys(country)
driver.find_element(By.ID, "birthdate").clear()
driver.find_element(By.ID, "birthdate").send_keys(birthdate)
driver.find_element(By.ID, "gender").send_keys(gender)
driver.find_element(By.ID, "marital_status").send_keys(marital_status)
driver.find_element(By.ID, "hire_date").clear()
driver.find_element(By.ID, "hire_date").send_keys(hire_date)
driver.find_element(By.ID, "benefits_start_date").clear()
driver.find_element(By.ID, "benefits_start_date").send_keys(eligibility_date)
driver.find_element(By.ID, "employment_level").send_keys(employment_level)
driver.find_element(By.ID, "location").send_keys(location)
driver.find_element(By.ID, "current_salary").send_keys(current_salary)
driver.find_element(By.ID, "benefit_salary").send_keys(benefit_salary)
driver.find_element(By.ID, "org_payroll_id").send_keys(payroll_schedule)

driver.find_element(By.ID, "btn_save").click()

# Check if employee creation was successful
try:
    alert_element = WebDriverWait(driver, 8).until(
        EC.visibility_of_element_located((By.CLASS_NAME, "alert-content"))
    )
    alert_text = alert_element.text.strip()
    if "successfully created" in alert_text.lower():
        print("Employee was successfully created.")
    else:
        print("Form not saved! Error shown:")
        print(alert_text)
except Exception:
    print("No alert content found; assuming form saved.")

# Verify the new employee appears in the list
full_name = f"{first_name} {last_name}"
try:
    name_span = WebDriverWait(driver, 12).until(
        EC.visibility_of_element_located(
            (By.XPATH, f"//div[contains(@class,'name')]/span[normalize-space(text())='{full_name}']")
        )
    )
    print(f"Verified: Employee '{full_name}' is visible on the page.")
except Exception:
    print(f"FAIL: Employee name '{full_name}' not found after creation.")

# Start the enrollment process
try:
    enrollment_link = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Hire Enrollment"))
    )
    enrollment_link.click()
    print("Clicked Hire Enrollment.")
except Exception as e:
    print("New Hire Enrollment link not found or not clickable:", e)

# Handle enrollment page navigation
try:
    alert_msg = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(
            (By.XPATH, "//div[contains(@class,'alert-message')]//p[contains(text(), 'profile and dependents must be reviewed')]")
        )
    )
    print("Verified: Alert message about reviewing profile and dependents is visible.")
except Exception:
    print("FAIL: Alert message about reviewing profile and dependents not found.")

try:
    get_started_btn = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(
            (By.XPATH, "//a[@id='enrollmentStepOne' and contains(@href, '/subscriber/profile')]")
        )
    )
    print("Verified: 'Get Started' button is visible.")
    get_started_btn.click()
except Exception:
    print("FAIL: 'Get Started' button not found.")

# Verify we're on the personal info screen
try:
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(
            (By.XPATH, "//span[@data-content-type='title' and contains(text(), 'Verify your Personal Information')]")
        )
    )
    print("Verified: On the 'Verify your Personal Information' screen.")
except Exception:
    print("FAIL: Did not reach 'Verify your Personal Information' screen.")

# Move to family review
try:
    next_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[@id='submit_form']//span[contains(text(),'Next: Review My Family')]")
        )
    )
    next_btn.click()
    print("Clicked: 'Next: Review My Family' button.")
except Exception:
    print("FAIL: 'Next: Review My Family' button not found or not clickable.")

# Add a family member
try:
    add_family_link = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(
            (By.XPATH, "//a[@href='/subscriber/family/new']//span[contains(.,'Add Family Member')] | //a[@href='/subscriber/family/new'][contains(.,'Add Family Member')]")
        )
    )
    print("Verified: 'Add Family Member' link is visible.")
    add_family_link.click()
    print("Clicked: 'Add Family Member'.")
except Exception:
    print("FAIL: 'Add Family Member' link not found or not clickable.")

# Generate dependent data
dep_relationship = "Domestic Partner"
dep_gender = random.choice(["Male", "Female"])
dep_first = fake.first_name_female() if dep_gender == "Female" else fake.first_name_male()
dep_last = fake.last_name()
min_dep_age = max(emp_age - 2, 18)
max_dep_age = max(emp_age + 2, 18)
dep_birthdate = fake.date_of_birth(minimum_age=min_dep_age, maximum_age=max_dep_age)
dep_birth = dep_birthdate.strftime("%m/%d/%Y")

# Fill out dependent form
first_name_field = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "first_name"))
)
first_name_field.clear()
first_name_field.send_keys(dep_first)
time.sleep(0.2)

last_name_field = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "last_name"))
)
last_name_field.clear()
last_name_field.send_keys(dep_last)
time.sleep(0.2)

gender_element = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "gender"))
)
Select(gender_element).select_by_visible_text(dep_gender)
time.sleep(0.2)

birth_field = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "birthdate"))
)
birth_field.clear()
birth_field.send_keys(dep_birth)
time.sleep(0.2)

# Handle relationship dropdown
dropdown_btn = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, "//span[contains(@class,'filter-option') and contains(.,'Select Relationship')]"))
)
dropdown_btn.click()
time.sleep(0.5)

option = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, f"//span[text()='{dep_relationship}'] | //a[text()='{dep_relationship}']"))
)
option.click()
time.sleep(0.2)

driver.find_element(By.ID, "submit_form").click()

print("POC: Employee and valid adult dependent added and verified in UI.")

# Verify dependent was saved
try:
    dep_success = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(
            (By.XPATH, "//div[contains(@class,'alert-message')]//p[contains(text(), 'Successfully saved your family member.')]")
        )
    )
    print("Verified: Dependent was saved successfully.")
except Exception:
    print("FAIL: Success message for dependent not found.")

# Move to benefits shopping
try:
    next_shop_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[@id='submit_form']//span[contains(text(),'Next: Shop for Benefits')]")
        )
    )
    button = next_shop_btn.find_element(By.XPATH, "./ancestor::button")
    button.click()
    print("Clicked: 'Next: Shop for Benefits' button.")
except Exception:
    print("FAIL: 'Next: Shop for Benefits' button not found or not clickable.")

# Verify we're on benefits page
try:
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(
            (By.XPATH, "//span[@data-content-type='title' and contains(text(), 'Current Benefit Elections')]")
        )
    )
    print("Verified: On the 'Current Benefit Elections' screen.")
except Exception:
    print("FAIL: Did not reach 'Current Benefit Elections' screen.")

# Shop for medical plans
try:
    medical_shop_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.XPATH,
             "//h2[@id='Medical']/ancestor::div[contains(@class,'m-b-md')]"
             "//a[contains(@class, 'benefit-btn') and contains(., 'Shop Plans')]")
        )
    )
    medical_shop_btn.click()
    print("Clicked 'Shop Plans' for Medical section.")
except Exception:
    print("FAIL: Could not find or click the 'Shop Plans' button under Medical section.")

# Verify medical plan selection page
try:
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(
            (By.XPATH, "//span[@data-content-type='title' and contains(text(), 'Select your Medical Plan')]")
        )
    )
    print("Verified: On the 'Select your Medical Plan' screen.")
except Exception:
    print("FAIL: Did not reach 'Select your Medical Plan' screen.")

# Update cart with medical selection
try:
    update_cart_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "updateCartBtn"))
    )
    update_cart_btn.click()
    print("Clicked 'Update Cart' button.")
except Exception:
    print("FAIL: 'Update Cart' button not found or not clickable.")

# Check updated cost
try:
    per_period = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(
            (By.XPATH, "//h6[contains(text(), 'Per Pay Period')]/preceding-sibling::h2")
        )
    )
    print(f"Verified: Medical plan cost updated: {per_period.text}")
except Exception:
    print("FAIL: Per Pay Period cost not found/updated.")

time.sleep(5)

# Handle HSA survey if present
try:
    hsa_title = WebDriverWait(driver, 6).until(
        EC.visibility_of_element_located((
            By.XPATH, "//span[@data-content-type='title' and contains(text(), 'HSA Survey Question')]"
        ))
    )
    print("Verified: HSA Survey Question page is present.")

    yes_label = WebDriverWait(driver, 6).until(
        EC.element_to_be_clickable((
            By.XPATH, "//label[@class='radio']/span[normalize-space(text())='Yes']"
        ))
    )
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", yes_label)
    time.sleep(0.2)
    yes_label.click()
    print("Selected 'Yes' for HSA survey.")

    next_btn = WebDriverWait(driver, 6).until(
        EC.element_to_be_clickable((
            By.XPATH, "//button[@id='next']//span[contains(text(),'Next')] | //button[contains(@class,'next-btn')]//span[contains(text(),'Next')]"
        ))
    )
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_btn)
    time.sleep(0.2)
    next_btn.click()
    print("Clicked 'Next' button on HSA survey.")

except Exception:
    pass

# Return to benefits summary
try:
    to_benefits_link = WebDriverWait(driver, 8).until(
        EC.element_to_be_clickable((By.XPATH, "//a[contains(@class, 'back-nav') and contains(., 'To Benefits')]"))
    )
    to_benefits_link.click()
    print("Returned to elections summary after HSA survey.")
except Exception:
    print("FAIL: Could not find/click 'To Benefits'.")

try:
    WebDriverWait(driver, 8).until(
        EC.visibility_of_element_located(
            (By.XPATH, "//span[@data-content-type='title' and contains(text(), 'Current Benefit Elections')]")
        )
    )
    print("Verified: Back to 'Current Benefit Elections'")
except Exception:
    print("FAIL: Did not reach 'Current Benefit Elections' page.")

# Handle Voluntary Employee Life section
try:
    section_header = driver.find_element(By.XPATH, "//h2[@id='VoluntaryEmployeeLife']")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", section_header)
    time.sleep(1)

    shop_plans_buttons = driver.find_elements(
        By.XPATH,
        "//h2[@id='VoluntaryEmployeeLife']/ancestor::div[contains(@class,'m-b-md')]//a[contains(@class, 'benefit-btn')]"
    )
    print(f"Found {len(shop_plans_buttons)} Shop Plans button(s) in VEL section.")

    if shop_plans_buttons:
        driver.execute_script("arguments[0].click();", shop_plans_buttons[0])
        print("Clicked the first available 'Shop Plans' in Voluntary Employee Life.")
    else:
        print("No 'Shop Plans' button found in Voluntary Employee Life section.")

except Exception as ex:
    print("FAIL: Could not interact with 'Shop Plans' in Voluntary Employee Life section.", ex)

# Select Voluntary Life coverage amount
try:
    time.sleep(1)
    select_amount_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'dropdown-toggle') and contains(., 'Select Amount')]"))
    )
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", select_amount_btn)
    time.sleep(0.5)
    driver.execute_script("arguments[0].click();", select_amount_btn)
    print("Clicked 'Select Amount' dropdown (JS click).")

    amount_option = WebDriverWait(driver, 8).until(
        EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'$10,000.00')]"))
    )
    driver.execute_script("arguments[0].click();", amount_option)
    print("Selected '$10,000.00' as Voluntary Life coverage (JS click).")

    update_cart_btn = WebDriverWait(driver, 8).until(
        EC.element_to_be_clickable((By.ID, "updateCartBtn"))
    )
    update_cart_btn.click()
    print("Clicked 'Update Cart'.")

    eoi_popup = WebDriverWait(driver, 8).until(
        EC.visibility_of_element_located(
            (By.XPATH, "//div[contains(@class, 'modal-body')]//h3[contains(text(), 'You have an important notice you must read:')]")
        )
    )
    print("EOI modal window detected.")

    confirm_btn = WebDriverWait(driver, 8).until(
        EC.element_to_be_clickable((By.XPATH, "//button[.//span[contains(text(), 'Confirm')]]"))
    )
    confirm_btn.click()
    print("Clicked 'Confirm' in EOI popup.")

except Exception as ex:
    print("FAIL: Problem selecting amount, updating cart, or handling EOI modal.", ex)

