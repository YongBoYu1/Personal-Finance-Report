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
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, StaleElementReferenceException,NoSuchElementException
import pickle as pkl
import time
import utils
import undetected_chromedriver as uc
import pandas as pd
from collections import defaultdict
import re
import gc

load_dotenv()
RBC_USERNAME = os.getenv("RBC_USERNAME")
RBC_PASSWORD = os.getenv("RBC_PASSWORD")
rbc_login_url = 'https://secure.royalbank.com/statics/login-service-ui/index#/full/signin?LANGUAGE=ENGLISH'

###################
# Login functions #
###################
def accept_cookies():
    """
    Accepts all cookies on the RBC login page
    """
    try:
        cookie_accept_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
        )
        time.sleep(utils.human_like_delay())
        cookie_accept_button.click()
        print("'Accept all cookies' clicked")
        time.sleep(utils.human_like_delay())
    except Exception as e:
        print(f"Error clicking 'Accept all cookies' button: {e}")


def handle_text_message_verification():
    """
    Handle the text message verification step
    """
    text_to_find = "Text me"
    phone_number = "2368****16"
    try:
        # Select the "Text me" option
        cell_slector = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//label[contains(@class, 'rbc-radio-label-wrapper')]//bc-radio-label[contains(text(), '{phone_number}')]/ancestor::label"))
        )
        cell_slector.click()
        time.sleep(utils.human_like_delay())

        # Click the "Continue" button
        continue_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "continue-button"))
        )
        continue_button.click()
        time.sleep(utils.human_like_delay())

        operation_selectors = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//label[contains(@class, 'rbc-radio-label-wrapper')]//bc-radio-label[contains(text(), '{text_to_find}')]/ancestor::label"))
        )
        operation_selectors.click()
        time.sleep(utils.human_like_delay())

        continue_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "continue-button"))
        )
        continue_button.click()
        time.sleep(utils.human_like_delay())


    except Exception as e:
        print(f"An error occurred: {e}")


def login(url, username, password):
    """This function logs into the RBC online banking account.

    Args:
        url (str): The URL of the login page.
        username (str): The username/card to log in with.
        password (str): The password to log in with.
    """
    try:

        driver.get(url)
        accept_cookies()
        # Fill the username field
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "userName"))
        )
        username_field.send_keys(username)
        time.sleep(utils.human_like_delay())

        signin_next_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "signinNext"))
        )
        signin_next_btn.click()
        time.sleep(utils.human_like_delay())

        # Fill the password field
        password_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "password"))
        )
        password_field.send_keys(password)

        signin_next_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "signinNext"))
        )
        signin_next_btn.click()
        time.sleep(utils.human_like_delay())
        
    except Exception as e:
        print(f"Error logging in: {e}")





def get_account_name(item):
    """The function returns the account name from the account item.

    Args:
        item (web  element): The account item.

    Returns:
        str: The account name.
    """
    
    #item = item.find_elements(By.CSS_SELECTOR, "li.accounts-table__row")
    account_name_element = WebDriverWait(item, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "span.accounts-table__account-name"))
    )
    #account_name_element = item.find_element(By.CSS_SELECTOR, "span.accounts-table__account-name")
    account_name = account_name_element.text
    return account_name


def nav_to_trans_page(item):
    """The function navigates to the transaction page for the given account.

    Args:
        item (_type_): _description_
    """
    
     # Find the account name element
    account_name_element = WebDriverWait(item, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "span.accounts-table__account-name"))
    )
    # Click on the account name
    account_name_element.click()


def get_ith_account(index):
    """Get the ith account from the account list. Either banking or credit.

    Args:
        index (int): The index of the account in the list.

    Returns:
        Web element: Get the i-th element from the account list.
    """
    try:
        # Find the account list within the bc-frame
        account_list = get_rbc_acounts(type = "banking")
        #account_items = account_list.find_elements(By.CSS_SELECTOR, "li.accounts-table__row")
        return account_list[index]
    except Exception as e:
        print(f"Error get_ith_banking account: {e}")


    
def get_rbc_acounts(type = "banking"):
    """Get the list of accounts from the RBC online banking page.
    

    Args:
        type (str, optional): 
        banking: get all the debit info
        credit: get all the credit info. This is not implemented yet
        . Defaults to "banking".

    Returns:
        webelement list: The list of accounts found on the page with the given type.
    """
    try:
       
        table = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table[role='presentation']"))
        )

        # Find the tbody within the table
        tbody = table.find_element(By.TAG_NAME, "tbody")

        # Find the bc-frame within the tbody
        rbc_frame = tbody.find_element(By.CSS_SELECTOR, "rbc-frame.rbc-frame")

        # Find the account list within the bc-frame
        if type == "banking":
            account_list = rbc_frame.find_element(By.CSS_SELECTOR, "ul.accounts-list")
            account_items = account_list.find_elements(By.CSS_SELECTOR, "li.accounts-table__row")

        print(f"Found {len(account_items)} account items")
        
        return account_items

    except Exception as e:
        print(f"Error get_banking_acounts: {e}")


def dict_to_csv(data, account_name):
    """Given a dictionary of data, save it to a CSV file with the given account name under the data dir.

    Args:
        data (dict): The Dictionary of data to save contain the account transcation.
        account_name (str): The account name for saving csv file.
    """
    df = pd.DataFrame(data)
    account_name = utils.replace_special_chars(account_name)
    df.to_csv(f"data/{account_name}.csv", index=False)
    print(f"Data saved to {account_name}.csv")


def wait_for_summary_page_load(driver, timeout=30):
    """This function waits for the summary page to reload so that the data can be processed next account.

    Args:
        driver (Web drive): _description_
        timeout (int, optional): Max time out wait. Defaults to 30.

    Returns:
        bool: True if the summary page loaded successfully, False otherwise.
    """
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, "//section[contains(@class, 'account-summary-header')]"))
        )
        print("Summary page loaded successfully")
        return True
    except TimeoutException:
        print("Timed out waiting for summary page to load")
        return False


def process_accounts(account_list):
    """Process each accounts in the account list.

    Args:
        account_list (list web element): The list of accounts to process.
    """
    
    # The problem is I think I will nees ro re-run the login function to get the account_list again
    i = 0
    while i < len(account_list):
        account = get_ith_account(i)
        account_name = get_account_name(account)
        nav_to_trans_page(account)
        account_data = trans_table_data()
        dict_to_csv(account_data, account_name)
        print(f"Data for {account_name} processed and saved to CSV")
        try:
            # Using a more generic selector for the "Accounts Summary" link
            account_summary_link = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Accounts Summary')]"))
            )
            account_summary_link.click()
            
            # Wait for the summary page to load
            if wait_for_summary_page_load(driver):
                print("Ready for next account")
            else:
                print("Warning: Summary page may not have loaded properly")
        except Exception as e:
            print(f"Error navigating back to summary: {e}")
        i += 1
        



def nav_to_trans_table():
    """This function navigates to the transaction table.

    Returns:
        Webelement: Find the where the transaction table is located.
    """

    try:
       
        table = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table[role='presentation']"))
        )
        print("wrap Table found")

        # Find the tbody within the table
        tbody = table.find_element(By.TAG_NAME, "tbody")

        # Find the first <tr> in the table
        first_row = WebDriverWait(tbody, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table tr"))
        )

        # Find the first <td> in the first row
        first_cell = WebDriverWait(first_row, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "td"))
        )

        return first_cell
    except Exception as e:
        print(f"Error nav_to_trans_table: {e}")



def trans_table_data():
    """Process the transaction table and return the data in a dictionary.

    Returns:
        Dict: The dictionary of the transaction data.
    """
    res = defaultdict(list)
    try:
       
        table_location = nav_to_trans_table()

        button = WebDriverWait(table_location, 10).until(
            EC.presence_of_element_located((By.ID, "30"))
        )
        # Click the button
        button.click()
        print("switched to 30 days option.")
        time.sleep(utils.human_like_delay())

        transaction = WebDriverWait(table_location, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "table.rbc-transaction-list-table"))
        )
        #print("Transaction table found")
        
        # Find the tbody within the table
        tbody = WebDriverWait(transaction, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "tbody"))
        )
        #print("TBODY found")

        # Find the rest of the rows
        rows = WebDriverWait(tbody, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "tr[data-role='transaction-list-table-transaction']"))
        )
        print("Rows found")
        print("Number of rows found", len(rows))  

            
        for tr in rows:
            td_elements = tr.find_elements(By.XPATH, ".//td[contains(@class, 'ng-star-inserted')]")
            
            # Use the current date (no need to find it for each row)
            # Loop through td elements
            for i, td in enumerate(td_elements):
                if i == 0:
                    res['Date'].append(td.text)
                if i == 1:
                    div_elements = td.find_elements(By.XPATH, ".//div[contains(@class, 'ng-star-inserted')]")
                    description = ' '.join([div.text for div in div_elements if div.text])
                    res['Description'].append(description)
                if i == 2:
                    if 'rbc-transaction-list-withdraw' in td.get_attribute('class'):
                        withdrawal = td.text                        
                    else:
                        withdrawal = ""
                    res['Withdrawals'].append(withdrawal)
                if i == 3:
                    if 'rbc-transaction-list-deposit' in td.get_attribute('class'):
                        deposit = td.text                       
                    else:
                        deposit = ""
                    res['Deposits'].append(deposit)
                if i == 4:
                    balance = td.text
                    res['Balance'].append(balance)
        return res
    except Exception as e:
        print(f"Error trans_table_data: {e}")


def main():
    debugging = True
    global driver
    print("Setting up driver...")

    # driver options
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--start-maximized")

    # Create the driver with these options
    if debugging:
        driver = uc.Chrome(options=options, enable_cdp_events=True)
    else:
        driver = uc.Chrome(options=options)
    

    # Load the RBC login page
    login(rbc_login_url, RBC_USERNAME, RBC_PASSWORD)    
    try:
        handle_text_message_verification()
    except Exception as e:
         print("Verification step was skipped:", e)

    # Get the banking accounts
    banking_accounts = get_rbc_acounts()
    process_accounts(banking_accounts)

    #credit_accounts = get_rbc_acounts(type = "credit")
    #process_accounts(credit_accounts)

    
    driver.quit()
    gc.collect()
if __name__ == "__main__":
    main()
