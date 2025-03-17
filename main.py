import csv
import os
import time
import re
import logging
from selenium.webdriver.support.ui import Select
import yaml
import pandas as pd
from fuzzywuzzy import fuzz
import smtplib
from email.mime.text import MIMEText
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc
from selenium.common.exceptions import TimeoutException, NoSuchElementException

lever_base_url = "https://jobs.lever.co"

logging.basicConfig(level=logging.INFO)

def load_config(file_location):
    with open(file_location, 'r') as stream:
        try:
            parameters = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            raise exc

    assert parameters.get("full_name"), "Full name is missing in YAML file."
    assert parameters.get("email"), "Email is missing in YAML file."
    assert parameters.get("phone"), "Phone number is missing in YAML file."
    assert parameters.get("linkedin"), "LinkedIn URL is missing in YAML file."
    assert parameters.get("resume_path"), "Resume path is missing in YAML file."

    credentials = {
        "full_name": parameters["full_name"],
        "email": parameters["email"],
        "phone": parameters["phone"],
        "linkedin": parameters["linkedin"],
        "resume": os.path.abspath(parameters["resume_path"])
    }

    optional_fields = {
        "current_location": parameters.get("current_location", "India"),
        "current_company": parameters.get("current_company", ""),
        "github": parameters.get("github", ""),
        "portfolio": parameters.get("portfolio", ""),
        "work_status": parameters.get("work_status", "")
    }

    credentials.update(optional_fields)
    return credentials
credentials = load_config("config/credentials.yaml")

EMAIL_SENDER = "your_email@gmail.com"
EMAIL_PASSWORD = "your_app_password"  
EMAIL_RECEIVER = "receiver_email@gmail.com"

def send_email(job_link):
    """Send email notification after successful submission."""
    subject = "Job Application Submitted Successfully"
    body = f"Your application for {job_link} has been submitted successfully on {time.ctime()}."
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        print(f"Email sent: Application for {job_link} submitted successfully")
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
def send_email(job_link):
    """Send email notification after successful submission."""
    subject = "Job Application Submitted Successfully"
    body = f"Your application for {job_link} has been submitted successfully on {time.ctime()}."
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        print(f"Email sent: Application for {job_link} submitted successfully")
    except Exception as e:
        print(f"Failed to send email: {str(e)}")

answers = {}
try:
    with open("config/answers.csv", mode="r",encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            question = row["Question"].strip().lower()
            answers[question] = row["Answer"].strip()
except FileNotFoundError:
    logging.error("Error: 'answers.csv' file not found.")
    exit()

chrome_options = Options()
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
driver = uc.Chrome(options=chrome_options)

job_links_file = "jobs/job_links.csv"
job_links = []

if os.path.exists(job_links_file):
    try:
        job_links_df = pd.read_csv(job_links_file)
        if not all(col in job_links_df.columns for col in ["platform", "company", "jobid"]):
            logging.error("Missing required columns in CSV file.")
            exit()

        for row in job_links_df.itertuples(index=False):
            if str(row.platform).lower() == "lever":
                job_links.append(f"{lever_base_url}/{row.company}/{row.jobid}")
    except pd.errors.ParserError as e:
        logging.error(f"Error parsing CSV file: {e}")
        exit()
else:
    logging.error(f"CSV file '{job_links_file}' does not exist.")
    exit()

if not job_links:
    logging.error("No Lever job links found in the CSV file.")
    exit()

FIELD_SELECTORS = {
    "full_name": ["input[name='name']", "input[id='name']"],
    "email": ["input[type='email']", "input[name*='email']"],
    "phone": ["input[type='tel']", "input[name*='phone']"],
    "linkedin": ["input[name*='linkedin']", "input[id*='linkedin']"],
    "resume": ["input[type='file']", "input[name*='resume']"],
    "current_location": ["input[name='location']"],
    "current_company": ["input[name='org']"],
    "github": ["input[name*='github']"],
    "portfolio": ["input[name*='portfolio']"]
}

def normalize_text(text):
    """Normalize text by removing special characters and extra spaces."""
    return re.sub(r"[^a-zA-Z0-9\s]", "", text).strip().lower()

def find_input_field(driver, selectors):
    """Finds an input field using multiple CSS selectors with explicit wait."""
    for selector in selectors:
        try:
            return WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
        except TimeoutException:
            continue
    return None

def open_job_and_click_apply(driver, job_link):
    """Opens job link, checks for 404 errors, clicks 'Apply' button if found, else skips."""
    try:
        print(f"\nOpening job: {job_link}")
        driver.get(job_link)
        time.sleep(2)

        if "404" in driver.page_source or "Not Found" in driver.page_source:
            print("⚠ Page not found (404). Skipping this job link.")
            return False

        apply_selectors = [
            "a.postings-btn.template-btn-submit.cerulean",
            "a[href*='/apply']",
            "button[class*='apply']",
            "a[class*='apply']",
        ]

        for selector in apply_selectors:
            try:
                button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                driver.execute_script("arguments[0].scrollIntoView();", button)
                driver.execute_script("arguments[0].click();", button)
                print("Clicked 'Apply' button")
                time.sleep(5)  # Increased wait time
                return True
            except TimeoutException:
                continue

        print("⚠ No 'Apply' button found, skipping.")
        return False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def handle_radio_buttons(application_field, answer):
    """Handle radio buttons within an application field."""
    radio_buttons = application_field.find_elements(By.CSS_SELECTOR, "input[type='radio']")
    if radio_buttons:
        normalized_answer = normalize_text(answer)
        options = [normalize_text(radio.get_attribute("value")) for radio in radio_buttons]
        print(f"Options found: {options}")
        for radio in radio_buttons:
            value = normalize_text(radio.get_attribute("value"))
            if value == normalized_answer or normalized_answer in value or value in normalized_answer:
                if not radio.is_selected():
                    driver.execute_script("arguments[0].click();", radio)
                print(f"Selected radio button with value '{value}'")
                return True
        print(f"No matching radio button found for answer '{answer}'")
        return False
    print("No radio buttons found")
    return False

def fill_form_and_submit(driver, answers):
    """Fills required fields, answers questions, uploads resume, and submits."""
    try:
        print("\nFilling the form...")

        for field, selectors in FIELD_SELECTORS.items():
            value = credentials.get(field)
            if value:
                input_field = find_input_field(driver, selectors)
                if input_field:
                    driver.execute_script("arguments[0].scrollIntoView();", input_field)
                    input_field.clear()
                    if field == "resume":
                        input_field.send_keys(credentials["resume"])
                        print(f"Uploaded Resume: {credentials['resume']}")
                    else:
                        input_field.send_keys(value)
                        print(f"Filled {field.replace('_', ' ').title()}: {value}")

      
        question_elements = driver.find_elements(By.CSS_SELECTOR, "li.application-question, li.application-question.custom-question")
        
        for question_element in question_elements:
            question_text = "Unknown question"
            try:
                try:
                    label_div = question_element.find_element(By.CSS_SELECTOR, "div.application-label")
                    question_text = label_div.find_element(By.CSS_SELECTOR, "div.text").text
                except NoSuchElementException:
                    print(f"Skipping question element due to missing label or text")
                    continue

                normalized_question = normalize_text(question_text)
                print(f"Found question: '{question_text}'")

               
                best_match = None
                for q in answers:
                    if fuzz.ratio(normalized_question, normalize_text(q)) > 80:  
                        best_match = q
                        break

                if best_match:
                    answer = answers[best_match]
                    print(f"Matched answer: '{answer}'")

                   
                    label_classes = label_div.get_attribute("class")
                    application_field = question_element.find_element(By.CSS_SELECTOR, "div.application-field")

                  
                    if application_field.find_elements(By.TAG_NAME, "textarea"):
                        textarea = application_field.find_element(By.TAG_NAME, "textarea")
                        textarea.clear()
                        textarea.send_keys(answer)
                        print(f"Filled text area with: '{answer}'")

                    elif application_field.find_elements(By.TAG_NAME, "select"):
                        select_element = application_field.find_element(By.TAG_NAME, "select")
                        select = Select(select_element)
                        options = [option.text for option in select.options]
                        print(f"Dropdown options: {options}")
                        normalized_answer = answer.strip()
                        matched_option = next((opt for opt in options if opt.lower() == normalized_answer.lower()), None)
                        if matched_option:
                            select.select_by_visible_text(matched_option)
                            print(f"Selected dropdown option: '{matched_option}'")
                        else:
                            print(f"Option '{answer}' not found in dropdown")

                    elif application_field.find_elements(By.CSS_SELECTOR, "input[type='text'], input[type='email']"):
                        text_input = application_field.find_element(By.CSS_SELECTOR, "input[type='text'], input[type='email']")
                        text_input.clear()
                        text_input.send_keys(answer)
                        print(f"Filled text input with: '{answer}'")

                    elif application_field.find_elements(By.CSS_SELECTOR, "input[type='radio']"):
                        handle_radio_buttons(application_field, answer)

                    elif application_field.find_elements(By.CSS_SELECTOR, "input[type='checkbox']"):
                        checkboxes = application_field.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
                        normalized_answer = normalize_text(answer)
                        for checkbox in checkboxes:
                            value = normalize_text(checkbox.get_attribute("value"))
                            if value == normalized_answer:
                                driver.execute_script("arguments[0].click();", checkbox)
                                print(f"Checked checkbox: '{answer}'")
                                break

                    else:
                        print("Unknown question type")

                else:
                    print(f"No matching answer found for '{question_text}'")

            except Exception as e:
                print(f"Error processing question '{question_text}': {str(e)}")


        submit_selectors = ["button#btn-submit", "button.postings-btn.template-btn-submit", "input[type='submit']"]
        for selector in submit_selectors:
            try:
                submit_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                driver.execute_script("arguments[0].scrollIntoView();", submit_button)
                submit_button.click()
                print("Form submitted successfully")
                break
            except TimeoutException:
                continue

    except Exception as e:
        print(f"Error filling form: {str(e)}")
def process_job_application(driver, job_link, answers):
    """Process a single job application with automation up to radio buttons."""
    if open_job_and_click_apply(driver, job_link):
        fill_form_and_submit(driver, answers)
        send_email(job_link)  
        return True
    return False


for job_link in job_links:
    try:
        if open_job_and_click_apply(driver, job_link):
            fill_form_and_submit(driver, answers)
            time.sleep(2)
    except Exception as e:
        print(f"Failed to process {job_link}: {str(e)}")
        
        if "invalid session id" in str(e).lower():
            driver.quit()
            driver = uc.Chrome(options=chrome_options)
            print("Browser restarted due to session crash")

driver.quit()
print("\nJob application process completed!")

