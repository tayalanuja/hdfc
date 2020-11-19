import os,time
import re
import cv2
import pytesseract
from pdf2image import convert_from_path
import io
import json
import base64
import sys
from google.cloud import vision
from google.cloud.vision import types
import traceback
import config.config as project_configs

key = project_configs.INTAIN_BANK_STATEMENT_GOOGLE_APPLICATION_CREDENTIALS
def google_ocr(file_name):
    try:
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = key
        client = vision.ImageAnnotatorClient()

        with io.open(file_name, 'rb') as image_file:
            content = image_file.read()
        image = types.Image(content=content)

        kwargs = {"image_context": {"language_hints": ["en", "hi", "mr", "bn", "ta"]}}
        response = client.document_text_detection(image=image,**kwargs)
        res = response.full_text_annotation
        #print(re•••••s)
        # print('#####################OCR DF CALLED#######################')
        bboxes = []
        for page in res.pages:
            for block in page.blocks:
                for paragraph in block.paragraphs:
                    p=""
                    for word in paragraph.words:
                        w = ""
                        for symbol in word.symbols:
                            w+=symbol.text
                        if w.strip() in ['|','||','| |',':','-']:
                                continue
                        bboxes.append([(word.bounding_box.vertices[0].x,word.bounding_box.vertices[0].y),
                                (word.bounding_box.vertices[2].x,word.bounding_box.vertices[2].y),w])                 
        return (bboxes)
    except:
        print(traceback.print_exc())
        return ""

def sort_bboxes(bboxes):        
    # cluster lines after sorting based on y-position
    lines = {}
    for box in bboxes:
        key = list(filter(lambda x:x in lines,range(box[0][1]-10,box[0][1]+11)))
        if len(key):
            key = key[0]
            lines[key] += [box]
        else:
            lines[box[0][1]] = [box]
    text=""
    for k in lines:
        lines[k].sort()
        w = ""
        for m in lines[k]:
            w+=m[2]+" "
        #print(w)
        text=text+w
    return (text)



def get_ocr(filename):
    # filename = cv2.imread(filename)
    # text = pytesseract.image_to_string(filename)
    bboxes = google_ocr(filename)
    text=sort_bboxes(bboxes)  
    # print("1")
    #print(text)
    text = re.sub('[^A-Z a-z 0-9 -/:]+', '\n', text)
    text = re.sub(r'(?m)^\s+', "", text)
    #print("********* Start ********\n",text,"\n********   END   ********")
    # output_directory = os.path.dirname(filename)
    # filename = filename.split("/")[-1]
    # filename = os.path.splitext(filename)[0]
    # txtFileName = os.path.join(output_directory,filename +'.txt')
    # with open(txtFileName,'w') as f:
    #     f.write(text)
    return (bboxes,text)

def pdf2jpg(pdf_file):
    try:
        pages = convert_from_path(pdf_file, 200,first_page=1,last_page=1 ,fmt="jpg")
    except:
        pages = convert_from_path(pdf_file, 100,first_page=1,last_page=1 ,fmt="jpg")
    pdf_file = pdf_file[:-4]
    for page in pages:
        page.save("%s.jpg" % (pdf_file), "JPEG")
        break
    print('***** Number of Pages in pdf file: ',len(pages),'*******')
    return len(pages)

def pdf2jpg2text(filename):
    if filename.endswith('.pdf') or filename.endswith('.PDF'): 
        pages = pdf2jpg(filename)
        coordinates = []
        blocks = []
        for i in range(pages):
            filename = filename.split('.')[:-1]
            filename = '.'.join(filename) + '.jpg'
            c,b = get_ocr(filename)
            coordinates+=c
            blocks+=b
        # print (coordinates,blocks)
        text="".join(blocks)
        # print(text)
        return (coordinates,text)

    else:
        return get_ocr(filename)

# if __name__ == "__main__":
#     file="/home/anuja/backup/Dropbox/hr/Bactrak_Documents/Employment/PAY/pay-2.jpg"
#     bboxes,text=pdf2jpg2text(file)
#     print(bboxes,text)