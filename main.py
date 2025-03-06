# # import csv
# # import undetected_chromedriver as uc
# # from selenium.webdriver.common.by import By
# # from selenium.webdriver.support.ui import WebDriverWait, Select
# # from selenium.webdriver.support import expected_conditions as EC
# # from selenium.webdriver.common.action_chains import ActionChains
# # from selenium.webdriver.chrome.options import Options
# # import time
# # import pandas as pd
# # import os
# # import yaml
# # import random
# # from datetime import datetime
# # from fake_useragent import UserAgent
# # from anticaptchaofficial.recaptchav2proxyless import recaptchaV2Proxyless

# # # Load configuration
# # with open("config/credentials.yaml", "r") as file:
# #     config = yaml.safe_load(file)

# # credentials = config["credentials"]
# # resume_path = os.path.abspath(config["resume_path"])

# # # Load answers
# # answers = {}
# # try:
# #     with open("config/answers.csv", mode="r") as file:
# #         reader = csv.DictReader(file)
# #         for row in reader:
# #             question = row["Question"].strip().lower()
# #             answers[question] = row["Answer"].strip()
# # except FileNotFoundError:
# #     print("Error: 'answers.csv' file not found.")
# #     exit()

# # # Setup browser
# # ua = UserAgent()
# # chrome_options = Options()
# # chrome_options.add_argument(f"user-agent={ua.random}")
# # chrome_options.add_argument("--disable-blink-features=AutomationControlled")
# # driver = uc.Chrome(options=chrome_options)

# # # Application tracking
# # applications_file = "applications.csv"
# # if not os.path.exists(applications_file):
# #     with open(applications_file, "w", newline="") as file:
# #         writer = csv.writer(file)
# #         writer.writerow(["Company", "Job Title", "Application Link", "Date Applied", "Status", "Questions Answered"])

# # def fill_structured_fields(driver):
# #     """Fill standard form fields like name, email, etc."""
# #     structured_fields = {
# #         "first_name": ("//label[contains(., 'First Name')]/following-sibling::div//input", credentials.get("first_name")),
# #         "last_name": ("//label[contains(., 'Last Name')]/following-sibling::div//input", credentials.get("last_name")),
# #         "email": ("//label[contains(., 'Email')]/following-sibling::div//input", credentials.get("email")),
# #         "phone": ("//label[contains(., 'Phone')]/following-sibling::div//input", credentials.get("phone")),
# #         "address": ("//label[contains(., 'Address')]/following-sibling::div//input", credentials.get("address")),
# #         "city": ("//label[contains(., 'City')]/following-sibling::div//input", credentials.get("city")),
# #         "state": ("//label[contains(., 'State')]/following-sibling::div//select", credentials.get("state")),
# #         "zip": ("//label[contains(., 'Zip')]/following-sibling::div//input", credentials.get("zip")),
# #     }

# #     for field, (xpath, value) in structured_fields.items():
# #         if value:
# #             try:
# #                 element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, xpath)))
# #                 element.clear()
# #                 element.send_keys(value)
# #                 print(f"Filled {field.replace('_', ' ').title()}")
# #                 time.sleep(random.uniform(0.5, 1.5))
# #             except Exception as e:
# #                 print(f"Could not fill {field.replace('_', ' ').title()}: {e}")

# # def handle_field_types(container, answer):
# #     """Handle different types of form fields"""
# #     # Try textarea
# #     try:
# #         textarea = container.find_element(By.TAG_NAME, "textarea")
# #         textarea.clear()
# #         for char in answer:
# #             textarea.send_keys(char)
# #             time.sleep(random.uniform(0.02, 0.1))
# #         print(f"Filled textarea with: {answer[:50]}...")
# #         return True
# #     except:
# #         pass

# #     # Try text input
# #     try:
# #         input_field = container.find_element(By.XPATH, ".//input[@type='text']")
# #         input_field.clear()
# #         input_field.send_keys(answer)
# #         print(f"Filled text input: {answer[:50]}...")
# #         return True
# #     except:
# #         pass

# #     # Handle radio buttons/checkboxes
# #     try:
# #         options = container.find_elements(By.XPATH, ".//input[@type='radio'] | .//input[@type='checkbox']")
# #         if options:
# #             for option in options:
# #                 label = container.find_element(By.XPATH, f"//label[@for='{option.get_attribute('id')}']")
# #                 if label.text.strip().lower() == answer.lower() or option.get_attribute("value").lower() == answer.lower():
# #                     if not option.is_selected():
# #                         option.click()
# #                         print(f"Selected option: {answer}")
# #                         return True
# #             print(f"No matching option found for: {answer}")
# #             return False
# #     except:
# #         pass

# #     # Handle dropdowns
# #     try:
# #         select = container.find_element(By.TAG_NAME, "select")
# #         dropdown = Select(select)
# #         try:
# #             dropdown.select_by_visible_text(answer)
# #             print(f"Selected dropdown: {answer}")
# #             return True
# #         except:
# #             try:
# #                 dropdown.select_by_value(answer)
# #                 print(f"Selected dropdown by value: {answer}")
# #                 return True
# #             except:
# #                 print(f"No dropdown option matched: {answer}")
# #                 return False
# #     except:
# #         pass

# #     # Handle acknowledgements
# #     if "acknowledge" in answer.lower():
# #         try:
# #             checkbox = container.find_element(By.XPATH, ".//input[@type='checkbox']")
# #             if not checkbox.is_selected():
# #                 checkbox.click()
# #                 print("Checked acknowledgement box")
# #                 return True
# #         except:
# #             pass

# #     print(f"Could not find suitable field for: {answer}")
# #     return False

# # def fill_dynamic_fields(driver):
# #     """Answer custom questions from CSV"""
# #     for question_text, answer in answers.items():
# #         try:
# #             print(f"\nAttempting: {question_text[:50]}...")
            
# #             # Normalize question text
# #             clean_question = question_text.lower().replace('?', '').replace(':', '').strip()
            
# #             # Find question container
# #             container = WebDriverWait(driver, 10).until(
# #                 EC.presence_of_element_located((By.XPATH, 
# #                     f"//div[contains(@class, 'application-question')][.//*[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{clean_question}')]]"
# #                 ))
# #             )
            
            
# #             # Scroll to element
# #             driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", container)
# #             time.sleep(0.5)
            
# #             # Handle the field
# #             if not handle_field_types(container, answer):
# #                 print(f"Failed to answer: {question_text[:50]}...")
            
# #         except Exception as e:
# #             print(f"Question not found: {question_text[:50]}... - {str(e)}")

# # # Process job links
# # job_links_df = pd.read_csv("jobs/job_links.csv")
# # job_links = job_links_df["job_link"].dropna().tolist()

# # for job_link in job_links:
# #     retry_count = 0
# #     max_retries = 2
# #     success = False

# #     while retry_count < max_retries and not success:
# #         try:
# #             print(f"\nProcessing: {job_link}")
# #             driver.get(job_link)
# #             time.sleep(random.uniform(3, 6))

# #             # Handle apply button
# #             try:
# #                 WebDriverWait(driver, 5).until(
# #                     EC.element_to_be_clickable((By.XPATH, "//a[contains(., 'Apply')]"))
# #                 ).click()
# #                 time.sleep(random.uniform(2, 4))
# #             except:
# #                 pass

# #             # Get job details
# #             try:
# #                 company_name = driver.find_element(By.CSS_SELECTOR, "a.main-header-logo img").get_attribute("alt")
# #                 company_name = company_name.replace(" logo", "")
# #             except:
# #                 company_name = "Unknown Company"

# #             try:
# #                 job_title = driver.find_element(By.CSS_SELECTOR, "div.posting-header h2").text.strip()
# #             except:
# #                 job_title = "Unknown Position"

# #             # Fill form
# #             fill_structured_fields(driver)
            
# #             # Upload resume
# #             try:
# #                 WebDriverWait(driver, 5).until(
# #                     EC.presence_of_element_located((By.NAME, "resume"))
# #                 ).send_keys(resume_path)
# #                 print("Resume uploaded")
# #                 time.sleep(1)
# #             except Exception as e:
# #                 print(f"Resume upload failed: {e}")

# #             # Answer custom questions
# #             fill_dynamic_fields(driver)

# #             # Handle CAPTCHA
# #             try:
# #                 iframe = WebDriverWait(driver, 10).until(
# #                     EC.presence_of_element_located((By.XPATH, "//iframe[contains(@src, 'recaptcha')]"))
# #                 )
# #                 driver.switch_to.frame(iframe)
# #                 site_key = driver.find_element(By.CLASS_NAME, "g-recaptcha").get_attribute("data-sitekey")
# #                 driver.switch_to.default_content()

# #                 solver = recaptchaV2Proxyless()
# #                 solver.set_key("YOUR_2CAPTCHA_API_KEY")  # Replace with your key
# #                 solver.set_website_url(job_link)
# #                 solver.set_website_key(site_key)

# #                 captcha_solution = solver.solve_and_return_solution()
# #                 if captcha_solution:
# #                     driver.execute_script(f'document.getElementById("g-recaptcha-response").innerHTML="{captcha_solution}"')
# #                     time.sleep(2)
# #             except:
# #                 pass

# #             # Submit application
# #             submit_button = WebDriverWait(driver, 10).until(
# #                 EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
# #             )
# #             submit_button.click()
# #             time.sleep(random.uniform(5, 8))

# #             # Log success
# #             with open(applications_file, "a", newline="") as file:
# #                 writer = csv.writer(file)
# #                 writer.writerow([
# #                     company_name,
# #                     job_title,
# #                     job_link,
# #                     datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
# #                     "Success",
# #                     str(answers)[:100] + "..."
# #                 ])
# #             print("Application submitted successfully!")
# #             success = True

# #         except Exception as e:
# #             print(f"Error: {str(e)}")
# #             retry_count += 1
# #             if retry_count < max_retries:
# #                 print(f"Retrying ({retry_count}/{max_retries})...")
# #                 time.sleep(random.uniform(10, 20))
# #             else:
# #                 print("Max retries reached")
# #                 with open(applications_file, "a", newline="") as file:
# #                     writer = csv.writer(file)
# #                     writer.writerow([
# #                         company_name,
# #                         job_title,
# #                         job_link,
# #                         datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
# #                         "Failed",
# #                         str(answers)[:100] + "..."
# #                     ])

# # driver.quit()
# # print("\nJob application process completed!")








# import csv
# import undetected_chromedriver as uc
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait, Select
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.chrome.options import Options
# import time
# import pandas as pd
# import os
# import yaml
# import random
# from datetime import datetime
# from fake_useragent import UserAgent

# # 🔹 Lever Base URL
# lever_base_url = "https://jobs.lever.co"

# # 🔹 Load configuration
# with open("config/credentials.yaml", "r") as file:
#     config = yaml.safe_load(file)


# credentials = config["credentials"]
# resume_path = os.path.abspath(config["resume_path"])

# # 🔹 Load answers from CSV
# answers = {}
# try:
#     with open("config/answers.csv", mode="r") as file:
#         reader = csv.DictReader(file)
#         for row in reader:
#             question = row["Question"].strip().lower()
#             answers[question] = row["Answer"].strip()
# except FileNotFoundError:
#     print("❌ Error: 'answers.csv' file not found.")
#     exit()

# # 🔹 Setup browser
# ua = UserAgent()
# chrome_options = Options()
# chrome_options.add_argument(f"user-agent={ua.random}")
# chrome_options.add_argument("--disable-blink-features=AutomationControlled")
# driver = uc.Chrome(options=chrome_options)

# # 🔹 Read job links from CSV
# job_links_file = "jobs/job_links.csv"
# job_links = []

# if os.path.exists(job_links_file):
#     job_links_df = pd.read_csv(job_links_file)
#     for _, row in job_links_df.iterrows():
#         company = row["company"].lower()
#         jobid = row["jobid"]
#         job_link = f"{lever_base_url}/{company}/{jobid}"
#         job_links.append(job_link)

# if not job_links:
#     print("❌ No job links found in the CSV file.")
#     exit()
# else:
#     print(f"✅ Loaded {len(job_links)} job links.")

# # 🔹 Required Fields with CSS Selectors
# FIELD_SELECTORS = {
#     "full_name": ["input[name*='name']", "input[id*='name']"],
#     "first_name": ["input[name*='first']", "input[id*='first']"],
#     "last_name": ["input[name*='last']", "input[id*='last']"],
#     "email": ["input[type='email']", "input[name*='email']", "input[id*='email']"],
#     "phone": ["input[type='tel']", "input[name*='phone']", "input[id*='phone']"],
#     "current_location": ["input[name*='location']", "input[id*='location']"],
#     "current_company": ["input[name*='company']", "input[id*='company']"],
#     "linkedin": ["input[name*='linkedin']", "input[id*='linkedin']", "input[placeholder*='LinkedIn']"],
# }

# def find_input_field(driver, selectors):
#     """Finds an input field using multiple CSS selectors."""
#     for selector in selectors:
#         try:
#             field = WebDriverWait(driver, 3).until(
#                 EC.presence_of_element_located((By.CSS_SELECTOR, selector))
#             )
#             return field
#         except:
#             continue
#     return None

# def fill_structured_fields(driver):
#     """Fills required form fields like name, email, phone, LinkedIn, etc."""
#     try:
#         # Handle Full Name (if applicable)
#         if credentials.get("full_name"):
#             name_field = find_input_field(driver, FIELD_SELECTORS["full_name"])
#             if name_field:
#                 name_field.clear()
#                 name_field.send_keys(credentials["full_name"])
#                 print(f"✅ Filled Full Name: {credentials['full_name']}")
#             else:
#                 first_field = find_input_field(driver, FIELD_SELECTORS["first_name"])
#                 last_field = find_input_field(driver, FIELD_SELECTORS["last_name"])
#                 if first_field and last_field:
#                     first_field.clear()
#                     first_field.send_keys(credentials["first_name"])
#                     last_field.clear()
#                     last_field.send_keys(credentials["last_name"])
#                     print(f"✅ Filled First Name: {credentials['first_name']}, Last Name: {credentials['last_name']}")

#         # Fill other required fields
#         for field, selectors in FIELD_SELECTORS.items():
#             if field not in ["full_name"]:
#                 value = credentials.get(field)
#                 if value:
#                     input_field = find_input_field(driver, selectors)
#                     if input_field:
#                         input_field.clear()
#                         input_field.send_keys(value)
#                         print(f"✅ Filled {field.replace('_', ' ').title()}: {value}")
#                     else:
#                         print(f"⚠ Could not find field: {field}")
#                         time.sleep(40)

#         # 🔹 Dynamically detect submit button types
#         submit_selectors = [
#             "button#btn-submit",  # Button with specific ID
#             "button[data-qa='btn-submit']",  # Button with data attribute
#             "button.postings-btn.template-btn-submit",  # Lever-style submit button
#             "//button[contains(text(),'Submit')]",  # Button with "Submit" text
#             "//button[contains(text(),'Apply')]",  # Button with "Apply" text
#             "//input[@type='submit']",  # Standard input submit
#             "//a[contains(text(),'Submit application')]"  # Link-based submission
#         ]

#         for selector in submit_selectors:
#             try:
#                 if selector.startswith("//"):  # XPath selector
#                     submit_button = WebDriverWait(driver, 5).until(
#                         EC.element_to_be_clickable((By.XPATH, selector))
#                     )
#                 else:  # CSS Selector
#                     submit_button = WebDriverWait(driver, 5).until(
#                         EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
#                     )

#                 submit_button.click()
#                 print(f"✅ Clicked submit button: {selector}")
#                 time.sleep(5)  # Allow submission to process
#                 return  # Stop checking after clicking

#             except:
#                 continue  # If not found, try the next selector



       

#     except Exception as e:
#         print(f"❌ Error filling form: {str(e)}")

# def open_job_and_click_apply(driver, job_link):
#     """Opens job link, clicks 'Apply' button if found, else skips."""
#     try:
#         print(f"\n🚀 Opening job: {job_link}")
#         driver.get(job_link)
#         time.sleep(2)

#         # Possible "Apply" buttons
#         selectors = [
#             "a.postings-btn.template-btn-submit.cerulean",  # Lever "Apply for this job"
#             "//a[contains(text(),'Apply')]",  
#             "//button[contains(text(),'Apply')]",
#             "//a[contains(@href, '/apply')]"
#         ]

#         for selector in selectors:
#             try:
#                 button = WebDriverWait(driver, 3).until(
#                     EC.element_to_be_clickable((By.XPATH, selector)) if selector.startswith("//") 
#                     else EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
#                 )
#                 link = button.get_attribute("href")
#                 driver.get(link) if link else button.click()
#                 print(f"✅ Clicked 'Apply' button: {link if link else 'Direct Click'}")
#                 time.sleep(3)
#                 return
#             except:
#                 continue

#         print("⚠ No 'Apply' button found, skipping.")

#     except Exception as e:
#         print(f"❌ Error: {str(e)}")

# # 🔹 Process job applications
# for job_link in job_links:
#     open_job_and_click_apply(driver, job_link)  # Clicks apply button if needed
#     fill_structured_fields(driver)  # Fills required fields

# driver.quit()
# print("\n🎉 Job application process completed!")





# import csv
# import undetected_chromedriver as uc
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait, Select
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.chrome.options import Options
# import time
# import pandas as pd
# import os
# import yaml
# from fake_useragent import UserAgent

# # 🔹 Lever Base URL
# lever_base_url = "https://jobs.lever.co"

# # 🔹 Load configuration
# with open("config/credentials.yaml", "r") as file:
#     config = yaml.safe_load(file)

# credentials = config["credentials"]
# resume_path = os.path.abspath(config["resume_path"])

# # 🔹 Load answers from CSV
# answers = {}
# try:
#     with open("config/answers.csv", mode="r") as file:
#         reader = csv.DictReader(file)
#         for row in reader:
#             question = row["Question"].strip().lower()
#             answers[question] = row["Answer"].strip()
# except FileNotFoundError:
#     print("❌ Error: 'answers.csv' file not found.")
#     exit()

# # 🔹 Setup browser
# ua = UserAgent()
# chrome_options = Options()
# chrome_options.add_argument(f"user-agent={ua.random}")
# chrome_options.add_argument("--disable-blink-features=AutomationControlled")
# driver = uc.Chrome(options=chrome_options)

# # 🔹 Read job links from CSV
# job_links_file = "jobs/job_links.csv"
# job_links = []

# if os.path.exists(job_links_file):
#     job_links_df = pd.read_csv(job_links_file)
#     for _, row in job_links_df.iterrows():
#         company = row["company"].lower()
#         jobid = row["jobid"]
#         job_link = f"{lever_base_url}/{company}/{jobid}"
#         job_links.append(job_link)

# if not job_links:
#     print("❌ No job links found in the CSV file.")
#     exit()
# else:
#     print(f"✅ Loaded {len(job_links)} job links.")

# # 🔹 Required Fields with CSS Selectors
# FIELD_SELECTORS = {
#     "full_name": ["input[name='name']", "input[id='name']", "input[placeholder*='Full name']", "input[type='text']"],
#     "first_name": ["input[name='first_name']", "input[id='first_name']", "input[placeholder*='First name']"],
#     "last_name": ["input[name='last_name']", "input[id='last_name']", "input[placeholder*='Last name']"],
#     "email": ["input[type='email']", "input[name*='email']", "input[id*='email']"],
#     "phone": ["input[type='tel']", "input[name*='phone']", "input[id*='phone']"],
#     "current_location": ["input[name*='location']", "input[id*='location']"],
#     "current_company": ["input[name*='company']", "input[id*='company']"],
#     "linkedin": ["input[name*='linkedin']", "input[id*='linkedin']", "input[placeholder*='LinkedIn']"],
# }

# def find_input_field(driver, selectors):
#     """Finds an input field using multiple CSS selectors."""
#     for selector in selectors:
#         try:
#             field = WebDriverWait(driver, 3).until(
#                 EC.presence_of_element_located((By.CSS_SELECTOR, selector))
#             )
#             return field
#         except:
#             continue
#     return None

# def open_job_and_click_apply(driver, job_link):
#     """Opens job link, clicks 'Apply' button if found, else skips."""
#     try:
#         print(f"\n🚀 Opening job: {job_link}")
#         driver.get(job_link)
#         time.sleep(2)

#         # Possible "Apply" buttons
#         apply_selectors = [
#             "a.postings-btn.template-btn-submit.cerulean",  
#             "a[href*='/apply']",
#             "button:contains('Apply')",
#             "a:contains('Apply')",
#         ]

#         for selector in apply_selectors:
#             try:
#                 button = WebDriverWait(driver, 3).until(
#                     EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
#                 )
#                 button.click()
#                 print(f"✅ Clicked 'Apply' button: {selector}")
#                 time.sleep(3)
#                 return
#             except:
#                 continue

#         print("⚠ No 'Apply' button found, skipping.")

#     except Exception as e:
#         print(f"❌ Error: {str(e)}")

# def fill_form_and_submit(driver):
#     """Fills required fields, answers custom questions, clicks submit, then waits before moving to the next job."""
#     try:
#         print("\n🚀 Filling the form...")

#         # 🔹 Handle Full Name properly
#         full_name_field = find_input_field(driver,"Full name")
#         if full_name_field:
#             full_name_field.clear()
#             full_name_field.send_keys(credentials["full_name"])
#             print(f"✅ Filled Full Name: {credentials['full_name']}")
#         else:
#             print("❌ ERROR: Could not find Full Name field.")
        
#         # (Optional) Handle First and Last Name separately if needed
#         first_name_field = find_input_field(driver, "First name")
#         last_name_field = find_input_field(driver, "Last name")
#         if first_name_field and last_name_field:
#             first_name_field.clear()
#             first_name_field.send_keys(credentials["first_name"])
#             last_name_field.clear()
#             last_name_field.send_keys(credentials["last_name"])
#             print(f"✅ Filled First Name: {credentials['first_name']}, Last Name: {credentials['last_name']}")

#         # 🔹 Fill other required fields
#         for field, selectors in FIELD_SELECTORS.items():
#             if field not in ["full_name", "first_name", "last_name"]:
#                 value = credentials.get(field)
#                 if value:
#                     input_field = find_input_field(driver, selectors)
#                     if input_field:
#                         input_field.clear()
#                         input_field.send_keys(value)
#                         print(f"✅ Filled {field.replace('_', ' ').title()}: {value}")

#         # 🔹 Wait 10 seconds before submission (change to 60 for production)
#         print("🛑 Waiting for 10 seconds before submitting...")
#         time.sleep(10)

#         # 🔹 Click submit button dynamically
#         submit_selectors = [
#             "button#btn-submit",
#             "button[data-qa='btn-submit']",
#             "button.postings-btn.template-btn-submit",
#             "button:contains('Submit')",
#             "button:contains('Apply')",
#             "input[type='submit']",
#             "a:contains('Submit application')"
#         ]

#         for selector in submit_selectors:
#             try:
#                 submit_button = WebDriverWait(driver, 5).until(
#                     EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
#                 )
#                 submit_button.click()
#                 print(f"✅ Clicked submit button: {selector}")
#                 time.sleep(5)
#                 return
#             except:
#                 continue  

#         print("⚠ No submit button found, skipping submission.")

#     except Exception as e:
#         print(f"❌ Error filling form: {str(e)}")

# # 🔹 Process job applications
# for job_link in job_links:
#     open_job_and_click_apply(driver, job_link)
#     fill_form_and_submit(driver)

# driver.quit()
# print("\n🎉 Job application process completed!")




# import csv
# import undetected_chromedriver as uc
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait, Select
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.chrome.options import Options
# import time
# import pandas as pd
# import os
# import yaml
# import random
# from datetime import datetime
# from fake_useragent import UserAgent
# from anticaptchaofficial.recaptchav2proxyless import recaptchaV2Proxyless

# # Load configuration
# with open("config/credentials.yaml", "r") as file:
#     config = yaml.safe_load(file)

# credentials = config["credentials"]
# resume_path = os.path.abspath(config["resume_path"])

# # Load answers
# answers = {}
# try:
#     with open("config/answers.csv", mode="r") as file:
#         reader = csv.DictReader(file)
#         for row in reader:
#             question = row["Question"].strip().lower()
#             answers[question] = row["Answer"].strip()
# except FileNotFoundError:
#     print("Error: 'answers.csv' file not found.")
#     exit()

# # Setup browser
# ua = UserAgent()
# chrome_options = Options()
# chrome_options.add_argument(f"user-agent={ua.random}")
# chrome_options.add_argument("--disable-blink-features=AutomationControlled")
# driver = uc.Chrome(options=chrome_options)

# # Application tracking
# applications_file = "applications.csv"
# if not os.path.exists(applications_file):
#     with open(applications_file, "w", newline="") as file:
#         writer = csv.writer(file)
#         writer.writerow(["Company", "Job Title", "Application Link", "Date Applied", "Status", "Questions Answered"])

# def fill_structured_fields(driver):
#     """Fill standard form fields like name, email, etc."""
#     structured_fields = {
#         "first_name": ("//label[contains(., 'First Name')]/following-sibling::div//input", credentials.get("first_name")),
#         "last_name": ("//label[contains(., 'Last Name')]/following-sibling::div//input", credentials.get("last_name")),
#         "email": ("//label[contains(., 'Email')]/following-sibling::div//input", credentials.get("email")),
#         "phone": ("//label[contains(., 'Phone')]/following-sibling::div//input", credentials.get("phone")),
#         "address": ("//label[contains(., 'Address')]/following-sibling::div//input", credentials.get("address")),
#         "city": ("//label[contains(., 'City')]/following-sibling::div//input", credentials.get("city")),
#         "state": ("//label[contains(., 'State')]/following-sibling::div//select", credentials.get("state")),
#         "zip": ("//label[contains(., 'Zip')]/following-sibling::div//input", credentials.get("zip")),
#     }

#     for field, (xpath, value) in structured_fields.items():
#         if value:
#             try:
#                 element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, xpath)))
#                 element.clear()
#                 element.send_keys(value)
#                 print(f"Filled {field.replace('_', ' ').title()}")
#                 time.sleep(random.uniform(0.5, 1.5))
#             except Exception as e:
#                 print(f"Could not fill {field.replace('_', ' ').title()}: {e}")

# def handle_field_types(container, answer):
#     """Handle different types of form fields"""
#     # Try textarea
#     try:
#         textarea = container.find_element(By.TAG_NAME, "textarea")
#         textarea.clear()
#         for char in answer:
#             textarea.send_keys(char)
#             time.sleep(random.uniform(0.02, 0.1))
#         print(f"Filled textarea with: {answer[:50]}...")
#         return True
#     except:
#         pass

#     # Try text input
#     try:
#         input_field = container.find_element(By.XPATH, ".//input[@type='text']")
#         input_field.clear()
#         input_field.send_keys(answer)
#         print(f"Filled text input: {answer[:50]}...")
#         return True
#     except:
#         pass

#     # Handle radio buttons/checkboxes
#     try:
#         options = container.find_elements(By.XPATH, ".//input[@type='radio'] | .//input[@type='checkbox']")
#         if options:
#             for option in options:
#                 label = container.find_element(By.XPATH, f"//label[@for='{option.get_attribute('id')}']")
#                 if label.text.strip().lower() == answer.lower() or option.get_attribute("value").lower() == answer.lower():
#                     if not option.is_selected():
#                         option.click()
#                         print(f"Selected option: {answer}")
#                         return True
#             print(f"No matching option found for: {answer}")
#             return False
#     except:
#         pass

#     # Handle dropdowns
#     try:
#         select = container.find_element(By.TAG_NAME, "select")
#         dropdown = Select(select)
#         try:
#             dropdown.select_by_visible_text(answer)
#             print(f"Selected dropdown: {answer}")
#             return True
#         except:
#             try:
#                 dropdown.select_by_value(answer)
#                 print(f"Selected dropdown by value: {answer}")
#                 return True
#             except:
#                 print(f"No dropdown option matched: {answer}")
#                 return False
#     except:
#         pass

#     # Handle acknowledgements
#     if "acknowledge" in answer.lower():
#         try:
#             checkbox = container.find_element(By.XPATH, ".//input[@type='checkbox']")
#             if not checkbox.is_selected():
#                 checkbox.click()
#                 print("Checked acknowledgement box")
#                 return True
#         except:
#             pass

#     print(f"Could not find suitable field for: {answer}")
#     return False

# def fill_dynamic_fields(driver):
#     """Answer custom questions from CSV"""
#     for question_text, answer in answers.items():
#         try:
#             print(f"\nAttempting: {question_text[:50]}...")
            
#             # Normalize question text
#             clean_question = question_text.lower().replace('?', '').replace(':', '').strip()
            
#             # Find question container
#             container = WebDriverWait(driver, 10).until(
#                 EC.presence_of_element_located((By.XPATH, 
#                     f"//div[contains(@class, 'application-question')][.//*[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{clean_question}')]]"
#                 ))
#             )
            
#             # Scroll to element
#             driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", container)
#             time.sleep(0.5)
            
#             # Handle the field
#             if not handle_field_types(container, answer):
#                 print(f"Failed to answer: {question_text[:50]}...")
            
#         except Exception as e:
#             print(f"Question not found: {question_text[:50]}... - {str(e)}")

# # Process job links
# job_links_df = pd.read_csv("jobs/job_links.csv")
# job_links = job_links_df["job_link"].dropna().tolist()

# for job_link in job_links:
#     retry_count = 0
#     max_retries = 2
#     success = False

#     while retry_count < max_retries and not success:
#         try:
#             print(f"\nProcessing: {job_link}")
#             driver.get(job_link)
#             time.sleep(random.uniform(3, 6))

#             # Handle apply button
#             try:
#                 WebDriverWait(driver, 5).until(
#                     EC.element_to_be_clickable((By.XPATH, "//a[contains(., 'Apply')]"))
#                 ).click()
#                 time.sleep(random.uniform(2, 4))
#             except:
#                 pass

#             # Get job details
#             try:
#                 company_name = driver.find_element(By.CSS_SELECTOR, "a.main-header-logo img").get_attribute("alt")
#                 company_name = company_name.replace(" logo", "")
#             except:
#                 company_name = "Unknown Company"

#             try:
#                 job_title = driver.find_element(By.CSS_SELECTOR, "div.posting-header h2").text.strip()
#             except:
#                 job_title = "Unknown Position"

#             # Fill form
#             fill_structured_fields(driver)
            
#             # Upload resume
#             try:
#                 WebDriverWait(driver, 5).until(
#                     EC.presence_of_element_located((By.NAME, "resume"))
#                 ).send_keys(resume_path)
#                 print("Resume uploaded")
#                 time.sleep(1)
#             except Exception as e:
#                 print(f"Resume upload failed: {e}")

#             # Answer custom questions
#             fill_dynamic_fields(driver)

#             # Handle CAPTCHA
#             try:
#                 iframe = WebDriverWait(driver, 10).until(
#                     EC.presence_of_element_located((By.XPATH, "//iframe[contains(@src, 'recaptcha')]"))
#                 )
#                 driver.switch_to.frame(iframe)
#                 site_key = driver.find_element(By.CLASS_NAME, "g-recaptcha").get_attribute("data-sitekey")
#                 driver.switch_to.default_content()

#                 solver = recaptchaV2Proxyless()
#                 solver.set_key("YOUR_2CAPTCHA_API_KEY")  # Replace with your key
#                 solver.set_website_url(job_link)
#                 solver.set_website_key(site_key)

#                 captcha_solution = solver.solve_and_return_solution()
#                 if captcha_solution:
#                     driver.execute_script(f'document.getElementById("g-recaptcha-response").innerHTML="{captcha_solution}"')
#                     time.sleep(2)
#             except:
#                 pass

#             # Submit application
#             submit_button = WebDriverWait(driver, 10).until(
#                 EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
#             )
#             submit_button.click()
#             time.sleep(random.uniform(5, 8))

#             # Log success
#             with open(applications_file, "a", newline="") as file:
#                 writer = csv.writer(file)
#                 writer.writerow([
#                     company_name,
#                     job_title,
#                     job_link,
#                     datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#                     "Success",
#                     str(answers)[:100] + "..."
#                 ])
#             print("Application submitted successfully!")
#             success = True

#         except Exception as e:
#             print(f"Error: {str(e)}")
#             retry_count += 1
#             if retry_count < max_retries:
#                 print(f"Retrying ({retry_count}/{max_retries})...")
#                 time.sleep(random.uniform(10, 20))
#             else:
#                 print("Max retries reached")
#                 with open(applications_file, "a", newline="") as file:
#                     writer = csv.writer(file)
#                     writer.writerow([
#                         company_name,
#                         job_title,
#                         job_link,
#                         datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#                         "Failed",
#                         str(answers)[:100] + "..."
#                     ])

# driver.quit()
# print("\nJob application process completed!")







# import csv
# import undetected_chromedriver as uc
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait, Select
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.chrome.options import Options
# import time
# import pandas as pd
# import os
# import yaml
# from fake_useragent import UserAgent

# # 🔹 Lever Base URL
# lever_base_url = "https://jobs.lever.co"

# # 🔹 Load configuration
# with open("config/credentials.yaml", "r") as file:
#     config = yaml.safe_load(file)

# credentials = config["credentials"]
# resume_path = os.path.abspath(config["resume_path"])

# # 🔹 Load answers from CSV
# answers = {}
# try:
#     with open("config/answers.csv", mode="r") as file:
#         reader = csv.DictReader(file)
#         for row in reader:
#             question = row["Question"].strip().lower()
#             answers[question] = row["Answer"].strip()
# except FileNotFoundError:
#     print("❌ Error: 'answers.csv' file not found.")
#     exit()

# # 🔹 Setup browser
# ua = UserAgent()
# chrome_options = Options()
# chrome_options.add_argument(f"user-agent={ua.random}")
# chrome_options.add_argument("--disable-blink-features=AutomationControlled")
# driver = uc.Chrome(options=chrome_options)

# # 🔹 Read job links from CSV
# job_links_file = "jobs/job_links.csv"
# job_links = []

# if os.path.exists(job_links_file):
#     job_links_df = pd.read_csv(job_links_file)
#     for _, row in job_links_df.iterrows():
#         company = row["company"].lower()
#         jobid = row["jobid"]
#         job_link = f"{lever_base_url}/{company}/{jobid}"
#         job_links.append(job_link)

# if not job_links:
#     print("❌ No job links found in the CSV file.")
#     exit()
# else:
#     print(f"✅ Loaded {len(job_links)} job links.")

# # 🔹 Required Fields with CSS Selectors
# FIELD_SELECTORS = {
#     "full_name": ["input[name='name']", "input[id='name']", "input[placeholder*='Full name']", "input[type='text']"],
#     "first_name": ["input[name='first_name']", "input[id='first_name']", "input[placeholder*='First name']"],
#     "last_name": ["input[name='last_name']", "input[id='last_name']", "input[placeholder*='Last name']"],
#     "email": ["input[type='email']", "input[name*='email']", "input[id*='email']"],
#     "phone": ["input[type='tel']", "input[name*='phone']", "input[id*='phone']"],
#     "current_location": ["input[name*='location']", "input[id*='location']"],
#     "current_company": ["input[name*='company']", "input[id*='company']"],
#     "linkedin": ["input[name*='linkedin']", "input[id*='linkedin']", "input[placeholder*='LinkedIn']"],
# }

# def find_input_field(driver, selectors):
#     """Finds an input field using multiple CSS selectors."""
#     for selector in selectors:
#         try:
#             field = WebDriverWait(driver, 3).until(
#                 EC.presence_of_element_located((By.CSS_SELECTOR, selector))
#             )
#             return field
#         except:
#             continue
#     return None

# def open_job_and_click_apply(driver, job_link):
#     """Opens job link, clicks 'Apply' button if found, else skips."""
#     try:
#         print(f"\n🚀 Opening job: {job_link}")
#         driver.get(job_link)
#         time.sleep(2)

#         # Possible "Apply" buttons
#         apply_selectors = [
#             "a.postings-btn.template-btn-submit.cerulean",  
#             "a[href*='/apply']",
#             "button:contains('Apply')",
#             "a:contains('Apply')",
#         ]

#         for selector in apply_selectors:
#             try:
#                 button = WebDriverWait(driver, 3).until(
#                     EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
#                 button.click()
#                 print(f"✅ Clicked 'Apply' button: {selector}")
#                 time.sleep(3)
#                 return
#             except:
#                 continue

#         print("⚠ No 'Apply' button found, skipping.")

#     except Exception as e:
#         print(f"❌ Error: {str(e)}")

# def fill_form_and_submit(driver):
#     """Fills required fields, answers custom questions, clicks submit, then waits before moving to the next job."""
#     try:
#         print("\n🚀 Filling the form...")

#         # 🔹 Handle Full Name properly
#         full_name_field = find_input_field(driver, FIELD_SELECTORS["full_name"])
#         if full_name_field:
#             full_name_field.clear()
#             full_name_field.send_keys(credentials["full_name"])
#             print(f"✅ Filled Full Name: {credentials['full_name']}")
#         else:
#             print("❌ ERROR: Could not find Full Name field.")
        
#         # (Optional) Handle First and Last Name separately if needed
#         first_name_field = find_input_field(driver, FIELD_SELECTORS["first_name"])
#         last_name_field = find_input_field(driver, FIELD_SELECTORS["last_name"])
#         if first_name_field and last_name_field:
#             first_name_field.clear()
#             first_name_field.send_keys(credentials["first_name"])
#             last_name_field.clear()
#             last_name_field.send_keys(credentials["last_name"])
#             print(f"✅ Filled First Name: {credentials['first_name']}, Last Name: {credentials['last_name']}")

#         # 🔹 Fill other required fields
#         for field, selectors in FIELD_SELECTORS.items():
#             if field not in ["full_name", "first_name", "last_name"]:
#                 value = credentials.get(field)
#                 if value:
#                     input_field = find_input_field(driver, selectors)
#                     if input_field:
#                         input_field.clear()
#                         input_field.send_keys(value)
#                         print(f"✅ Filled {field.replace('_', ' ').title()}: {value}")

#         # 🔹 Wait 10 seconds before submission (change to 60 for production)
        
        

#         # 🔹 Click submit button dynamically
#         submit_selectors = [
#             "button#btn-submit",
#             "button[data-qa='btn-submit']",
#             "button.postings-btn.template-btn-submit",
#             "button:contains('Submit')",
#             "button:contains('Apply')",
#             "input[type='submit']",
#             "a:contains('Submit application')"
#         ]

#         for selector in submit_selectors:
#             try:
#                 submit_button = WebDriverWait(driver, 5).until(
#                     EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
#                 submit_button.click()
#                 print(f"✅ Clicked submit button: {selector}")
#                 time.sleep(5)
#                 return
#             except:
#                 continue  

#         print("⚠ No submit button found, skipping submission.")

#     except Exception as e:
#         print(f"❌ Error filling form: {str(e)}")

# # 🔹 Process job applications
# for job_link in job_links:
#     open_job_and_click_apply(driver, job_link)
#     fill_form_and_submit(driver)

# driver.quit()
# print("\n🎉 Job application process completed!")





# import csv
# import undetected_chromedriver as uc
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait, Select
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.chrome.options import Options
# import time
# import pandas as pd
# import os
# import yaml
# from fake_useragent import UserAgent

# # 🔹 Lever Base URL
# lever_base_url = "https://jobs.lever.co"

# # 🔹 Load configuration
# with open("config/credentials.yaml", "r") as file:
#     config = yaml.safe_load(file)

# credentials = config["credentials"]
# resume_path = os.path.abspath(config["resume_path"])

# # 🔹 Load answers from CSV
# answers = {}
# try:
#     with open("config/answers.csv", mode="r") as file:
#         reader = csv.DictReader(file)
#         for row in reader:
#             question = row["Question"].strip().lower()
#             answers[question] = row["Answer"].strip()
# except FileNotFoundError:
#     print("❌ Error: 'answers.csv' file not found.")
#     exit()

# # 🔹 Setup browser
# ua = UserAgent()
# chrome_options = Options()
# chrome_options.add_argument(f"user-agent={ua.random}")
# chrome_options.add_argument("--disable-blink-features=AutomationControlled")
# driver = uc.Chrome(options=chrome_options)

# # 🔹 Read job links from CSV
# job_links_file = "jobs/job_links.csv"
# job_links = []

# if os.path.exists(job_links_file):
#     job_links_df = pd.read_csv(job_links_file)
#     for _, row in job_links_df.iterrows():
#         company = row["company"].lower()
#         jobid = row["jobid"]
#         job_link = f"{lever_base_url}/{company}/{jobid}"
#         job_links.append(job_link)

# if not job_links:
#     print("❌ No job links found in the CSV file.")
#     exit()
# else:
#     print(f"✅ Loaded {len(job_links)} job links.")

# # 🔹 Required Fields with CSS Selectors
# FIELD_SELECTORS = {
#     "full_name": ["input[name='name']", "input[id='name']", "input[placeholder*='Full name']", "input[type='text']"],
#     "email": ["input[type='email']", "input[name*='email']", "input[id*='email']"],
#     "phone": ["input[type='tel']", "input[name*='phone']", "input[id*='phone']"],
#     "linkedin": ["input[name*='linkedin']", "input[id*='linkedin']", "input[placeholder*='LinkedIn']"],
#     "resume": ["input[type='file']", "input[name*='resume']", "input[id*='resume']"]
# }

# def find_input_field(driver, selectors):
#     """Finds an input field using multiple CSS selectors."""
#     for selector in selectors:
#         try:
#             field = WebDriverWait(driver, 3).until(
#                 EC.presence_of_element_located((By.CSS_SELECTOR, selector))
#             )
#             return field
#         except:
#             continue
#     return None

# def open_job_and_click_apply(driver, job_link):
#     """Opens job link, clicks 'Apply' button if found, else skips."""
#     try:
#         print(f"\n🚀 Opening job: {job_link}")
#         driver.get(job_link)
#         time.sleep(2)

#         # Possible "Apply" buttons
#         apply_selectors = [
#             "a.postings-btn.template-btn-submit.cerulean",  
#             "a[href*='/apply']",
#             "button:contains('Apply')",
#             "a:contains('Apply')",
#         ]

#         for selector in apply_selectors:
#             try:
#                 button = WebDriverWait(driver, 3).until(
#                     EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
#                 button.click()
#                 print(f"✅ Clicked 'Apply' button")
#                 time.sleep(3)
#                 return
#             except:
#                 continue

#         print("⚠ No 'Apply' button found, skipping.")

#     except Exception as e:
#         print(f"❌ Error: {str(e)}")

# def fill_form_and_submit(driver):
#     """Fills required fields, answers custom questions, uploads resume and LinkedIn, then submits."""
#     try:
#         print("\n🚀 Filling the form...")

#         # 🔹 Fill required fields
#         for field, selectors in FIELD_SELECTORS.items():
#             value = credentials.get(field)
#             if value:
#                 input_field = find_input_field(driver, selectors)
#                 if input_field:
#                     input_field.clear()
#                     if field == "resume":
#                         input_field.send_keys(resume_path)
#                         print(f"✅ Uploaded Resume: {resume_path}")
#                     else:
#                         input_field.send_keys(value)
#                         print(f"✅ Filled {field.replace('_', ' ').title()}: {value}")

#         # 🔹 Answer custom questions dynamically
#         questions = driver.find_elements(By.CSS_SELECTOR, "label")  
#         for question in questions:
#             try:
#                 q_text = question.text.strip().lower()
#                 if q_text in answers:
#                     answer = answers[q_text]

#                     # Find the input field next to the label
#                     parent = question.find_element(By.XPATH, "./..")
#                     input_field = parent.find_element(By.TAG_NAME, "input")

#                     if input_field.get_attribute("type") == "text":
#                         input_field.clear()
#                         input_field.send_keys(answer)
#                     elif input_field.get_attribute("type") == "radio":
#                         radio_button = parent.find_element(By.XPATH, f".//input[@value='{answer}']")
#                         radio_button.click()
#                     elif input_field.get_attribute("type") == "checkbox":
#                         checkbox = parent.find_element(By.XPATH, f".//input[@value='{answer}']")
#                         checkbox.click()
#                     elif input_field.tag_name == "textarea":
#                         input_field.clear()
#                         input_field.send_keys(answer)
#                     elif input_field.tag_name == "select":
#                         dropdown = Select(input_field)
#                         dropdown.select_by_visible_text(answer)
                    
#                     print(f"✅ Answered: {q_text} -> {answer}")
#             except Exception as e:
#                 print(f"⚠ Could not answer question: {q_text}")

#         # 🔹 Click submit button dynamically
#         submit_selectors = [
#             "button#btn-submit",
#             "button[data-qa='btn-submit']",
#             "button.postings-btn.template-btn-submit",
#             "button:contains('Submit')",
#             "button:contains('Apply')",
#             "input[type='submit']",
#             "a:contains('Submit application')"
#         ]

#         for selector in submit_selectors:
#             try:
#                 submit_button = WebDriverWait(driver, 5).until(
#                     EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
#                 submit_button.click()
#                 print(f"✅ Clicked submit button")
#                 time.sleep(5)
#                 return
#             except:
#                 continue  

#         print("⚠ No submit button found, skipping submission.")

#     except Exception as e:
#         print(f"❌ Error filling form: {str(e)}")

# # 🔹 Process job applications
# for job_link in job_links:
#     open_job_and_click_apply(driver, job_link)
#     fill_form_and_submit(driver)

# driver.quit()
# print("\n🎉 Job application process completed!")


### taken as a referenmce 


# import csv
# import undetected_chromedriver as uc
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait, Select
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.chrome.options import Options
# import time
# import pandas as pd
# import os
# import yaml
# from fake_useragent import UserAgent

# # 🔹 Lever Base URL
# lever_base_url = "https://jobs.lever.co"

# # 🔹 Load configuration
# with open("config/credentials.yaml", "r") as file:
#     config = yaml.safe_load(file)


# resume_path = os.path.abspath(config["resume_path"])

# # 🔹 Load answers from CSV
# answers = {}
# try:
#     with open("config/answers.csv", mode="r") as file:
#         reader = csv.DictReader(file)
#         for row in reader:
#             question = row["Question"].strip().lower()
#             answers[question] = row["Answer"].strip()
# except FileNotFoundError:
#     print("❌ Error: 'answers.csv' file not found.")
#     exit()

# # 🔹 Setup browser
# ua = UserAgent()
# chrome_options = Options()
# chrome_options.add_argument(f"user-agent={ua.random}")
# chrome_options.add_argument("--disable-blink-features=AutomationControlled")
# driver = uc.Chrome(options=chrome_options)

# # 🔹 Read job links from CSV
# job_links_file = "jobs/job_links.csv"
# job_links = []

# if os.path.exists(job_links_file):
#     job_links_df = pd.read_csv(job_links_file)
#     for _, row in job_links_df.iterrows():
#         company = row["company"].lower()
#         jobid = row["jobid"]
#         job_link = f"{lever_base_url}/{company}/{jobid}"
#         job_links.append(job_link)

# if not job_links:
#     print("❌ No job links found in the CSV file.")
#     exit()
# else:
#     print(f"✅ Loaded {len(job_links)} job links.")

# # 🔹 Required Fields with CSS Selectors
# FIELD_SELECTORS = {
#     "full_name": ["input[name='name']", "input[id='name']", "input[placeholder*='Full name']", "input[type='text']"],
#     "email": ["input[type='email']", "input[name*='email']", "input[id*='email']"],
#     "phone": ["input[type='tel']", "input[name*='phone']", "input[id*='phone']"],
#     "linkedin": ["input[name*='linkedin']", "input[id*='linkedin']", "input[placeholder*='LinkedIn']"],
#     "resume": ["input[type='file']", "input[name*='resume']", "input[id*='resume']"]
# }

# def find_input_field(driver, selectors):
#     """Finds an input field using multiple CSS selectors."""
#     for selector in selectors:
#         try:
#             field = WebDriverWait(driver, 3).until(
#                 EC.presence_of_element_located((By.CSS_SELECTOR, selector))
#             )
#             return field
#         except:
#             continue
#     return None

# def open_job_and_click_apply(driver, job_link):
#     """Opens job link, clicks 'Apply' button if found, else skips."""
#     try:
#         print(f"\n🚀 Opening job: {job_link}")
#         driver.get(job_link)
#         time.sleep(2)

#         # Possible "Apply" buttons
#         apply_selectors = [
#             "a.postings-btn.template-btn-submit.cerulean",  
#             "a[href*='/apply']",
#             "button[class*='apply']", 
#             "a[class*='apply']",
#         ]

#         for selector in apply_selectors:
#             try:
#                 button = WebDriverWait(driver, 3).until(
#                     EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
#                 button.click()
#                 print(f"✅ Clicked 'Apply' button")
#                 time.sleep(3)
#                 return
#             except:
#                 continue

#         print("⚠ No 'Apply' button found, skipping.")

#     except Exception as e:
#         print(f"❌ Error: {str(e)}")

# def fill_form_and_submit(driver):
#     """Fills required fields, answers custom questions, uploads resume and LinkedIn, then submits."""
#     try:
#         print("\n🚀 Filling the form...")

#         # 🔹 Fill required fields
#         for field, selectors in FIELD_SELECTORS.items():
#             value = credentials.get(field)
#             if value:
#                 input_field = find_input_field(driver, selectors)
#                 if input_field:
#                     input_field.clear()
#                     if field == "resume":
#                         input_field.send_keys(resume_path)
#                         print(f"✅ Uploaded Resume: {resume_path}")
#                     else:
#                         input_field.send_keys(value)
#                         print(f"✅ Filled {field.replace('_', ' ').title()}: {value}")

#         # 🔹 Answer custom questions dynamically
#         question_selectors = ["label"]  # Target all labels for questions
#         question_fields = driver.find_elements(By.CSS_SELECTOR, "label, div.question, span, p ".join(question_selectors))

#         for question in question_fields:
#             try:
#                 q_text = question.text.strip().lower()
#                 if q_text in answers:
#                     answer = answers[q_text]

#                     # Find the corresponding input field using CSS selectors
#                     parent = question.find_element(By.XPATH, "./..")
#                     # input_field = parent.find_element(By.CSS_SELECTOR, "input, textarea, select")
#                     input_field = question.find_element(By.XPATH, "following-sibling::input | following-sibling::textarea | following-sibling::select")


#                     if input_field.tag_name == "input":
#                         input_type = input_field.get_attribute("type")
#                         if input_type == "text":
#                             input_field.clear()
#                             input_field.send_keys(answer)
#                         elif input_type in ["radio", "checkbox"]:
#                             option_selector = f"input[value='{answer}']"
#                             option_field = parent.find_element(By.CSS_SELECTOR, option_selector)
#                             option_field.click()
#                     elif input_field.tag_name == "textarea":
#                         input_field.clear()
#                         input_field.send_keys(answer)
#                     elif input_field.tag_name == "select":
#                         dropdown = Select(input_field)
#                         dropdown.select_by_visible_text(answer)

#                     print(f"✅ Answered: {q_text} -> {answer}")
#             except Exception as e:
#                 print(f"⚠ Could not answer question: {q_text}")

#         # 🔹 Click submit button dynamically
#         submit_selectors = [
#             "button#btn-submit",
#             "button[data-qa='btn-submit']",
#             "button.postings-btn.template-btn-submit",
#             "button[class*='submit']", 
#             "input[type='submit']",
#             "a[class*='submit']"
#         ]

#         for selector in submit_selectors:
#             try:
#                 submit_button = WebDriverWait(driver, 5).until(
#                     EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
#                 submit_button.click()
#                 print(f" Clicked submit button")
#                 time.sleep(5)
#                 return
#             except:
#                 continue  

#         print("⚠ No submit button found, skipping submission.")

#     except Exception as e:
#         print(f" Error filling form: {str(e)}")

# # 🔹 Process job applications
# for job_link in job_links:
#     open_job_and_click_apply(driver, job_link)
#     fill_form_and_submit(driver)

# driver.quit()
# print("\n🎉 Job application process completed!")







#updated 



# ##

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
from fake_useragent import UserAgent

# 🔹 Lever Base URL
lever_base_url = "https://jobs.lever.co"

# 🔹 Load configuration from YAML file
def load_config(file_location):
    with open(file_location, 'r') as stream:
        try:
            parameters = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            raise exc

    # Validate required fields
    assert parameters.get("full_name") is not None, "Full name is missing in YAML file."
    assert parameters.get("email") is not None, "Email is missing in YAML file."
    assert parameters.get("phone") is not None, "Phone number is missing in YAML file."
    assert parameters.get("linkedin") is not None, "LinkedIn URL is missing in YAML file."
    assert parameters.get("resume_path") is not None, "Resume path is missing in YAML file."

  

    # Extract credentials
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
        "linkedin": parameters.get("linkedin", ""),
        "github": parameters.get("github", ""),
        "portfolio": parameters.get("portfolio", ""),
        "work_status": parameters.get("work_status", "")
    }

    # Add optional fields to credentials
    credentials.update(optional_fields)
    return credentials

# 🔹 Load credentials from YAML
credentials = load_config("config/credentials.yaml")

# 🔹 Load answers from CSV
answers = {}
try:
    with open("config/answers.csv", mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            question = row["Question"].strip().lower()
            answers[question] = row["Answer"].strip()
except FileNotFoundError:
    print(" Error: 'answers.csv' file not found.")
    exit()

# 🔹 Setup browser
ua = UserAgent()
chrome_options = Options()
chrome_options.add_argument(f"user-agent={ua.random}")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
driver = uc.Chrome(options=chrome_options)

# 🔹 Read job links from CSV
job_links_file = "jobs/job_links.csv"
job_links = []

if os.path.exists(job_links_file):
    job_links_df = pd.read_csv(job_links_file)
    for _, row in job_links_df.iterrows():
        company = row["company"].lower()
        jobid = row["jobid"]
        job_link = f"{lever_base_url}/{company}/{jobid}"
        job_links.append(job_link)

if not job_links:
    print(" No job links found in the CSV file.")
    exit()
else:
    print(f" Loaded {len(job_links)} job links.")

# 🔹 Required Fields with CSS Selectors
FIELD_SELECTORS = {
    "full_name": ["input[name='name']", "input[id='name']", "input[placeholder*='Full name']", "input[type='text']"],
    "email": ["input[type='email']", "input[name*='email']", "input[id*='email']"],
    "phone": ["input[type='tel']", "input[name*='phone']", "input[id*='phone']"],
    "linkedin": ["input[name*='linkedin']", "input[id*='linkedin']", "input[placeholder*='LinkedIn']"],
    "resume": ["input[type='file']", "input[name*='resume']", "input[id*='resume']"],
    #"current_location": ["input[name*='location']", "input[id*='location']","input[placeholder*='Current location']","input[placeholder*='City, State']"],
    #"current_company": ["input[name*='company']", "input[id*='company']", "input[placeholder*='Current company']", "input[placeholder*='Employer']"],
    # "linkedin": ["input[name*='linkedin']", "input[id*='linkedin']", "input[placeholder*='LinkedIn']", "input[placeholder*='LinkedIn URL']"],
    # "github": ["input[name*='github']", "input[id*='github']", "input[placeholder*='GitHub']", "input[placeholder*='GitHub URL']"],
    # "portfolio": ["input[name*='portfolio']", "input[id*='portfolio']", "input[placeholder*='Portfolio']", "input[placeholder*='Portfolio URL']"],
    # "work_status": ["select[name*='work_status']", "select[id*='work_status']", "input[name*='work_status']", "input[id*='work_status']"]
}


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
    """Opens job link, clicks 'Apply' button if found, else skips."""
    try:
        print(f"\n🚀 Opening job: {job_link}")
        driver.get(job_link)
        time.sleep(2)

        # Possible "Apply" buttons
        apply_selectors = [
            "a.postings-btn.template-btn-submit.cerulean",  
            "a[href*='/apply']",
            "button[class*='apply']", 
            "a[class*='apply']",
        ]

        for selector in apply_selectors:
            try:
                button = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                button.click()
                print(f"✅ Clicked 'Apply' button")
                time.sleep(10)
                return
            except:
                continue

        print("⚠ No 'Apply' button found, skipping.")

    except Exception as e:
        print(f"❌ Error: {str(e)}")

def fill_form_and_submit(driver):
    """Fills required fields, answers custom questions, uploads resume and LinkedIn, then submits."""
    try:
        print("\n Filling the form...")

        # 🔹 Fill required fields
        for field, selectors in FIELD_SELECTORS.items():
            value = credentials.get(field)
            if value:
                input_field = find_input_field(driver, selectors)
                if input_field:
                    input_field.clear()
                    if field == "resume":
                        input_field.send_keys(credentials["resume"])
                        print(f" Uploaded Resume: {credentials['resume']}")
                    else:
                        input_field.send_keys(value)
                        print(f" Filled {field.replace('_', ' ').title()}: {value}")

        # 🔹 Answer custom questions dynamically
        question_selectors = ["label"]  # Target all labels for questions
        question_fields = driver.find_elements(By.CSS_SELECTOR, "label, div.question, span, p ".join(question_selectors))

        for question in question_fields:
            try:
                q_text = question.text.strip().lower()
                if q_text in answers:
                    answer = answers[q_text]

                    # Find the corresponding input field using CSS selectors
                    parent = question.find_element(By.XPATH, "./..")
                    input_field = question.find_element(By.XPATH, "following-sibling::input | following-sibling::textarea | following-sibling::select")

                    if input_field.tag_name == "input":
                        input_type = input_field.get_attribute("type")
                        if input_type == "text":
                            input_field.clear()
                            input_field.send_keys(answer)
                        elif input_type in ["radio", "checkbox"]:
                            option_selector = f"input[value='{answer}']"
                            option_field = parent.find_element(By.CSS_SELECTOR, option_selector)
                            option_field.click()
                    elif input_field.tag_name == "textarea":
                        input_field.clear()
                        input_field.send_keys(answer)
                    elif input_field.tag_name == "select":
                        dropdown = Select(input_field)
                        dropdown.select_by_visible_text(answer)

                    print(f"✅ Answered: {q_text} -> {answer}")
            except Exception as e:
                print(f"⚠ Could not answer question: {q_text}")

        # 🔹 Click submit button dynamically
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
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                submit_button.click()
                print(f"Clicked submit button")
                time.sleep(5)
                return
            except:
                continue  

        print("⚠ No submit button found, skipping submission.")

    except Exception as e:
        print(f"❌ Error filling form: {str(e)}")

# 🔹 Process job applications
for job_link in job_links:
    open_job_and_click_apply(driver, job_link)
    fill_form_and_submit(driver)

driver.quit()
print("\n🎉 Job application process completed!")

