from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
import os
import random
import time
import re
from datetime import datetime
import pandas as pd
from decimal import Decimal, InvalidOperation


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
    chrome_options.add_argument("--verbose")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("start-maximized")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--remote-debugging-port=9222")

    if debugging:
        chrome_options.add_experimental_option("detach", True)       
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


def summarize_nas(df):
    """
    Summarizes the missing values in a DataFrame.
    
    Parameters:
    df (pd.DataFrame): The DataFrame to summarize.

    Returns:
    pd.DataFrame: A summary DataFrame containing the count and percentage of missing values for each column.
    """
    # Calculate the number of missing values per column
    nas = df.isna().sum()
    
    # Calculate the percentage of missing values per column
    nas_percent = (nas / len(df)) * 100
    
    # Create a summary DataFrame
    summary_df = pd.DataFrame({
        'Missing Values': nas,
        'Percentage': nas_percent
    }).sort_values(by='Missing Values', ascending=False)
    
    return summary_df


def df_to_csv(df, csv_name,type):
    """This function saves the transaction data to a csv file.

    Args:
        df (pd.DataFrame): The transaction data in a pandas DataFrame.
        csv_name (str): The name of the csv file.
        type (str): The type of account. Either 'credit' or 'banking'.
    """
    if type == 'credit':
        file_path = f'data/credit/{csv_name}'
        
    else:
        file_path = f'data/banking/{csv_name}'
    
    df.to_csv(file_path, index=False)
    print(f"{csv_name} saved at {file_path}! \n")
    


def set_csv_name(account, df, insitution):
    """This function sets the name of the csv file to save the transaction data to.

    Args:
        account (str): The account name.
        df (pd.DataFrame): The transaction data in a pandas DataFrame.

    Returns:
        str: The csv name in the format: account_first_date_to_last_date.csv
    """
    # Convert date strings to datetime objects
    if insitution =='cibc':
        first_date = datetime.strptime(df['Date'].iloc[0], '%b %d, %Y')

        last_date = datetime.strptime(df['Date'].iloc[-1], '%b %d, %Y')
    if insitution =='rbc':
        first_date = datetime.strptime(df['Date'].iloc[0], '%b %d, %Y')
        last_date = datetime.strptime(df['Date'].iloc[-1], '%b %d, %Y')
    if insitution =='td':
        print('td time format') 
        print(df['Date'].iloc[0])
        first_date = datetime.strptime(df['Date'].iloc[0], '%b %d, %Y')
        last_date = datetime.strptime(df['Date'].iloc[-1], '%b %d, %Y')
    # Format dates in a file-friendly format (YYYYMMDD)
    first_date_str = first_date.strftime('%Y%m%d')
    last_date_str = last_date.strftime('%Y%m%d')
    
    # Remove any invalid filename characters from the account name
    #safe_account_name = ''.join(c for c in account if c.isalnum() or c in ('-', '_'))
    account_name = account.replace(" ", "_")
    return f"{account_name}_{first_date_str}_to_{last_date_str}.csv"



def clean_numeric(value):
    try:
        return str(Decimal(value.replace(',', '').replace('$', '').strip()))
    except InvalidOperation:
        return "0.00"