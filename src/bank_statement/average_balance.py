import os
import pandas as pd
import re
import csv
import traceback
import datetime

def date_formatting(csv_file):
    df = pd.read_csv(csv_file)

    for index, row in df.iterrows():
        x = row['Txn Date']
        x = x.replace("\n","").replace(" ","")
        x = re.sub(r'([A-Za-z])(\d{1,2})', r'\1 \2', x)
        x = re.sub(r'(\d{1,2})([A-Za-z])', r'\1 \2', x)
        row['Txn Date'] = x

    for index, row in df.iterrows():
        x = row['Value Date']
        x = x.replace("\n","").replace(" ","")
        x = re.sub(r'([A-Za-z])(\d{1,2})', r'\1 \2', x)
        x = re.sub(r'(\d{1,2})([A-Za-z])', r'\1 \2', x)
        row['Value Date'] = x
    return df

def get_monthly_balance_sheet(df,month):
    new_ind = []
    for index, row in df.iterrows():
        row_value = row['Txn Date']
        if row_value.__contains__(month):
            x = row_value
            # print(index)
            # print(row_value)
            
            new_ind.append(index)
    y = df.loc[new_ind]  
    # print(y)
    return y


def monthly_average_balance(dataframe,month):
    total_balance = 0
    # print(dataframe)
    
    if month not in {'Apr','Jun','Sep','Nov'}:
        number_of_days = 31

    else:
        number_of_days = 30

    for index, row in dataframe.iterrows():
        balance = row['Balance']
        balance = balance.replace(",","")
        total_balance = float(balance) + total_balance

    monthly_average = total_balance/number_of_days
    # print('Average Monthly Balance for {} is :'.format(month),monthly_average)
    return monthly_average

def opening_closing_balance(df,month):
    for index, row in df.iterrows():
        balance = row['Balance']
        balance = balance.replace(",","")
        opening_balance = balance
        break

    for index, row in df.iterrows():
        balance = row['Balance']
        balance = balance.replace(",","")
        closing_balance = balance
    
    return opening_balance,closing_balance

        
def get_monthly_avg_balance(csv_file):
    df = date_formatting(csv_file)
    month = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    try:
        for item in month:
            dataframe = get_monthly_balance_sheet(df,item)
            if not dataframe.empty:
                monthly_average = monthly_average_balance(dataframe,item)
                opening_balance,closing_balance = opening_closing_balance(dataframe,item)

                print("\nOpening Balance for {} month is ".format(item),opening_balance)
                print("Closing Balance for {} month is ".format(item),closing_balance)
                print('Average Monthly Balance for {} is :'.format(item),monthly_average,"\n")
    except:
        pass

def guess_date(string):
    for fmt in ["%Y/%m/%d", "%d-%m-%Y", "%Y%m%d",'%d/%m/%Y']:
        try:
            return datetime.datetime.strptime(string, fmt).date()
        except ValueError:
            continue
    raise ValueError(string)


def get_monthly_avg_bal(file_path,bank_name):
    try:
        statement = pd.read_excel(file_path,sheet_name='transaction_data')
    except:
        file_path = os.getcwd() + file_path 
        statement = pd.read_excel(file_path,sheet_name='transaction_data')
    # print(statement)
    list_of_date = statement['Date'].to_list()
    list_of_balance = statement['Balance'].to_list()
    # print(list_of_date)
    # print(list_of_balance)
    new_list_of_date = []
    new_list_of_balance = []
    for i,date in enumerate(list_of_date):
        date = str(date).strip()
        if new_list_of_date:
            if str(new_list_of_date[-1]) == date:
                new_list_of_date[-1] = date
                new_list_of_balance[-1] = list_of_balance[i]
            else:
                new_list_of_date.append(date)
                new_list_of_balance.append(list_of_balance[i])
        elif i == 0:
            new_list_of_date.append(date)
            new_list_of_balance.append(list_of_balance[i])

    df = pd.DataFrame({'Date':new_list_of_date,'Balance':new_list_of_balance})
    # print(df)
    
    # df['month'] = pd.DatetimeIndex(df['Date']).date
    # df['month_year'] = pd.to_datetime(df['Date']).dt.to_period('D')
    # print(df)

    df = pd.DataFrame()
    return df

if __name__ == "__main__":
    file_path = '/home/rahul/Downloads/1_19.xlsx'
    bank_name = 'HDFC BANK'
    get_monthly_avg_bal(file_path,bank_name)
    string = '11/03/20'
    # d = guess_date(string)
    # print("::::::::: ",d)
    samples = "2017/5/23", "22-04-2015", "20150504",'10/03/20' 

    for sample in samples:
        print(guess_date(sample))