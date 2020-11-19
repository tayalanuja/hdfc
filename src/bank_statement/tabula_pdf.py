import tabula
import pandas as pd
import numpy as np
import traceback
from .correct_df import get_correct_df
from .valid_dataframe_single_page import get_valid_dataframe_single_page

def get_table_data(input_pdf,income_document_image, inputleft, inputtop, inputwidth, inputheight, bank_name,columns_distance_values,reduced_percentage,pdf_file_path):
    input_pdf.append(income_document_image)
    # reduced_percentage = reduced_percentage.strip()
    reduced_percentage = float(reduced_percentage)
    page_num = len(input_pdf)
    if input_pdf[0].endswith('-page1.jpg'):
        page_num += 1

    print ('++++ inputleft,inputtop,inputwidth,inputheight == {} ,columns_distance_values == {} -----'.format((inputleft, inputtop, inputwidth, inputheight),columns_distance_values))

    top = float(inputtop)/reduced_percentage
    left = float(inputleft)/reduced_percentage
    bottom = float(inputheight)+float(inputtop)
    bottom = float(bottom)/reduced_percentage
    right_width = float(inputleft) + float(inputwidth)
    right_width = float(right_width)/reduced_percentage

    for i, val in enumerate(columns_distance_values): 
        columns_distance_values[i] = (float(val)/reduced_percentage + float(inputleft)/reduced_percentage)
    columns_distance_values = sorted(columns_distance_values)
    columns_distance_values = tuple(columns_distance_values)

    df = tabula.read_pdf(pdf_file_path, guess=False, pages= page_num , silent=True,
                    pandas_options={
                        'header': None,
                        'error_bad_lines': False,
                        'warn_bad_lines': False
                    },  encoding="utf-8",area = (top,left,bottom,right_width), columns = columns_distance_values)   
    try:
        rows = df.values.tolist()
        df = pd.DataFrame(rows)
        bank_name = bank_name.strip()
        if bank_name == "CANARA BANK" or bank_name == "BANK OF WIKI" or bank_name=="HDFC BANK":
            df = get_valid_dataframe_single_page(df,bank_name,page_num)
    except:
        df = pd.DataFrame()
    return df


def get_direct_table_data(pdf_file,page_count,bank_name):
    pagewise_dataframes = []
    for page_number in range(1,page_count+1):
        print('Statement is processing for page number : ',page_number)
        try:
            df = get_page_df(pdf_file,bank_name,page_number)
            print(" DataFrame for page number {} is\n".format(page_number),df)
            
        except:
            print(traceback.print_exc())
            df = pd.DataFrame()
        if isinstance(df, pd.DataFrame):
            if not df.empty:
                df = get_correct_df(df,bank_name)
                pagewise_dataframes.append(df)
    final_data = pd.concat(pagewise_dataframes, ignore_index = True)
    print("++++++++++++++++++++++++ final Data ++++++++++++++++++++++++\n",final_data)
    return final_data

def get_page_df(pdf_file,bank_name,page_number):
    if bank_name == 'ICICI BANK':

        df = tabula.read_pdf(pdf_file,index= False,pages = page_number,multiple_tables=True,pandas_options={
                            'header': None, 
                        }) 
        count_row0 = df[0].shape[0]

        if len(df)==3:
            count_row1 = df[1].shape[0]
            count_row2 = df[2].shape[0]
            
        elif len(df)==2:
            count_row1 = df[1].shape[0]
            if count_row1>count_row0:
                df = df[1]
            else:
                df = df[0]
        else:
            df = df[0]

    elif bank_name == 'KARUR VYSYA BANK':
        df = tabula.read_pdf(pdf_file,index= False,pages = page_number,multiple_tables=True,pandas_options={
                            'header': None, 
                        }) 
        count_row0 = df[0].shape[0]
            
        if len(df)==2:
            count_row1 = df[1].shape[0]
            if count_row1>count_row0:
                df = df[1]
            else:
                df = df[0]
        else:
            df = df[0]

    elif bank_name == 'UJJIVAN SMALL FINANCE BANK':
        df = tabula.read_pdf(pdf_file,index= False,pages = page_number,multiple_tables=True,pandas_options={
                            'header': None, 
                        }) 
        try:
            count_row0 = df[0].shape[0]
            if len(df)==2:
                count_row1 = df[1].shape[0]
                if count_row1>count_row0:
                    df = df[1]
                else:
                    df = df[0]
            else:
                df = df[0]
        except:
            df = pd.DataFrame()

    elif bank_name == 'BANDHAN BANK':
        df = tabula.read_pdf(pdf_file,index= False,pages = page_number,multiple_tables=True,pandas_options={
                            'header': None, 
                        }) 
        try:
            count_row0 = df[0].shape[0]
            if len(df)==2:
                count_row1 = df[1].shape[0]
                if count_row1>count_row0:
                    df = df[1]
                else:
                    df = df[0]
            else:
                df = df[0]
        except:
            df = pd.DataFrame()

    elif bank_name == 'BANK OF BARODA':

        df = tabula.read_pdf(pdf_file,index= False,pages = page_number,multiple_tables=True,pandas_options={
                            'header': None, 
                        }) 
        try:
            count_row0 = df[0].shape[0]

            # print(" ",len(df),'\n',df)
            if len(df)==3:
                count_row1 = df[1].shape[0]
                count_row2 = df[2].shape[0]
                
            elif len(df)==2:
                count_row1 = df[1].shape[0]
                if count_row1>count_row0:
                    df = df[1]
                else:
                    df = df[0]
            else:
                df = df[0]
        except:
            df = pd.DataFrame()


    elif bank_name == "AXIS BANK":            
        df = tabula.read_pdf(pdf_file,index= False,pages = page_number,pandas_options={
                            'header': None,
                            'error_bad_lines': False,
                            'warn_bad_lines': False
                        })
        bank_name_list = []
        if page_number == 1 and df.shape[1] == 8:
            if str(df.loc[0][7]) == 'Branch Name':
                bank_name = "AXIS BANK A"
                bank_name_list.append(bank_name)
            else:
                bank_name = "AXIS BANK"
                bank_name_list.append(bank_name)

        else:
            bank_name_list.append(bank_name)
            
        bank_name = bank_name_list[0]

    elif bank_name == 'HDFC BANK':

        df = tabula.read_pdf(pdf_file,index= False,pages = page_number,multiple_tables=True,pandas_options={
                            'header': None, 
                        }) 
        count_row0 = df[0].shape[0]

        if len(df)==3:
            count_row1 = df[1].shape[0]
            count_row2 = df[2].shape[0]
            
        elif len(df)==2:
            count_row1 = df[1].shape[0]
            if count_row1>count_row0:
                df = df[1]
            else:
                df = df[0]
        else:
            df = df[0]
    elif bank_name == 'DBS BANK':    
        if page_number >2:        
            df = tabula.read_pdf(pdf_file,index= False,pages = page_number,pandas_options={
                                'header': None,
                                'error_bad_lines': False,
                                'warn_bad_lines': False
                            })
        else:
            df = pd.DataFrame()
    else:            

        df = tabula.read_pdf(pdf_file,index= False,pages = page_number,pandas_options={
                            'header': None,
                            'error_bad_lines': False,
                            'warn_bad_lines': False
                        })
        if df is None:
            df = pd.DataFrame()
    return df
    # data = df.dropna(axis='columns', how='all')