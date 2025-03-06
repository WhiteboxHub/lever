import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
import time
from webdriver_manager.chrome import ChromeDriverManager

# Load the CSV file
def load_answers(csv_file):
    answers = {}
    with open(csv_file, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row if there is one
        for row in reader:
            question_id, answer_value = row  # Assuming two columns: question_id, answer_value
            answers[question_id] = answer_value
    return answers

# Set up Selenium driver

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
#service = Service('chromedriver.exe')  # Update with the correct driver path

driver.get("https://jobs.lever.co/curai/d0a6aa0d-ab59-4c1a-9140-9b9d7d203a37/apply")  # Replace with your target URL
time.sleep(10)

# Load answers
answers = load_answers("config/answers.csv")

# Loop through the answers and select radio buttons
for question_id, answer_value in answers.items():
    try:
        radio_button_xpath = f"//input[@name='{question_id}'][@value='{answer_value}']"
        radio_button = time.sleep(EC.element_to_be_clickable((By.XPATH, radio_button_xpath)))
        radio_button.click()
    except Exception as e:
        print(f"Could not select answer for {question_id}: {e}")

# Close the browser
time.sleep(30)
driver.quit()