from datetime import datetime
import time
#import base64
import pickle
import nltk
# import spacy
import traceback
import pandas as pd

from .Pay_Slip import Utilityfunctions,FunctionLibrary,image_orientationandskew_correction
from .Pay_Slip.Testing import salaryslip_detection
from .Pay_Slip.Utilityfunctions import *

import config.config as project_configs

key = project_configs.INTAIN_BANK_STATEMENT_GOOGLE_APPLICATION_CREDENTIALS

def hr_payslip(file_path):
    try:
            output_folder_path = os.getcwd()+"/webserverflask/static/data/temp/"
        #     output_folder_path = os.getcwd()
            print(file_path,output_folder_path)
            out_imPath=image_orientationandskew_correction.orientation_correction(output_folder_path, file_path)
            out_image_path=image_orientationandskew_correction.skewcorrect(out_imPath)
            df, _ = Utilityfunctions.visionocr(out_image_path, key)
            response = salaryslip_detection(out_image_path,df)
            # print(response)
            data={}
            for i in response['Attribute_values']:
                    data[i['varname']]=i['value']
            return(data)

    except:
        print(traceback.print_exc())

        data = {}
        data['employer_name'] = "NA"
        data['employer_address'] = 'NA'
        data['employee_name'] = 'NA'
        data['employee_id'] = 'NA'
        data['employee_panno'] = 'NA'
        data['employee_uanno'] = 'NA' 
        data['employee_doj'] =  'NA'
        data['employee_designation'] =  'NA'
        data['bank_accoutnno'] =  'NA'
        data['bank_name'] = "NA"
        data['periodofpay'] = 'NA'
        data['net_salary'] = 'NA'        
        return data


if __name__ == "__main__":
        file_dir="/home/anuja/backup/Dropbox/Datasets/Salary Slip-20200909T060323Z-001/image-test/"
        result=pd.DataFrame()
        for file_name in os.listdir(file_dir):
                response=hr_payslip(file_dir+file_name)
                # print(response)
                data={}
                for i in response['Attribute_values']:
                        data[i['varname']]=i['value']
                data['file']=file_name
                print(data)
                # print(type(data))
                # result=result.append({'file':data['file'],'employer_name':data['employer_name'],'employee_name':data['employee_name'],'net_salary':data['net_salary'],'periodofpay':data['periodofpay']},ignore_index = True)

        # print(result)
        # excel_path="/home/anuja/backup/Dropbox/Datasets/Salary Slip-20200909T060323Z-001/resultsall.csv"
        # writer = pd.ExcelWriter(excel_path,engine='xlsxwriter')
        # df.to_excel(writer)
        # result.to_csv(excel_path)
 

