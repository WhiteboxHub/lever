
import csv
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd
import os
import yaml
import logging

import re
from fuzzywuzzy import fuzz
from fake_useragent import UserAgent


lever_base_url = "https://jobs.lever.co"

def load_config(file_location):
    with open(file_location, 'r') as stream:
        try:
            parameters = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            raise exc

    
    assert parameters.get("full_name") is not None, "Full name is missing in YAML file."
    assert parameters.get("email") is not None, "Email is missing in YAML file."
    assert parameters.get("phone") is not None, "Phone number is missing in YAML file."
    assert parameters.get("linkedin") is not None, "LinkedIn URL is missing in YAML file."
    assert parameters.get("resume_path") is not None, "Resume path is missing in YAML file."

    credentials = {
        "full_name": parameters["full_name"],
        "email": parameters["email"],
        "phone": parameters["phone"],
        "linkedin": parameters["linkedin"],
        "resume": os.path.abspath(parameters["resume_path"])
    }

    optional_fields = {
        "current_location": parameters.get("current_location", ""),
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
    with open("config/answers.csv", mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            question = row["Question"].strip().lower()
            answers[question] = row["Answer"].strip()
except FileNotFoundError:
    print("Error: 'answers.csv' file not found.")
    exit()

# Setup browser
# ua = UserAgent()
chrome_options = Options()
# chrome_options.add_argument(f"user-agent={ua.random}")
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
            platform = str(row.platform).lower()
            company = str(row.company).lower()
            jobid = str(row.jobid)

            if platform == "lever" and company and jobid:
                job_link = f"{lever_base_url}/{company}/{jobid}"
                job_links.append(job_link)
            else:
                logging.info(f"Skipping invalid row: platform={platform}, company={company}, jobid={jobid}")

    except pd.errors.ParserError as e:
        logging.error(f"Error parsing CSV file: {e}")
        exit()

else:
    logging.error(f"CSV file '{job_links_file}' does not exist.")
    exit()

if not job_links:
    logging.error("No Lever job links found in the CSV file.")
    exit()
else:
    logging.info(f"Loaded {len(job_links)} Lever job links.")

FIELD_SELECTORS = {
    "full_name": ["input[name='name']", "input[id='name']", "input[placeholder*='Full name']", "input[type='text']"],
    "email": ["input[type='email']", "input[name*='email']", "input[id*='email']"],
    "phone": ["input[type='tel']", "input[name*='phone']", "input[id*='phone']"],
    "linkedin": ["input[name*='linkedin']", "input[id*='linkedin']", "input[placeholder*='LinkedIn']"],
    "resume": ["input[type='file']", "input[name*='resume']", "input[id*='resume']"],
    "current_location": ["input[name*='location']", "input[id*='location']", "input[placeholder*='Location']"],
    "current_company": ["input[name*='company']", "input[id*='company']", "input[placeholder*='Company']"],
}

def normalize_text(text):
    """Normalize text by removing special characters and extra spaces."""
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)  
    text = " ".join(text.split()) 
    return text.lower()

def find_input_field(driver, selectors):
    """Finds an input field using multiple CSS selectors."""
    for selector in selectors:
        try:
            field = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            return field
        except:
            continue
    return None

def open_job_and_click_apply(driver, job_link):
    """Opens job link, checks for 404 errors, clicks 'Apply' button if found, else skips."""
    try:
        print(f"\n Opening job: {job_link}")
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
                button = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
                button.click()
                print(f"Clicked 'Apply' button")
                time.sleep(10)
                return True
            except:
                continue

        print("⚠ No 'Apply' button found, skipping.")
        return False

    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def fill_form_and_submit(driver):
    """Fills required fields, answers custom questions, uploads resume and LinkedIn, then submits."""
    try:
        print("\nFilling the form...")

        
        for field, selectors in FIELD_SELECTORS.items():
            value = credentials.get(field)
            if value:
                input_field = find_input_field(driver, selectors)
                if input_field:
                    input_field.clear()
                    if field == "resume":
                        input_field.send_keys(credentials["resume"])
                        print(f"Uploaded Resume: {credentials['resume']}")
                    else:
                        input_field.send_keys(value)
                        print(f"Filled {field.replace('_', ' ').title()}: {value}")
                else:
                    print(f"⚠ Field '{field}' not found on the form.")
       
        question_elements = driver.find_elements(By.CSS_SELECTOR, "div.application-label, div.question, span, p")

        for question_element in question_elements:
            q_text = normalize_text(question_element.text)
            print(f"Form Question: {q_text}")
            best_match = None
            best_score = 0

            
            for question_key in answers.keys():
                normalized_key = normalize_text(question_key)
                print(f"CSV Question: {normalized_key}")
                score = fuzz.ratio(q_text, normalized_key)
                if score > best_score and score > 60: 
                    best_score = score
                    best_match = question_key

            if best_match:
                answer = answers[best_match]
          
                try:
                    parent_element = question_element.find_element(By.XPATH, "./following-sibling::div[contains(@class, 'application-field')]")
                except Exception as e:
                    print(f"Error locating parent element for question '{q_text}': {str(e)}")
                    continue

                
                if "how did you hear about us" in q_text.lower():
                    checkbox_options = answer.split(", ")
                    for option in checkbox_options:
                        option_selector = f"input[type='checkbox'][value='{option}']"
                        try:
                            option_field = WebDriverWait(parent_element, 5).until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, option_selector))
                            )
                            driver.execute_script("arguments[0].scrollIntoView();", option_field)
                            driver.execute_script("arguments[0].click();", option_field)
                            print(f"Clicked checkbox: {option}")
                        except Exception as e:
                            print(f"Error clicking checkbox for option '{option}': {str(e)}")

                elif "export control and compliance" in q_text.lower():
                    textarea_selector = "textarea.card-field-input"
                    try:
                        textarea_field = WebDriverWait(parent_element, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, textarea_selector))
                        )
                        driver.execute_script("arguments[0].scrollIntoView();", textarea_field)
                        textarea_field.clear()
                        textarea_field.send_keys(answer)
                        print(f"Filled textarea: {answer}")
                    except Exception as e:
                        print(f"Error filling textarea: {str(e)}")

                elif "gender" in q_text.lower() or "decline to self-identify" in q_text.lower():
                    dropdown_selector = "select"
                    try:
                        dropdown_field = WebDriverWait(parent_element, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, dropdown_selector))
                        )
                        select = Select(dropdown_field)
                        select.select_by_visible_text(answer)
                        print(f"Selected dropdown option: {answer}")
                    except Exception as e:
                        print(f"Error selecting dropdown option: {str(e)}")

                print(f"Answered: {q_text} -> {answer}")
            else:
                print(f"⚠ No matching answer found for: {q_text}")

       
        acknowledge_selector = "input[type='checkbox'][value='I acknowledge']"
        acknowledge_fields = driver.find_elements(By.CSS_SELECTOR, acknowledge_selector)
        for acknowledge_field in acknowledge_fields:
            try:
                driver.execute_script("arguments[0].scrollIntoView();", acknowledge_field)
                driver.execute_script("arguments[0].click();", acknowledge_field)
                print("Clicked 'Acknowledge' checkbox.")
            except Exception as e:
                print(f"Error clicking 'Acknowledge' checkbox: {str(e)}")

      
        submit_selectors = [
            "button#btn-submit",
            "button[data-qa='btn-submit']",
            "button.postings-btn.template-btn-submit",
            "button[class*='submit']",
            "input[type='submit']",
            "a[class*='submit']"
        ]

        for selector in submit_selectors:
            try:
                submit_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
                submit_button.click()
                print(f"Clicked submit button")
                time.sleep(5)
                return True
            except:
                continue

        print("⚠ No submit button found, skipping submission.")
        return False

    except Exception as e:
        print(f"Error filling form: {str(e)}")
        return False

for job_link in job_links:
    if open_job_and_click_apply(driver, job_link):
        fill_form_and_submit(driver)

driver.quit()
print("\ Job application process completed!")

for job_link in job_links:
    if open_job_and_click_apply(driver, job_link):
        fill_form_and_submit(driver)

driver.quit()
print("\ Job application process completed!")