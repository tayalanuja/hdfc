import io
import os
import re
import csv
import traceback
import pandas as pd
from google.cloud import vision
from google.cloud.vision import types
import config.config as project_configs
from .process_BS import ocr,group_ocr_words,generate_lines
from pdf2image import convert_from_path
from PIL import Image
# Image.MAX_IMAGE_PIXELS = None


apikey = project_configs.INTAIN_BANK_STATEMENT_GOOGLE_APPLICATION_CREDENTIALS
ifsc_code = project_configs.INTAIN_BANK_STATEMENT_IFSC_CODE_CSV
bank_tags = project_configs.INTAIN_BANK_STATEMENT_BANK_TAGS_CSV

def google_vision(file_name):
    try:
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = apikey
        client = vision.ImageAnnotatorClient()

        with io.open(file_name, 'rb') as image_file:
            content = image_file.read()
        image = types.Image(content=content)
        response=client.text_detection(image=image)
        texts = response.text_annotations

        for text in texts:
            
            vertices = (['{},{}'.format(vertex.x, vertex.y) for vertex in text.bounding_poly.vertices])
        try:
            return re.sub('[^A-Z a-z 0-9 -/:]+', '\n', texts[0].description)
            # return texts[0].description
        except:
            return ""
        return re.sub('[^A-Z a-z 0-9 -/:]+', '\n', texts[0].description)
        # return texts[0].description
    except:
        print(traceback.print_exc())


def get_required_text(text):
    key = ['txn date','txn','transaction date','post date','particulars','cheque/reference no','cheque no.','channel','chq./ref.no.','narration','naration','transaction remarks','remitter',
            'chq/ref no','transaction date','description','value date','my portfolio','utr number','remarks']
    flag = False
    text_lower = text.lower()

    for item in key:
        if item in text_lower and not flag:
            text = text_lower.split(item)[0]
            flag = True
            # return text
    text2 = text.splitlines()
    text = ' '.join(text2)

    return text.lower()
        
def get_bank_name(text,ifsc_code):
    new_text = get_required_text(text)
    # print(new_text)
    
    ifsc_list  = re.findall(r'[a-z]{4}[0o][0-9]{6}',new_text)
    print("--------detected IFSC Code-------",ifsc_list)
    df = pd.read_excel(ifsc_code)
    bank_tagline = pd.read_excel(bank_tags)
    new_bank_name = ''
    if ifsc_list: 
        bank_name = ifsc_list[0]
        IFSC = bank_name[0:4]
        for index, row in df.iterrows():
            x = row['IFSC_CODE']
            x = x.lower()
            if x == IFSC:
                new_bank_name = row['Bank_Name']
                print('------bank name from IFSC------',new_bank_name)
                return new_bank_name
    
    else:
        if new_text:
            for index, row in df.iterrows():
                x = row['Bank_Name']
                if str(x) in new_text.upper():
                    new_bank_name = x.upper()
                    if new_bank_name == 'INDIAN BANK':
                        if 'experience next generation banking' in new_text.lower():
                            return 'SOUTH INDIAN BANK'
                    return new_bank_name
            for index, row in bank_tagline.iterrows():
                bank_tag = row['tag_line']
                new_bank_name = row['bank_name']
                if bank_tag.upper() in new_text.upper():
                    return new_bank_name

    return 'Unknown Bank'
    
                
def get_document_type(file_name):
    try:
        if file_name.endswith('.pdf') or file_name.endswith('.PDF'):
            pages = convert_from_path(file_name,250,first_page=1, last_page=1)
            for page in pages:
                page.save("%s-page100.jpg" % (file_name[:-4]), "JPEG")
            file_path = file_name[:-4]
            image_name = file_path + '-page100.jpg'    
        else:
            image_name = file_name
            
    except:
        if file_name.endswith('.pdf') or file_name.endswith('.PDF'):
            pages = convert_from_path(file_name,100,first_page=1, last_page=1)
            print(pages)
            for page in pages:
                page.save("%s-page100.jpg" % (file_name[:-4]), "JPEG")
            file_path = file_name[:-4]
            image_name = file_path + '-page100.jpg'    
        else:
            image_name = file_name

    boxes = ocr(image_name,False,apikey)
    # print(boxes)
    df,word_order = group_ocr_words(boxes[0][1:])
    # print(df)
    lines = generate_lines(df,word_order)
    text = '\n'.join(lines)

    text = google_vision(image_name)
    # print(text.split('\n'))
    # readable_status = get_readable_status(im)
    text_data_lower = text.lower()
    Bank_statement_keywords = ['particulars','statement','account','income','credit','debit','Chq','ifsc code','naration','biaya']
    flag = False
    for item in Bank_statement_keywords:
        if item in text_data_lower and not flag:
            flag = True
            document_type = "Bank Statement"
    bank_name = get_bank_name(text,ifsc_code)
    # try:
    #     document_type = document_type
    # except:
    #     document_type = "Unknown"

    # bank_name = bank_name.strip()
    # print("------document_type = {},bank_name = {} ------".format(document_type,bank_name))
    text_dataframe = df.to_json(orient='records')
    # return document_type,bank_name,text_dataframe,str(word_order)

    print(">>>>>>>>>>>> Bank Names is  >>>>>>>>>>",bank_name)
    return text_dataframe,str(word_order),bank_name

