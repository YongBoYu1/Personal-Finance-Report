from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
import os
import random
import time
import re




def replace_special_chars(input_string):
    return re.sub(r'[^a-zA-Z0-9]', '_', input_string)


def get_drive_services():
    chrome_driver_path = 'chromedriver-win32/chromedriver.exe'

    if not os.path.exists(chrome_driver_path):
        raise FileNotFoundError(f"ChromeDriver not found at {chrome_driver_path}")

    # Create a Service object
    service = Service(chrome_driver_path)
    #driver = webdriver.Chrome(service=service)
    return service


def human_like_delay():
    return random.uniform(0.5, 2.5)

def get_drive_options(debugging):   
    # Set up Chrome options to keep the browser window open
    chrome_options = Options()

    if debugging:
        chrome_options.add_experimental_option("detach", True)
        chrome_options.add_argument("--verbose")
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_argument("start-maximized")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--remote-debugging-port=9222")
    else:
        chrome_options.add_argument("--headless")
    #driver = webdriver.Chrome(options=chrome_options)
    return chrome_options

def smooth_scroll(driver, scroll_to=1000, step=100):
    current_scroll = 0
    while current_scroll < scroll_to:
        driver.execute_script(f"window.scrollTo(0, {current_scroll});")
        current_scroll += step
        time.sleep(0.1)  # Add a small delay to make it smoother