
import pandas as pd
import numpy as np
import traceback
def get_valid_dataframe_single_page(df,bank_name,page_num):
    bank_name = bank_name.strip()
    rows = df.values.tolist()

    #################################### Header Extraction ###################################
    headers = []
    last_column = []
    number_of_columns = []
    for row in rows:
        last_column.append(row[len(row)-1])
        number_of_columns.append(len(row)-1)
    number_of_columns = number_of_columns[0]
    for i,row in enumerate(rows):
        # print("*******",last_column[i])
        number_of_columns = len(row)-1
        # print("KKKKK",row[len(row)-1])
        
        if str(row[len(row)-1]) == str(last_column[0]) and str(last_column[0]) != 'nan':
            headers.append(row)
            # print("IIIIIIIIIIII",headers)
        if (str(last_column[1]) == 'nan' or last_column[1] is None )and i == 1:
            headers.append(row)
            # print("^^^^^^")
        if i == 3:
            break
    # print(">>>>>>>",number_of_columns)
    new_header = []

    if headers:
        header_length = len(headers[0])
        for i in range(header_length):

            if len(headers) == 2:
                res2 = str(headers[0][i]) + ' ' + str(headers[1][i])
            elif len(headers) == 3:
                res2 = str(headers[0][i]) + ' ' + str(headers[1][i]) + ' ' +str(headers[2][i])
            elif len(headers) == 1:
                res2 = str(headers[0][i])
            else:
                res2 = ''
            res2 = res2.replace("None","").replace('nan','')
            new_header.insert(i,res2)
    
    else:
        headers = [None] * number_of_columns

    # print('new_header',headers)

        
    # print('new_headerrrrrrrrrrrrrrrrrrrrrr',new_header)

    
    balance_key = ['balance(inr)','balance (inr)','balance','balance(in rs.)','balance amount','closing balance','account balance']
    for index,item in enumerate(new_header):
        for header_item in balance_key:
            if header_item == item.lower().strip() or header_item.lower().__contains__(item.lower().strip()):
                balance_index = index

    ################################# Valid Transaction ###########################
    # valid_transactions = [] 
    # for row in rows:
    #     if row not in headers:
    #         valid_transactions.append(row)
    valid_transactions = rows
    ################################# Bank ########################################

    transactions = []   
    if bank_name == "HDFC BANK":  
        d_i =  0        
        p_i =  1        
        for v_t in valid_transactions:
            if v_t[d_i] is None or type(v_t[d_i]) == type(None) or str(v_t[d_i]) == 'nan': 
                if v_t[p_i] is not None :
                    if str(v_t[p_i]) != 'nan': 
                                                
                        try:
                            transactions[-1][p_i] = str(transactions[-1][p_i]) + ' ' + str(v_t[p_i])
                        except:
                            transactions.append(v_t)              
                        # transactions[-1][p_i] = str(transactions[-1][p_i]) + str(v_t[p_i])
            else:
                transactions.append(v_t)             
        # if new_header:
        #     transactions.insert(0, new_header) 
        dfObj = pd.DataFrame(transactions) 
        # print("XXXXXXXXXXXXXX",dfObj)

    elif bank_name == "CANARA BANK" or bank_name == "BANK OF WIKI":
        # if page_num > 0:


        b_i =  6        #index of date column        from BANK_DETAILS
        p_i =  3        #index of particular(transaction) column  from BANK_DETAILS
        for v_t in valid_transactions:
            # print("** v_t[b_i] **",v_t[b_i])
            if v_t[b_i] is None or type(v_t[b_i]) == type(None) or str(v_t[b_i]) == 'nan'  or v_t[b_i] == 'nan':
                # print("KKK ",v_t[p_i])
                if v_t[p_i] is not None:
                    if str(v_t[p_i]) != 'nan':
                        
                        try:
                            transactions[-1][p_i] = str(transactions[-1][p_i]) + ' ' + str(v_t[p_i])
                        except:
                            transactions.append(v_t)
                        #     transactions[-1][p_i] = str(v_t[p_i])
                        #     print("KKKlll ",transactions[-1][p_i])
                        # else:
                        #     transactions[-1][p_i] = str(transactions[-1][p_i]) + ' ' + str(v_t[p_i])

            else:   
                # print('++ ',v_t)
                transactions.append(v_t)
        # if new_header:
        #     transactions.insert(0, new_header) 
        dfObj = pd.DataFrame(transactions)


    if bank_name == "KOTAK MAHINDRA BANK":
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
        return dfObj

    if not transactions or bank_name == "Unknown Bank" or dfObj.empty :
        print("----------- Unknown Bank -----------")
        transactions = []  
        try:
            if balance_index:
                b_i = balance_index
                index_0 = 0
                index_1 = 1
                index_2 = 2
                index_3 = 3
                if header_length >4:
                    index_4 = 4
                if header_length >5:
                    index_5 = 5
                if header_length >6:
                    index_6 = 6
                if header_length >7:
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
                                    transactions[-1][index_2] = str(transactions[-1][index_2]) + str(v_t[index_2])
                                    transactions[-1][index_2] = transactions[-1][index_2].replace('None','').replace('nan','')
                                except:
                                    pass        
                        if v_t[index_3] is not None :
                            if str(v_t[index_3]) != 'nan': 
                                try:              
                                    transactions[-1][index_3] = str(transactions[-1][index_3]) + str(v_t[index_3])
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
                                        transactions[-1][index_7] = str(transactions[-1][index_7]) + str(v_t[index_7])
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

    return dfObj