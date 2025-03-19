
import csv
import os
import time
import re
import logging
from selenium.webdriver.support.ui import Select
import yaml
import pandas as pd
from fuzzywuzzy import fuzz
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc
from selenium.common.exceptions import TimeoutException, NoSuchElementException

lever_base_url = "https://jobs.lever.co"

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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

    resume_path = os.path.abspath(parameters["resume_path"])
    if not os.path.isfile(resume_path):
        logging.error(f"Resume file not found at: {resume_path}")
        raise FileNotFoundError(f"Resume file not found at: {resume_path}")
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

answers = {}
try:
    with open("config/answers.csv", mode="r", encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            question = row["Question"].strip().lower()
            answers[question] = row["Answer"]
except FileNotFoundError:
    logging.error("Error: 'answers.csv' file not found.")
    exit()

if not answers:
    logging.error("No answers loaded from 'answers.csv'. Please check the file.")
    exit()

chrome_options = Options()
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
driver = uc.Chrome(options=chrome_options)

job_links_file = "jobs/job_links.csv"
job_links = []

if os.path.exists(job_links_file):
    try:
        job_links_df = pd.read_csv(job_links_file)
        required_columns = ["platform", "company", "platform_job_id", "platform_link"]
        if not all(col in job_links_df.columns for col in required_columns):
            logging.error("Missing required columns in CSV file.")
            exit()

        # Filter for Lever jobs and construct URLs
        for row in job_links_df.itertuples(index=False):
            if str(row.platform).lower() == "lever":
                job_links.append(f"{lever_base_url}/{row.company}/{row.platform_job_id}")
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
    "linkedin": ["input[name='urls[LinkedIn]']", "input[id*='linkedin']"],
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
        logging.info(f"Opening job: {job_link}")
        driver.get(job_link)
        time.sleep(2)

        if "404" in driver.page_source or "Not Found" in driver.page_source:
            logging.warning("Page not found (404). Skipping this job link.")
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
                logging.info("Clicked 'Apply' button")
                time.sleep(5)
                return True
            except TimeoutException:
                continue

        logging.warning("No 'Apply' button found, skipping.")
        return False
    except Exception as e:
        logging.error(f"Error opening job link: {str(e)}")
        return False

def handle_radio_buttons(application_field, answer):
    """Handle radio buttons with fuzzy matching and improved logging."""
    radio_buttons = application_field.find_elements(By.CSS_SELECTOR, "input[type='radio']")
    if radio_buttons:
        normalized_answer = normalize_text(answer)
        options = [normalize_text(radio.get_attribute("value")) for radio in radio_buttons]
        logging.info(f"Radio button options: {options}")

        # Exact match first
        for radio in radio_buttons:
            value = normalize_text(radio.get_attribute("value"))
            if value == normalized_answer:
                if not radio.is_selected():
                    driver.execute_script("arguments[0].click();", radio)
                logging.info(f"Selected radio button (exact match): '{value}'")
                return True

        # Fuzzy match as fallback
        best_match = None
        best_score = 0
        for radio in radio_buttons:
            value = normalize_text(radio.get_attribute("value"))
            score = fuzz.ratio(value, normalized_answer)
            logging.debug(f"Comparing '{value}' with '{normalized_answer}' - Score: {score}")
            if score > 80 and score > best_score:
                best_match = radio
                best_score = score

        if best_match:
            if not best_match.is_selected():
                driver.execute_script("arguments[0].click();", best_match)
            logging.info(f"Selected radio button (fuzzy match): '{best_match.get_attribute('value')}' (Score: {best_score})")
            return True

        logging.warning(f"No matching radio button found for answer '{answer}' among options {options}")
        return False
    logging.info("No radio buttons found")
    return False


def handle_checkboxes(application_field, answer):
    """Handle checkboxes with improved matching for acknowledgements."""
    checkboxes = application_field.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
    if checkboxes:
        normalized_answer = normalize_text(answer)
        options = [normalize_text(cb.get_attribute("value")) for cb in checkboxes]
        logging.info(f"Checkbox options: {options}")

        # Special case for "I acknowledge"
        if "acknowledge" in normalized_answer:
            for checkbox in checkboxes:
                value = normalize_text(checkbox.get_attribute("value"))
                if "acknowledge" in value:
                    if not checkbox.is_selected():
                        driver.execute_script("arguments[0].click();", checkbox)
                    logging.info(f"Checked checkbox (acknowledgement match): '{value}'")
                    return True

        # Exact match
        for checkbox in checkboxes:
            value = normalize_text(checkbox.get_attribute("value"))
            if value == normalized_answer:
                if not checkbox.is_selected():
                    driver.execute_script("arguments[0].click();", checkbox)
                logging.info(f"Checked checkbox (exact match): '{value}'")
                return True

        # Fuzzy match
        best_match = None
        best_score = 0
        for checkbox in checkboxes:
            value = normalize_text(checkbox.get_attribute("value"))
            score = fuzz.ratio(value, normalized_answer)
            if score > 80 and score > best_score:
                best_match = checkbox
                best_score = score
        if best_match:
            if not best_match.is_selected():
                driver.execute_script("arguments[0].click();", best_match)
            logging.info(f"Checked checkbox (fuzzy match): '{best_match.get_attribute('value')}' (Score: {best_score})")
            return True

        logging.warning(f"No matching checkbox found for answer '{answer}' among options {options}")
        return False
    logging.info("No checkboxes found")
    return False



def fill_form_and_submit(driver, answers):
    """Fills required fields, answers questions, uploads resume, waits 1 minute, and submits."""
    try:
        logging.info("Filling the form...")

        filled_fields = set()
        for field, selectors in FIELD_SELECTORS.items():
            value = credentials.get(field)
            if value and field not in filled_fields:
                if input_field := find_input_field(driver, selectors):
                    driver.execute_script("arguments[0].scrollIntoView();", input_field)
                    input_field.clear()
                    if field == "resume":
                        resume_path = credentials["resume"]
                        logging.info(f"Attempting to upload resume from: {resume_path}")
                        input_field.send_keys(resume_path)
                        logging.info(f"Uploaded Resume: {resume_path}")
                    else:
                        input_field.send_keys(value)
                        logging.info(f"Filled {field.replace('_', ' ').title()}: {value}")
                    filled_fields.add(field)

        question_elements = driver.find_elements(By.CSS_SELECTOR, "li.application-question, li.application-question.custom-question")
        logging.info(f"Found {len(question_elements)} question elements")
        for question_element in question_elements:
            question_text = "Unknown question"
            try:
                label_div = question_element.find_element(By.CSS_SELECTOR, "div.application-label")
                question_text = label_div.text.strip()
            except NoSuchElementException:
                question_text = question_element.text.strip() if question_element.text.strip() else "Unknown question"
                logging.warning(f"No label div found, using element text: '{question_text}'")

            normalized_question = normalize_text(question_text)
            logging.info(f"Found question: '{question_text}'")

            best_match = None
            for q in answers:
                q_normalized = normalize_text(q)
                score = fuzz.ratio(normalized_question, q_normalized)
                # Substring match for long questions like Acknowledgements
                if ("acknowledge" in q_normalized and "acknowledge" in normalized_question) or score > 70:
                    best_match = q
                    logging.debug(f"Matched '{q}' with score: {score}")
                    break

            if best_match:
                answer = answers[best_match]
                logging.info(f"Matched answer: '{answer}'")

                application_field = question_element.find_element(By.CSS_SELECTOR, "div.application-field")
                is_required = "required" in application_field.get_attribute("class") or "✱" in question_text

                if application_field.find_elements(By.TAG_NAME, "textarea"):
                    textarea = application_field.find_element(By.TAG_NAME, "textarea")
                    textarea.clear()
                    textarea.send_keys(answer)
                    logging.info(f"Filled text area with: '{answer}'")

                elif application_field.find_elements(By.TAG_NAME, "select"):
                    select_elements = application_field.find_elements(By.TAG_NAME, "select")
                    logging.info(f"Found {len(select_elements)} dropdown(s) in this question")
                    answer_parts = answer.split() if " " in answer else [answer]
                    for idx, select_element in enumerate(select_elements):
                        select = Select(select_element)
                        options = [option.text for option in select.options]
                        logging.info(f"Dropdown {idx + 1} options: {options}")
                        part_answer = answer_parts[min(idx, len(answer_parts) - 1)].strip()
                        normalized_part_answer = part_answer.lower()
                        matched_option = next((opt for opt in options if opt.lower() == normalized_part_answer), None)
                        if matched_option:
                            select.select_by_visible_text(matched_option)
                            logging.info(f"Selected dropdown {idx + 1} option: '{matched_option}'")
                        else:
                            best_match_option = None
                            best_score = 0
                            for opt in options:
                                score = fuzz.ratio(opt.lower(), normalized_part_answer)
                                if score > 50 and score > best_score:
                                    best_match_option = opt
                                    best_score = score
                            if best_match_option:
                                select.select_by_visible_text(best_match_option)
                                logging.info(f"Selected dropdown {idx + 1} option (fuzzy match): '{best_match_option}' (Score: {best_score})")
                            else:
                                logging.warning(f"Option '{part_answer}' not found in dropdown {idx + 1}")

                elif application_field.find_elements(By.CSS_SELECTOR, "input[type='text'], input[type='email']"):
                    field_name = application_field.find_element(By.CSS_SELECTOR, "input").get_attribute("name")
                    if field_name not in filled_fields or is_required:
                        text_input = application_field.find_element(By.CSS_SELECTOR, "input[type='text'], input[type='email']")
                        text_input.clear()
                        text_input.send_keys(answer)
                        logging.info(f"Filled text input with: '{answer}'")
                        filled_fields.add(field_name)

                elif application_field.find_elements(By.CSS_SELECTOR, "input[type='radio']"):
                    handle_radio_buttons(application_field, answer)

                elif application_field.find_elements(By.CSS_SELECTOR, "input[type='checkbox']"):
                    handle_checkboxes(application_field, answer)

                else:
                    logging.warning("Unknown question type")

            else:
                logging.warning(f"No matching answer found for '{question_text}'")

        logging.info("Form filled. Waiting 1 minute for manual review before submission...")
        time.sleep(60)

        submit_selectors = ["button#btn-submit", "button.postings-btn.template-btn-submit", "input[type='submit']"]
        for selector in submit_selectors:
            try:
                submit_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                driver.execute_script("arguments[0].scrollIntoView();", submit_button)
                submit_button.click()
                logging.info("Form submitted successfully")
                break
            except TimeoutException:
                continue
        else:
            logging.warning("No submit button found.")

    except Exception as e:
        logging.error(f"Error filling form: {str(e)}")
def process_job_application(driver, job_link, answers, max_retries=2):
    """Process a single job application with retries."""
    for attempt in range(max_retries + 1):
        try:
            if open_job_and_click_apply(driver, job_link):
                fill_form_and_submit(driver, answers)
                return True
        except Exception as e:
            logging.error(f"Attempt {attempt + 1} failed for {job_link}: {str(e)}")
            if attempt < max_retries:
                time.sleep(5)
                driver.quit()
                driver = uc.Chrome(options=chrome_options)
                logging.info("Browser restarted for retry")
            else:
                logging.error(f"All retries exhausted for {job_link}")
    return False

for job_link in job_links:
    try:
        process_job_application(driver, job_link, answers)
        time.sleep(2)
    except Exception as e:
        logging.error(f"Failed to process {job_link}: {str(e)}")
        if "invalid session id" in str(e).lower():
            logging.warning("Browser session crashed. Restarting...")
            driver.quit()
            driver = uc.Chrome(options=chrome_options)
            logging.info("Browser restarted due to session crash")

driver.quit()
logging.info("Job application process completed!")