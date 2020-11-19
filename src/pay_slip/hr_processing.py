import os
import cv2 as cv
import traceback
import shutil
import time
import pandas as pd
from PIL import Image
import json
from .payslip import hr_payslip
from . import payslip_db
from . import functions_library
import config.config as project_configs

import pprint

base_dir = os.getcwd()
print(base_dir)
data_dir = os.path.join(base_dir, "webserverflask","static", "data")
if not os.path.isdir(data_dir):
    os.makedirs(data_dir)
input_dir = os.path.join(data_dir, "ss_input")
if not os.path.isdir(input_dir):
    os.makedirs(input_dir)
images_dir = os.path.join(data_dir, "images")
if not os.path.isdir(images_dir):
    os.makedirs(images_dir)
excel_dir = os.path.join(data_dir, "excels")
if not os.path.isdir(excel_dir):
    os.makedirs(excel_dir)
    
with open(project_configs.INTAIN_CREDIT_ATTRIBUTE_JSON) as jsFile:
    attr_config_dict = json.load(jsFile)

attrs = []
########################################################################################################################
def extract_images(emailid, job_dir):
    job_dir = "Job_"+job_dir
    job_status = "In Process"    
    payslip_db.update_jobstatus(emailid, job_dir.replace("Job_", ""), job_status)
    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    print("Processing Job |", job_dir)
    job_dir_path = os.path.join(input_dir, job_dir)
    pdf_inv_list = os.listdir(job_dir_path)
    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    images_job_dir = os.path.join(images_dir, job_dir)
    if os.path.isdir(images_job_dir):
        shutil.rmtree(images_job_dir)
    os.makedirs(images_job_dir)
    index=0
    excel_result=pd.DataFrame()
    excel_path=os.path.join("static","data","excels", job_dir+'.xlsx')
    full_path=os.path.join(excel_dir,job_dir+'.xlsx')
    batch_name=payslip_db.get_batch_name(job_dir)

    for pdf_inv in pdf_inv_list:
        try:
            database_data = {}
            database_data['emailid'] = emailid
            database_data['job_id'] = job_dir.replace("Job_", "")
            database_data['file_name'] = pdf_inv
            # database_data['user_edited'] = False
            curtime=time.time()
            ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
            print("Processing Document |", pdf_inv)
            pdf_filepath = os.path.join(job_dir_path, pdf_inv)
            database_data['image_path'] = os.path.join("static","data", "ss_input", job_dir, pdf_inv)
            output_dir_name = os.path.splitext(pdf_inv)[0]
            output_dir_path = os.path.join(images_job_dir, output_dir_name)
            if os.path.isdir(output_dir_path):
                shutil.rmtree(output_dir_path)
            os.makedirs(output_dir_path)
            print("Splitting Document...")
            # if pdf_filepath.split(".")[-1]=="pdf":
            num_images = functions_library.wandPdfSplit(pdf_filepath, output_dir_path)
            print("Splitting done. Document has", str(num_images), "images")
            ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
            print("Running AI...")
            imagelist=[]
            inv_img_list = sorted(os.listdir(output_dir_path))
            # inv_img_list = [f for f in inv_img_list if f.lower().endswith(".jpg")]
            resultlist=[]
            for inv_img in inv_img_list:
                img_path = os.path.join(output_dir_path, inv_img)
                imgpath1='static' + img_path.split('static')[1]
                imagelist.append(imgpath1)
                database_data['images'] = sorted(imagelist)
                excel_result.at[index,'file']=inv_img
                excel_result.at[index,'Applicant ID']=batch_name
                final_output={}
                input_img_path = os.path.join(output_dir_path, inv_img)
                inv_img_name = os.path.splitext(inv_img)[0]
                response = hr_payslip(input_img_path)
                attrs = attr_config_dict['attrs_payslip']
                base_dir = os.getcwd()
                data_dir = os.path.join(base_dir, "static", "data")
                result={}
                input_image_path = 'static' + input_img_path.split('static')[1]

                for i in range(len(list(attrs))):
                    attrib = attrs[i]
                    result[attrib] = response[attrib]
                    excel_result.at[index,attrib]=response[attrib]
                    # database_data[attrib + "_X0"] = 0
                    # database_data[attrib + "_Y0"] = 0
                    # database_data[attrib + "_W"] = 0
                    # database_data[attrib + "_H"] = 0
                    result[attrib + "_user_edited"] = 0 # user edited flag
                    if response[attrib] == 'NA':
                        result[attrib + "_conf"] = 0
                    else:
                        result[attrib + "_conf"] = .7
                # print(result,inv_img)
                final_output["Output"]=result
                print("imgpath1",imgpath1)
                final_output["image"]=imgpath1
                resultlist.append(final_output)
                print("final_output",final_output)

                index=index+1
            database_data["Result"]=resultlist
            database_data['image_path'] = os.path.join("static","data", "ss_input", job_dir, pdf_inv)
            payslip_db.payslip_result(database_data,excel_path)

        except Exception as e:
            database_data = {}
            database_data['emailid'] = emailid
            database_data['job_id'] = job_dir.replace("Job_", "")
            database_data['file_name'] = pdf_inv
            database_data['image_path'] = os.path.join("static","data", "ss_input", job_dir, pdf_inv)
            # database_data['excel_path'] = "static/data/excels/"+job_dir+"_"+ output_dir_name + '_table.csv'

            #database_data['excel_path'] = "static/data/excels/"+job_dir+"_"+ output_dir_name + '_table.xlsx'

            for attrib in attrs:
                database_data[attrib] = "NA"
                database_data[attrib + "_conf"] = 0.0
                excel_result.at[index,attrib]="NA"
                # database_data[attrib + "_X0"] = 0.0
                # database_data[attrib + "_Y0"] = 0.0
                # database_data[attrib + "_W"] = 0.0
                # database_data[attrib + "_H"] = 0.0
                # database_data[attrib + "_image"] = os.path.join("static","data", "input", job_dir, pdf_inv)
            index=index+1    
            # Handle few other keys
            try:
                database_data['images'] = sorted(imagelist)
            except NameError:
                database_data['images'] = []

            print(traceback.print_exc())
            payslip_db.payslip_result(database_data,excel_path)
            ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
        
        curtime1=time.time()
        print("----------Document Processed----------",curtime1-curtime)

        job_status = "Complete"
        print("excel result",excel_result)
        writer = pd.ExcelWriter(full_path,engine='openpyxl')
        excel_result.to_excel(writer,sheet_name = 'Payslip Result',index=False)
        writer.save()
        payslip_db.update_jobstatus(emailid, job_dir.replace("Job_", ""), job_status)
        print("----------Job Processed----------")
        # access_db.update_excel(emailid, job_dir)
        print("------------END------------")

if __name__ == "__main__":
    pass
