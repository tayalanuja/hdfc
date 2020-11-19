import pandas as pd
import config.config as project_configs
txndata_csv = project_configs.INTAIN_BANK_STATEMENT_TXNDATA_CSV


def get_correct_df(df,bank_name):
    # if bank_name == 'ANDHRA BANK':
    #     all_transaction = df.values.tolist()
    #     for i,item in enumerate(all_transaction[0]):
    #         if str(item) == 'nan' or item == None:
    #             print('INDEX   ',i)                
    #             df.drop(columns=[i])
    if bank_name == "ANDHRA BANK":
        if (str(df.loc[0][2]) == 'nan' or df.loc[0][2] is None):
            df = df[[0,2,1,3,4,5]]
        df.to_csv(txndata_csv, encoding='utf-8',header=False, index=False)
        df = pd.read_csv(txndata_csv,names=[0,1,2,3,4,5])
    elif bank_name == 'ALLAHABAD BANK':
        if df.shape[1] > 6:
            df = df.dropna(axis='columns', how='all')
            df.to_csv(txndata_csv, encoding='utf-8',header=False, index=False)
            df = pd.read_csv(txndata_csv,names=[0,1,2,3,4,5])
    
    elif bank_name == "AXIS BANK A":
        if df.shape[1] > 8:
            df = df.dropna(axis='columns', how='all')
        elif df.shape[1] == 7:
            df[7] = pd.Series()
            df = df[[0,1,2,7,3,4,5,6]]
        df.to_csv(txndata_csv, encoding='utf-8',header=False, index=False)
        df = pd.read_csv(txndata_csv,names=[0,1,2,3,4,5,6,7])
       
    elif bank_name == "AXIS BANK":
        if df.shape[1] > 7:
            df = df.dropna(axis='columns', how='all')
        elif df.shape[1] == 6:
            df[6] = pd.Series()
            df = df[[0,6,1,2,3,4,5]]
        df.to_csv(txndata_csv, encoding='utf-8',header=False, index=False)
        df = pd.read_csv(txndata_csv,names=[0,1,2,3,4,5,6])


    elif bank_name == 'BANK OF BARODA':
        all_transaction = df.values.tolist()
        for i,item in enumerate(all_transaction[0]):
            if str(item) == 'nan' or item == None:
                if sum(pd.isnull(df[i])) == df.shape[0]:
                    df = df.drop([i], axis=1)
                if (str(df.loc[0][2]) == 'nan' or df.loc[0][2] is None) and str(df.loc[0][3]) == 'Description':
                    df[2] = df[2].astype(str).replace('nan','') + df[3].astype(str).replace('nan','')
                    df = df.drop([3], axis=1)
        df.to_csv(txndata_csv, encoding='utf-8',header=False, index=False)
        df = pd.read_csv(txndata_csv,names=[0,1,2,3,4,5,6,7])

    elif bank_name == 'BANK OF INDIA':
        if str(df.loc[0][2]) == 'Description Cheque No' and (str(df.loc[0][3]) == 'nan' or df.loc[0][3] is None):
            df.iloc[0,3] = 'Cheque No'
            df.iloc[0,2] = 'Description'
        elif str(df.loc[0][3]) == 'Description Cheque No' and (str(df.loc[0][2]) == 'nan' or df.loc[0][2] is None):
            df.iloc[0,3] = 'Cheque No'
            df.iloc[0,2] = 'Description'
        elif str(df.loc[0][3]) == 'Description' and (str(df.loc[0][2]) == 'nan' or df.loc[0][2] is None):
            df.iloc[0,2] = 'Description'
            df = df.drop([3], axis=1)
        df = df.dropna(axis='columns', how='all')
        df.to_csv(txndata_csv, encoding='utf-8',header=False, index=False)
        df = pd.read_csv(txndata_csv,names=[0,1,2,3,4,5,6])

    elif bank_name == 'DBS BANK':
        if str(df.loc[0][2]) == 'Details of transaction' and (str(df.loc[0][1]) == 'nan' or df.loc[0][1] is None):
            df.iloc[0,1] = 'Details of transaction'
            df = df.drop([2], axis=1)
        df.to_csv(txndata_csv, encoding='utf-8',header=False, index=False)
        df = pd.read_csv(txndata_csv,names=[0,1,2,3,4])

    elif bank_name == "GREATER BANK":
        if df.shape[1] > 7:
            df = df.dropna(axis='columns', how='all')
            df.to_csv(txndata_csv, encoding='utf-8',header=False, index=False)
            df = pd.read_csv(txndata_csv,names=[0,1,2,3,4,5,6])

    elif bank_name == "HDFC BANK":
        if df.shape[1] > 7:
            df = df.dropna(axis='columns', how='all')
            df.to_csv(txndata_csv, encoding='utf-8',header=False, index=False)
            df = pd.read_csv(txndata_csv,names=[0,1,2,3,4,5,6])
        if df.shape[1] == 6:
            col_one_list = df[5].tolist()
            col_one_list_new =[]
            credit_col = []
            bal_col = []
            for i,val in enumerate(col_one_list):
                val = str(val).strip()
                if 'Closing Bal' in val:
                    break
                elif ' ' in val:
                    val_list = val.split()
                    credit_col.append(val_list[0])
                    bal_col.append(val_list[1])
                else:
                    credit_col.append('')
                    bal_col.append(val)
            df[5] = pd.DataFrame(credit_col)
            df[6] = pd.DataFrame(bal_col)
            
            if not credit_col:
                for i,val in enumerate(col_one_list):
                    val = str(val).strip()
                    if val and val != 'nan' :
                        s = val.replace(',','')
                        s = int(float(s))
                        col_one_list_new.append(s)
                if col_one_list_new[0] > col_one_list_new[1]:
                    df[6] = ""
                    cols = list(df)
                    cols[5], cols[6] = cols[6], cols[5]
                    df = df.loc[:,cols]
                else:
                    df[6] = ""
                    cols = list(df)
                    cols[4], cols[6] = cols[6], cols[4]
                    df = df.loc[:,cols]
            df.to_csv(txndata_csv, encoding='utf-8',header=False, index=False)
            df = pd.read_csv(txndata_csv,names=[0,1,2,3,4,5,6])

    elif bank_name == "ICICI BANK":
        if str(df.loc[0][2]) == 'nan' or df.loc[0][2] is None:
            df[2] = df[2].astype(str).replace('nan','') + df[3].astype(str).replace('nan','')
            df = df.drop([3], axis=1)
        if str(df.loc[0][4]) == 'nan' or df.loc[0][4] is None:
            df[4] = df[4].astype(str).replace('nan','') + df[5].astype(str).replace('nan','')
            df = df.drop([5], axis=1)
            
    elif bank_name == 'INDUSIND BANK':
        if str(df.loc[0][2]) == 'nan' or df.loc[0][2] is None:
            df = df.drop([2], axis=1)
        if str(df.loc[0][3]) == 'nan' or df.loc[0][3] is None:
            df = df.drop([3], axis=1)
        if str(df.loc[0][4]) == 'nan' or df.loc[0][4] is None:
            df = df.drop([4], axis=1)
        if (str(df.loc[0][5]) == 'nan' or df.loc[0][5] is None) and df.shape[1]>6:
            df[5] = df[5].astype(str).replace('nan','') + df[5].astype(str).replace('nan','')
            df = df.drop([5], axis=1)
        df.to_csv(txndata_csv, encoding='utf-8',header=False, index=False)
        df = pd.read_csv(txndata_csv,names=[0,1,2,3,4,5])

    elif bank_name == "YES BANK":
        if str(df.loc[0][2]) == 'nan' or df.loc[0][2] is None:
            df[2] = df[2].astype(str).replace('nan','') + df[3].astype(str).replace('nan','')
            df = df.drop([3], axis=1)
        df.to_csv(txndata_csv, encoding='utf-8',header=False, index=False)
        df = pd.read_csv(txndata_csv,names=[0,1,2,3,4,5])

    elif bank_name == "ANDHRA BANK":
        if (str(df.loc[0][2]) == 'nan' or df.loc[0][2] is None):
            df = df[[0,2,1,3,4,5]]
        df.to_csv(txndata_csv, encoding='utf-8',header=False, index=False)
        df = pd.read_csv(txndata_csv,names=[0,1,2,3,4,5])
    
    elif bank_name == "CANARA BANK":
        if df.shape[1] > 7:
            df = df.dropna(axis='columns', how='all')
            df.to_csv(txndata_csv, encoding='utf-8',header=False, index=False)
            df = pd.read_csv(txndata_csv,names=[0,1,2,3,4,5,6])
    elif bank_name == "CENTRAL BANK OF INDIA":
        if df.shape[1] > 8:
            df = df.dropna(axis='columns', how='all')
            df.to_csv(txndata_csv, encoding='utf-8',header=False, index=False)
            df = pd.read_csv(txndata_csv,names=[0,1,2,3,4,5,6,7])

    elif bank_name == "INDIAN BANK":
        if df.shape[1] > 8:
            df = df.dropna(axis='columns', how='all')
            df.to_csv(txndata_csv, encoding='utf-8',header=False, index=False)
            df = pd.read_csv(txndata_csv,names=[0,1,2,3,4,5,6,7])
    elif bank_name == "INDIAN OVERSEAS BANK":
        if df.shape[1] == 6:
            df[6] = pd.Series()
            df = df[[0,6,1,2,3,4,5]]
            df.to_csv(txndata_csv, encoding='utf-8',header=False, index=False)
            df = pd.read_csv(txndata_csv,names=[0,1,2,3,4,5,6])


    elif bank_name == 'MAHARASHTRA GRAMIN BANK':
        if df.shape[1] > 5:
            df = df.dropna(axis='columns', how='all')
            df.to_csv(txndata_csv, encoding='utf-8',header=False, index=False)
            df = pd.read_csv(txndata_csv,names=[0,1,2,3,4])

    elif bank_name == "PUNJAB NATIONAL BANK":
        if df.shape[1] == 5:
            df[5] = pd.Series()
            df = df[[0,5,1,2,3,4]]
        elif df.shape[1] > 6:
            df = df.dropna(axis='columns', how='all')
        df.to_csv(txndata_csv, encoding='utf-8',header=False, index=False)
        df = pd.read_csv(txndata_csv,names=[0,1,2,3,4,5])

    elif bank_name == "STATE BANK OF INDIA":
        if df.shape[1] > 7:
            df = df.dropna(axis='columns', how='all')
            df.to_csv(txndata_csv, encoding='utf-8',header=False, index=False)
            df = pd.read_csv(txndata_csv,names=[0,1,2,3,4,5,6])
    
    elif bank_name == "UNION BANK OF INDIA":
        if df.shape[1] == 6:
            df[6] = pd.Series()
            df[7] = pd.Series()
            df = df[[0,1,2,3,7,4,6,5]]
        elif df.shape[1] == 7:
            df[7] = pd.Series()
            df = df[[0,1,2,3,7,4,5,6]]
        elif df.shape[1] > 8:
            df = df.dropna(axis='columns', how='all')
        df.to_csv(txndata_csv, encoding='utf-8',header=False, index=False)
        df = pd.read_csv(txndata_csv,names=[0,1,2,3,4,5,6,7])

    elif bank_name == "UNITED BANK OF INDIA":
        if df.shape[1] == 5:
            df[5] = pd.Series()
            df[6] = pd.Series()
            df = df[[0,1,2,5,3,4,6]]
        elif df.shape[1] == 6:
            df[6] = pd.Series()
            df = df[[0,1,2,6,3,4,5]]
        elif df.shape[1] > 7:
            df = df.dropna(axis='columns', how='all')
        df.to_csv(txndata_csv, encoding='utf-8',header=False, index=False)
        df = pd.read_csv(txndata_csv,names=[0,1,2,3,4,5,6])

    elif bank_name == "AHMEDNAGAR MERCHANTS CO-OP BANK LTD":
        if df.shape[1] > 6:
            df = df.dropna(axis='columns', how='all')
            df.to_csv(txndata_csv, encoding='utf-8',header=False, index=False)
            df = pd.read_csv(txndata_csv,names=[0,1,2,3,4,5])

    elif bank_name == "SARASWAT CO-OPERATIVE BANK LTD.":
        if df.shape[1] == 5:
            df[5] = pd.Series()
            df = df[[0,5,1,2,5,3,4]]

        if df.shape[1] > 6:
            df = df.dropna(axis='columns', how='all')
        df.to_csv(txndata_csv, encoding='utf-8',header=False, index=False)
        df = pd.read_csv(txndata_csv,names=[0,1,2,3,4,5])

    elif bank_name == "UJJIVAN SMALL FINANCE BANK":
        if df.shape[1] > 6:
            df = df.dropna(axis='columns', how='all')
            df.to_csv(txndata_csv, encoding='utf-8',header=False, index=False)
            df = pd.read_csv(txndata_csv,names=[0,1,2,3,4,5])
    elif bank_name == "IDBI BANK":
        for i in range(0,8):
            if str(df.loc[0][i]) == 'nan':
                df = df.drop([i], axis=1)
                df.to_csv(txndata_csv, encoding='utf-8',header=False, index=False)
                df = pd.read_csv(txndata_csv,names=[0,1,2,3,4,5,6,7,8])

    # else:
    #         df = df.dropna(axis='columns', how='all')
    #         df.to_csv(txndata_csv, encoding='utf-8',header=False, index=False)
    #         df = pd.read_csv(txndata_csv,names=[0,1,2,3,4,5])
    return df