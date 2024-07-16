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
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, ElementNotInteractableException
import pickle as pkl
import time
import utils
import undetected_chromedriver as uc
import pandas as pd
import re
from datetime import datetime

debugging = True   
# This script download the CIBC credit card history as csv file


# Load environment variables from a .env file
load_dotenv()
CIBC_USERNAME = os.getenv("CIBC_USERNAME")
CIBC_PASSWORD = os.getenv("CIBC_PASSWORD")
cibc_login_url = 'https://www.cibconline.cibc.com/ebm-resources/online-banking/client/index.html#/auth/signon'


def accept_cookies():
    try:
        cookie_accept_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
        )
        print("Clicking 'Accept all cookies' button")
        time.sleep(utils.human_like_delay())
        cookie_accept_button.click()
        print("'Accept all cookies' button clicked")
        time.sleep(utils.human_like_delay())
    except Exception as e:
        print(f"Error clicking 'Accept all cookies' button: {e}")


def login(url, username, password):

    driver.get(url)
    accept_cookies()
    username_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "11-field"))
    )
    time.sleep(utils.human_like_delay())
    username_field.send_keys(username)
    time.sleep(utils.human_like_delay())

    password_field = driver.find_element(By.ID, "22-field")
    password_field.send_keys(password)
    time.sleep(utils.human_like_delay())

    login_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'primary-button') and contains(., 'Sign on')]"))
    )
    print("Clicking on the login button.")
    time.sleep(utils.human_like_delay())
    login_button.click()

    # Wait for the verification code input field to be present
    try:
        # Wait for the select element to be present
        select_element = WebDriverWait(driver, 20).until(
             EC.presence_of_element_located((By.CSS_SELECTOR, 'select[data-test-id="otvc-contact-methods"]'))
        )

        # Create a Select object
        select = Select(select_element)

        # Select the option by visible text
        select.select_by_visible_text("Text: 23X-XXX-X116") #todo: Make this dynamic. This is the phone number that will receive the verification code
        time.sleep(utils.human_like_delay())

        #print("Text option selected successfully.")

        # Wait for the Send button to be clickable
        send_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-test-id="otvc-send-btn"]'))
        )

        # Click the Send button
        send_button.click()
        time.sleep(utils.human_like_delay())
        print("Send button clicked successfully.")

        # Input filed for verification code
         # Wait for the verification code input field to be present
        verification_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[data-test-id="otvc-verification-code-inputbox"]'))
        )

        # Ask the user to input the verification code
        #todo: Make a UI for this
        verification_code = input("Please enter the 6-digit verification code from CIBC: ")

        # Input the verification code
        verification_input.send_keys(verification_code)# todo: Make a ui for this
        time.sleep(utils.human_like_delay())
        print("Verification code entered.")

        # Hit the Next button
        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-test-id="primary-btn"]'))
        )
        next_button.click()

    except Exception as e:
        print(f"An error occurred: {e}")


def extract_row_data(row):
    date = row.find_element(By.TAG_NAME, 'td').text
    #print(f"Date: {date}")
    # Extract category from image title and merchant name from span
    merchant_cell = row.find_element(By.CSS_SELECTOR, 'td:nth-child(2)')

    # Initialize category as None
    category = None

    # Try to find the img tag and get its title
    img_element = merchant_cell.find_elements(By.TAG_NAME, 'img')
    if img_element:
        category = img_element[0].get_attribute('title')

    # Extract merchant name from span
    merchant_name = merchant_cell.find_element(By.TAG_NAME, 'span').text
    amount_cell = row.find_element(By.CSS_SELECTOR, 'td:nth-child(4)')
    amount = amount_cell.text

    return [date, category, merchant_name, amount]


def extract_trans_history():
    # Start with the first page
    page_num = 1
    all_data = []
    while True:
        print(f"Extracting data from page {page_num}....")
        try:
            table = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'table.spend-manager-transaction-table'))
            )
            print("Located the transaction table.")

            #Finding body of the table 
            tbody = table.find_element(By.TAG_NAME, 'tbody')
            # Get all rows from the table
            rows = tbody.find_elements(By.TAG_NAME, 'tr')
        except TimeoutException:
            print("Table not found. Exiting loop.")
            break

        
        for row in rows:
            try:
                row_data = extract_row_data(row)
                all_data.append(row_data)        
            except Exception as e:
                print(f"An error occurred: {e}")

        utils.smooth_scroll(driver, 1000, 100)
        time.sleep(utils.human_like_delay())
        time.sleep(utils.human_like_delay())
        try:
            # Locate the Next button using its unique class combination
            next_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'ui-button.ui-next.ui-size-medium.ui-display-link'))
            )
            try:
                next_button.click()
            except ElementNotInteractableException:
                print("Next button is not clickable. We've likely reached the last page.")
                break
            
            print("Next button clicked.")
            time.sleep(utils.human_like_delay())
            utils.smooth_scroll(driver, 1000, 100)
            time.sleep(utils.human_like_delay())
            
            page_num += 1
        except TimeoutException:
            print("Next button not found or not clickable. Assuming we've reached the last page.")
            break
    return all_data


def get_credit_accounts_data():
    dic = {}
    credit_container = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.account-groups-container.credit-accounts"))
    )

    # Find the card container within the credit container
    card_container = WebDriverWait(credit_container, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.card-container"))
    )
     
     # Find the account name within the card container
    account = WebDriverWait(card_container, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.account-name"))
    )

    account_name = account.text
    load_trans_history_page(account)
    print(f"Extracting transaction history for account: {account_name}.")
    trans_data = extract_trans_history()
    trans_df = data_to_df(trans_data)
    dic[account_name] = trans_df
    # Optional: Click on the account if needed
    return dic


def load_trans_history_page(account, history_length = '3 months'):

    # Find and click the specific link
    link = WebDriverWait(account, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.account-name-header[data-test-id^="account-card-account-name-link-"]'))
    )
    link.click()
    time.sleep(utils.human_like_delay())
   
    try:
        #print("Finding the PERSONAL SPEND MANAGER link To Find The Transcation History.")
        element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((
            By.CSS_SELECTOR, 
            "li.personalSpendManager a[data-text='PERSONAL SPEND MANAGER']"
        )))
        element.click()
      
        # todo: Make this dynamic, 14 days, 3 months, 6 months, 14 montths
        three_month = WebDriverWait(driver, 10).until(EC.presence_of_element_located((
            By.XPATH, 
            "//ui-button[contains(@class, 'active') and @aria-label='3 months']"
        )))
        three_month.click()
        time.sleep(utils.human_like_delay())

    except Exception as e:
        print(f"An error occurred: {e}")


def data_to_df(trans_data):

    # Create a pandas DataFrame from the data
    df_dict = {
        'Date': [data[0] for data in trans_data],
        'Category': [data[1] for data in trans_data],
        'Merchant': [data[2] for data in trans_data],
        'Amount': [data[3] for data in trans_data]
    }
    df = pd.DataFrame(df_dict)
    return df


def set_csv_name(account, df):
    # Convert date strings to datetime objects
    first_date = datetime.strptime(df['Date'].iloc[0], '%b %d, %Y')
    last_date = datetime.strptime(df['Date'].iloc[-1], '%b %d, %Y')
    
    # Format dates in a file-friendly format (YYYYMMDD)
    first_date_str = first_date.strftime('%Y%m%d')
    last_date_str = last_date.strftime('%Y%m%d')
    
    # Remove any invalid filename characters from the account name
    #safe_account_name = ''.join(c for c in account if c.isalnum() or c in ('-', '_'))
    account_name = account.replace(" ", "_")
    return f"{account_name}_{first_date_str}_to_{last_date_str}.csv"
    

def main():
    global driver
    print("Setting up driver...")

    # driver options
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--start-maximized")

    # Create the driver with these options
    driver = uc.Chrome(options=options, enable_cdp_events=True)

    # Login to CIBC online banking account.
    login(cibc_login_url, CIBC_USERNAME, CIBC_PASSWORD)
    print("Logged in successfully.")

    credit_data = get_credit_accounts_data()
    for account, df in credit_data.items():
        print(f"Account: {account}")
        csv_name = set_csv_name(account,df)
        df.to_csv(f'data/{csv_name}', index=False)
    driver.quit()

if __name__ == "__main__":
    main()
