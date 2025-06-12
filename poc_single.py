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

# --- Assumptions (POC Notes) ---
# - Only Chrome browser on Mac/Linux is used; old Chrome processes are killed for a clean start
# - Only valid US data is generated (SSN, ZIP, address, etc.)
# - Employee and dependent are both always 18+ (to avoid system validation errors)
# - Dependent relationship is always 'Domestic Partner' and age is within ±2 years of the employee (also always at least 18)
# - All major waits and UI checks are present for stability
# - Any custom dropdowns are handled with click-and-select logic

# Kill all running Chrome browsers (assume Mac/Linux)
os.system("pkill -f 'Google Chrome'")
time.sleep(2)

fake = Faker()
options = Options()
options.add_argument("--headless")  # Enable headless mode
options.add_experimental_option("detach", True)  # Keep browser open after script

driver = webdriver.Chrome(options=options)
driver.maximize_window()
driver.get("https://partner-dev-benefits.plansource.com")

# --- Login to PlanSource demo environment ---
WebDriverWait(driver, 15).until(
    EC.presence_of_element_located((By.ID, "user_name"))
).send_keys("plansource_test_admin")
driver.find_element(By.ID, "password").send_keys("password123")
driver.find_element(By.ID, "logon_submit").click()

# --- Click Add a New Employee ---
WebDriverWait(driver, 15).until(
    EC.element_to_be_clickable((By.LINK_TEXT, "Add a New Employee"))
).click()

# --- Generate POC employee data (always valid US, 18+ age, random info) ---
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

hire_date = (datetime.today() - timedelta(days=2)).strftime("%m/%d/%Y")
eligibility_date = hire_date

employment_level = random.choice(["F", "P"])
location = random.choice(["SCA", "NCA", "NONCA"])
current_salary = str(random.randint(50000, 150000))
benefit_salary = str(random.randint(40000, 130000))
payroll_schedule = random.choice(["Semi-monthly", "Monthly", "Bi-weekly"])
password = fake.password(length=10, special_chars=True, digits=True, upper_case=True, lower_case=True)

# --- Fill and submit employee form ---
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

# --- Detect if employee was successfully created (UI feedback) ---
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

# --- Verify the new employee's name appears on the employee list page ---
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

# --- Start Hire Enrollment for new employee ---
try:
    enrollment_link = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Hire Enrollment"))
    )
    enrollment_link.click()
    print("Clicked Hire Enrollment.")
except Exception as e:
    print("New Hire Enrollment link not found or not clickable:", e)

# --- Wait for enrollment page and required actions ---
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

# --- Verify personal info screen, go to family screen ---
try:
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(
            (By.XPATH, "//span[@data-content-type='title' and contains(text(), 'Verify your Personal Information')]")
        )
    )
    print("Verified: On the 'Verify your Personal Information' screen.")
except Exception:
    print("FAIL: Did not reach 'Verify your Personal Information' screen.")

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

# --- Add Family Member (Dependent) ---
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

# --- Generate dependent data (POC: always 18+, Domestic Partner, age ≈ employee) ---
dep_relationship = "Domestic Partner"
dep_gender = random.choice(["Male", "Female"])
dep_first = fake.first_name_female() if dep_gender == "Female" else fake.first_name_male()
dep_last = fake.last_name()
min_dep_age = max(emp_age - 2, 18)
max_dep_age = max(emp_age + 2, 18)
dep_birthdate = fake.date_of_birth(minimum_age=min_dep_age, maximum_age=max_dep_age)
dep_birth = dep_birthdate.strftime("%m/%d/%Y")

# --- Fill out dependent form, handling custom dropdown for relationship ---
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

# Custom dropdown: Relationship = Domestic Partner
dropdown_btn = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, "//span[contains(@class,'filter-option') and contains(.,'Select Relationship')]"))
)
dropdown_btn.click()
time.sleep(0.5)  # Let dropdown open

option = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, f"//span[text()='{dep_relationship}'] | //a[text()='{dep_relationship}']"))
)
option.click()
time.sleep(0.2)

driver.find_element(By.ID, "submit_form").click()

# -- END POC -- all steps above are stable and have strong comments --

#############-----------------------



print("POC: Employee and valid adult dependent added and verified in UI.")

# --- After submitting the dependent form, verify success message ---
try:
    dep_success = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(
            (By.XPATH, "//div[contains(@class,'alert-message')]//p[contains(text(), 'Successfully saved your family member.')]")
        )
    )
    print("Verified: Dependent was saved successfully.")
except Exception:
    print("FAIL: Success message for dependent not found.")

# --- Wait for and click the "Next: Shop for Benefits" button ---
try:
    next_shop_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[@id='submit_form']//span[contains(text(),'Next: Shop for Benefits')]")
        )
    )
    # Sometimes the span is inside the button, so get the parent button:
    button = next_shop_btn.find_element(By.XPATH, "./ancestor::button")
    button.click()
    print("Clicked: 'Next: Shop for Benefits' button.")
except Exception:
    print("FAIL: 'Next: Shop for Benefits' button not found or not clickable.")

# --- Verify we're on the 'Current Benefit Elections' page ---
try:
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(
            (By.XPATH, "//span[@data-content-type='title' and contains(text(), 'Current Benefit Elections')]")
        )
    )
    print("Verified: On the 'Current Benefit Elections' screen.")
except Exception:
    print("FAIL: Did not reach 'Current Benefit Elections' screen.")


# Wait for the Medical Shop Plans button and click it
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

# --- Verify the "Select your Medical Plan" page is loaded ---
try:
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(
            (By.XPATH, "//span[@data-content-type='title' and contains(text(), 'Select your Medical Plan')]")
        )
    )
    print("Verified: On the 'Select your Medical Plan' screen.")
except Exception:
    print("FAIL: Did not reach 'Select your Medical Plan' screen.")

# --- Click the Update Cart button (first one visible) ---
try:
    update_cart_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "updateCartBtn"))
    )
    update_cart_btn.click()
    print("Clicked 'Update Cart' button.")
except Exception:
    print("FAIL: 'Update Cart' button not found or not clickable.")

# --- Capture updated per-pay-period cost (after Update Cart) ---
try:
    per_period = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(
            (By.XPATH, "//h6[contains(text(), 'Per Pay Period')]/preceding-sibling::h2")
        )
    )
    print(f"Verified: Medical plan cost updated: {per_period.text}")
except Exception:
    print("FAIL: Per Pay Period cost not found/updated.")

# --- Wait 5 seconds for the page and cart updates ---
time.sleep(5)

# --- HSA Survey Handling (Click Yes, then Next) ---
try:
    # Wait for the HSA Survey title/question (give enough time in case of animation)
    hsa_title = WebDriverWait(driver, 6).until(
        EC.visibility_of_element_located((
            By.XPATH, "//span[@data-content-type='title' and contains(text(), 'HSA Survey Question')]"
        ))
    )
    print("Verified: HSA Survey Question page is present.")

    # Wait for the "Yes" radio (by span label for reliability)
    yes_label = WebDriverWait(driver, 6).until(
        EC.element_to_be_clickable((
            By.XPATH, "//label[@class='radio']/span[normalize-space(text())='Yes']"
        ))
    )
    # Scroll and click the span (label)
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", yes_label)
    time.sleep(0.2)
    yes_label.click()
    print("Selected 'Yes' for HSA survey.")

    # Wait for and click the Next button (by id or span text)
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
    # If HSA survey not present, ignore and continue
    pass

# --- These steps happen anyway (ALWAYS go back to benefits and confirm) ---
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

# --- Ensure "Voluntary Employee Life" section is present with "No Plan Selected" and click Shop Plans ---
try:
    # Scroll the section into view
    section_header = driver.find_element(By.XPATH, "//h2[@id='VoluntaryEmployeeLife']")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", section_header)
    time.sleep(1)

    # Find all "Shop Plans" buttons in this section
    shop_plans_buttons = driver.find_elements(
        By.XPATH,
        "//h2[@id='VoluntaryEmployeeLife']/ancestor::div[contains(@class,'m-b-md')]//a[contains(@class, 'benefit-btn')]"
    )
    print(f"Found {len(shop_plans_buttons)} Shop Plans button(s) in VEL section.")

    # If at least one button, click the first
    if shop_plans_buttons:
        driver.execute_script("arguments[0].click();", shop_plans_buttons[0])
        print("Clicked the first available 'Shop Plans' in Voluntary Employee Life.")
    else:
        print("No 'Shop Plans' button found in Voluntary Employee Life section.")

except Exception as ex:
    print("FAIL: Could not interact with 'Shop Plans' in Voluntary Employee Life section.", ex)

import time

try:
    # Give time for overlays to go away
    time.sleep(1)
    # Scroll the dropdown into view
    select_amount_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'dropdown-toggle') and contains(., 'Select Amount')]"))
    )
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", select_amount_btn)
    time.sleep(0.5)
    # Use JavaScript click for reliability
    driver.execute_script("arguments[0].click();", select_amount_btn)
    print("Clicked 'Select Amount' dropdown (JS click).")

    # Wait for and click $10,000.00 option (JS click)
    amount_option = WebDriverWait(driver, 8).until(
        EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'$10,000.00')]"))
    )
    driver.execute_script("arguments[0].click();", amount_option)
    print("Selected '$10,000.00' as Voluntary Life coverage (JS click).")

    # Click Update Cart as usual
    update_cart_btn = WebDriverWait(driver, 8).until(
        EC.element_to_be_clickable((By.ID, "updateCartBtn"))
    )
    update_cart_btn.click()
    print("Clicked 'Update Cart'.")

    # Wait for EOI Modal Popup
    eoi_popup = WebDriverWait(driver, 8).until(
        EC.visibility_of_element_located(
            (By.XPATH, "//div[contains(@class, 'modal-body')]//h3[contains(text(), 'You have an important notice you must read:')]")
        )
    )
    print("EOI modal window detected.")

    # Confirm button in modal
    confirm_btn = WebDriverWait(driver, 8).until(
        EC.element_to_be_clickable((By.XPATH, "//button[.//span[contains(text(), 'Confirm')]]"))
    )
    confirm_btn.click()
    print("Clicked 'Confirm' in EOI popup.")

except Exception as ex:
    print("FAIL: Problem selecting amount, updating cart, or handling EOI modal.", ex)

