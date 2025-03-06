import csv
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd
import os
import yaml
import random
from datetime import datetime
from fake_useragent import UserAgent
from anticaptchaofficial.recaptchav2proxyless import recaptchaV2Proxyless

# Load configuration
with open("config/credentials.yaml", "r") as file:
    config = yaml.safe_load(file)

credentials = config["credentials"]
resume_path = os.path.abspath(config["resume_path"])

# Load answers
answers = {}
try:
    with open("config/answers.csv", mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            question = row["Question"].strip().lower()
            answers[question] = row["Answer"].strip()
except FileNotFoundError:
    print("Error: 'answers.csv' file not found.")
    exit()

# Setup browser
ua = UserAgent()
chrome_options = Options()
chrome_options.add_argument(f"user-agent={ua.random}")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
driver = uc.Chrome(options=chrome_options)

# Application tracking
applications_file = "applications.csv"
if not os.path.exists(applications_file):
    with open(applications_file, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Company", "Job Title", "Application Link", "Date Applied", "Status", "Questions Answered"])

def fill_structured_fields(driver):
    """Fill standard form fields like name, email, etc."""
    structured_fields = {
        "first_name": ("//label[contains(., 'First Name')]/following-sibling::div//input", credentials.get("first_name")),
        "last_name": ("//label[contains(., 'Last Name')]/following-sibling::div//input", credentials.get("last_name")),
        "email": ("//label[contains(., 'Email')]/following-sibling::div//input", credentials.get("email")),
        "phone": ("//label[contains(., 'Phone')]/following-sibling::div//input", credentials.get("phone")),
        "address": ("//label[contains(., 'Address')]/following-sibling::div//input", credentials.get("address")),
        "city": ("//label[contains(., 'City')]/following-sibling::div//input", credentials.get("city")),
        "state": ("//label[contains(., 'State')]/following-sibling::div//select", credentials.get("state")),
        "zip": ("//label[contains(., 'Zip')]/following-sibling::div//input", credentials.get("zip")),
    }

    for field, (xpath, value) in structured_fields.items():
        if value:
            try:
                element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, xpath)))
                element.clear()
                element.send_keys(value)
                print(f"Filled {field.replace('_', ' ').title()}")
                time.sleep(random.uniform(0.5, 1.5))
            except Exception as e:
                print(f"Could not fill {field.replace('_', ' ').title()}: {e}")

def handle_field_types(container, answer):
    """Handle different types of form fields"""
    # Try textarea
    try:
        textarea = container.find_element(By.TAG_NAME, "textarea")
        textarea.clear()
        for char in answer:
            textarea.send_keys(char)
            time.sleep(random.uniform(0.02, 0.1))
        print(f"Filled textarea with: {answer[:50]}...")
        return True
    except:
        pass

    # Try text input
    try:
        input_field = container.find_element(By.XPATH, ".//input[@type='text']")
        input_field.clear()
        input_field.send_keys(answer)
        print(f"Filled text input: {answer[:50]}...")
        return True
    except:
        pass

    # Handle radio buttons/checkboxes
    try:
        options = container.find_elements(By.XPATH, ".//input[@type='radio'] | .//input[@type='checkbox']")
        if options:
            for option in options:
                label = container.find_element(By.XPATH, f"//label[@for='{option.get_attribute('id')}']")
                if label.text.strip().lower() == answer.lower() or option.get_attribute("value").lower() == answer.lower():
                    if not option.is_selected():
                        option.click()
                        print(f"Selected option: {answer}")
                        return True
            print(f"No matching option found for: {answer}")
            return False
    except:
        pass

    # Handle dropdowns
    try:
        select = container.find_element(By.TAG_NAME, "select")
        dropdown = Select(select)
        try:
            dropdown.select_by_visible_text(answer)
            print(f"Selected dropdown: {answer}")
            return True
        except:
            try:
                dropdown.select_by_value(answer)
                print(f"Selected dropdown by value: {answer}")
                return True
            except:
                print(f"No dropdown option matched: {answer}")
                return False
    except:
        pass

    # Handle acknowledgements
    if "acknowledge" in answer.lower():
        try:
            checkbox = container.find_element(By.XPATH, ".//input[@type='checkbox']")
            if not checkbox.is_selected():
                checkbox.click()
                print("Checked acknowledgement box")
                return True
        except:
            pass

    print(f"Could not find suitable field for: {answer}")
    return False

def fill_dynamic_fields(driver):
    """Answer custom questions from CSV"""
    for question_text, answer in answers.items():
        try:
            print(f"\nAttempting: {question_text[:50]}...")
            
            # Normalize question text
            clean_question = question_text.lower().replace('?', '').replace(':', '').strip()
            
            # Find question container
            container = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, 
                    f"//div[contains(@class, 'application-question')][.//*[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{clean_question}')]]"
                ))
            )
            
            
            # Scroll to element
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", container)
            time.sleep(0.5)
            
            # Handle the field
            if not handle_field_types(container, answer):
                print(f"Failed to answer: {question_text[:50]}...")
            
        except Exception as e:
            print(f"Question not found: {question_text[:50]}... - {str(e)}")

# Process job links
job_links_df = pd.read_csv("jobs/job_links.csv")
job_links = job_links_df["job_link"].dropna().tolist()

for job_link in job_links:
    retry_count = 0
    max_retries = 2
    success = False

    while retry_count < max_retries and not success:
        try:
            print(f"\nProcessing: {job_link}")
            driver.get(job_link)
            time.sleep(random.uniform(3, 6))

            # Handle apply button
            try:
                WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[contains(., 'Apply')]"))
                ).click()
                time.sleep(random.uniform(2, 4))
            except:
                pass

            # Get job details
            try:
                company_name = driver.find_element(By.CSS_SELECTOR, "a.main-header-logo img").get_attribute("alt")
                company_name = company_name.replace(" logo", "")
            except:
                company_name = "Unknown Company"

            try:
                job_title = driver.find_element(By.CSS_SELECTOR, "div.posting-header h2").text.strip()
            except:
                job_title = "Unknown Position"

            # Fill form
            fill_structured_fields(driver)
            
            # Upload resume
            try:
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.NAME, "resume"))
                ).send_keys(resume_path)
                print("Resume uploaded")
                time.sleep(1)
            except Exception as e:
                print(f"Resume upload failed: {e}")

            # Answer custom questions
            fill_dynamic_fields(driver)

            # Handle CAPTCHA
            try:
                iframe = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//iframe[contains(@src, 'recaptcha')]"))
                )
                driver.switch_to.frame(iframe)
                site_key = driver.find_element(By.CLASS_NAME, "g-recaptcha").get_attribute("data-sitekey")
                driver.switch_to.default_content()

                solver = recaptchaV2Proxyless()
                solver.set_key("YOUR_2CAPTCHA_API_KEY")  # Replace with your key
                solver.set_website_url(job_link)
                solver.set_website_key(site_key)

                captcha_solution = solver.solve_and_return_solution()
                if captcha_solution:
                    driver.execute_script(f'document.getElementById("g-recaptcha-response").innerHTML="{captcha_solution}"')
                    time.sleep(2)
            except:
                pass

            # Submit application
            submit_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
            )
            submit_button.click()
            time.sleep(random.uniform(5, 8))

            # Log success
            with open(applications_file, "a", newline="") as file:
                writer = csv.writer(file)
                writer.writerow([
                    company_name,
                    job_title,
                    job_link,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Success",
                    str(answers)[:100] + "..."
                ])
            print("Application submitted successfully!")
            success = True

        except Exception as e:
            print(f"Error: {str(e)}")
            retry_count += 1
            if retry_count < max_retries:
                print(f"Retrying ({retry_count}/{max_retries})...")
                time.sleep(random.uniform(10, 20))
            else:
                print("Max retries reached")
                with open(applications_file, "a", newline="") as file:
                    writer = csv.writer(file)
                    writer.writerow([
                        company_name,
                        job_title,
                        job_link,
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "Failed",
                        str(answers)[:100] + "..."
                    ])

driver.quit()
print("\nJob application process completed!")