import pandas as pd
import numpy as np

def format_finance_df(df, type='banking'):
    """_summary_

    Args:
        df (DataFrame): The DataFrame to format.
        type (str, optional): Wheather is credit or banking account. Defaults to 'banking'.

    Returns:
        _type_: _description_
    """
    res_df = df.copy()
    if type == 'banking':
       res_df['Date'] = pd.to_datetime(res_df['Date']).dt.strftime('%Y-%m-%d')
       res_df['Withdrawals'] = res_df['Withdrawals'].str.replace(',', '').str.replace('$', '').astype(float)
       res_df['Deposits'] = res_df['Deposits'].str.replace(',', '').str.replace('$', '').astype(float)
       res_df['Balance'] = res_df['Balance'].str.replace(',', '').str.replace('$', '').astype(float)   
       #df['Description'] = df['Description'].astype('category')
    else:
        res_df['Date'] = pd.to_datetime(res_df['Date']).dt.strftime('%Y-%m-%d')
        res_df['Amount'] = res_df['Amount'].replace({'−': '-'}, regex=True)\
                                            .str.replace(',', '')\
                                            .str.replace('$', '')\
                                            .astype(float)
        res_df['type'] = 'credit'
    return res_df


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