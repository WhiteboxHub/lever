# import csv
# import undetected_chromedriver as uc
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.chrome.options import Options
# import time
# import os
# import yaml
# import random
# from datetime import datetime
# from fake_useragent import UserAgent
# from anticaptchaofficial.recaptchav2proxyless import recaptchaV2Proxyless


# # Load credentials and resume path from config.yaml
# with open("credentials/sunil.yaml", "r") as file:
#     config = yaml.safe_load(file)

# credentials = config["credentials"]
# resume_path = os.path.abspath(config["resume_path"])

# # Set up Chrome options with a random user agent
# ua = UserAgent()
# chrome_options = Options()
# chrome_options.add_argument(f"user-agent={ua.random}")
# chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Prevent bot detection

# # Use undetected ChromeDriver
# driver = uc.Chrome(options=chrome_options)

# # File to save application data
# applications_file = "applications.csv"

# # Create applications file with headers if not present
# if not os.path.exists(applications_file):
#     with open(applications_file, mode="w", newline="") as file:
#         writer = csv.writer(file)
#         writer.writerow(["Company", "Job Title", "Application Link", "Date Applied", "Status"])

# # Read job links from the text file
# with open("job_links.txt", "r") as file:
#     job_links = file.read().splitlines()

# if not job_links:
#     print("No job links available. End of the links.")
# else:
#     for job_link in job_links:
#         retry_count = 0
#         max_retries = 3

#         while retry_count < max_retries:
#             try:
#                 print(f"Processing job link: {job_link}")

#                 # Open job link with human-like delay
#                 driver.get(job_link)
#                 time.sleep(random.uniform(5, 15))

#                 # Extract company name
#                 try:
#                     company_name = driver.find_element(By.CSS_SELECTOR, "a.main-header-logo img").get_attribute("alt")
#                     company_name = company_name.replace(" logo", "")
#                 except:
#                     company_name = "Unknown Company"

#                 # Extract job title
#                 try:
#                     job_title = driver.find_element(By.CSS_SELECTOR, "div.section.page-centered.posting-header h2").text.strip()
#                 except:
#                     job_title = "Unknown Job Title"

#                 # Fill out form
#                 WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "name"))).send_keys(credentials["name"])
#                 time.sleep(random.uniform(2, 5))

#                 WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "email"))).send_keys(credentials["email"])
#                 time.sleep(random.uniform(2, 5))

#                 WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "phone"))).send_keys(credentials["phone"])
#                 time.sleep(random.uniform(2, 5))

#                 # Upload resume
#                 print(f"Uploading resume from: {resume_path}")
#                 file_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "resume")))
#                 file_input.send_keys(resume_path)
#                 time.sleep(random.uniform(2, 5))

#                 # Fill LinkedIn profile (if exists)
#                 try:
#                     WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "urls[LinkedIn]"))).send_keys(credentials["linkedin_url"])
#                     time.sleep(random.uniform(2, 5))
#                 except:
#                     pass

#                 # Handle CAPTCHA
#                 try:
#                     recaptcha_frame = WebDriverWait(driver, 10).until(
#                         EC.presence_of_element_located((By.XPATH, "//iframe[contains(@src, 'recaptcha')]"))
#                     )
#                     driver.switch_to.frame(recaptcha_frame)

#                     site_key = driver.find_element(By.CLASS_NAME, "g-recaptcha").get_attribute("data-sitekey")
#                     driver.switch_to.default_content()

#                     print("Solving CAPTCHA using 2Captcha...")

#                     solver =  recaptchaV2Proxyless()
#                     solver.set_verbose(1)
#                     solver.set_key("YOUR_2CAPTCHA_API_KEY")  # Replace with your API key
#                     solver.set_website_url(job_link)
#                     solver.set_website_key(site_key)

#                     captcha_solution = solver.solve_and_return_solution()
#                     if captcha_solution:
#                         driver.execute_script(f'document.getElementById("g-recaptcha-response").innerHTML="{captcha_solution}"')
#                         time.sleep(3)
#                         print("CAPTCHA solved successfully!")
#                     else:
#                         print("Failed to solve CAPTCHA.")
#                         raise Exception("CAPTCHA Failed")
#                 except Exception as e:
#                     print("No CAPTCHA found or failed to solve:", e)

#                 # Simulate human-like mouse movement
#                 actions = ActionChains(driver)
#                 actions.move_by_offset(random.randint(5, 50), random.randint(5, 50)).perform()
#                 time.sleep(random.uniform(2, 5))

#                 # Submit the form
#                 submit_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "btn-submit")))
#                 submit_button.click()

#                 # Wait for success confirmation
#                 try:
#                     WebDriverWait(driver, 20).until(
#                         EC.any_of(
#                             EC.url_contains("success"),
#                             EC.presence_of_element_located((By.CSS_SELECTOR, "div.success-message"))
#                         )
#                     )
#                     print("Application submitted successfully!")
#                     status = "Success"
#                 except:
#                     status = "Failed"

#                 # Save to CSV
#                 with open(applications_file, mode="a", newline="") as file:
#                     writer = csv.writer(file)
#                     writer.writerow([company_name, job_title, job_link, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), status])

#                 time.sleep(random.uniform(5, 10))  # Delay before next application
#                 break  # Exit retry loop if successful

#             except Exception as e:
#                 print(f"Error for {job_link}: {e}")
#                 retry_count += 1
#                 if retry_count < max_retries:
#                     print(f"Retrying... ({retry_count}/{max_retries})")
#                     time.sleep(random.uniform(10, 20))
#                 else:
#                     print("Failed after multiple attempts.")
#                     with open(applications_file, mode="a", newline="") as file:
#                         writer = csv.writer(file)
#                         # writer.writerow([company_name, job_title, job_link, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Failed"])

#     print("All job links processed.")

# # Close browser
# driver.quit()



import csv
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
import time
import os
import yaml
import random
from datetime import datetime
from fake_useragent import UserAgent
from anticaptchaofficial.recaptchav2proxyless import recaptchaV2Proxyless

# Load credentials and resume path from config.yaml
with open("credentials/sunil.yaml", "r") as file:
    config = yaml.safe_load(file)

credentials = config["credentials"]
resume_path = os.path.abspath(config["resume_path"])

# Set up Chrome options with a random user agent
ua = UserAgent()
chrome_options = Options()
chrome_options.add_argument(f"user-agent={ua.random}")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Prevent bot detection

# Use undetected ChromeDriver
driver = uc.Chrome(options=chrome_options)

# File to save application data
applications_file = "applications.csv"

# Create applications file with headers if not present
if not os.path.exists(applications_file):
    with open(applications_file, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Company", "Job Title", "Application Link", "Date Applied", "Status"])

# Read job links from the text file
with open("job_links.txt", "r") as file:
    job_links = file.read().splitlines()

if not job_links:
    print("No job links available. End of the links.")
else:
    for job_link in job_links:
        retry_count = 0
        max_retries = 3

        while retry_count < max_retries:
            try:
                print(f"Processing job link: {job_link}")

                # Open job link with human-like delay
                driver.get(job_link)
                time.sleep(random.uniform(5, 15))

                # Extract company name
                try:
                    company_name = driver.find_element(By.CSS_SELECTOR, "a.main-header-logo img").get_attribute("alt")
                    company_name = company_name.replace(" logo", "")
                except Exception as e:
                    print(f"Error extracting company name: {e}")
                    company_name = "Unknown Company"

                # Extract job title
                try:
                    job_title = driver.find_element(By.CSS_SELECTOR, "div.section.page-centered.posting-header h2").text.strip()
                except Exception as e:
                    print(f"Error extracting job title: {e}")
                    job_title = "Unknown Job Title"

                # Fill out form
                try:
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "name"))).send_keys(credentials["name"])
                    time.sleep(random.uniform(2, 5))

                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "email"))).send_keys(credentials["email"])
                    time.sleep(random.uniform(2, 5))

                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "phone"))).send_keys(credentials["phone"])
                    time.sleep(random.uniform(2, 5))

                    # Upload resume
                    print(f"Uploading resume from: {resume_path}")
                    file_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "resume")))
                    file_input.send_keys(resume_path)
                    time.sleep(random.uniform(2, 5))

                    # Fill LinkedIn profile (if exists)
                    try:
                        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "urls[LinkedIn]"))).send_keys(credentials["linkedin_url"])
                        time.sleep(random.uniform(2, 5))
                    except Exception as e:
                        print(f"LinkedIn field not found: {e}")

                    # Handle CAPTCHA
                    try:
                        recaptcha_frame = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, "//iframe[contains(@src, 'recaptcha')]"))
                        )
                        driver.switch_to.frame(recaptcha_frame)

                        site_key = driver.find_element(By.CLASS_NAME, "g-recaptcha").get_attribute("data-sitekey")
                        driver.switch_to.default_content()

                        print("Solving CAPTCHA using 2Captcha...")

                        solver = recaptchaV2Proxyless()
                        solver.set_verbose(1)
                        solver.set_key("YOUR_2CAPTCHA_API_KEY")  # Replace with your API key
                        solver.set_website_url(job_link)
                        solver.set_website_key(site_key)

                        captcha_solution = solver.solve_and_return_solution()
                        if captcha_solution:
                            driver.execute_script(f'document.getElementById("g-recaptcha-response").innerHTML="{captcha_solution}"')
                            time.sleep(3)
                            print("CAPTCHA solved successfully!")
                        else:
                            print("Failed to solve CAPTCHA.")
                            raise Exception("CAPTCHA Failed")
                    except Exception as e:
                        print(f"No CAPTCHA found or failed to solve: {e}")

                    # Simulate human-like mouse movement
                    actions = ActionChains(driver)
                    actions.move_by_offset(random.randint(5, 50), random.randint(5, 50)).perform()
                    time.sleep(random.uniform(2, 5))

                    # Check for required fields
                    try:
                        required_fields = driver.find_elements(By.CSS_SELECTOR, "input[required], select[required], textarea[required]")
                        for field in required_fields:
                            if not field.get_attribute("value"):
                                print(f"Required field '{field.get_attribute('name')}' is empty. Filling it now.")
                                if field.get_attribute("type") == "text":
                                    field.send_keys("N/A")  # Fill with a default value
                                elif field.get_attribute("type") == "select":
                                    field.send_keys("Option 1")  # Select the first option
                    except Exception as e:
                        print(f"No required fields found or already filled: {e}")

                    # Submit the form
                    submit_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "btn-submit")))
                    submit_button.click()

                    # Wait for success confirmation
                    try:
                        WebDriverWait(driver, 20).until(
                            EC.any_of(
                                EC.url_contains("success"),
                                EC.presence_of_element_located((By.CSS_SELECTOR, "div.success-message"))
                            )
                        )
                        print("Application submitted successfully!")
                        status = "Success"
                    except Exception as e:
                        print(f"Failed to confirm success: {e}")
                        status = "Failed"

                    # Save to CSV
                    with open(applications_file, mode="a", newline="") as file:
                        writer = csv.writer(file)
                        writer.writerow([company_name, job_title, job_link, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), status])

                    time.sleep(random.uniform(5, 10))  # Delay before next application
                    break  # Exit retry loop if successful

                except Exception as e:
                    print(f"Error filling out the form: {e}")
                    raise  # Re-raise the exception to trigger a retry

            except Exception as e:
                print(f"Error for {job_link}: {e}")
                retry_count += 1
                if retry_count < max_retries:
                    print(f"Retrying... ({retry_count}/{max_retries})")
                    time.sleep(random.uniform(10, 20))
                else:
                    print("Failed after multiple attempts.")
                    with open(applications_file, mode="a", newline="") as file:
                        writer = csv.writer(file)
                        writer.writerow([company_name, job_title, job_link, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Failed"])

    print("All job links processed.")

# Close browser
driver.quit()



