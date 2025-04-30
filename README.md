
# Lever Automation Script

This script automates the process of applying to jobs on the Lever platform. It uses Selenium to interact with web elements and fill out application forms based on predefined configurations and answers.

## Features

- **Profile Selection**: Dynamically select a profile from available YAML configuration files.
- **Resume Upload**: Automatically uploads the resume specified in the configuration.
- **Form Filling**: Fills out basic fields such as name, email, phone, etc., based on the selected profile.
- **Custom Questions**: Handles custom questions using predefined answers from a CSV file.
- **Logging**: Logs the status of each application attempt to a CSV file.
- **Error Handling**: Retries failed application submissions and logs errors for debugging.

## Requirements

- Python 3.x
- Selenium
- undetected-chromedriver
- webdriver-manager
- pandas
- fuzzywuzzy
- python-Levenshtein
- PyYAML

## Setup

1. **Install Dependencies**:
   
   ```bash
   pip install -m requirements.txt
   ```

2. **Prepare Configuration Files**:
   - Place your YAML configuration files in the `config/` directory.
   - use `configuration.yaml` file as reference to create the YAML config file.
   - Ensure your resume file path is correct in the YAML configuration.
   - Prepare a CSV file named `answers.csv` with columns `Question` and `Answer` for custom questions.

3. **Job Links**:
   - Prepare a CSV file named `job_links.csv` in the `jobs/` directory with columns `company`, `platform`, `job_id`, and `platform_link`.

## Usage

1. **Run the Script**:
   
   ```bash
   python main.py
   ```

2. **Follow the Prompts**:
   - Select the profile you want to use for the application.
   - The script will process each job link in the `job_links.csv` file and attempt to submit the application.

## Logs

- Application status logs are saved in `logs/application.csv`.
<!-- - Detailed logs are saved in `lever_automation.log`. -->

## Notes

- Ensure ChromeDriver is compatible with your installed version of Chrome.
- The script includes a pause for manual review before submitting the application.
- Adjust the locators in `locators/lever_locators.json` if the web elements change on the Lever platform.

