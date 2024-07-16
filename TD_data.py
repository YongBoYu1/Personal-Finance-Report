
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import os
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, StaleElementReferenceException
import pickle as pkl
import time
import utils
from collections import defaultdict
import pandas as pd


# Parameters setting
debugging = True   

# Load environment variables from a .env file
load_dotenv()
TD_USERNAME = os.getenv("TD_USERNAME")
TD_PASSWORD = os.getenv("TD_PASSWORD")
td_utl = 'https://authentication.td.com/uap-ui/?consumer=easyweb&locale=en_CA#/uap/login'

def click_120_days():
    try:
        # Wait for the 120 days link to be present in the DOM
        days_120_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "ql4"))
        )
        #print("120 days element found in the DOM.")

        

        # Scroll the element into view
        driver.execute_script("arguments[0].scrollIntoView(true);", days_120_element)
        print("Scrolled to the 120 days element.")

        # Try to click using different methods
        try:
            days_120_element.click()
        except ElementClickInterceptedException:
            driver.execute_script("arguments[0].click();", days_120_element)

        # Wait for the 120 days option to become bold (selected)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//span[text()='120 days' and @style='font-weight: bold;']"))
        )

    except TimeoutException:
        print("Timed out waiting for the 120 days element.")
    except StaleElementReferenceException:
        print("StaleElementReferenceException occurred. The page may have been updated.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")



def download_csv():
    # Wait for the select element to be present
    select_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "ExportTypeSelect"))
    )
    # Create a Select object
    select = Select(select_element)
    print("Select object created.")
    # Select by value
    select.select_by_value('csv')
    print("CSV option selected.")

    button = driver.find_element(By.ID, "download_button")
    print("Download button found.")
    button.click()
    print("Download button clicked.")
    print("CSV file downloaded.")



def login_to_td(url, username, password):
    driver.get(url)

    username_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "username"))
    )
    username_field.send_keys(username)

    password_field = driver.find_element(By.ID, "uapPassword")
    password_field.send_keys(password)

    login_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'btn-block') and contains(@class, 'td-button-secondary') and contains(., 'Login')]"))
    )
    login_button.click()

    try:
        
        # Wait for the Send button to be clickable
        text_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'tds-button') and contains(text(), 'Text me')]"))
        )
        
        # Click the Send button
        text_button.click()
        time.sleep(utils.human_like_delay())

        # Input filed for verification code
         # Wait for the verification code input field to be present
        verification_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "code"))
        )

        # Ask the user to input the verification code
        #todo: Make a UI for this
        verification_code = input("Please enter the 6-digit verification code from TD Bank: ")

        # Input the verification code
        verification_input.send_keys(verification_code)# todo: Make a ui for this
        time.sleep(utils.human_like_delay())
        #print("Verification code entered.")

        # Hit the Enter button
        enter_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'tdsbutton') and @translate='BUTTON.ENTER']"))
        )
        enter_button.click()

        print("Verification code sent.")

    except Exception as e:
        print(f"An error occurred: {e}")


def dict_to_csv(data, account_name):
    df = pd.DataFrame(data)
    account_name = utils.replace_special_chars(account_name)
    df.to_csv(f"data/{account_name}.csv", index=False)
    print(f"Data saved to {account_name}.csv")


def set_drive_services():
    chrome_driver_path = 'chromedriver-win32/chromedriver.exe'

    if not os.path.exists(chrome_driver_path):
        raise FileNotFoundError(f"ChromeDriver not found at {chrome_driver_path}")

    # Create a Service object
    service = Service(chrome_driver_path)
    return service


def set_drive_options():   
    # Set up Chrome options to keep the browser window open
    chrome_options = Options()

    if debugging:
        chrome_options.add_experimental_option("detach", True)
    else:
        chrome_options.add_argument("--headless")

    return chrome_options


def get_accounts():
    # Found the table container
    container = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located ((By.ID, "pfsTableCA_BANKBanking"))
    )

    # Then, find all account links within this container
    account_rows = WebDriverWait(container, 10).until(
        EC.presence_of_all_elements_located((
            By.CSS_SELECTOR, 
            "tduf-balance-summary-account-row-content.ng-star-inserted"
        ))
    )

    account_list = []

    for row in account_rows:  
        try:     
            account_name_element = WebDriverWait(row, 4).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a.uf-account-name-and-link"))
            )
            #account_name = account_name_element.text.strip()
            #if 'ACCOUNT' in link.text: # Filter out the account links
            link_text = account_name_element.text
            print(link_text)
            account_list.append(account_name_element.text)
        except Exception as e:
            print(f"An error occurred finding account: {e}")
       
    return account_list


def wait_for_download(directory, timeout=60):
    seconds = 0
    dl_wait = True
    while dl_wait and seconds < timeout:
        time.sleep(1)
        dl_wait = False
        for fname in os.listdir(directory):
            if fname.endswith('.crdownload'):
                dl_wait = True
        seconds += 1
    return seconds < timeout



def get_trans_data():
    res = defaultdict(list)

    # Wait for the table to be present
    table = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((
            By.CSS_SELECTOR,
            "table.td-table.td-table-border-row.td-table-border-column.td-margin-bottom-medium"
        ))
    )
    
    # Get the table rows
    rows = table.find_elements(By.TAG_NAME, "tr")

    for i, row in enumerate(rows):
        if i == 0:
            continue

        class_attr = row.get_attribute("class")
        if "td-JShide td-details3" in class_attr:
            continue

        # Get the row cells
        cells = row.find_elements(By.TAG_NAME, "td")

        if len(cells) == 5:
            date = cells[0].text.strip() if cells[0].text else "N/A"
            res['Date'].append(date)
            description = cells[1].text.strip() if cells[1].text else "N/A"
            res['Description'].append(description)
            debit = cells[2].text.strip() if cells[2].text else "0.00"
            res['Withdrawals'].append(debit)
            credit = cells[3].text.strip() if cells[3].text else "0.00"
            res['Deposits'].append(credit)
            balance = cells[4].text.strip() if cells[4].text else "N/A"
            res['Balance'].append(balance)

    return res


def main():
    global driver
    service = set_drive_services()
    chrome_options = set_drive_options()
    driver = webdriver.Chrome(service=service, options=chrome_options)


    # Begin the process     
    login_to_td(td_utl, TD_USERNAME, TD_PASSWORD)

    # Wait for the page to load
    account_list = get_accounts()
    print(account_list)
   

    for account in account_list:

        print(f"Downloading transactions for account: {account}")

        # Click the checking account
        cur_account_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//a[@class='uf-account-name-and-link ng-star-inserted' and contains(text(), '{account}')]"))
            
        )
        cur_account_link.click()
        # Switch to the frame containing the account details
        WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.NAME, 'tddetails')))
        print('Switched to the frame containing the account details.')


        
        click_120_days()
        print('Selected the  120 days option.')


        trans_data=get_trans_data()
        # Save the data to a CSV file
        dict_to_csv(trans_data, account)
        time.sleep(3)

    
        # Back to the main page     
        accounts_page_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[@href='servlet/ca.tdbank.banking.servlet.FinancialSummaryServlet' and @data-analytics-click='Accounts']"))
        )
        accounts_page_link.click()
        driver.switch_to.default_content()
        time.sleep(5)
            


if __name__ == "__main__":
    main()

