
# Import the required libraries
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import os
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, StaleElementReferenceException
import time
import utils
from collections import defaultdict
import pandas as pd
import undetected_chromedriver as uc
import gc
from bs4 import BeautifulSoup

# ####These section seems like for Mac ONLY#######
import ssl
import certifi
# Use certifi for SSL certificates
os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['SSL_CERT_DIR'] = os.path.dirname(certifi.where())
ssl_context = ssl.create_default_context(cafile=certifi.where())
# ####These section seems like for Mac ONLY#######

# Load environment variables from a .env file
load_dotenv()
TD_USERNAME = os.getenv("TD_USERNAME")
TD_PASSWORD = os.getenv("TD_PASSWORD")
td_utl = 'https://authentication.td.com/uap-ui/?consumer=easyweb&locale=en_CA#/uap/login'

def accept_cookies():
    """Accept the cookies on the TD Online Bank website.
    """
    try:
        # Wait for the cookies banner to be present in the DOM
        cookies_banner = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "onetrust-banner-sdk"))
        )

        # Click the Accept All Cookies button
        accept_all_button = WebDriverWait(cookies_banner, 15).until(
            EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
        )
        accept_all_button.click()
    except TimeoutException:
        print("Timed out waiting for the cookies banner.")


def click_120_days():
    """
    Click the 120 days link and wait for the option to become bold (selected).
    """
    try:
        # Wait for the 120 days link to be present in the DOM
        days_120_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "ql4"))
        )

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


def login_to_td(url, username, password):
    """This function logs into the TD Online Bank website using the provided credentials.

    Args:
        url (str): The login url for the TD Online Bank website.
        username (str): The username credentials for the TD Online Bank account. 
        password (str): The password credentials for the TD Online Bank account.
    """
    driver.get(url)

    username_field = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, "username"))
    )
    print("Username field found.")
    username_field.send_keys(username)

    password_field = driver.find_element(By.ID, "uapPassword")
    password_field.send_keys(password)
    accept_cookies()
    login_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'btn-block') and contains(@class, 'td-button-secondary') and contains(., 'Login')]"))
    )
    login_button.click()
    try:
        
        # Wait for the Send button to be clickable
        text_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'td-button') and contains(text(), 'Text me')]"))
        )
        print("text_button button found.")
        
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
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'td-button') and @translate='BUTTON.ENTER']"))
        )
        enter_button.click()

        print("Verification code sent.")
    except Exception as e:
        print(f"An error occurred: verification code  {e}")


def get_accounts(type='banking'): #only gets the bank accounts
    """
    Get the list of accounts from the TD Online Bank website.
    """
    account_list = []
    if type == 'banking':
        # Found the table banking container
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
        # process each account
        for row in account_rows:  
            try:     
                account_name_element = WebDriverWait(row, 4).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "a.uf-account-name-and-link"))
                )
                #if 'ACCOUNT' in link.text: # Filter out the account links
                link_text = account_name_element.text
                print(link_text)
                account_list.append(account_name_element.text)
            except Exception as e:
                print(f"An error occurred finding account: {e}")
        
        return account_list
    else:
        print("Type not supported yet.")
        return None


def get_trans_data():
    """_Processes the transaction data from the TD Online Bank website table.

    Returns:
        Dict: The transaction data in a dictionary format.
    """
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

        # Convert each Selenium WebElement in cells to a BeautifulSoup object
        cells_soup = [BeautifulSoup(cell.get_attribute('outerHTML'), 'html.parser') for cell in cells]

        if len(cells_soup) == 5:
            ## Extract date
            date_cell = cells_soup[0]
            date_text = date_cell.get_text(strip=True)
            res['Date'].append(date_text)

            # Handle description
            description_cell = cells_soup[1]
            description_div = description_cell.find('div', class_='td-forscreenreader')
            if description_div:
                description = description_div.get_text(strip=True).split('View more')[-1].strip()
            else:
                description = description_cell.get_text(strip=True).split('View more')[-1].strip()
            res['Description'].append(description)

            # Extract debit, credit, and balance
            withdrawls = utils.clean_numeric(cells_soup[2].get_text(strip=True))
            res['Withdrawals'].append(withdrawls)

            deposits = utils.clean_numeric(cells_soup[3].get_text(strip=True))
            res['Deposits'].append(deposits)

            balance = utils.clean_numeric(cells_soup[4].get_text(strip=True))
            res['Balance'].append(balance)
            

    return res


def process_accounts(account_list):
    """Process each accounts in the account list.

    Args:
        account_list (list web element): The list of accounts to process.
    """
    for account in account_list:

        print(f"Downloading transactions for account: {str(account)}")

        # Click the checking account
        cur_account_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//a[@class='uf-account-name-and-link ng-star-inserted' and contains(text(), '{account}')]"))
            
        )
        cur_account_link.click()
        # Switch to the frame containing the account details
        WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.NAME, 'tddetails')))
        print('Switched to the frame containing the account details.')

        # The following code is optional. It selects the 120 days option.
        # We commented it out because I am tring 30 days option, which is the default.
        #click_120_days()

        trans_data = get_trans_data()
        # Save the data to a CSV file
        trans_df = pd.DataFrame(trans_data)
        csv_name = str(account) + '_td.csv'
        #csv_name = utils.set_csv_name(account, trans_df, 'td')
        utils.df_to_csv(trans_df, csv_name, type='banking')
        time.sleep(3)

    
        # Back to the main page     
        accounts_page_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[@href='servlet/ca.tdbank.banking.servlet.FinancialSummaryServlet' and @data-analytics-click='Accounts']"))
        )
        accounts_page_link.click()
        driver.switch_to.default_content()
        utils.human_like_delay()



def main():
    global driver
    print("Setting up driver...")   
    # driver options
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--start-maximized")
    # Add arguments to ignore SSL errors
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    
    # Disable web security for testing (use with caution)
    options.add_argument('--disable-web-security')
    driver = uc.Chrome(options=options, enable_cdp_events=True)

    print("Driver setup complete.")

    print("logging in ....")
    login_to_td(td_utl, TD_USERNAME, TD_PASSWORD)

    print("Get Account List...")
    account_list = get_accounts()

    print("Processing accounts...")
    process_accounts(account_list)


    driver.quit()   

    gc.collect()
if __name__ == "__main__":
    main()

