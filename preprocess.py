import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
import utils 

def generate_date_range(from_date, to_date):
    # Parse the input strings to datetime objects
    from_date = datetime.strptime(from_date, '%Y-%m-%d')
    to_date = datetime.strptime(to_date, '%Y-%m-%d')

    # Calculate the number of days between the two dates
    delta = (to_date - from_date).days

    # Generate the date list
    date_list = [(from_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(delta + 1)]
    
    return date_list


def transform_debit_df(df):
    # Create 'withdraw' DataFrame
    withdraw_df = df[['Date', 'Description', 'Withdrawals']].copy()
    withdraw_df = withdraw_df[withdraw_df['Withdrawals'].notna() & (withdraw_df['Withdrawals'] != 0)]
    withdraw_df = withdraw_df.rename(columns={'Withdrawals': 'Amount'})
    withdraw_df['Type'] = 'withdraw'

    # Create 'deposits' DataFrame
    deposits_df = df[['Date', 'Description', 'Deposits']].copy()
    deposits_df = deposits_df[deposits_df['Deposits'].notna() & (deposits_df['Deposits'] != 0)]
    deposits_df = deposits_df.rename(columns={'Deposits': 'Amount'})
    deposits_df['Type'] = 'deposits'

    # Concatenate the two DataFrames
    result_df = pd.concat([withdraw_df, deposits_df], ignore_index=True)

    # Sort by Date
    result_df = result_df.sort_values('Date')
    
    return result_df


   
def format_finance_df(df, type='banking'):
    """_summary_

    Args:
        df (DataFrame): The DataFrame to format.
        type (str, optional): Wheather is credit or banking account. Defaults to 'banking'.

    Returns:
        _type_: _description_
    """
    res_df = df.copy()
    res_df['Date'] = pd.to_datetime(res_df['Date'], format='%b %d, %Y').dt.strftime('%Y-%m-%d')
    
    if type == 'banking':
       # Cast Date column in to yyyy-MM-dd format. eg: (Jul 22, 2023) -> (2023-07-22)       
       for column in ['Withdrawals', 'Deposits', 'Balance']:    
        if column in res_df.columns:      
        # For the column in 'Withdrawals', 'Deposits', 'Balance'. Rm the '$' ,',' '' '-'. Cast it into float object.
            res_df[column] = res_df[column].str.replace('−', '-')
            res_df[column] = res_df[column].str.replace(',', '')
            res_df[column] = res_df[column].str.replace('$', '')
            res_df[column] = res_df[column].astype(float)
        else:
            print(f'Column {column} not found in the DataFrame.')

    else: # credit
        # For the Amount column. Rm the '$' ,',' '' '-'. Cast it into float object.
        res_df['Amount'] = res_df['Amount'].str.replace('−', '-')
        res_df['Amount'] = res_df['Amount'].str.replace(',', '')
        res_df['Amount'] = res_df['Amount'].str.replace('$', '') 
        res_df['Amount'] = res_df['Amount'].astype(float)

    return res_df


def main():
   # todo: Add the data path to the json and parse it as config file
   # TD Banking data
   td_cheq = pd.read_csv('data/TD_EVERY_DAY_CHEQUING_ACCOUNT.csv')
   td_save = pd.read_csv('data/TD_EVERY_DAY_SAVINGS_ACCOUNT.csv')
   td_save['Withdrawals'] = td_save['Withdrawals'].astype(str)
   td_save['Deposits'] = td_save['Deposits'].astype(str)
   
   td_cheq = format_finance_df(td_cheq)
   td_save = format_finance_df(td_save)
   
   # RBC Banking data
   rbc_cheq = pd.read_csv('data/RBC_Day_to_Day_Banking.csv')
   rbc_cheq = format_finance_df(rbc_cheq)
   rbc_cheq['Withdrawals'] = abs(rbc_cheq['Withdrawals']) 
   rbc_cheq = rbc_cheq.fillna(0)

   # preprocess the debit data
   debit_dfs = [td_cheq, td_save, rbc_cheq]  
   # Concatenate the transformed dataframes
   debit_df = pd.concat(debit_dfs, axis=0).drop_duplicates()
   debit_df = transform_debit_df(debit_df)
   debit_df['Category'] = None

   # Credit data, read and preprocess
   cibc_credit = pd.read_csv('data/CIBC_MasterCard_20240714_to_20240418.csv')
   cibc_credit = format_finance_df(cibc_credit, 'credit')
   cibc_credit['Type'] = 'credit'
   cibc_credit = cibc_credit.rename(columns={'Merchant': 'Description'})
   cibc_credit = cibc_credit[['Date', 'Description', 'Amount','Type', 'Category']]
   
   # Stack and preprocess the debit and credit data together 
   stacked_df = pd.concat([debit_df, cibc_credit], axis=0)
   stacked_df = stacked_df.reset_index(drop=True) 
   stacked_df['Category'] = stacked_df['Category'].fillna('Debit_Card')

   # Fill in the missing dates
   max_date , min_date  = stacked_df['Date'].max(),stacked_df['Date'].min()   
   date_range = generate_date_range(min_date, max_date)
   date_df = pd.DataFrame(date_range, columns=['Date'])

   # Result and fill na 
   res_df = pd.merge(date_df, stacked_df, on='Date', how='left')

   res_df['Amount'] = res_df['Amount'].fillna(0)
   res_df['Description'] = res_df['Description'].fillna('No Transaction')
   res_df['Type'] = res_df['Type'].fillna('None')
   res_df['Category'] = res_df['Category'].fillna('None')

   # Create 'year' and 'month' columns
   res_df['Year'] = res_df['Date'].str[:4].astype(int)
   res_df['Month'] = res_df['Date'].str[5:7].astype(int)
   # sort it by date
   res_df = res_df.sort_values('Date')
   
   res_df.to_csv('data/trans_data.csv', index=False)

   
   print(f"The head of the ended df\n {res_df.head()}")
if __name__ == '__main__':
    
    main()