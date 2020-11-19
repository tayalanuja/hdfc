import collections
import tensorflow as tf
import pandas as pd
from PIL import Image
import os
import io
import re
import cv2
import numpy as np
from pdf2image import convert_from_path
from flask import jsonify
import config.config as project_configs

from .image_orientationandskew_correction import *
from .Utilityfunctions import *
import traceback
import sys
import os

# What model to download.
# Path to frozen detection graph. This is the actual model that is used for the object detection.
PATH_TO_CKPT = project_configs.INTAIN_CREDIT_INTERFACE_GRAPH

# List of the strings that is used to add correct label for each box.
PATH_TO_LABELS = project_configs.INTAIN_BANK_STATEMENT_LABEL_MAP

NUM_CLASSES = 19


print('Pay Slip Loading model')
print(os.getcwd())
detection_graph = tf.Graph()
with detection_graph.as_default():
    od_graph_def = tf.GraphDef()
    with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')
print('Pay Slip Model loaded successfully.')

label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES,use_display_name=True)
category_index = label_map_util.create_category_index(categories)


''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
size= (600,800)
#def pdf2jpg(pdf_file):
def salaryslip_detection(img_file,df):

    try:
        im= Image.open(img_file)
        im_resized = im.resize(size, Image.ANTIALIAS)
        
        salaryslipattributes= salaryslip_extraction(df,img_file,im_resized,detection_graph,label_map,category_index)
        print(salaryslipattributes)
        final_data = []
        # labels = ['EMPLOYER NAME','EMPLOYER ADDRESS','EMPLOYEE NAME','EMPLOYEE ID','EMPLOYEE PANNO','EMPLOYEE UANNO','EMPLOYEE DOJ','EMPLOYEE DESIGNATION','BANKACCTNO','BANKNAME','PERIODOFPAY','NETSALARY']
        # varnames=['employer_name','employer_address','employee_name','employee_id','employee_panno','employee_uanno','employee_doj','employee_designation','bank_accoutnno','bank_name','periodofpay','net_salary']
        # labels = ['EMPLOYER NAME','EMPLOYER ADDRESS','EMPLOYEE NAME','EMPLOYEE ID','EMPLOYEE PANNO','EMPLOYEE UANNO','EMPLOYEE DOJ','EMPLOYEE DESIGNATION','BANKACCTNO','BANKNAME','PERIODOFPAY','NETSALARY']
        # varnames=['employer_name','employer_address','employee_name','employee_id','employee_panno','employee_uanno','employee_doj','employee_designation','bank_accoutnno','bank_name','periodofpay','net_salary']
        labels = ['EMPLOYER NAME','EMPLOYEE NAME','PERIODOFPAY','NETSALARY','GROSSSALARY']
        varnames=['employer_name','employee_name','periodofpay','net_salary','gross_salary']
        dickey = ['confidence_score','confidence_score_green','label','order_id','value','varname']
        for i, data in enumerate(salaryslipattributes):
            dicvalue = [data[1], 70, labels[i],i,data[0],varnames[i]]
            res = {dickey[i]: dicvalue[i] for i in range(len(dickey))}
            final_data.append(res)        
        response={}
        response["Attribute_values"]=final_data
        return response

    except Exception as e:
        print(e)
        print(traceback.print_exc())
        return "NA"

if __name__ == "__main__":
    # input_image_path = '/home/jyoti/Desktop/GraphCNN/Payslips/payslip-data21april/payslip-data/24.jpg'
    # output_folder_path = '/home/jyoti/Desktop/GraphCNN/Payslips/payslip-data21april/Testfolder'
    input_image_path = '/home/anuja/backup/Dropbox/Datasets/Salary Slip-20200909T060323Z-001/image-test/20_0.jpg'

    output_folder_path = '/home/anuja/backup/Dropbox/Datasets/Salary Slip-20200909T060323Z-001/bank/'
    out_imPath=orientation_correction(output_folder_path, input_image_path)
    out_image_path=skewcorrect(out_imPath)
    df, _ = visionocr(out_image_path, 'apikey.json')
    response=salaryslip_detection(out_image_path,df)
    print(response)



