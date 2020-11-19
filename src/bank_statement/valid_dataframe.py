
import pandas as pd
import traceback
import re
# from pandas import ExcelWriter


def get_new_bank_name(header,bank_name):
    try:        
        if bank_name == 'ICICI BANK':
            for column_name in header:
                column_name = str(column_name).strip().lower()
                if column_name.__contains__('mode'):
                    bank_type = 'ICICI BANK 6'
                elif column_name == 'autosweep' or column_name.__contains__('reverse'):
                    bank_type = 'ICICI BANK 80'
                elif column_name == 'location' :
                    bank_type = 'ICICI BANK 81'
                elif column_name == 'transaction id':
                    bank_type = 'ICICI BANK 9'
                elif column_name.__contains__('s no'):
                    bank_type = 'ICICI BANK 82'
                
        elif bank_name == 'AXIS BANK':
            for column_name in header:
                if column_name == 'Branch Name' :
                    bank_type = 'AXIS BANK A'

        elif bank_name == 'INDUSIND BANK':
            for column_name in header:
                if column_name == 'Particulars' :
                    bank_type = 'INDUSIND BANK A'
        elif bank_name == "KOTAK MAHINDRA BANK":
            if len(header) == 8:
                bank_type = "KOTAK MAHINDRA BANK 8"
        else:
            bank_type = bank_name
        return bank_type
    except:
        print(traceback.print_exc())
        return bank_name

def get_balance_index(new_header):
    balance_key = ['balance(inr)','balance (inr','balance','balance(in rs.)','balance amount','closing balance','account balance']
    for index,item in enumerate(new_header):
        if item:
            for header_item in balance_key:                
                if header_item == item.lower().strip() or header_item.__contains__(item.lower().strip()):
                    balance_index = index
                    return balance_index
    return len(new_header)-1

def get_description_index(new_header):
    balance_key = ['description']
    for index,item in enumerate(new_header):
        item = item.lower().strip()
        for header_item in balance_key:
            if header_item == item or header_item.lower().__contains__(item):
                balance_index = index
                return balance_index
    return len(new_header)-1

def get_valid_dataframe(bank_name,df):
    # df = df.dropna(axis=0, how='all', thresh=None, subset=None, inplace=False)

    # converting to list
    # print(bank_name)
    # print("************************-------------------- \n",df)
    bank_name = bank_name.strip()
    all_transaction = df.values.tolist()
    all_transaction_new = []
    rows = []
    for row in all_transaction:
        nan_list_first = []
        for item in row:
            if str(item) == 'nan':
                nan_list_first.append(item)
        if len(nan_list_first) != len(row):
            all_transaction_new.append(row)
    empty_list = []

    for row in all_transaction_new:
        if str(row[0]) == 'nan' or row[0] == None:
            empty_list.append(item)

    if len(all_transaction_new) == len(empty_list):
        
        for row in all_transaction_new:
            row.pop(0)
            rows.append(row)
    else:
        rows = all_transaction_new

    #################################### Header Extraction ###################################
    headers = []
    last_column = []
    for i,row in enumerate(rows):
        if i<3:
            last_column.append(row[len(row)-1])
        else:
            break
    print('last_column',last_column)
    
    if bank_name == "INDUSIND BANK" or bank_name == "PUNJAB NATIONAL BANK" or bank_name == "AXIS BANK" or bank_name == 'YES BANK':
        for i,row in enumerate(rows):
            if bank_name == "AXIS BANK" and i < 2:
                if len(row) == 8 and i == 0:
                    headers.append(row)
                    break
                elif len(row) == 7:
                    headers.append(row)

            elif bank_name == 'INDUSIND BANK' and i<2:
                if str(row[1]).__contains__('Particulars'):
                    headers.append(row)
                    break
                else:
                    headers.append(row)
            
            elif bank_name == 'PUNJAB NATIONAL BANK' and i<3:
                if i==0:
                    headers.append(row)
                elif i == 1 and str(row[5]).__contains__('Narration'):
                    headers.append(row)
                elif i == 2:
                    headers.append(row)
                else:
                    break

            elif i<2:
                headers.append(row)
            elif i == 2:
                break
    
    elif bank_name == "UNION BANK OF INDIA" or bank_name == "HDFC BANK":
        for i,row in enumerate(rows):
            if i==0:
                headers.append(row)
            else:
                break

    else: 
        for i,row in enumerate(rows):
            if i >2:
                break
            elif i==0 and row[len(row)-1] == last_column[0]:
                headers.append(row)
            elif (str(last_column[1]) == 'nan' or last_column[1] is None or any(i.isdigit() for i in str(last_column[1])) == False or str(last_column[1]).lower().__contains__('balance') == True) and str(last_column[1]).lower().__contains__('cr') == False   and i == 1 :
                headers.append(row)
            elif (str(last_column[2]) == 'nan' or last_column[2] is None or any(i.isdigit() for i in str(last_column[1])) == False) and str(last_column[1]).lower().__contains__('cr') == False and any(i.isdigit() for i in str(last_column[2])) == False and str(last_column[2]).lower().__contains__('cr') == False and i == 2 :
                headers.append(row)

    print("--------------- ",headers)
    initial_header = []
    new_header = []

    header_length = len(headers[0])
    for i in range(header_length):
        
        if len(headers) == 2:
            res2 = str(headers[0][i]).strip() + ' ' + str(headers[1][i]).strip()
        elif len(headers) == 3:
            res2 = str(headers[0][i]).strip() + ' ' + str(headers[1][i]).strip() + ' ' +str(headers[2][i]).strip()
        elif len(headers) == 1:
            res2 = str(headers[0][i]).strip()
        else:
            res2 = ''
        res2 = res2.replace("None","").replace('nan','')
        initial_header.insert(i,res2)

    print('initial_header',initial_header)
    for i,item in enumerate(initial_header):
        item = str(item).lower()
        item = re.sub(r"\s\s+" , " ", item)
        if item.__contains__('txn date') or item.__contains__('txn. date') or item.__contains__('transaction date') or item.__contains__('post date') :
            new_header.append('Date')
        elif item.__contains__('tran date') :
            new_header.append('Date')
        elif item.__contains__('cr') and item.__contains__('dr'):
            new_header.append('Dr/Cr')
        elif item.__contains__('dr') or item.__contains__('withdrawal'):
            new_header.append('Debit')
        elif item.__contains__('particular') or item.__contains__('description') or item.__contains__('naration') or item.__contains__('narration'):
            new_header.append('Description')
        elif item.__contains__('details') or item.__contains__('transaction remarks') or item == 'remarks':
            new_header.append('Description')
        elif any(re.findall(r'(\bcr\b)',item.lower())) or any(re.findall(r'(eposit)',item)):
            new_header.append('Credit')
        elif item.__contains__('value dt'):
            new_header.append('Value Date')
        elif i == len(initial_header)-1 and (item.__contains__('balance') or item.__contains__('balace') or item.__contains__('closing bal')) :
            new_header.append('Balance')
        elif i == len(initial_header)-2 and item.__contains__('balance')  :
            new_header.append('Balance')
        elif item.__contains__('amount') :
            new_header.append('Amount')
        elif item.__contains__('value date'):
            new_header.append('Value Date')
        # elif item.lower().__contains__('chq') :
        #     new_header.append('Cheque No')
        # elif (item.lower().__contains__('cr')and item.lower().__contains__('dr')) or (item.lower().__contains__('deposit')and item.lower().__contains__('withdrawal')) :
        #     new_header.append('Amount')
        else:
            column_item = item.strip().title()
            new_header.append(column_item)

    bank_type = get_new_bank_name(new_header,bank_name)
    print('new_header',new_header,bank_name, bank_type)

    balance_index = get_balance_index(new_header)
    description_index = get_description_index(new_header)
    ################################# Valid Transaction ###########################

    valid_transactions_new = [] 
    valid_transactions = []
    opening_closing_row = []
    for row in rows:
        try: 
            row[description_index] = str(row[description_index]).lower()
            if row[description_index].__contains__('debit:0') or row[description_index].__contains__('number of credit') or row[description_index].__contains__('opening balance') or row[description_index].__contains__('closing balance'):
                opening_closing_row.append(row)
        except:
            pass

    for row in rows:
        if row not in headers and row not in opening_closing_row :
            valid_transactions_new.append(row)
    
    for row in valid_transactions_new:
        nan_list = []
        for item in row:
            if str(item) == 'nan':
                nan_list.append(item)
        if len(nan_list) != len(row):
            valid_transactions.append(row)
    

            

    ################################# Bank ########################################

    transactions = []     
    dfObj = pd.DataFrame()             # list to store single row entries
    # print(":::::::::::::::::;valid_transactions:::::::::::::::::::::",valid_transactions)


    if bank_name == "ALLAHABAD BANK":
        print("++++++++++++++++++++++++   ALLAHABAD BANK  ++++++++++++++++")
        d_i =  0        
        p_i =  2       
        for index,v_t in enumerate(valid_transactions):
            if index == len(valid_transactions) - 1:
                print('last_row',v_t)
            elif v_t[d_i] is None or type(v_t[d_i]) == type(None) or str(v_t[d_i]) == 'nan' :
                if v_t[p_i] is not None :
                    if str(v_t[p_i]) != 'nan':
                        try:
                            transactions[-1][p_i] = str(transactions[-1][p_i]) + str(v_t[p_i])
                        except:
                            print(traceback.print_exc())
                            pass
            else:
                transactions.append(v_t)
                
        if new_header:
            transactions.insert(0, new_header) 
        dfObj = pd.DataFrame(transactions)

    if bank_name == "AHMEDNAGAR MERCHANTS CO-OP BANK LTD":
        print("++++++++++++++++++++++++   AHMEDNAGAR MERCHANTS CO-OP BANK LTD  ++++++++++++++++")
        d_i =  0        
        p_i =  2       
        for index,v_t in enumerate(valid_transactions):
            if index == len(valid_transactions) - 2 or index == len(valid_transactions) - 1:
                print('last_row',v_t)
            elif v_t[d_i] is None or type(v_t[d_i]) == type(None) or str(v_t[d_i]) == 'nan' :
                if v_t[p_i] is not None :
                    if str(v_t[p_i]) != 'nan':
                        try:
                            transactions[-1][p_i] = str(transactions[-1][p_i]) + str(v_t[p_i])
                        except:
                            print(traceback.print_exc())
                            pass

            else:
                transactions.append(v_t)
                
        if new_header:
            transactions.insert(0, new_header) 
        dfObj = pd.DataFrame(transactions)


    elif bank_name == "CITY UNION BANK":
        print("++++++++++++++++++++++++   CITY UNION BANK  ++++++++++++++++")
        d_i =  0        
        p_i =  1       
        for index,v_t in enumerate(valid_transactions):
            if index == len(valid_transactions) - 1:
                print('last_row',v_t)
            elif v_t[d_i] is None or type(v_t[d_i]) == type(None) or str(v_t[d_i]) == 'nan' :
                if v_t[p_i] is not None :
                    if str(v_t[p_i]) != 'nan':
                        try:
                            transactions[-1][p_i] = str(transactions[-1][p_i]) + str(v_t[p_i])
                        except:
                            print(traceback.print_exc())
                            pass

            else:
                transactions.append(v_t)
                
        if new_header:
            transactions.insert(0, new_header) 
        dfObj = pd.DataFrame(transactions)


    elif bank_name == "KOTAK MAHINDRA BANK":
        if len(new_header) == 5:
            d_i =  0        
            p_i =  1       
            c_n = 2
            for v_t in valid_transactions:
                if v_t[d_i] is None or type(v_t[d_i]) == type(None) or str(v_t[d_i]) == 'nan' :
                    if v_t[p_i] is not None :
                        if str(v_t[p_i]) != 'nan':
                            try:
                                transactions[-1][p_i] = str(transactions[-1][p_i]) + str(v_t[p_i])
                            except:
                                pass
                    if v_t[c_n] is not None :
                        if str(v_t[c_n]) != 'nan':
                            try:
                                transactions[-1][c_n] = str(transactions[-1][c_n]) + str(v_t[c_n])
                            except:
                                pass
                else:
                    transactions.append(v_t)
                    
            if new_header:
                transactions.insert(0, new_header) 
                
            dfObj = pd.DataFrame(transactions) 
            # dfObj.loc[2,list(statement.columns.values)]=1
            dfObj.xs(0)[7] = "CR_DR"
            # print("+++++++++++++++++++++++++++ dfObj ++++++++++++++++++++++++++\n",dfObj)
            
            # dfObj.to_csv('xxx.csv', encoding='utf-8',header=False, index=False)
            
            # statement = pd.read_csv('xxx.csv')
            statement =dfObj
            statement.rename(columns=statement.iloc[0], inplace = True)
            statement.drop([0], inplace = True)
            statement.rename(columns = {7: 'col_1_new_name'}, inplace = True)

            print("statement\n",statement)
            statement['Credit'] = "" 

            print("list(statement.columns.values)\n",list(statement.columns.values))
            xx = statement['Dr/Cr'].values.tolist()
            for item in xx:
                if item.lower().__contains__('cr'):
                    statement.loc[statement['Dr/Cr'] == item , 'Credit'] = statement['Dr/Cr']
                    statement.loc[statement['Dr/Cr'] == item, 'Dr/Cr'] = ''
            statement.rename(columns = {'Dr/Cr': 'Amount'}, inplace = True)
            dfObj = statement
            
            print("***************************\n",statement)       
        
        if len(new_header) == 8:
            d_i =  1        
            p_i =  2     
            for v_t in valid_transactions:
                if v_t[d_i] is None or type(v_t[d_i]) == type(None) or str(v_t[d_i]) == 'nan':
                    if v_t[p_i] is not None :
                        if str(v_t[p_i]) != 'nan':
                            try:
                                transactions[-1][p_i] = str(transactions[-1][p_i]) + str(v_t[p_i])
                            except:
                                pass
                else:
                    transactions.append(v_t)
            if new_header:
                transactions.insert(0, new_header) 

            dfObj = pd.DataFrame(transactions) 
            # dfObj.loc[2,list(statement.columns.values)]=1
            dfObj.xs(0)[7] = "CR_DR"
            print("+++++++++++++++++++++++++++ dfObj ++++++++++++++++++++++++++\n",dfObj)
            
            # dfObj.to_csv('xxx.csv', encoding='utf-8',header=False, index=False)
            
            # statement = pd.read_csv('xxx.csv')
            statement =dfObj
            statement.rename(columns=statement.iloc[0], inplace = True)
            statement.drop([0], inplace = True)
            statement.rename(columns = {7: 'col_1_new_name'}, inplace = True)

            print("statement\n",statement)
            statement['Credit'] = "" 

            print("list(statement.columns.values)",list(statement.columns.values))
            statement.loc[statement['Dr/Cr'] == 'CR', 'Credit'] = statement['Amount']
            statement.loc[statement['Dr/Cr'] == 'CR', 'Amount'] = ''
            dfObj = statement
            
            # print("***************************\n",statement)

        
    elif bank_name == "AXIS BANK":
        print("----------- Axis Bank -----------")
        transactions = []  
        # try:
        yyy = ''
        zzz = ''
        if header_length == 7:
            b_i = 5
            index_2 = 2
            for v_t in valid_transactions:
                if v_t[b_i] is None or type(v_t[b_i]) == type(None) or str(v_t[b_i]) == 'nan': 
                    if v_t[index_2] is not None :
                        if str(v_t[index_2]) != 'nan':   
                            try:
                                yyy = str(v_t[index_2])
                            except:
                                print(traceback.print_exc())
                                pass
                else:
                    try:
                        transactions.append(v_t)
                        if yyy:
                            transactions[-1][index_2] = yyy + ' ' + transactions[-1][index_2]
                        yyy = ''
                    except:
                        print(traceback.print_exc())
                        pass
            if new_header:
                transactions.insert(0, new_header) 
            dfObj = pd.DataFrame(transactions) 
                    
        elif header_length == 8:
            b_i = 6
            index_2 = 2
            index_7 = 7

            for v_t in valid_transactions:
                if v_t[b_i] is None or type(v_t[b_i]) == type(None) or str(v_t[b_i]) == 'nan': 
                    if v_t[index_2] is not None :
                        if str(v_t[index_2]) != 'nan':   
                            try:
                                yyy = str(v_t[index_2])
                            except:
                                print(traceback.print_exc())
                                pass
                    if v_t[index_7] is not None :
                        if str(v_t[index_7]) != 'nan':   
                            try:
                                zzz = str(v_t[index_7])
                            except:
                                print(traceback.print_exc())
                                pass
                else:
                    try:
                        transactions.append(v_t)
                        if yyy:
                            transactions[-1][index_2] = yyy + ' ' + transactions[-1][index_2]
                            yyy = ''
                        if zzz:
                            transactions[-1][index_7] = zzz + ' ' + transactions[-1][index_7]
                            zzz = ''
                    except:
                        print(traceback.print_exc())
                        pass
                
            if new_header:
                transactions.insert(0, new_header) 
            dfObj = pd.DataFrame(transactions) 

            statement =dfObj
            statement.rename(columns=statement.iloc[0], inplace = True)
            statement.drop([0], inplace = True)
            statement.rename(columns = {7: 'col_1_new_name'}, inplace = True)

            print("statement\n",statement)
            statement['Credit'] = "" 

            print("list(statement.columns.values)",list(statement.columns.values))
            statement.loc[statement['Dr/Cr'] == 'CR', 'Credit'] = statement['Amount']
            statement.loc[statement['Dr/Cr'] == 'Cr', 'Credit'] = statement['Amount']

            statement.loc[statement['Dr/Cr'] == 'CR', 'Amount'] = ''
            statement.loc[statement['Dr/Cr'] == 'Cr', 'Amount'] = ''

            # statement.rename(columns = {7: 'col_1_new_name'}, inplace = True)
            statement.rename(columns={"Amount": "Debit"},inplace = True)
            dfObj = statement

        # except:
        #     print(traceback.print_exc())
        #     d_i =  0       
        #     p_i =  2        
        #     for v_t in valid_transactions:
        #         if v_t[d_i] is None or type(v_t[d_i]) == type(None) or str(v_t[d_i]) == 'nan':
        #             if v_t[p_i] is not None:
        #                 if str(v_t[p_i]) != 'nan':
        #                     try:
        #                         transactions[-1][p_i] += str(v_t[p_i])
        #                     except:
        #                         pass
        #         else:
        #             transactions.append(v_t)



    elif bank_name == "BANK OF BARODA":
        d_i =  1        #index of date column        from BANK_DETAILS
        p_i =  2        #index of particular(transaction) column  from BANK_DETAILS
        for v_t in valid_transactions:
            if v_t[d_i] is None or type(v_t[d_i]) == type(None):
                if v_t[p_i] is not None:
                    if str(v_t[p_i]) != 'nan':
                        try:
                            transactions[-1][p_i] += str(v_t[p_i])
                        except:
                            pass
            else:
                transactions.append(v_t)
        if new_header:
            transactions.insert(0, new_header)
        dfObj = pd.DataFrame(transactions) 


    elif bank_name == "COSMOS BANK":
        print("++++++++++++++++++++++++   COSMOS BANK  ++++++++++++++++")
        d_i =  0        
        p_i =  1       
        for index,v_t in enumerate(valid_transactions):
            if str(v_t[1]).__contains__('Sub Total') or str(v_t[1]).__contains__('GrandTotal') :
                print('last_row',v_t)
            elif v_t[d_i] is None or type(v_t[d_i]) == type(None) or str(v_t[d_i]) == 'nan' :
                if v_t[p_i] is not None :
                    if str(v_t[p_i]) != 'nan':
                        try:
                            transactions[-1][p_i] = str(transactions[-1][p_i]) + ' '+str(v_t[p_i])
                        except:
                            print(traceback.print_exc())
                            pass

            else:
                transactions.append(v_t)
                
        if new_header:
            transactions.insert(0, new_header) 
        dfObj = pd.DataFrame(transactions)

    elif bank_name == "INDUSIND BANK":
        print("--------------- INDUSIND BANK ------------------")

        if bank_type == 'INDUSIND BANK A':
            d_i =  5        #index of date column        from BANK_DETAILS
            p_i =  1        #index of particular(transaction) column  from BANK_DETAILS
            for v_t in valid_transactions:
                if v_t[d_i] is None or type(v_t[d_i]) == type(None):
                    if v_t[p_i] is not None:
                        if str(v_t[p_i]) != 'nan':
                            try:
                                transactions[-1][p_i] += str(v_t[p_i])
                                transactions[-1][p_i] = str(transactions[-1][p_i]).replace('None','').replace('nan','')
                            except:
                                pass
                else:
                    transactions.append(v_t)

        else:
            b_i = 0
            index_1 = 1
            index_2 = 2
            index_5 = 5
            yyy = ''
            zzz = ''
            for v_t in valid_transactions:
                if v_t[b_i] is None or type(v_t[b_i]) == type(None) or str(v_t[b_i]) == 'nan':   
                    try:
                        yyy = str(v_t[index_2])
                    except:
                        print(traceback.print_exc())
                        pass  
                    try:
                        zzz = str(v_t[index_1])
                    except:
                        print(traceback.print_exc())
                        pass  
                    try:
                        balance = str(v_t[index_5])
                    except:
                        print(traceback.print_exc())
                        pass  

                else:
                    try:
                        transactions.append(v_t)
                        if yyy:
                            transactions[-1][index_2] = yyy + ' ' + str(transactions[-1][index_2])
                            transactions[-1][index_2] = str(transactions[-1][index_2]).replace('None','').replace('nan','')
                            yyy = ''
                        if zzz:
                            transactions[-1][index_1] = zzz + ' ' + str(transactions[-1][index_1])
                            transactions[-1][index_1] = str(transactions[-1][index_1]).replace('None','').replace('nan','')
                            zzz = ''
                        if balance:
                            transactions[-1][index_5] = balance + ' ' + str(transactions[-1][index_5])
                            transactions[-1][index_5] = str(transactions[-1][index_5]).replace('None','').replace('nan','')
                    except:
                        print(traceback.print_exc())
                        pass
        if new_header:
            transactions.insert(0, new_header) 
        dfObj = pd.DataFrame(transactions) 
        print(dfObj)


    elif bank_name == "IDBI BANK":
        print("++++++++++++++++++++++++   IDBI BANK  ++++++++++++++++")
        d_i =  1        
        p_i =  3       
        for index,v_t in enumerate(valid_transactions):
            if index == len(valid_transactions) - 2 or index == len(valid_transactions) - 1:
                print('last_row',v_t)
            elif v_t[d_i] is None or type(v_t[d_i]) == type(None) or str(v_t[d_i]) == 'nan' :
                if v_t[p_i] is not None :
                    if str(v_t[p_i]) != 'nan':
                        try:
                            transactions[-1][p_i] = str(transactions[-1][p_i]) + str(v_t[p_i])
                        except:
                            print(traceback.print_exc())
                            pass

            else:
                transactions.append(v_t)
                
        if new_header:
            transactions.insert(0, new_header) 
            
        dfObj = pd.DataFrame(transactions) 
        # dfObj.loc[2,list(statement.columns.values)]=1
        dfObj.xs(0)[9] = "CR_DR"

        statement =dfObj
        statement.rename(columns=statement.iloc[0], inplace = True)
        statement.drop([0], inplace = True)
        statement.rename(columns = {9: 'col_1_new_name'}, inplace = True)

        statement['Credit'] = "" 

        print("list(statement.columns.values)\n",list(statement.columns.values))
        xx = statement['Dr/Cr'].values.tolist()
        statement.loc[statement['Dr/Cr'] == 'CR', 'Credit'] = statement['Amount']
        statement.loc[statement['Dr/Cr'] == 'CR', 'Amount'] = ''
        statement.rename(columns = {'Amount': 'Debit'}, inplace = True)
        dfObj = statement.copy()


    elif bank_name == "BANK OF INDIA":
        if len(new_header) == 7:
            d_i =  1        #index of date column        from BANK_DETAILS
            p_i =  2        #index of particular(transaction) column  from BANK_DETAILS
            for v_t in valid_transactions:
                if str(v_t[0]).__contains__('Name') or str(v_t[0]).__contains__('Address') :
                    
                    print('last_row',v_t)
                    break
                if v_t[d_i] is None or type(v_t[d_i]) == type(None) or str(v_t[d_i]) == 'nan':
                    if v_t[p_i] is not None:
                        if str(v_t[p_i]) != 'nan':
                            try:
                                transactions[-1][p_i] += str(v_t[p_i])
                            except:
                                pass
                else:
                    transactions.append(v_t)
            if new_header:
                transactions.insert(0, new_header)
        if len(new_header) == 6:
            d_i =  0        #index of date column        from BANK_DETAILS
            p_i =  1        #index of particular(transaction) column  from BANK_DETAILS

            for v_t in valid_transactions:
                if v_t[d_i] is None or type(v_t[d_i]) == type(None) or str(v_t[d_i]) != 'nan':
                    if v_t[p_i] is not None:
                        if str(v_t[p_i]) != 'nan':
                            try:
                                transactions[-1][p_i] += str(v_t[p_i])
                            except:
                                pass
                else:
                    transactions.append(v_t)

            if new_header:
                transactions.insert(0, new_header) 
        dfObj = pd.DataFrame(transactions) 

    elif bank_name == "ANDHRA BANK":        
        d_i =  0     
        p_i =  2       
        for v_t in valid_transactions:
            if type(v_t[d_i]) == type(None) or v_t[d_i] is None or str(v_t[d_i]) == 'nan' or v_t[d_i] == 'nan':
                try:
                    transactions[-1][p_i] += str(v_t[p_i])
                except:
                    pass
            else:
                transactions.append(v_t)
        if new_header:
            transactions.insert(0, new_header) 
        dfObj = pd.DataFrame(transactions) 

    elif bank_name == "GREATER BANK":  
        d_i =  0        
        p_i =  3        
        for v_t in valid_transactions:
            if v_t[d_i] is None or type(v_t[d_i]) == type(None) or str(v_t[d_i]) == 'nan': 
                if v_t[p_i] is not None :
                    if str(v_t[p_i]) != 'nan':               
                        transactions[-1][p_i] = str(transactions[-1][p_i]) + str(v_t[p_i])
            else:
                transactions.append(v_t)             
        if new_header:
            transactions.insert(0, new_header) 
        dfObj = pd.DataFrame(transactions) 

    elif bank_name == "HDFC BANK":  
        d_i =  0        
        p_i =  1        
        for v_t in valid_transactions:
            if str(v_t[p_i]).__contains__('statement summary'):
                print('last_row',v_t)
                break
            if v_t[d_i] is None or type(v_t[d_i]) == type(None) or str(v_t[d_i]) == 'nan': 
                if v_t[p_i] is not None :
                    if str(v_t[p_i]) != 'nan':  
                        try :           
                            transactions[-1][p_i] = str(transactions[-1][p_i]) + str(v_t[p_i])
                        except:
                            pass
            else:
                transactions.append(v_t)             
        if new_header:
            transactions.insert(0, new_header) 
        dfObj = pd.DataFrame(transactions) 

    elif bank_name == "CANARA BANK" or bank_name == 'BANK OF WIKI':
        d_i =  0     
        p_i =  3      
        for v_t in valid_transactions:
            if v_t[d_i] is not None or type(v_t[d_i]) != type(None)  :
                transactions.append(v_t)
            else:
                try:
                    transactions[-1][p_i] += str(v_t[p_i])
                except:
                    pass
        if new_header:
            transactions.insert(0, new_header) 
        dfObj = pd.DataFrame(transactions) 

    # elif bank_name == "BANK OF MAHARASHTRA":
    #     d_i =  0       
    #     p_i =  3       
    #     for v_t in valid_transactions:
    #         if v_t[d_i] is not None or type(v_t[d_i]) != type(None)  :
    #             transactions.append(v_t)
    #         else:
    #             try:
    #                 transactions[-1][p_i] += str(v_t[p_i])
    #             except:
    #                 pass
    #     if new_header:
    #         transactions.insert(0, new_header) 
    #     dfObj = pd.DataFrame(transactions) 

    elif bank_name == "ICICI BANK":
        if len(new_header) == 9:
            d_i = 0       
            p_i = 1     
            for v_t in valid_transactions:
                if v_t[d_i] is None or type(v_t[d_i]) == type(None) or str(v_t[d_i]) == 'nan'  :
                    if v_t[p_i] is not None :
                        if str(v_t[p_i]) != 'nan':  
                            transactions[-1][p_i] = str(transactions[-1][p_i]) + str(v_t[p_i])
                else:
                    transactions.append(v_t)

            if new_header:
                transactions.insert(0, new_header) 

            dfObj = pd.DataFrame(transactions) 

            statement =dfObj
            statement.rename(columns=statement.iloc[0], inplace = True)
            statement.drop([0], inplace = True)
            statement['Credit'] = "" 

            print("list(statement.columns.values)",list(statement.columns.values))
            statement.loc[statement['Dr/Cr'] == 'CR', 'Credit'] = statement['Amount']
            statement.loc[statement['Dr/Cr'] == 'CR', 'Amount'] = ''
            # print(statement)
            dfObj = statement
              
        elif bank_type == 'ICICI BANK 80':
            d_i = 0       
            p_i = 1     
            for v_t in valid_transactions:
                if v_t[d_i] is None or type(v_t[d_i]) == type(None) or str(v_t[d_i]) == 'nan'  :
                    if v_t[p_i] is not None :
                        if str(v_t[p_i]) != 'nan':  
                            transactions[-1][p_i] = str(transactions[-1][p_i]) + str(v_t[p_i])
                else:
                    transactions.append(v_t)
            if new_header:
                transactions.insert(0, new_header)
            dfObj = pd.DataFrame(transactions)

        elif bank_type == 'ICICI BANK 81':
            d_i = 0       
            p_i = 1     
            for v_t in valid_transactions:
                if v_t[d_i] is None or type(v_t[d_i]) == type(None) or str(v_t[d_i]) == 'nan'  :
                    if v_t[p_i] is not None :
                        if str(v_t[p_i]) != 'nan':  
                            transactions[-1][p_i] = str(transactions[-1][p_i]) + str(v_t[p_i])
                else:
                    transactions.append(v_t)
            if new_header:
                transactions.insert(0, new_header)
            dfObj = pd.DataFrame(transactions)

        elif bank_type == 'ICICI BANK 82':
            d_i = 7       
            p_i = 4
            index_0 = 0     
            for v_t in valid_transactions:
                if v_t[d_i] is None or type(v_t[d_i]) == type(None) or str(v_t[d_i]) == 'nan'  :
                    if v_t[p_i] is not None :
                        if str(v_t[p_i]) != 'nan':  
                            transactions[-1][p_i] = str(transactions[-1][p_i]) + str(v_t[p_i])
                    if v_t[index_0] is not None :
                        if str(v_t[index_0]) != 'nan':
                            try:     
                                transactions[-1][index_0] = str(transactions[-1][index_0]) + str(v_t[index_0])
                                transactions[-1][index_0] = transactions[-1][index_0].replace('None','').replace('nan','')
                            except:
                                pass
                else:
                    transactions.append(v_t)
            if new_header:
                transactions.insert(0, new_header)
            dfObj = pd.DataFrame(transactions)

        elif len(new_header) == 6:
            d_i =  0       
            p_i =  2      
            for v_t in valid_transactions:
                print(">>>>",v_t[d_i],type(v_t[d_i]),len(v_t[d_i]))
                if v_t[d_i] is None or type(v_t[d_i]) == type(None) or str(v_t[d_i]) == 'nan' or not str(v_t[d_i]).replace(" ",""):
                    if v_t[p_i] is not None :
                        if str(v_t[p_i]) != 'nan':  
                            try:
                                transactions[-1][p_i] = str(transactions[-1][p_i]) + ' '+ str(v_t[p_i])
                            except:
                                print(traceback.print_exc())
                                pass
                else:
                    transactions.append(v_t)                    
            if new_header:
                transactions.insert(0, new_header) 

            dfObj = pd.DataFrame(transactions) 



    elif bank_name == "PAYTM PAYMENTS BANK": 
               
        d_i = 3        
        p_i = 1       
        for v_t in valid_transactions:
            if v_t[d_i] is None or type(v_t[d_i]) == type(None) or str(v_t[d_i]) == 'nan' :
                if v_t[p_i] is not None :
                    if str(v_t[p_i]) != 'nan':
                        try:
                            transactions[-1][p_i] = str(transactions[-1][p_i]) + str(v_t[p_i])
                        except:
                            pass

            else:
                transactions.append(v_t)
                
        if new_header:
            transactions.insert(0, new_header) 
            
        dfObj = pd.DataFrame(transactions) 
        # dfObj.loc[2,list(statement.columns.values)]=1
        dfObj.xs(0)[4] = "CR_DR"
        # print("+++++++++++++++++++++++++++ dfObj ++++++++++++++++++++++++++\n",dfObj)
        
        # dfObj.to_csv('xxx.csv', encoding='utf-8',header=False, index=False)
        
        # statement = pd.read_csv('xxx.csv')
        statement =dfObj
        statement.rename(columns=statement.iloc[0], inplace = True)
        statement.drop([0], inplace = True)
        statement.rename(columns = {4: 'col_1_new_name'}, inplace = True)

        print("statement\n",statement)
        statement['Credit'] = "" 

        print("list(statement.columns.values)\n",list(statement.columns.values))
        xx = statement['Amount'].values.tolist()
        for item in xx:
            if item.lower().__contains__('+'):
                statement.loc[statement['Amount'] == item , 'Credit'] = statement['Amount']
                statement.loc[statement['Amount'] == item, 'Amount'] = ''
        statement.rename(columns = {'Amount': 'Debit'}, inplace = True)
        dfObj = statement.copy()
        
        print("***************************\n",statement)  
        # if new_header:
        #     transactions.insert(0, new_header) 
        # dfObj = pd.DataFrame(transactions) 

    elif bank_name == "PUNJAB NATIONAL BANK": 
               
        if len(new_header) == 6:
            d_i =  4       
            p_i =  5      
            for v_t in valid_transactions:
                # print("..>>",v_t[d_i])
                if v_t[d_i] is None or type(v_t[d_i]) == type(None) or str(v_t[d_i]) == 'nan' or not v_t[d_i]  :
                    if v_t[p_i] is not None :
                        if str(v_t[p_i]) != 'nan':  
                            try:
                                transactions[-1][p_i] = str(transactions[-1][p_i]) + str(v_t[p_i])
                                transactions[-1][p_i] = transactions[-1][p_i].replace('None','').replace('nan','')
                            except:
                                pass
                else:
                    transactions.append(v_t)     

        elif len(new_header) == 8:   
            d_i =  4       
            p_i =  5      

            for v_t in valid_transactions:
                # print("..>>",v_t[d_i])
                if v_t[d_i] is None or type(v_t[d_i]) == type(None) or str(v_t[d_i]) == 'nan' or not v_t[d_i]  :
                    if v_t[p_i] is not None :
                        if str(v_t[p_i]) != 'nan':  
                            try:
                                transactions[-1][p_i] = str(transactions[-1][p_i]) + str(v_t[p_i])
                            except:
                                pass
                else:
                    transactions.append(v_t)                  
        
        
        if new_header:
            transactions.insert(0, new_header) 
        dfObj = pd.DataFrame(transactions) 

    elif bank_name == "STATE BANK OF INDIA":
        d_i =  6        #index of date column        from BANK_DETAILS
        p_i =  2        #index of particular(transaction) column  from BANK_DETAILS
        index_0=0
        index_1 = 1
        index_3 = 3
        for v_t in valid_transactions:
            if v_t[d_i] is None or type(v_t[d_i]) == type(None) or str(v_t[d_i]) == 'nan':
                if v_t[p_i] is not None:
                    if str(v_t[p_i]) != 'nan':
                        try:
                            transactions[-1][p_i] += str(v_t[p_i])

                        except:
                            pass
                if v_t[index_0] is not None:
                    if str(v_t[index_0]) != 'nan':
                        try:
                            transactions[-1][index_0] = str(transactions[-1][index_0])+' '+ str(v_t[index_0])
                            transactions[-1][index_0] = transactions[-1][index_0].replace('None','').replace('nan','')
                        except:
                            pass
                if v_t[p_i] is not None:
                    if str(v_t[index_1]) != 'nan':
                        try:
                            transactions[-1][index_1] = str(transactions[-1][index_1])+' '+ str(v_t[index_1])
                            transactions[-1][index_1] = transactions[-1][index_1].replace('None','').replace('nan','')
                        except:
                            pass
                if v_t[p_i] is not None:
                    if str(v_t[index_3]) != 'nan':
                        try:
                            transactions[-1][index_3] = str(transactions[-1][index_3])+' '+ str(v_t[index_3])
                            transactions[-1][index_3] = transactions[-1][index_3].replace('None','').replace('nan','')
                        except:
                            pass
            else:
                transactions.append(v_t)
        if new_header:
            transactions.insert(0, new_header)
        dfObj = pd.DataFrame(transactions) 


    elif bank_name == "TAMILNAD MERCANTILE BANK LTD":
        d_i =  0        #index of date column        from BANK_DETAILS
        p_i =  2        #index of particular(transaction) column  from BANK_DETAILS

        for v_t in valid_transactions:
            if v_t[d_i] is None or type(v_t[d_i]) == type(None):
                if v_t[p_i] is not None:
                    if str(v_t[p_i]) != 'nan':
                        try:
                            transactions[-1][p_i] += str(v_t[p_i])
                        except:
                            pass
            else:
                transactions.append(v_t)
        if new_header:
            transactions.insert(0, new_header)
        dfObj = pd.DataFrame(transactions) 


    elif bank_name == "SARASWAT CO-OPERATIVE BANK LTD.":
        print("----------- SARASWAT CO-OPERATIVE BANK LTD. -----------")
        transactions = []  
        # try:
        yyy = ''
        b_i = 5
        index_2 = 2
        for v_t in valid_transactions:
            if v_t[b_i] is None or type(v_t[b_i]) == type(None) or str(v_t[b_i]) == 'nan': 
                if v_t[index_2] is not None :
                    if str(v_t[index_2]) != 'nan':   
                        try:
                            yyy = str(v_t[index_2])
                        except:
                            print(traceback.print_exc())
                            pass
            else:
                try:
                    transactions.append(v_t)
                    if yyy:
                        transactions[-1][index_2] = yyy + ' ' + str(transactions[-1][index_2])
                        transactions[-1][index_2] = transactions[-1][index_2].replace('None','').replace('nan','')
                    yyy = ''
                except:
                    print(traceback.print_exc())
                    pass
        if new_header:
            transactions.insert(0, new_header) 
        dfObj = pd.DataFrame(transactions) 

    elif bank_name == "UNION BANK OF INDIA":
        print("++++++++++++++++++++++++  UNION BANK OF INDIA ++++++++++++++++")
        d_i =  0        
        p_i =  1  
        utr_no = 3     
        if len(new_header) == 8:        
            for index,v_t in enumerate(valid_transactions):
                # if index == len(valid_transactions) - 1:
                #     print('last_row',v_t)
                if v_t[d_i] is None or type(v_t[d_i]) == type(None) or str(v_t[d_i]) == 'nan' :
                    if v_t[p_i] is not None :
                        if str(v_t[p_i]) != 'nan':
                            try:
                                transactions[-1][p_i] = str(transactions[-1][p_i]) + str(v_t[p_i])
                                transactions[-1][p_i] = transactions[-1][p_i].replace('None','').replace('nan','')

                            except:
                                print(traceback.print_exc())
                                pass
                    if v_t[utr_no] is not None:
                        if str(v_t[utr_no]) != 'nan':
                            try:
                                transactions[-1][utr_no] = str(transactions[-1][utr_no])+' '+ str(v_t[utr_no])
                                transactions[-1][utr_no] = transactions[-1][utr_no].replace('None','').replace('nan','')
                            except:
                                pass

                else:
                    transactions.append(v_t)
                
        if new_header:
            transactions.insert(0, new_header) 
        dfObj = pd.DataFrame(transactions)

    elif bank_name == "YES BANK":
        d_i =  0        #index of date column        from BANK_DETAILS
        p_i =  2        #index of particular(transaction) column  from BANK_DETAILS

        for v_t in valid_transactions:
            if v_t[d_i] is None or type(v_t[d_i]) == type(None):
                if v_t[p_i] is not None:
                    if str(v_t[p_i]) != 'nan':
                        try:
                            transactions[-1][p_i] += str(v_t[p_i])
                        except:
                            pass
            else:
                transactions.append(v_t)
        if new_header:
            transactions.insert(0, new_header)
        dfObj = pd.DataFrame(transactions) 

    elif bank_name == "UJJIVAN SMALL FINANCE BANK":
        d_i =  0        #index of date column        from BANK_DETAILS
        p_i =  1        #index of particular(transaction) column  from BANK_DETAILS

        for v_t in valid_transactions:
            if v_t[d_i] is None or type(v_t[d_i]) == type(None):
                if v_t[p_i] is not None:
                    if str(v_t[p_i]) != 'nan':
                        try:
                            transactions[-1][p_i] += str(v_t[p_i])
                        except:
                            pass
            else:
                transactions.append(v_t)
        if new_header:
            transactions.insert(0, new_header)
        dfObj = pd.DataFrame(transactions) 



    if not transactions or bank_name == "Unknown Bank" or dfObj.empty :
        print("----------- Unknown Bank -----------")
        transactions = []  
        print("+++++++++++ Balance Index +++++++++",balance_index)
        try:
            if balance_index:
                b_i = balance_index
                index_0 = 0
                index_1 = 1
                index_2 = 2
                index_3 = 3
                # if header_length >4:
                index_4 = 4
                # if header_length >5:
                index_5 = 5
                # if header_length >6:
                index_6 = 6
                # if header_length >7:
                index_7 = 7

                for v_t in valid_transactions:
                    if v_t[b_i] is None or type(v_t[b_i]) == type(None) or str(v_t[b_i]) == 'nan': 
                        if v_t[index_0] is not None :
                            if str(v_t[index_0]) != 'nan':
                                try:     
                                    transactions[-1][index_0] = str(transactions[-1][index_0]) + str(v_t[index_0])
                                    transactions[-1][index_0] = transactions[-1][index_0].replace('None','').replace('nan','')
                                except:
                                    pass
                        if v_t[index_1] is not None :
                            if str(v_t[index_1]) != 'nan': 
                                try:            
                                    transactions[-1][index_1] = str(transactions[-1][index_1]) + str(v_t[index_1])
                                    transactions[-1][index_1] = transactions[-1][index_1].replace('None','').replace('nan','')
                                except:
                                    pass
                        if v_t[index_2] is not None :
                            if str(v_t[index_2]) != 'nan':   
                                try:            
                                    transactions[-1][index_2] = str(transactions[-1][index_2]) + ' ' + str(v_t[index_2])
                                    transactions[-1][index_2] = transactions[-1][index_2].replace('None','').replace('nan','')
                                except:
                                    pass        
                        if v_t[index_3] is not None :
                            if str(v_t[index_3]) != 'nan': 
                                try:              
                                    transactions[-1][index_3] = str(transactions[-1][index_3]) + ' ' + str(v_t[index_3])
                                    transactions[-1][index_3] = transactions[-1][index_3].replace('None','').replace('nan','')
                                except:
                                    pass
                        if header_length >4:
                            if v_t[index_4] is not None :
                                if str(v_t[index_4]) != 'nan':  
                                    try:             
                                        transactions[-1][index_4] = str(transactions[-1][index_4]) + str(v_t[index_4])
                                        transactions[-1][index_4] = transactions[-1][index_4].replace('None','').replace('nan','')
                                    except:
                                        pass
                        if header_length >5:
                            if v_t[index_5] is not None :
                                if str(v_t[index_5]) != 'nan':               
                                    try:
                                        transactions[-1][index_5] = str(transactions[-1][index_5]) + str(v_t[index_5])
                                        transactions[-1][index_5] = transactions[-1][index_5].replace('None','').replace('nan','')
                                    except:
                                        pass
                        if header_length >6:
                            if v_t[index_6] is not None :
                                if str(v_t[index_6]) != 'nan':    
                                    try:           
                                        transactions[-1][index_6] = str(transactions[-1][index_6]) + str(v_t[index_6])   
                                        transactions[-1][index_6] = transactions[-1][index_6].replace('None','').replace('nan','') 
                                    except:
                                        pass
                        if header_length >7:
                            if v_t[index_7] is not None :
                                if str(v_t[index_7]) != 'nan':   
                                    try:            
                                        transactions[-1][index_7] = str(transactions[-1][index_7]) +  str(v_t[index_7])
                                        transactions[-1][index_7] = transactions[-1][index_7].replace('None','').replace('nan','')
                                    except:
                                        pass  
                    else:
                        transactions.append(v_t)
        except:
            print(traceback.print_exc())
            d_i =  0       
            p_i =  2        
            for v_t in valid_transactions:
                if v_t[d_i] is None or type(v_t[d_i]) == type(None) or str(v_t[d_i]) == 'nan':
                    if v_t[p_i] is not None:
                        if str(v_t[p_i]) != 'nan':
                            try:
                                transactions[-1][p_i] += str(v_t[p_i])
                            except:
                                pass
                else:
                    transactions.append(v_t)
        if new_header:
            transactions.insert(0, new_header) 
        dfObj = pd.DataFrame(transactions) 
    return dfObj,bank_type