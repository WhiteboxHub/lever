import csv
import os
import time
import re
import json
import logging
import yaml
import pandas as pd
from fuzzywuzzy import fuzz
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    WebDriverException,
    ElementNotInteractableException,
    StaleElementReferenceException
)
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('lever_automation.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class LeverAutomation:
    def __init__(self):
        self.lever_base_url = "https://jobs.lever.co"
        self.profile_yaml = self.select_profile()
        self.load_locators()
        self.credentials = self.load_config(f"config/{self.profile_yaml}")
        self.answers = self.load_answers("answers.csv")
        self.driver = self.setup_driver()
        
    def select_profile(self):
        """Dynamically list YAML files in config/"""
        config_dir = "config"
        yaml_files = [
            f for f in os.listdir(config_dir)
            if os.path.isfile(os.path.join(config_dir, f)) and f.lower().endswith(('.yaml', '.yml'))
        ]
        
        if not yaml_files:
            logging.error("No YAML files found in config directory.")
            raise FileNotFoundError("No YAML files found in config.")

        yaml_files.sort()
        print("Select a profile:")
        for idx, yaml_file in enumerate(yaml_files, 1):
            print(f"{idx} = {yaml_file}")
        
        while True:
            try:
                choice = input(f"Enter profile number (1-{len(yaml_files)}): ").strip()
                profile_num = int(choice)
                if 1 <= profile_num <= len(yaml_files):
                    selected_yaml = yaml_files[profile_num - 1]
                    logging.info(f"Selected profile: {selected_yaml}")
                    return selected_yaml
                else:
                    print(f"Please enter a number between 1 and {len(yaml_files)}.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    def load_locators(self):
        try:
            with open("locators/lever_locators.json", "r") as f:
                self.locators = json.load(f)
        except FileNotFoundError:
            logging.error("Locators file not found.")
            raise
        except json.JSONDecodeError:
            logging.error("Invalid JSON in locators file.")
            raise

    def load_config(self, file_location):
        try:
            with open(file_location, 'r') as stream:
                data = yaml.safe_load(stream)
        except FileNotFoundError:
            logging.error(f"Config file '{file_location}' not found.")
            raise
        except yaml.YAMLError as exc:
            logging.error(f"Error parsing YAML file: {exc}")
            raise

        required_fields = ["full_name", "email", "phone", "linkedin", "resume_path", "current_company", "current_location"]
        credentials = {}
        
        for field in required_fields:
            if field not in data:
                logging.error(f"Required field '{field}' missing in YAML.")
                raise KeyError(f"Required field '{field}' missing in YAML.")
            credentials[field] = str(data[field])


        phone = credentials["phone"]
        cleaned_phone = re.sub(r'[^\d+]', '', phone)
        if not re.match(r"^\+?\d{8,15}$", cleaned_phone):
            logging.warning(f"Phone number format warning (continuing anyway): {phone}")

        credentials["github"] = str(data.get("github", ""))
        credentials["portfolio"] = str(data.get("portfolio", ""))
        credentials["work_status"] = str(data.get("work_status", ""))

        base_dir = os.path.dirname(os.path.abspath(__file__))
        resume_path = os.path.join(base_dir, credentials["resume_path"])
        if not os.path.isfile(resume_path):
            logging.error(f"Resume file not found at: {resume_path}")
            raise FileNotFoundError(f"Resume file not found at: {resume_path}")
        credentials["resume"] = resume_path

        return credentials

    def load_answers(self, file_path):
        answers = {}
        try:
            with open(file_path, mode="r", encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    question = row["Question"].strip().lower()
                    answers[question] = row["Answer"].strip()
            return answers
        except FileNotFoundError:
            logging.error(f"Answers file '{file_path}' not found.")
            raise

    def setup_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--start-maximized")
        
        service = Service(ChromeDriverManager().install())
        driver = uc.Chrome(options=chrome_options, service=service)
        return driver

    def normalize_text(self, text):
        if not text:
            return ""
        return re.sub(r"[^a-zA-Z0-9\s]", "", text).strip().lower()

    def find_element(self, locator_key, sub_key=None, multiple=False, timeout=10):
        if sub_key:
            selectors = self.locators.get(locator_key, {}).get(sub_key, [])
        else:
            selectors = self.locators.get(locator_key, [])
        if not isinstance(selectors, list):
            selectors = [selectors]
        logging.info(f"Trying selectors for {locator_key}{'.' + sub_key if sub_key else ''}: {[s['value'] for s in selectors]}")
        
        for selector in selectors:
            selector_type = selector.get('type', 'css')
            selector_value = selector.get('value', '')
            logging.info(f"Attempting {selector_type} selector: {selector_value}")
            
            try:
                by_type = By.CSS_SELECTOR if selector_type == 'css' else By.XPATH
                if multiple:
                    return WebDriverWait(self.driver, timeout).until(
                        EC.presence_of_all_elements_located((by_type, selector_value)))
                return WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((by_type, selector_value)))
            except TimeoutException:
                logging.warning(f"Timeout {selector_type} selector {selector_value}")
                continue
            except NoSuchElementException:
                logging.warning(f"Element not found for {selector_type} selector {selector_value}")
                continue
            except ElementNotInteractableException:
                logging.warning(f"Element not interactable for {selector_type} selector {selector_value}")
                continue
            except Exception as e:
                logging.warning(f"Unexpected error for {selector_type} selector {selector_value}: {str(e)}")
                continue
        logging.error(f"No selectors worked for {locator_key}{'.' + sub_key if sub_key else ''}")
        return None

    def upload_resume(self):
        value = self.credentials["resume"]
        logging.info(f"Attempting to upload resume: {value}")

        resume_input = self.find_element("resume_path")
        if not resume_input:
            logging.warning("Resume file input not found, it may be optional")
            return False

        logging.info(f"Found resume input: {resume_input.get_attribute('outerHTML')}")

        try:
            upload_button = self.find_element("resume_upload_button")
            if upload_button:
                logging.info(f"Upload button found: {upload_button.get_attribute('outerHTML')}")
                self.driver.execute_script("arguments[0].scrollIntoView(true);", upload_button)
                self.driver.execute_script("arguments[0].click();", upload_button)
                logging.info("Clicked resume upload button")
                time.sleep(1)
            else:
                logging.info("No resume upload button found")
        except Exception as e:
            logging.warning(f"Failed to click upload button: {str(e)}")

        try:
            self.driver.execute_script(
                "arguments[0].style.display='block'; "
                "arguments[0].style.visibility='visible'; "
                "arguments[0].style.opacity='1'; "
                "arguments[0].style.zIndex='9999'; "
                "arguments[0].classList.remove('invisible-resume-upload'); "
                "arguments[0].removeAttribute('disabled');",
                resume_input
            )
            logging.info("Made resume input visible")
        except Exception as e:
            logging.warning(f"Failed to apply visibility script: {str(e)}")

        try:
            resume_input.send_keys(value)
            logging.info(f"Uploaded resume: {value}")
        except ElementNotInteractableException as e:
            logging.error(f"Resume input not interactable: {str(e)}")
            return False
        except Exception as e:
            logging.error(f"Failed to upload resume: {str(e)}")
            return False

 
        try:
            confirmation_selectors = [s['value'] for s in self.locators.get("resume_upload_confirmation", []) if s['type'] == 'css']
            if confirmation_selectors:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ", ".join(confirmation_selectors)))
                )
                logging.info("Resume upload confirmed")
            else:
                logging.info("No confirmation selectors defined")
        except TimeoutException:
            logging.info("No upload confirmation found")
        except Exception as e:
            logging.warning(f"Error checking upload confirmation: {str(e)}")

        time.sleep(2)
        return True

    def open_job_and_click_apply(self, job_link):
        logging.info(f"Opening job: {job_link}")
        self.driver.get(job_link)
        time.sleep(2)

        if any(text in self.driver.page_source for text in ["404", "Not Found", "Page not found"]):
            logging.warning("Page not found (404)")
            return "404"

        if "already applied" in self.driver.page_source.lower():
            logging.info("Job already applied to")
            return "already applied"

        if "apply" in self.driver.current_url.lower():
            logging.info("Direct job application form detected")
            return True

        for selector in self.locators["APPLY_SELECTORS"]:
            selector_type = selector.get('type', 'css')
            selector_value = selector.get('value', '')
            logging.info(f"Attempting {selector_type} selector for apply button: {selector_value}")
            try:
                by_type = By.CSS_SELECTOR if selector_type == 'css' else By.XPATH
                apply_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((by_type, selector_value)))
                self.driver.execute_script("arguments[0].scrollIntoView();", apply_button)
                self.driver.execute_script("arguments[0].click();", apply_button)
                logging.info(f"Clicked 'Apply' button using {selector_type} selector")
                time.sleep(3)
                return True
            except (TimeoutException, NoSuchElementException):
                logging.warning(f"Failed to click apply button with {selector_type} selector")
                continue

        logging.warning("No 'Apply' button found")
        return False

    def fill_basic_fields(self):
        
        self.upload_resume()

        filled_fields = set()

        for field_key, selectors in self.locators["FIELD_SELECTORS"].items():
            if field_key in ["resume", "resume_path", "resume_upload_button", "resume_upload_confirmation"]:
                continue
            if field_key not in self.credentials or field_key in filled_fields:
                continue

            value = self.credentials[field_key]
            if not value:
                logging.warning(f"No value for {field_key} in credentials")
                continue

            selectors = selectors if isinstance(selectors, list) else [selectors]
            logging.info(f"Attempting to fill {field_key} with: {value}")

            for selector in selectors:
                selector_type = selector.get('type', 'css')
                selector_value = selector.get('value', '')
                try:
                    by_type = By.CSS_SELECTOR if selector_type == 'css' else By.XPATH
                    input_field = WebDriverWait(self.driver, 10).until(
                        EC.visibility_of_element_located((by_type, selector_value))
                    )
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", input_field)
                    input_field.clear()
                    input_field.send_keys(value)
                    logging.info(f"Filled {field_key}: {value}")
                    filled_fields.add(field_key)
                    break
                except (TimeoutException, NoSuchElementException, ElementNotInteractableException) as e:
                    logging.warning(f"Failed to fill {field_key} with {selector_type} selector {selector_value}: {str(e)}")
                    continue

    def handle_location_dropdown(self):
        try:
            location_input = self.find_element("LOCATION_SELECTORS", "input")
            if location_input:
                is_required = False
                parent_elements = self.driver.find_elements(By.XPATH, ".//ancestor::*[contains(., '*')]")
                for parent in parent_elements:
                    if any(indicator in parent.text for indicator in self.locators["QUESTION_FIELD_SELECTORS"]["required_indicator"]):
                        is_required = True
                        break

                location_value = str(self.credentials["current_location"])
                logging.info(f"Attempting to fill location with: {location_value}")
                location_input.click()
                location_input.clear()
                location_input.send_keys(location_value)
                logging.info(f"Filled location with: {location_value}")
                time.sleep(1)

                try:
                    options = self.find_element("LOCATION_SELECTORS", "options", multiple=True)
                    if options:
                        for option in options:
                            if location_value.lower() in option.text.lower():
                                option.click()
                                logging.info(f"Selected location option: {option.text}")
                                break
                        else:
                            logging.info("No matching location option found")
                    elif is_required:
                        logging.warning("Location is required but no dropdown options found")
                except Exception as e:
                    logging.info(f"No location dropdown options available: {str(e)}")
            else:
                logging.info("No location input found")
        except Exception as e:
            logging.warning(f"Location dropdown handling failed: {str(e)}")

    def handle_radio_buttons(self, question_element, answer, question_text):
        radio_buttons = []
        for selector in self.locators["QUESTION_FIELD_SELECTORS"]["radio_button"]:
            try:
                radio_buttons.extend(
                    question_element.find_elements(
                        By.CSS_SELECTOR if selector["type"] == "css" else By.XPATH,
                        selector["value"]
                    )
                )
            except NoSuchElementException:
                continue

        if not radio_buttons:
            logging.warning(f"No radio buttons found for question: {question_text}")
            return False

        normalized_answer = self.normalize_text(answer)
        logging.info(f"Radio button options for '{question_text}': {[rb.get_attribute('value') or rb.text for rb in radio_buttons]}")

        for radio in radio_buttons:
            try:
                value = self.normalize_text(radio.get_attribute("value") or radio.text)
                if value == normalized_answer:
                    if not radio.is_selected():
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", radio)
                        self.driver.execute_script("arguments[0].click();", radio)
                        logging.info(f"Selected radio button: '{value}' for '{question_text}'")
                    return True
            except (StaleElementReferenceException, ElementNotInteractableException) as e:
                logging.warning(f"Error interacting with radio button: {str(e)}")
                continue

    
        best_match = None
        best_score = 0
        for radio in radio_buttons:
            try:
                value = self.normalize_text(radio.get_attribute("value") or radio.text)
                score = fuzz.ratio(value, normalized_answer)
                if score > 80 and score > best_score:
                    best_match = radio
                    best_score = score
            except StaleElementReferenceException:
                continue

        if best_match:
            try:
                if not best_match.is_selected():
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", best_match)
                    self.driver.execute_script("arguments[0].click();", best_match)
                logging.info(f"Selected radio button (fuzzy): '{best_match.get_attribute('value') or best_match.text}' (Score: {best_score}) for '{question_text}'")
                return True
            except (ElementNotInteractableException, StaleElementReferenceException) as e:
                logging.warning(f"Failed to select fuzzy-matched radio button: {str(e)}")

        logging.warning(f"No matching radio button found for answer '{answer}' in question '{question_text}'")
        return False

    def handle_checkboxes(self, question_element, question_text):
        checkboxes = []
        for selector in self.locators["QUESTION_FIELD_SELECTORS"]["checkbox"]:
            try:
                checkboxes.extend(
                    question_element.find_elements(
                        By.CSS_SELECTOR if selector["type"] == "css" else By.XPATH,
                        selector["value"]
                    )
                )
            except NoSuchElementException:
                continue

        if not checkboxes:
            logging.info(f"No checkboxes found for question: {question_text}")
            return False

        normalized_question = self.normalize_text(question_text)
        logging.info(f"Checkboxes found for '{question_text}': {[cb.get_attribute('name') or cb.text for cb in checkboxes]}")

        for checkbox in checkboxes:
            try:
                if any(keyword in normalized_question for keyword in ["certify", "agree", "acknowledge", "confirm"]):
                    if not checkbox.is_selected():
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", checkbox)
                        self.driver.execute_script("arguments[0].click();", checkbox)
                        logging.info(f"Checked checkbox for '{question_text}'")
                    return True
            except (ElementNotInteractableException, StaleElementReferenceException) as e:
                logging.warning(f"Failed to interact with checkbox: {str(e)}")
                continue
        for checkbox in checkboxes:
            try:
                if checkbox.get_attribute("required") or "required" in (checkbox.get_attribute("class") or "").lower():
                    if not checkbox.is_selected():
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", checkbox)
                        self.driver.execute_script("arguments[0].click();", checkbox)
                        logging.info(f"Checked required checkbox for '{question_text}'")
                    return True
            except (ElementNotInteractableException, StaleElementReferenceException) as e:
                logging.warning(f"Failed to check required checkbox: {str(e)}")
                continue

        logging.info(f"No relevant checkboxes checked for '{question_text}'")
        return False

    def handle_custom_questions(self):
        question_elements = self.find_element("QUESTION_SELECTORS", multiple=True) or []
        logging.info(f"Found {len(question_elements)} question elements")

        for question_element in question_elements:
            try:
                
                label = None
                for selector in self.locators["QUESTION_FIELD_SELECTORS"]["label"]:
                    try:
                        label = question_element.find_element(
                            By.CSS_SELECTOR if selector["type"] == "css" else By.XPATH,
                            selector["value"]
                        )
                        break
                    except NoSuchElementException:
                        continue
                question_text = label.text.strip() if label else question_element.text.strip() or "Unknown question"
                logging.info(f"Processing question: {question_text}")

                normalized_question = self.normalize_text(question_text)

                if any(keyword in normalized_question for keyword in ["resume", "cv", "upload file"]):
                    logging.info(f"Skipping resume question: {question_text}")
                    continue

                # Find matching answer
                best_match = None
                best_score = 0
                for q in self.answers:
                    score = fuzz.ratio(self.normalize_text(q), normalized_question)
                    if score > best_score:
                        best_match = q
                        best_score = score

                if best_match and best_score > 70:
                    answer = self.answers[best_match]
                    logging.info(f"Matched '{question_text}' to '{best_match}' (Score: {best_score})")

                    # Try textarea
                    for selector in self.locators["QUESTION_FIELD_SELECTORS"]["textarea"]:
                        try:
                            textarea = question_element.find_element(
                                By.CSS_SELECTOR if selector["type"] == "css" else By.XPATH,
                                selector["value"]
                            )
                            self.driver.execute_script("arguments[0].scrollIntoView(true);", textarea)
                            textarea.clear()
                            textarea.send_keys(answer)
                            logging.info(f"Filled textarea with: {answer} for '{question_text}'")
                            break
                        except (NoSuchElementException, ElementNotInteractableException):
                            continue

                    # Try text input
                    for selector in self.locators["QUESTION_FIELD_SELECTORS"]["text_input"]:
                        try:
                            text_input = question_element.find_element(
                                By.CSS_SELECTOR if selector["type"] == "css" else By.XPATH,
                                selector["value"]
                            )
                            self.driver.execute_script("arguments[0].scrollIntoView(true);", text_input)
                            text_input.clear()
                            text_input.send_keys(answer)
                            logging.info(f"Filled text input with: {answer} for '{question_text}'")
                            break
                        except (NoSuchElementException, ElementNotInteractableException):
                            continue

                    # Try dropdown
                    for selector in self.locators["QUESTION_FIELD_SELECTORS"]["dropdown"]:
                        try:
                            select_element = question_element.find_element(
                                By.CSS_SELECTOR if selector["type"] == "css" else By.XPATH,
                                selector["value"]
                            )
                            select = Select(select_element)
                            select.select_by_visible_text(answer)
                            logging.info(f"Selected dropdown option: {answer} for '{question_text}'")
                            break
                        except (NoSuchElementException, ElementNotInteractableException):
                            continue

                    # Try radio buttons
                    if self.handle_radio_buttons(question_element, answer, question_text):
                        continue

                    # Try checkboxes
                    if self.handle_checkboxes(question_element, question_text):
                        continue

                    logging.warning(f"Could not answer question: {question_text}")
                else:
                    # Handle checkboxes for unmatched questions
                    if self.handle_checkboxes(question_element, question_text):
                        continue
                    logging.warning(f"No match found for question: {question_text}")
            except Exception as e:
                logging.warning(f"Error processing question '{question_text}': {str(e)}")

    def handle_acknowledgements(self):
        for selector in self.locators["ACKNOWLEDGEMENT_SELECTORS"]:
            selector_type = selector.get('type', 'css')
            selector_value = selector.get('value', '')
            try:
                by_type = By.CSS_SELECTOR if selector_type == 'css' else By.XPATH
                checkbox = self.driver.find_element(by_type, selector_value)
                if not checkbox.is_selected():
                    self.driver.execute_script("arguments[0].click();", checkbox)
                    logging.info(f"Checked acknowledgement checkbox with {selector_type} selector {selector_value}")
            except NoSuchElementException:
                logging.info(f"No acknowledgement checkbox found with {selector_type} selector {selector_value}")
                continue

    def submit_application(self):
        for selector in self.locators["SUBMIT_SELECTORS"]:
            selector_type = selector.get('type', 'css')
            selector_value = selector.get('value', '')
            try:
                by_type = By.CSS_SELECTOR if selector_type == 'css' else By.XPATH
                submit_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((by_type, selector_value)))
                self.driver.execute_script("arguments[0].scrollIntoView();", submit_button)
                self.driver.execute_script("arguments[0].click();", submit_button)
                logging.info(f"Form submitted successfully with {selector_type} selector {selector_value}")
                return True
            except (TimeoutException, NoSuchElementException):
                logging.warning(f"Failed to submit with {selector_type} selector {selector_value}")
                continue
        logging.warning("No submit button found")
        return False

    def process_job_application(self, job_link, max_retries=2):
        job_id = job_link.split('/')[-1]
        for attempt in range(max_retries + 1):
            try:
                result = self.open_job_and_click_apply(job_link)
                if result == "404":
                    self.log_application_status(job_link, "Failed")
                    return "failed"
                elif result == "already applied":
                    self.log_application_status(job_link, "already applied")
                    return "already applied"
                elif not result:
                    self.log_application_status(job_link, "failed")
                    return False
                
                self.fill_basic_fields()
                self.handle_location_dropdown()
                self.handle_custom_questions()
                self.handle_acknowledgements()

                # Pause for 3 minutes
                logging.info("Pausing for 3 minutes for manual review...")
                time.sleep(90)
                logging.info("Resuming after pause")

                if self.submit_application():
                    self.log_application_status(job_link, "success")
                    return True
                else:
                    self.log_application_status(job_link, "failed")
                    return False
                
            except WebDriverException as e:
                logging.error(f"Attempt {attempt + 1} failed: {e}")
                if attempt < max_retries:
                    time.sleep(5)
                    self.driver.quit()
                    self.driver = self.setup_driver()
                else:
                    logging.error("All retries exhausted")
                    self.log_application_status(job_id, "failed")
                    return False

    def log_application_status(self, job_id, status):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_file = "logs/application.csv"
        
        try:
            os.makedirs("logs", exist_ok=True)
            file_exists = os.path.isfile(log_file)
            
            with open(log_file, mode='a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f, quoting=csv.QUOTE_ALL)
                if not file_exists:
                    writer.writerow(["jobId", "timestamp", "status"])
                writer.writerow([job_id, timestamp, status])
                f.flush()
            logging.info(f"Logged to CSV: \"{job_id}\",\"{timestamp}\",\"{status}\"")
        except Exception as e:
            logging.error(f"Failed to log to {log_file}: {e}")

    def run(self, job_links_file="jobs/job_links.csv"):
        if not os.path.exists(job_links_file):
            logging.error(f"CSV file '{job_links_file}' not found.")
            return

        job_links_df = pd.read_csv(job_links_file)
        required_columns = ["company", "platform", "job_id", "platform_link"]
        
        if not all(col in job_links_df.columns for col in required_columns):
            logging.error("Missing required columns in CSV file.")
            return

        job_links = []
        for row in job_links_df.itertuples(index=False):
            if str(row.platform).lower() == "lever":
                job_links.append(f"{self.lever_base_url}/{row.company}/{row.job_id}")

        if not job_links:
            logging.error("No Lever job links found in the CSV file.")
            return

        for job_link in job_links:
            logging.info(f"Processing job: {job_link}")
            self.process_job_application(job_link)

        self.driver.quit()
        logging.info("Job application process completed!")

if __name__ == "__main__":
    automation = LeverAutomation()
    automation.run()