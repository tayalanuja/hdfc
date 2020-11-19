import numpy as np
import cv2
import os
import six.moves.urllib as urllib
import sys
import tarfile
import tensorflow as tf
import zipfile
import io
import re
import string

import pandas as pd
import traceback
from collections import defaultdict
from io import StringIO

from PIL import Image
import nltk
import numpy as np
from nltk import sent_tokenize
from nltk.chunk.regexp import *
from nltk.corpus import stopwords
import tensorflow.compat.v1 as tf

from google.cloud import vision
from google.cloud.vision import types
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans
from scipy.ndimage import interpolation as inter

from .utils import label_map_util

from .utils import visualization_utils as vis_util
from .utils import ops as utils_ops

from .FunctionLibrary import attribute_type
from .FunctionLibrary import attribute_symbol
from .FunctionLibrary import attribute_distribution
from .FunctionLibrary import startendchar
from .FunctionLibrary import attribute_length
from .FunctionLibrary import wordpattern
from .FunctionLibrary import addrowno
from .FunctionLibrary import ParaCode
from .FunctionLibrary import extract_date
from .FunctionLibrary import cleantext
from .FunctionLibrary import cleantotal
from textblob import TextBlob

def image_resize(img):
    basewidth = 700
    # img = Image.open('somepic.jpg')
    wpercent = (basewidth / float(img.size[0]))
    hsize = int((float(img.size[1]) * float(wpercent)))
    img = img.resize((basewidth, hsize), Image.ANTIALIAS)

    return img

def load_image_into_numpy_array(image):
    (im_width, im_height) = image.size
    return np.array(image.getdata()).reshape((im_height, im_width, 3)).astype(np.uint8)


def get_cords(output_dict, image, label):
    label_index = np.isin(output_dict['detection_classes'], label)
    boxes_data = output_dict['detection_boxes'][label_index]
    #     output_dict['detection_classes'] = output_dict['detection_classes'][label_index]
    boxes_score = output_dict['detection_scores'][label_index]
    boxes = np.squeeze(boxes_data)
    scores = np.squeeze(boxes_score)
    # set a min thresh score, say 0.8
    min_score_thresh = 0.52
    scores_value = scores[scores>min_score_thresh]
    #scores_value = np.around(scores_value, decimals=0)
    scores_value = np.around(scores_value, decimals=2)
    scores_value = scores_value.tolist()
    scores_value = [round(elem, 2)*100 for elem in scores_value]
    bboxes = boxes[scores > min_score_thresh]

    # get image size
    im_width, im_height = image.size
    final_box = []
    new_cords = []
    new_list = []
    for box in bboxes:
        ymin, xmin, ymax, xmax = box
        final_box.append([xmin * im_width, xmax * im_width, ymin * im_height, ymax * im_height])
        x0dim= xmin * im_width
        x2dim= xmax * im_width
        y0dim= ymin * im_height
        y2dim= ymax * im_height
        wdim = x2dim- x0dim
        hdim = y2dim -y0dim
        #new_list.append([str(x0dim),str(y0dim),str(wdim),str(hdim)])
        new_list.append([x0dim,y0dim,wdim,hdim])

    return final_box, new_list,scores_value

def visionocr(imagePath, apikey):
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = apikey
    client = vision.ImageAnnotatorClient()

    with io.open(imagePath, 'rb') as image_file:
        content = image_file.read()

    image = types.Image(content=content)

    # Performs text detection on image
    # kwargs = {"image_context": {"language_hints": ["en", "hi", "mr", "bn", "ta"]}}
    # response = client.document_text_detection(image, **kwargs)
    response = client.text_detection(image)

    texts = response.text_annotations
    imvertices = []
    resp = ''
    for text in texts[1:]:
        vertices = (['{}\t{}'.format(vertex.x, vertex.y) for vertex in text.bounding_poly.vertices])
        vertices = ' '.join(vertices)
        vertices = vertices.split()
        vertices = [int(x) for x in vertices]
        vertices.insert(0, text.description)
        imvertices.append(vertices)
        resp += re.sub('[^A-Za-z0-9]+', ' ', str(text.description)) + ' '
    df = pd.DataFrame(imvertices, columns=['Token', 'x0', 'y0', 'x1', 'y1', 'x2', 'y2', 'x3', 'y3'])
    textlist = resp.split()
    return df, textlist

def extract_attribute(df, cords):
    df = df.sort_values(by=['x0', 'y0'])
    cords = cords[0]
    x0 = int(cords[0]) -9
    x2 = int(cords[1]) +8
    y0 = int(cords[2]) -9
    y2 = int(cords[3]) +8
    attributedf = df[(df['x0'] > x0) & (df['y0'] > y0) & (df['x2'] < x2) & (df['y2'] < y2)]
    return attributedf

def run_inference_for_single_image(image, graph):
    with graph.as_default():
        with tf.Session() as sess:
            # Get handles to input and output tensors
            ops = tf.get_default_graph().get_operations()
            all_tensor_names = {output.name for op in ops for output in op.outputs}
            tensor_dict = {}
            for key in ['num_detections', 'detection_boxes', 'detection_scores', 'detection_classes',
                        'detection_masks']:
                tensor_name = key + ':0'
                if tensor_name in all_tensor_names:
                    tensor_dict[key] = tf.get_default_graph().get_tensor_by_name(tensor_name)
            if 'detection_masks' in tensor_dict:
                # The following processing is only for single image
                detection_boxes = tf.squeeze(tensor_dict['detection_boxes'], [0])
                detection_masks = tf.squeeze(tensor_dict['detection_masks'], [0])
                # Reframe is required to translate mask from box coordinates to image coordinates and fit the image size.
                real_num_detection = tf.cast(tensor_dict['num_detections'][0], tf.int32)
                detection_boxes = tf.slice(detection_boxes, [0, 0], [real_num_detection, -1])
                detection_masks = tf.slice(detection_masks, [0, 0, 0], [real_num_detection, -1, -1])
                detection_masks_reframed = utils_ops.reframe_box_masks_to_image_masks(
                    detection_masks, detection_boxes, image.shape[0], image.shape[1])
                detection_masks_reframed = tf.cast(
                    tf.greater(detection_masks_reframed, 0.5), tf.uint8)
                # Follow the convention by adding back the batch dimension
                tensor_dict['detection_masks'] = tf.expand_dims(detection_masks_reframed, 0)
            image_tensor = tf.get_default_graph().get_tensor_by_name('image_tensor:0')

            # Run inference
            output_dict = sess.run(tensor_dict, feed_dict={image_tensor: np.expand_dims(image, 0)})

            # all outputs are float32 numpy arrays, so convert types as appropriate
            output_dict['num_detections'] = int(output_dict['num_detections'][0])
            output_dict['detection_classes'] = output_dict['detection_classes'][0].astype(np.uint8)
            output_dict['detection_boxes'] = output_dict['detection_boxes'][0]
            output_dict['detection_scores'] = output_dict['detection_scores'][0]
            if 'detection_masks' in output_dict:
                output_dict['detection_masks'] = output_dict['detection_masks'][0]
    return output_dict

def salaryslip_extraction(df,image_path,im_resized,detection_graph,label_map,category_index):
    employername_label=[8]
    employeraddress_label=[9]
    employeename_label=[1]
    employeeid_label=[18]
    employeepanno_label= [5]
    employeeuanno_label= [19]
    employeedoj_label=[6]
    employeedesignation_label=[7]
    bankacctno_label=[14]
    bankname_label=[15]
    periodofpay_label = [13]
    netsalary_label = [12]
    label = [8,9,1,18,5,19,6,7,14,15,13,12]
    # label = [8,1,13,12]
    image = Image.open(image_path)  ## Original image
    image_np_org = load_image_into_numpy_array(image)

    image_resized = im_resized.convert("RGB")
    # the array based representation of the image will be used later in order to prepare the
    # result image with boxes and labels on it.
    image_np = load_image_into_numpy_array(image_resized)
    # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
    image_np_expanded = np.expand_dims(image_np, axis=0)
    # Actual detection.
    output_dict = run_inference_for_single_image(image_np, detection_graph)

    label_index = np.isin(output_dict['detection_classes'], label)
    x = output_dict['detection_boxes'][label_index]
    y = output_dict['detection_classes'][label_index]
    z = output_dict['detection_scores'][label_index]

    # Localization of employer details
    employername_cords,newemployername_cords,employername_score= get_cords(output_dict,image,employername_label)
    employeraddress_cords, newemployeraddress_cords,employeraddress_score=get_cords(output_dict,image,employeraddress_label)
    
    # Localization of employee details
    employeename_cords,newemployeename_cords,employeename_score= get_cords(output_dict,image,employeename_label)
    employeeid_cords, newemployeeid_cords,employeeid_score=get_cords(output_dict,image,employeeid_label)
    employeepanno_cords, newemployeepanno_cords,employeepanno_score=get_cords(output_dict,image,employeepanno_label)
    employeeuanno_cords, newemployeeuanno_cords,employeeuanno_score=get_cords(output_dict,image,employeeuanno_label)
    employeedoj_cords, newemployeedoj_cords,employeedoj_score=get_cords(output_dict,image,employeedoj_label)
    employeedesignation_cords, newemployeedesignation_cords,employeedesignation_score=get_cords(output_dict,image,employeedesignation_label)

    # Localization of bank details
    employeebankaccountno_cords,newemployeebankaccountno_cords,employeebankaccountno_score =get_cords(output_dict,image,bankacctno_label)
    bankname_cords, newbankname_cords,bankname_score =get_cords(output_dict,image,bankname_label)
    periodofpay_cords, newperiodofpay_cords,periodofpay_score =get_cords(output_dict,image,periodofpay_label)
    netsalary_cords,newnetsalary_cords,netsalary_score =get_cords(output_dict,image,netsalary_label)

    
########### Dataframe arrangement #################################################################

    #df, _ = visionocr(image_path, 'apikey.json')
    linNodf = addrowno(df)    
    linewise_df = linNodf.copy()
    linewise_df.sort_values(['linNo','x0'],inplace = True)
    linewise_df['Token'] = linewise_df[['Token','x0','y0','linNo']].groupby('linNo')['Token'].transform(lambda x: ' '.join(x))
    linewise_df.drop_duplicates(subset = ['Token','linNo'],inplace = True)
    linewise_df.reset_index(drop = True, inplace=True)


########### EmployerName Extraction ########################################################
    try:
        employername_text="NA"
        confidence_employername=0
        if employername_cords:
            employernamedf=extract_attribute(df,employername_cords)
            if employernamedf.empty:
                employeename_text="NA"
                confidence_employername=0
            else:
                employernamedf= ParaCode(employernamedf)
                employername_list = employernamedf[0].tolist()
                employername_text = " ".join(employername_list)
                confidence_employername= employername_score[0]    
                    
        else:
            comp_id=['ltd','limited','inc','co','pvt','solution','solutions','consultancy','services','office']
            wordlist=[".","%","+",",","/"]
            all_tokens=linewise_df.loc[:,'Token']
            text=' '.join(all_tokens.astype(str))
            text = re.sub(r'[^.%,/a-zA-Z0-9\s+]', "",text)
            text = re.sub(r'\s+', " ",text)
            # print(text)
            words=text.split()
            # print(words)
            # employername_text='NA'
            for word in words:
                if employername_text=='NA' and word not in wordlist and (word.lower() in comp_id or TextBlob(word.lower()).words[0].spellcheck()[0][0] in comp_id):
                    if words.index(word) >3:
                        company=words[words.index(word)-3:words.index(word)+1]
                        employername_text=' '.join(company)
                        confidence_employername=70
                        
                    else:
                        company=words[0:words.index(word)+1]
                        employername_text=' '.join(company)
                        confidence_employername=70
    except Exception as e:
        employername_text= traceback.format_exc()
        confidence_employername=0

    employername_data=[employername_text,confidence_employername]

########### Employer Address Extraction ########################################################
    try:
        employeraddress_text= "NA" 
        if employeraddress_cords:
            employeraddressdf=extract_attribute(df,employeraddress_cords)
            employeraddressdf=employeraddressdf[~employeraddressdf.Token.str.contains('EMPLOYEE|EMPLOYER|ADDRESS|Employee|Address')]
            if employeraddressdf.empty:
                employeraddress_text="NA"
                confidence_employeraddress=0
            else:
                employeraddressdf= ParaCode(employeraddressdf)
                employeraddress_list = employeraddressdf[0].tolist()
                employeraddress_text = " ".join(employeraddress_list)
                confidence_employeraddress=employeraddress_score[0]
        else:
            employeraddress_text= "NA"
            confidence_employeraddress=0
    except Exception as e:
        employeraddress_text= traceback.format_exc()
        confidence_employeraddress=0
    employeraddress_data=[employeraddress_text,confidence_employeraddress]

########### EmployeeName Extraction ########################################################
    try:
        employeename_text="NA"
        if employeename_cords:
            employeenamedf=extract_attribute(df,employeename_cords)
            employeenamedf=employeenamedf[~employeenamedf.Token.str.contains('EMP|Emp|EMPLOYEE|NAME|Member|EMPNAME|Emp.|Name.:|Employee|Name|name|Name:|name:|Associate|of|the')]
            if employeenamedf.empty:
                employeename_text= "NA"
                confidence_employeename=0
            else:    
                employeenamedf= ParaCode(employeenamedf)
                employeename_list = employeenamedf[0].tolist()
                employeename_text = " ".join(employeename_list)
                confidence_employeename=employeename_score[0]
        else:
            employeenamedf_org=df.copy()
            employeenamedf=employeenamedf_org.copy()
            employeename_index = linewise_df[linewise_df['Token'].str.contains('emp name|employee name|empname|employeename|emp. name|emp name.:|employee name|employee name.:|emp name:|employee name:|name of the employee|name|mr|ms|mrs', na=False, case = False, regex = True)].index.tolist()
            if employeename_index:
                employeename_linNo = linewise_df.iloc[employeename_index[0]]['linNo']
                employeenamedf = linNodf[linNodf['linNo']==employeename_linNo]
                employeenamedf.sort_values(['x0'],inplace = True)
                temp_df = employeenamedf.reset_index(drop=True)
                employeename_index = temp_df[temp_df['Token'].str.contains('emp name|employee name|empname|employeename|emp. name|emp name.:|employee name|employee name.:|emp name:|employee name:|name of the employee|name|mr|ms|mrs', na=False, case = False, regex = True)].index.tolist()
                temp_df.drop(temp_df.loc[0:employeename_index[0]].index, inplace=True)
                employeenamedf = temp_df.astype(str)

                # # print(employeenamedf[employeenamedf['Token'].str.contains('emp name|employee name|empname|employeename|emp. name|emp name.:|employee name|employee name.:|emp name:|employee name:|name of the employee', na=False, case = False, regex = True)])
                # employeenamedf = employeenamedf[employeenamedf['Token'].str.contains('name|name.:|name:', na=False, case = False, regex = True).shift(1).fillna(False)]
                employeenamedf_list = employeenamedf['Token'].tolist()
                employeename_text = " ".join(employeenamedf_list)
                confidence_employeename=80

                stop = stopwords.words('english')
                text = ' '.join([i for i in employeename_text.split() if i not in stop])

                exclude = set(string.punctuation)
                text = ''.join(ch for ch in text if ch not in exclude)


                token = nltk.word_tokenize(text)
                tag = nltk.pos_tag(token)

                grammar = """NP: {<NNP><NNP>}  
                                """  # Chunk three consecutive nouns"

                # name = 'No name in the receipt'
                for sent in sent_tokenize(text):
                    sentence = sent.split()
                    regexp_tagger = nltk.RegexpParser(grammar)

                    output= regexp_tagger.parse(tag)
                    namelist = []
                    for subtree in output.subtrees(filter=lambda t: t.label() == 'NP'):
                        name = (' '.join([x[0] for x in subtree]))
                        namelist.append(name)
                if namelist:
                    employeename_text = namelist[0]
                else:
                    employeename_text= "NA"
                confidence_employeename=60
            else:
                employeename_text= "NA"
                confidence_employeename=0
    except Exception as e:
        # print(traceback.print_exc())
        employeename_text= 'NA'
        confidence_employeename=traceback.format_exc()
    
    employeename_data=[employeename_text,confidence_employeename]
    
########### Employee ID Extraction ########################################################
    try:
        employeeid_text='NA'
        if employeeid_cords:
            employeeiddf1=extract_attribute(df,employeeid_cords)
            # when OCR does not return any text
            if employeeiddf1.empty:
                employeeid_text= "NA"
                confidence_employeeid=0
            else:
                employeeiddf=addrowno(employeeiddf1)
                employeeiddf['attribute_length']=employeeiddf['Token'].apply(lambda x: attribute_length(x))
                employeeiddf=employeeiddf[(employeeiddf['attribute_length']>2)]
                employeeiddf['attribute_type']=employeeiddf['Token'].apply(lambda x: attribute_type(x))
                employeeiddf = employeeiddf[(employeeiddf['attribute_type'] ==1)|(employeeiddf['attribute_type'] ==3)]
                if employeeiddf.empty:
                    employeeiddf=employeeiddf1.copy()
                employeeid_list=employeeiddf['Token'].tolist()
                employeeid_text = " ".join(employeeid_list)
                confidence_employeeid=employeeid_score[0]        
        else:
            employeeiddf_org=df.copy()
            employeeiddf=employeeiddf_org.copy()
            employeeiddf['Token'] = employeeiddf['Token'].str.replace(",|:| ","")

            Id_index = linewise_df[linewise_df['Token'].str.contains('employee id|emp id|employee code|emp code|emp no|personnel no.|employee number|e.no:|emp.code|ecode|associate id', na=False, case = False, regex = True)].index.tolist()
            if Id_index:
                id_linNo = linewise_df.iloc[Id_index[0]]['linNo']                
                employeeiddf = linNodf[linNodf['linNo']==id_linNo]
                employeeiddf['attribute_length']=employeeiddf['Token'].apply(lambda x: attribute_length(x))
                employeeiddf=employeeiddf[(employeeiddf['attribute_length']>2)]
                employeeiddf['attribute_type']=employeeiddf['Token'].apply(lambda x: attribute_type(x))
                employeeiddf = employeeiddf[(employeeiddf['attribute_type'] ==1)|(employeeiddf['attribute_type'] ==3)]
                if len(employeeiddf['Token'])>1:
                    employeeiddf['attribute_symbol']=employeeiddf['Token'].apply(lambda x: attribute_symbol(x))
                    employeeiddf['attribute_symbol']=employeeiddf['attribute_symbol'].astype(int)
                    employeeiddf=employeeiddf[(employeeiddf['attribute_symbol']==0)]
                    employeeid_list=employeeiddf['Token'].tolist()
                    if len(employeeid_list)>1:
                        employeeid_text=employeeid_list[0]
                        confidence_employeeid=80       
                    else:
                        employeeid_text = " ".join(employeeid_list)
                        confidence_employeeid=80       
                else:
                    if employeeiddf.empty:
                        employeeiddf=employeeiddf_org.copy()
                        prefix_employeeiddf = employeeiddf[employeeiddf['Token'].str.contains('Emp#',regex=True)]
                        prefix_employeeid_list=prefix_employeeiddf['Token'].tolist()
                        employeeid_text = " ".join(prefix_employeeid_list)
                        confidence_employeeid=60       
                        if not prefix_employeeid_list:
                            employeeid_text='NA'
                            confidence_employeeid=0       
                    else:
                        employeeid_list=employeeiddf['Token'].tolist()
                        employeeid_text = " ".join(employeeid_list)
                        confidence_employeeid=60       
            else:
                employeeid_text='NA'
                confidence_employeeid=0       
    except Exception as e:
        #print(traceback.print_exc())
        employeeid_text= traceback.format_exc()
        confidence_employeeid=0

    employeeid_data=[employeeid_text,confidence_employeeid]       


########### Employee Panno Extraction ########################################################
    try:
        employeepanno_text='NA'
        if employeepanno_cords:

            employeepannodf1=extract_attribute(df,employeepanno_cords)
            employeepannodf1=employeepannodf1[~employeepannodf1.Token.str.contains(':|Employee|PAN|PAN:|Pan|No|NO|no|No.|NO.|no.|No.:|NO.:|no.:|Number:|Permanent|Account|Number|Income|Tax')]
            # when OCR does not return any text
            if employeepannodf1.empty:
                employeepanno_text= "NA"
                confidence_employeepanno=0
            else:                
                employeepannodf=addrowno(employeepannodf1)
                employeepannodf['attribute_length']=employeepannodf['Token'].apply(lambda x: attribute_length(x))
                employeepannodf=employeepannodf[(employeepannodf['attribute_length']==10)]
                if len(employeepannodf['Token'])>1:
                    employeepannodf['wordpattern']=employeepannodf['Token'].apply(lambda x:wordpattern(x))
                    employeepannodf = employeepannodf[(employeepannodf['wordpattern'] ==1)]
                    if len(employeepannodf['Token'])>1:
                        employeepannodf['attribute_type']=employeepannodf['Token'].apply(lambda x: attribute_type(x))
                        employeepannodf = employeepannodf[(employeepannodf['attribute_type'] ==3)]

                        if len(employeepannodf['Token'])>1:
                            employeepannodf['startendchar']=employeepannodf['Token'].apply(lambda x: startendchar(x))
                            employeepannodf = employeepannodf[(employeepannodf['startendchar'] ==3)]
                            employeepanno_list=employeepannodf['Token'].tolist()
                            if len(employeepanno_list)>1:
                                employeepanno_text = employeepanno_list[0]
                                confidence_employeepanno=employeepanno_score[0]
                            else:
                                employeepanno_text = " ".join(employeepanno_list)
                                confidence_employeepanno=employeepanno_score[0]

                        else:
                            if employeepannodf.empty:
                                employeepanno_text= "NA"
                                confidence_employeepanno=0
                            else:
                                employeepanno_list=employeepannodf['Token'].tolist()
                                employeepanno_text = " ".join(employeepanno_list)
                                confidence_employeepanno=employeepanno_score[0]
                    else:
                        if employeepannodf.empty:
                            employeepanno_text= "NA"
                            confidence_employeepanno=0
                        else:
                            employeepanno_list=employeepannodf['Token'].tolist()
                            employeepanno_text = " ".join(employeepanno_list)
                            confidence_employeepanno=employeepanno_score[0]
                else:
                    if employeepannodf.empty:
                        employeepanno_text= "NA"
                        confidence_employeepanno=0
                    else:
                        employeepanno_list=employeepannodf['Token'].tolist()
                        employeepanno_text = " ".join(employeepanno_list)
                        confidence_employeepanno=employeepanno_score[0]
        
        else:            
            employeepannodf_org=df.copy()
            employeepannodf=employeepannodf_org.copy()
            employeepannodf['attribute_length']=employeepannodf['Token'].apply(lambda x: attribute_length(x))
            employeepannodf=employeepannodf[(employeepannodf['attribute_length']==10)]
            if len(employeepannodf['Token'])>1:
                employeepannodf['wordpattern']=employeepannodf['Token'].apply(lambda x: wordpattern(x))
                employeepannodf = employeepannodf[(employeepannodf['wordpattern'] ==1)]
                if len(employeepannodf['Token'])>1:
                    employeepannodf['attribute_type']=employeepannodf['Token'].apply(lambda x: attribute_type(x))
                    employeepannodf = employeepannodf[(employeepannodf['attribute_type'] ==3)]
                    if len(employeepannodf['Token'])>1:
                        employeepannodf['startendchar']=employeepannodf['Token'].apply(lambda x: startendchar(x))
                        employeepannodf = employeepannodf[(employeepannodf['startendchar'] ==3)]
                        employeepanno_list=employeepannodf['Token'].tolist()

                        if len(employeepanno_list)>1:
                            employeepanno_text = employeepanno_list[0]
                            confidence_employeepanno=85
                        else:
                            employeepanno_text = " ".join(employeepanno_list)
                            confidence_employeepanno=85
                    else:
                        if employeepannodf.empty:
                            employeepannodf=employeepannodf_org.copy()
                            employeepannodf['attribute_length']=employeepannodf['Token'].apply(lambda x: attribute_length(x))
                            employeepannodf=employeepannodf[(employeepannodf['attribute_length']>=10)]
                            prefix_employeepannodf = employeepannodf[employeepannodf['Token'].str.contains('PAN|Pan|pan',regex=True)]
                            prefix_employeepanno_list=prefix_employeepannodf['Token'].tolist()
                            employeepanno_text = " ".join(prefix_employeepanno_list)
                            confidence_employeepanno=70
                            if not prefix_employeepanno_list:
                                employeepanno_text='NA'
                                confidence_employeepanno=0
                        else:
                            employeepanno_list=employeepannodf['Token'].tolist()
                            employeepanno_text = " ".join(employeepanno_list)
                            confidence_employeepanno=70
                else:
                    if employeepannodf.empty:
                        employeepanno_text='NA'
                        confidence_employeepanno=0
                    else:
                        employeepanno_list=employeepannodf['Token'].tolist()
                        employeepanno_text = " ".join(employeepanno_list)
                        confidence_employeepanno=60
            else:
                if employeepannodf.empty:
                    employeepanno_text='NA'
                    confidence_employeepanno=0
                else:
                    employeepanno_list=employeepannodf['Token'].tolist()
                    employeepanno_text = " ".join(employeepanno_list)
                    confidence_employeepanno=40
    except Exception as e:
        #print(traceback.print_exc())
        employeepanno_text= traceback.format_exc()
        confidence_employeepanno=0
    employeepanno_data=[employeepanno_text,confidence_employeepanno]

########### Employee UANNO Extraction ########################################################
    try:
        employeeuanno_text='NA'
        if employeeuanno_cords:
            employeeuannodf1=extract_attribute(df,employeeuanno_cords)
            employeeuannodf1=employeeuannodf1[~employeeuannodf1.Token.str.contains('Universal|Account|Number|Details')]
            # when OCR does not return any text
            if employeeuannodf1.empty:
                employeeuanno_text= "NA"
            else:
                employeeuannodf=addrowno(employeeuannodf1)                
                employeeuannodf['attribute_type']=employeeuannodf['Token'].apply(lambda x: attribute_type(x))
                employeeuannodf = employeeuannodf[(employeeuannodf['attribute_type'] ==1)]
                if len(employeeuannodf['Token'])>1:
                    employeeuannodf['attribute_length']=employeeuannodf['Token'].apply(lambda x: attribute_length(x))
                    employeeuannodf=employeeuannodf[(employeeuannodf['attribute_length']==12)]                   
                    if len(employeeuannodf['Token'])>1:
                        employeeuannodf['startendchar']=employeeuannodf['Token'].apply(lambda x: startendchar(x))
                        employeeuannodf = employeeuannodf[(employeeuannodf['startendchar'] ==2)]
                        if employeeuannodf.empty:
                            employeeuannodf=employeeuannodf1
                            employeeuanno_list=employeeuannodf['Token'].tolist()
                            confidence_employeeuanno=employeeuanno_score[0]
                        else:
                            employeeuanno_list=employeeuannodf['Token'].tolist()
                            if len(employeeuanno_list)>1:
                                employeeuanno_text = employeeuanno_list[0]
                                confidence_employeeuanno=employeeuanno_score[0]
                            else:
                                employeeuanno_text = " ".join(employeeuanno_list)
                                confidence_employeeuanno=employeeuanno_score[0]
                    else:
                        if employeeuannodf.empty:
                            employeeuanno_text='NA'
                            confidence_employeeuanno=0
                        else:
                            employeeuanno_list=employeeuannodf['Token'].tolist()
                            employeeuanno_text = " ".join(employeeuanno_list)
                            confidence_employeeuanno=employeeuanno_score[0]
                else:
                    if employeeuannodf.empty:
                        employeeuanno_text='NA'
                        confidence_employeeuanno=0
                    else:
                        employeeuanno_list=employeeuannodf['Token'].tolist()
                        employeeuanno_text = " ".join(employeeuanno_list)
                        confidence_employeeuanno=employeeuanno_score[0]
        else:            
            employeeuannodf_org=df.copy()
            employeeuannodf=employeeuannodf_org.copy()
            UAN_index = linNodf[linNodf['Token'].str.contains('UAN', na=False, regex = True)].index.tolist()
            if UAN_index:
                uan_linNo = linNodf.iloc[UAN_index[0]]['linNo']
                employeeuannodf = linNodf[linNodf['linNo']==uan_linNo]
                employeeuannodf['attribute_type']=employeeuannodf['Token'].apply(lambda x: attribute_type(x))
                employeeuannodf = employeeuannodf[(employeeuannodf['attribute_type'] ==1)]
                
                if len(employeeuannodf['Token'])>1:
                    employeeuannodf['attribute_length']=employeeuannodf['Token'].apply(lambda x: attribute_length(x))
                    employeeuannodf=employeeuannodf[(employeeuannodf['attribute_length']==12)]
                    if len(employeeuannodf['Token'])>1:
                        employeeuannodf['startendchar']=employeeuannodf['Token'].apply(lambda x: startendchar(x))
                        employeeuannodf = employeeuannodf[(employeeuannodf['startendchar'] ==2)]

                        employeeuanno_list=employeeuannodf['Token'].tolist()
                        if len(employeeuanno_list)>1:
                            employeeuanno_text = employeeuanno_list[0]
                            confidence_employeeuanno=80
                        else:
                            employeeuanno_text = " ".join(employeeuanno_list)
                            confidence_employeeuanno=80                    
                    else:
                        #employeeuannodf=employeeuannodf
                        if employeeuannodf.empty:                            
                            #employeeuanno_list=[]
                            employeeuannodf=employeeuannodf_org.copy()                            
                            employeeuannodf['attribute_length']=employeeuannodf['Token'].apply(lambda x: attribute_length(x))
                            employeeuannodf=employeeuannodf[(employeeuannodf['attribute_length']>=12)]
                            prefix_employeeuannodf = employeeuannodf[employeeuannodf['Token'].str.contains('UAN|Uan|uan',regex=True)]
                            prefix_employeeuanno_list=prefix_employeeuannodf['Token'].tolist()
                            employeeuanno_text = " ".join(prefix_employeeuanno_list)
                            confidence_employeeuanno=70
                            if not prefix_employeeuanno_list:
                                employeeuanno_text='NA'
                                confidence_employeeuanno=0  
                        else:
                            employeeuanno_list=employeeuannodf['Token'].tolist()
                            employeeuanno_text = " ".join(employeeuanno_list)
                            confidence_employeeuanno=70
                else:
                    if employeeuannodf.empty:
                        #employeeuanno_list=[]
                        employeeuannodf=employeeuannodf_org.copy()
                        employeeuannodf['attribute_length']=employeeuannodf['Token'].apply(lambda x: attribute_length(x))
                        employeeuannodf=employeeuannodf[(employeeuannodf['attribute_length']>=12)]
                        prefix_employeeuannodf = employeeuannodf[employeeuannodf['Token'].str.contains('UAN|Uan|uan',regex=True)]
                        prefix_employeeuanno_list=prefix_employeeuannodf['Token'].tolist()
                        employeeuanno_text = " ".join(prefix_employeeuanno_list)
                        confidence_employeeuanno=60
                        if not prefix_employeeuanno_list:
                            employeeuanno_text='NA'
                            confidence_employeeuanno=0  
                    else:
                        employeeuanno_list=employeeuannodf['Token'].tolist()
                        employeeuanno_text = " ".join(employeeuanno_list)
                        confidence_employeeuanno=60                  
            else:
                employeeuanno_text='NA'
                confidence_employeeuanno=0
    except Exception as e:
        #print(traceback.print_exc())
        employeeuanno_text= traceback.format_exc()
        confidence_employeeuanno=0
    employeeuanno_data=[employeeuanno_text,confidence_employeeuanno]
 
########### Employee DOJ Extraction ########################################################
    try:
        employeedoj_text= "NA"
        if employeedoj_cords:
            employeedojdf1= extract_attribute(df,employeedoj_cords)
            if employeedojdf1.empty == False:
                employeedojdf = ParaCode(employeedojdf1)
                employeedoj_list = employeedojdf[0].tolist()
                employeedoj_text = " ".join(employeedoj_list)
                employeedoj_text = extract_date(employeedoj_text)
                if employeedoj_text=='NA':
                    confidence_employeedoj=0
                else:
                    confidence_employeedoj=employeedoj_score[0]

                # when OCR does not return any text
            else:
                employeedojdf=employeedojdf1.copy()
                employeedoj_list = employeedojdf[0].tolist()
                employeedoj_text = " ".join(employeedoj_list)
                confidence_employeedoj= 0
        else:
            employeedojdf_org=df.copy()
            employeedojdf=employeedojdf_org.copy()
            employeedoj_index = linewise_df[linewise_df['Token'].str.contains('date of joining|doj|date join|joining date|date of join|date of joining:|joining date:|entity doj', na=False, case = False, regex = True)].index.tolist()
            if employeedoj_index:
                employeedoj_linNo = linewise_df.iloc[employeedoj_index[0]]['linNo']
                employeedojdf = linNodf[linNodf['linNo']==employeedoj_linNo]
                employeedojdf = ParaCode(employeedojdf)
                employeedoj_list = employeedojdf[0].tolist()
                employeedoj_text = " ".join(employeedoj_list)
                employeedoj_text = extract_date(employeedoj_text)
                if employeedoj_text=='NA':
                    confidence_employeedoj=0
                else:
                    confidence_employeedoj= 60
            else:
                employeedoj_text= "NA"
                confidence_employeedoj=0
    
    except Exception as e:
        #print(traceback.print_exc())
        employeedoj_text= traceback.format_exc()
        confidence_employeedoj=0

    employeedoj_data=[employeedoj_text,confidence_employeedoj]

########### Employee Designation Extraction ########################################################
    try:
        employeedesignation_text= "NA"
        if employeedesignation_cords:
            employeedesignationdf1=extract_attribute(df,employeedesignation_cords)
            employeedesignationdf1=employeedesignationdf1[~employeedesignationdf1.Token.str.contains('Desg.|Dsgn.|Designation|DESIGNATION|designation|designation:|Designation:|Desig.|Desig.:|Job|title|BANK|NAME')]
            if employeedesignationdf1.empty:
                employeedesignation_text="NA"
                confidence_employeedesignation=0
            else:       
                employeedesignationdf= ParaCode(employeedesignationdf1)
                employeedesignation_list = employeedesignationdf[0].tolist()
                employeedesignation_text = ", ".join(employeedesignation_list)
                confidence_employeedesignation=employeedesignation_score[0]
        
        else:
            employeedesignationdf_org=df.copy()
            employeedesignationdf=employeedesignationdf_org.copy()
            designation_index = linewise_df[linewise_df['Token'].str.contains('desg.|dsgn.|designation|designation:|desig.|desig.:', na=False, case = False, regex = True)].index.tolist()
            if designation_index:
                designation_linNo = linewise_df.iloc[designation_index[0]]['linNo']
                employeedesignationdf = linNodf[linNodf['linNo']==designation_linNo]
                employeedesignationdf.sort_values(['x0'],inplace = True)
                employeedesignationdf = employeedesignationdf.astype(str)
                employeedesignationdf = employeedesignationdf[employeedesignationdf['Token'].str.contains('desg.|dsgn.|designation|designation:|desig.|desig.:', na=False, case = False, regex = True).shift(1).fillna(False)]
                employeedesignation_list = employeedesignationdf['Token'].tolist()
                employeedesignation_text = ", ".join(employeedesignation_list)
                confidence_employeedesignation=60

            else:
                employeedesignation_text= "NA"
                confidence_employeedesignation=0
    except Exception as e:
        employeedesignation_text= traceback.format_exc()
        confidence_employeedesignation=0
    
    employeedesignation_data=[employeedesignation_text,confidence_employeedesignation]
    
########### Employee Bank Account number Extraction ########################################################
    try:
        employeebankaccountno_text='NA'
        if employeebankaccountno_cords:
            employeebankaccountnodf1=extract_attribute(df,employeebankaccountno_cords)
            employeebankaccountnodf1=employeebankaccountnodf1[~employeebankaccountnodf1.Token.str.contains('BANK|Bank|A/c|Ac/No.|A/C|Number:|AC|ACCOUNT|Account|Account:|Acc|NUMBER|Number|number|Salary|NO.:|No.:|No|NO|No.|NO.')]
            employeebankaccountnodf1['Token'] = employeebankaccountnodf1['Token'].str.replace(':|,| ','')
            
            # when OCR does not return any text
            if employeebankaccountnodf1.empty:
                employeebankaccountno_text= "NA"
                confidence_employeebankaccount=0
            else:
                employeebankaccountnodf=addrowno(employeebankaccountnodf1)
                employeebankaccountnodf['attribute_type']=employeebankaccountnodf['Token'].apply(lambda x: attribute_type(x))
                employeebankaccountnodf = employeebankaccountnodf[(employeebankaccountnodf['attribute_type'] ==1)|(employeebankaccountnodf['attribute_type'] ==3)]
                if employeebankaccountnodf.empty:
                    employeebankaccountno_text='NA'
                    confidence_employeebankaccount=0  
                else:                  
                    employeebankaccountno_list=employeebankaccountnodf['Token'].tolist()
                    employeebankaccountno_text = " ".join(employeebankaccountno_list)
                    confidence_employeebankaccount=employeebankaccountno_score[0]        
        else:            
            employeebankaccountnodf_org=df.copy()
            employeebankaccountnodf=employeebankaccountnodf_org.copy()
            Accountno_index = linewise_df[linewise_df['Token'].str.contains('salary account|bank a/c|bank ac/no|bank ac/no.|bank account|bank ac|bank account:|bank acc|bank details|bank name & account no|bank account#', na=False, case = False, regex = True)].index.tolist()
            if Accountno_index:
                accountno_linNo = linewise_df.iloc[Accountno_index[0]]['linNo']
                employeebankaccountnodf = linNodf[linNodf['linNo']==accountno_linNo]
                # print(employeebankaccountnodf)
                # employeebankaccountnodf['attribute_type']=employeebankaccountnodf['Token'].loc[:,'']
                employeebankaccountnodf['attribute_type']=employeebankaccountnodf['Token'].apply(lambda x: attribute_type(x))
                employeebankaccountnodf = employeebankaccountnodf[(employeebankaccountnodf['attribute_type'] ==1)|(employeebankaccountnodf['attribute_type'] ==3)]
                if len(employeebankaccountnodf['Token'])>1:
                    employeebankaccountnodf['attribute_symbol']=employeebankaccountnodf['Token'].apply(lambda x: attribute_symbol(x))
                    employeebankaccountnodf['attribute_symbol'] = employeebankaccountnodf['attribute_symbol'].astype(int)
                    employeebankaccountnodf=employeebankaccountnodf[(employeebankaccountnodf['attribute_symbol']==0)]                
                    employeebankaccountno_list=employeebankaccountnodf['Token'].tolist()
                    if len(employeebankaccountno_list)>1:
                        employeebankaccountno_text = employeebankaccountno_list[0]
                        confidence_employeebankaccount=80                            
                    else:
                        employeebankaccountno_text = " ".join(employeebankaccountno_list)
                        confidence_employeebankaccount=80                                            
                else:
                    if employeebankaccountnodf.empty:
                        employeebankaccountnodf=employeebankaccountnodf_org.copy()
                        prefix_employeebankaccountnodf = employeebankaccountnodf[employeebankaccountnodf['Token'].str.contains('salary account|bank a/c|bank ac/no|bank ac/no.|bank account|bank ac|bank account:|bank acc|bank details|bank name & account no|bank account#',regex=True)]
                        prefix_employeebankaccountno_list=prefix_employeebankaccountnodf['Token'].tolist()
                        employeebankaccountno_text = " ".join(prefix_employeebankaccountno_list)
                        confidence_employeebankaccount=70                            
                        if not prefix_employeebankaccountno_list:
                            employeebankaccountno_text='NA'
                            confidence_employeebankaccount=0                            
                    else:
                        employeebankaccountno_list=employeebankaccountnodf['Token'].tolist()
                        employeebankaccountno_text=" ".join(employeebankaccountno_list)
                        confidence_employeebankaccount=60                            
            else:
                employeebankaccountno_text='NA'
                confidence_employeebankaccount=0                            
    except Exception as e:
        #print(traceback.print_exc())
        employeebankaccountno_text= traceback.format_exc()
        confidence_employeebankaccount=0
    
    employeebankaccountno_data=[employeebankaccountno_text,confidence_employeebankaccount]

########### Bank name Extraction ########################################################
    try:
        bankname_text='NA'
        if bankname_cords:
            banknamedf=extract_attribute(df,bankname_cords)
            banknamedf=banknamedf[~banknamedf.Token.str.contains(':|NAME|NAME:|Name:|Name|name')] 
            banknamedf['Token'] = banknamedf['Token'].str.lower()
            banknamedf.drop_duplicates(subset ="Token", keep = 'last', inplace = True)
            banknamedf['Token'] = banknamedf['Token'].str.upper()
            # when OCR does not return any text
            if banknamedf.empty:
                bankname_text= "NA"
                confidence_bankname=0
            else:
                banknamedf= ParaCode(banknamedf)
                bankname_list = banknamedf[0].tolist()
                bankname_text = " ".join(bankname_list)
                confidence_bankname=bankname_score[0]
        else:
            allbanks_name=['Canara','Indian','IDBI','Dena','Corporation','Axis','AXIS','ICICI','HDFC','Federal','YES','CANARA']
            banknamedf_org=df.copy()
            banknamedf=banknamedf_org.copy()
            bankname_index = linewise_df[linewise_df['Token'].str.contains('bank name|bank name:|bank details', na=False, case = False, regex = True)].index.tolist()
            if bankname_index:
                bankname_linNo = linewise_df.iloc[bankname_index[0]]['linNo']
                banknamedf = linNodf[linNodf['linNo']==bankname_linNo]
                banknamedf.sort_values(['x0'],inplace = True)
                banknamedf = banknamedf[banknamedf['Token'].isin(allbanks_name)]
                if banknamedf.empty:
                    bankname_text='NA'
                    confidence_bankname=0
                else:
                    bankname_list = banknamedf['Token'].tolist()
                    bankname_text = " ".join(bankname_list)
                    confidence_bankname=80
            else:
                bankname_text='NA'
                confidence_bankname=0
    except Exception as e:
        #print(traceback.print_exc())
        bankname_text= traceback.format_exc()
        confidence_bankname=0
    bankname_data=[bankname_text,confidence_bankname]

########### Period of Pay Extraction ########################################################
    try:
        periodofpay_text= "NA"
        if periodofpay_cords:
            periodofpaydf=extract_attribute(df,periodofpay_cords)
            if periodofpaydf.empty:
                periodofpay_text='NA'
                confidence_periodofpay=0
            else:
                periodofpaydf= ParaCode(periodofpaydf)
                if periodofpaydf.empty:
                    periodofpay_text='NA'
                    confidence_periodofpay=0
                else:                    
                    text = periodofpaydf[0].tolist()
                    text = " ".join(text)
                    periodofpay_list = re.findall(r'''January\s{0,3}\d{2,4}|Jan\s{0,3}\d{2,4}|February\s{0,3}\d{2,4}|Feb\s{0,3}\d{2,4}|March\s{0,3}\d{2,4}|Mar\s{0,3}\d{2,4}|April\s{0,3}\d{2,4}|Apr\s{0,3}\d{2,4}|May\s{0,3}\d{2,4}|June\s{0,3}\d{2,4}|Jun\s{0,3}\d{2,4}|July\s{0,3}\d{2,4}|Jul\s{0,3}\d{2,4}|August\s{0,3}\d{2,4}|Aug\s{0,3}\d{2,4}|September\s{0,3}\d{2,4}|Sept\s{0,3}\d{2,4}|October\s{0,3}\d{2,4}|Oct\s{0,3}\d{2,4}|November\s{0,3}\d{2,4}|Nov\s{0,3}\d{2,4}|December\s{0,3}\d{2,4}|Dec\s{0,3}\d{2,4}|January-\s{0,3}\d{2,4}|Jan-\s{0,3}\d{2,4}|February-\s{0,3}\d{2,4}|Feb-\s{0,3}\d{2,4}|March-\s{0,3}\d{2,4}|Mar-\s{0,3}\d{2,4}|April-\s{0,3}\d{2,4}|Apr-\s{0,3}\d{2,4}|May-\s{0,3}\d{2,4}|June-\s{0,3}\d{2,4}|Jun-\s{0,3}\d{2,4}|July-\s{0,3}\d{2,4}|Jul-\s{0,3}\d{2,4}|August-\s{0,3}\d{2,4}|Aug-\s{0,3}\d{2,4}|September-\s{0,3}\d{2,4}|Sept-\s{0,3}\d{2,4}|October-\s{0,3}\d{2,4}|Oct-\s{0,3}\d{2,4}|November-\s{0,3}\d{2,4}|Nov-\s{0,3}\d{2,4}|December-\s{0,3}\d{2,4}|Dec-\s{0,3}\d{2,4}|january-\s{0,3}\d{2,4}|jan-\s{0,3}\d{2,4}|february-\s{0,3}\d{2,4}|feb-\s{0,3}\d{2,4}|march-\s{0,3}\d{2,4}|mar-\s{0,3}\d{2,4}|april-\s{0,3}\d{2,4}|apr-\s{0,3}\d{2,4}|may-\s{0,3}\d{2,4}|june-\s{0,3}\d{2,4}|jun-\s{0,3}\d{2,4}|july-\s{0,3}\d{2,4}|jul-\s{0,3}\d{2,4}|august-\s{0,3}\d{2,4}|aug-\s{0,3}\d{2,4}|september-\s{0,3}\d{2,4}|sept-\s{0,3}\d{2,4}|october-\s{0,3}\d{2,4}|oct-\s{0,3}\d{2,4}|november-\s{0,3}\d{2,4}|nov-\s{0,3}\d{2,4}|december-\s{0,3}\d{2,4}|dec-\s{0,3}\d{2,4}|JANUARY\s{0,3}\d{2,4}|JAN\s{0,3}\d{2,4}|FEBRUARY\s{0,3}\d{2,4}|FEB\s{0,3}\d{2,4}|MARCH\s{0,3}\d{2,4}|MAR\s{0,3}\d{2,4}|APRIL\s{0,3}\d{2,4}|APR\s{0,3}\d{2,4}|MAY\s{0,3}\d{2,4}|JUNE\s{0,3}\d{2,4}|JUN\s{0,3}\d{2,4}|JULY\s{0,3}\d{2,4}|JUL\s{0,3}\d{2,4}|AUGUST\s{0,3}\d{2,4}|AUG\s{0,3}\d{2,4}|SEPTEMBER\s{0,3}\d{2,4}|SEPT\s{0,3}\d{2,4}|OCTOBER\s{0,3}\d{2,4}|OCT\s{0,3}\d{2,4}|NOVEMBER\s{0,3}\d{2,4}|NOV\s{0,3}\d{2,4}|DECEMBER\s{0,3}\d{2,4}|DEC\s{0,3}\d{2,4}|JANUARY-\s{0,3}\d{2,4}|JAN-\s{0,3}\d{2,4}|FEBRUARY-\s{0,3}\d{2,4}|FEB-\s{0,3}\d{2,4}|MARCH-\s{0,3}\d{2,4}|MAR-\s{0,3}\d{2,4}|APRIL-\s{0,3}\d{2,4}|APR-\s{0,3}\d{2,4}|MAY-\s{0,3}\d{2,4}|JUNE-\s{0,3}\d{2,4}|JUN-\s{0,3}\d{2,4}|JULY-\s{0,3}\d{2,4}|JUL-\s{0,3}\d{2,4}|AUGUST-\s{0,3}\d{2,4}|AUG-\s{0,3}\d{2,4}|SEPTEMBER-\s{0,3}\d{2,4}|SEPT-\s{0,3}\d{2,4}|OCTOBER-\s{0,3}\d{2,4}|OCT-\s{0,3}\d{2,4}|NOVEMBER-\s{0,3}\d{2,4}|NOV-\s{0,3}\d{2,4}|DECEMBER-\s{0,3}\d{2,4}|DEC-\s{0,3}\d{2,4}''',text)
                    if periodofpay_list==[]:
                        periodofpay_text=='NA'                    
                        confidence_periodofpay=0
                    else:
                        periodofpay_text = " ".join(periodofpay_list)
                        confidence_periodofpay=periodofpay_score[0]
        if periodofpay_text=='NA':
            periodofpaydf_org=df.copy()
            periodofpaydf=periodofpaydf_org.copy()
            periodofpay_index = linewise_df[linewise_df['Token'].str.contains('month|period|pay slip|payslip|pay period|salary slip for', na=False, case = False, regex = True)].index.tolist()
            if periodofpay_index:
                periodofpay_linNo = linewise_df.iloc[periodofpay_index[0]]['linNo']
                periodofpaydf = linNodf[linNodf['linNo']==periodofpay_linNo]
                periodofpaydf=ParaCode(periodofpaydf)
                text = periodofpaydf[0].tolist()
                text = " ".join(text)
                periodofpay_list = re.findall(r'''January\s{0,3}\d{2,4}|Jan\s{0,3}\d{2,4}|February\s{0,3}\d{2,4}|Feb\s{0,3}\d{2,4}|March\s{0,3}\d{2,4}|Mar\s{0,3}\d{2,4}|April\s{0,3}\d{2,4}|Apr\s{0,3}\d{2,4}|May\s{0,3}\d{2,4}|June\s{0,3}\d{2,4}|Jun\s{0,3}\d{2,4}|July\s{0,3}\d{2,4}|Jul\s{0,3}\d{2,4}|August\s{0,3}\d{2,4}|Aug\s{0,3}\d{2,4}|September\s{0,3}\d{2,4}|Sept\s{0,3}\d{2,4}|October\s{0,3}\d{2,4}|Oct\s{0,3}\d{2,4}|November\s{0,3}\d{2,4}|Nov\s{0,3}\d{2,4}|December\s{0,3}\d{2,4}|Dec\s{0,3}\d{2,4}|January-\s{0,3}\d{2,4}|Jan-\s{0,3}\d{2,4}|February-\s{0,3}\d{2,4}|Feb-\s{0,3}\d{2,4}|March-\s{0,3}\d{2,4}|Mar-\s{0,3}\d{2,4}|April-\s{0,3}\d{2,4}|Apr-\s{0,3}\d{2,4}|May-\s{0,3}\d{2,4}|June-\s{0,3}\d{2,4}|Jun-\s{0,3}\d{2,4}|July-\s{0,3}\d{2,4}|Jul-\s{0,3}\d{2,4}|August-\s{0,3}\d{2,4}|Aug-\s{0,3}\d{2,4}|September-\s{0,3}\d{2,4}|Sept-\s{0,3}\d{2,4}|October-\s{0,3}\d{2,4}|Oct-\s{0,3}\d{2,4}|November-\s{0,3}\d{2,4}|Nov-\s{0,3}\d{2,4}|December-\s{0,3}\d{2,4}|Dec-\s{0,3}\d{2,4}|january-\s{0,3}\d{2,4}|jan-\s{0,3}\d{2,4}|february-\s{0,3}\d{2,4}|feb-\s{0,3}\d{2,4}|march-\s{0,3}\d{2,4}|mar-\s{0,3}\d{2,4}|april-\s{0,3}\d{2,4}|apr-\s{0,3}\d{2,4}|may-\s{0,3}\d{2,4}|june-\s{0,3}\d{2,4}|jun-\s{0,3}\d{2,4}|july-\s{0,3}\d{2,4}|jul-\s{0,3}\d{2,4}|august-\s{0,3}\d{2,4}|aug-\s{0,3}\d{2,4}|september-\s{0,3}\d{2,4}|sept-\s{0,3}\d{2,4}|october-\s{0,3}\d{2,4}|oct-\s{0,3}\d{2,4}|november-\s{0,3}\d{2,4}|nov-\s{0,3}\d{2,4}|december-\s{0,3}\d{2,4}|dec-\s{0,3}\d{2,4}|JANUARY\s{0,3}\d{2,4}|JAN\s{0,3}\d{2,4}|FEBRUARY\s{0,3}\d{2,4}|FEB\s{0,3}\d{2,4}|MARCH\s{0,3}\d{2,4}|MAR\s{0,3}\d{2,4}|APRIL\s{0,3}\d{2,4}|APR\s{0,3}\d{2,4}|MAY\s{0,3}\d{2,4}|JUNE\s{0,3}\d{2,4}|JUN\s{0,3}\d{2,4}|JULY\s{0,3}\d{2,4}|JUL\s{0,3}\d{2,4}|AUGUST\s{0,3}\d{2,4}|AUG\s{0,3}\d{2,4}|SEPTEMBER\s{0,3}\d{2,4}|SEPT\s{0,3}\d{2,4}|OCTOBER\s{0,3}\d{2,4}|OCT\s{0,3}\d{2,4}|NOVEMBER\s{0,3}\d{2,4}|NOV\s{0,3}\d{2,4}|DECEMBER\s{0,3}\d{2,4}|DEC\s{0,3}\d{2,4}|JANUARY-\s{0,3}\d{2,4}|JAN-\s{0,3}\d{2,4}|FEBRUARY-\s{0,3}\d{2,4}|FEB-\s{0,3}\d{2,4}|MARCH-\s{0,3}\d{2,4}|MAR-\s{0,3}\d{2,4}|APRIL-\s{0,3}\d{2,4}|APR-\s{0,3}\d{2,4}|MAY-\s{0,3}\d{2,4}|JUNE-\s{0,3}\d{2,4}|JUN-\s{0,3}\d{2,4}|JULY-\s{0,3}\d{2,4}|JUL-\s{0,3}\d{2,4}|AUGUST-\s{0,3}\d{2,4}|AUG-\s{0,3}\d{2,4}|SEPTEMBER-\s{0,3}\d{2,4}|SEPT-\s{0,3}\d{2,4}|OCTOBER-\s{0,3}\d{2,4}|OCT-\s{0,3}\d{2,4}|NOVEMBER-\s{0,3}\d{2,4}|NOV-\s{0,3}\d{2,4}|DECEMBER-\s{0,3}\d{2,4}|DEC-\s{0,3}\d{2,4}''',text)
                if periodofpay_list:
                    periodofpay_text = periodofpay_list[0]
                    confidence_periodofpay=80
                else:
                    periodofpaydf=linNodf[(linNodf['linNo']>=periodofpay_linNo)&(linNodf['linNo']<=periodofpay_linNo+2)]
                    periodofpaydf=ParaCode(periodofpaydf)
                    text = periodofpaydf[0].tolist()
                    text = " ".join(text)
                    periodofpay_list = re.findall(r'''January\s{0,3}\d{2,4}|Jan\s{0,3}\d{2,4}|February\s{0,3}\d{2,4}|Feb\s{0,3}\d{2,4}|March\s{0,3}\d{2,4}|Mar\s{0,3}\d{2,4}|April\s{0,3}\d{2,4}|Apr\s{0,3}\d{2,4}|May\s{0,3}\d{2,4}|June\s{0,3}\d{2,4}|Jun\s{0,3}\d{2,4}|July\s{0,3}\d{2,4}|Jul\s{0,3}\d{2,4}|August\s{0,3}\d{2,4}|Aug\s{0,3}\d{2,4}|September\s{0,3}\d{2,4}|Sept\s{0,3}\d{2,4}|October\s{0,3}\d{2,4}|Oct\s{0,3}\d{2,4}|November\s{0,3}\d{2,4}|Nov\s{0,3}\d{2,4}|December\s{0,3}\d{2,4}|Dec\s{0,3}\d{2,4}|January-\s{0,3}\d{2,4}|Jan-\s{0,3}\d{2,4}|February-\s{0,3}\d{2,4}|Feb-\s{0,3}\d{2,4}|March-\s{0,3}\d{2,4}|Mar-\s{0,3}\d{2,4}|April-\s{0,3}\d{2,4}|Apr-\s{0,3}\d{2,4}|May-\s{0,3}\d{2,4}|June-\s{0,3}\d{2,4}|Jun-\s{0,3}\d{2,4}|July-\s{0,3}\d{2,4}|Jul-\s{0,3}\d{2,4}|August-\s{0,3}\d{2,4}|Aug-\s{0,3}\d{2,4}|September-\s{0,3}\d{2,4}|Sept-\s{0,3}\d{2,4}|October-\s{0,3}\d{2,4}|Oct-\s{0,3}\d{2,4}|November-\s{0,3}\d{2,4}|Nov-\s{0,3}\d{2,4}|December-\s{0,3}\d{2,4}|Dec-\s{0,3}\d{2,4}|january-\s{0,3}\d{2,4}|jan-\s{0,3}\d{2,4}|february-\s{0,3}\d{2,4}|feb-\s{0,3}\d{2,4}|march-\s{0,3}\d{2,4}|mar-\s{0,3}\d{2,4}|april-\s{0,3}\d{2,4}|apr-\s{0,3}\d{2,4}|may-\s{0,3}\d{2,4}|june-\s{0,3}\d{2,4}|jun-\s{0,3}\d{2,4}|july-\s{0,3}\d{2,4}|jul-\s{0,3}\d{2,4}|august-\s{0,3}\d{2,4}|aug-\s{0,3}\d{2,4}|september-\s{0,3}\d{2,4}|sept-\s{0,3}\d{2,4}|october-\s{0,3}\d{2,4}|oct-\s{0,3}\d{2,4}|november-\s{0,3}\d{2,4}|nov-\s{0,3}\d{2,4}|december-\s{0,3}\d{2,4}|dec-\s{0,3}\d{2,4}|JANUARY\s{0,3}\d{2,4}|JAN\s{0,3}\d{2,4}|FEBRUARY\s{0,3}\d{2,4}|FEB\s{0,3}\d{2,4}|MARCH\s{0,3}\d{2,4}|MAR\s{0,3}\d{2,4}|APRIL\s{0,3}\d{2,4}|APR\s{0,3}\d{2,4}|MAY\s{0,3}\d{2,4}|JUNE\s{0,3}\d{2,4}|JUN\s{0,3}\d{2,4}|JULY\s{0,3}\d{2,4}|JUL\s{0,3}\d{2,4}|AUGUST\s{0,3}\d{2,4}|AUG\s{0,3}\d{2,4}|SEPTEMBER\s{0,3}\d{2,4}|SEPT\s{0,3}\d{2,4}|OCTOBER\s{0,3}\d{2,4}|OCT\s{0,3}\d{2,4}|NOVEMBER\s{0,3}\d{2,4}|NOV\s{0,3}\d{2,4}|DECEMBER\s{0,3}\d{2,4}|DEC\s{0,3}\d{2,4}|JANUARY-\s{0,3}\d{2,4}|JAN-\s{0,3}\d{2,4}|FEBRUARY-\s{0,3}\d{2,4}|FEB-\s{0,3}\d{2,4}|MARCH-\s{0,3}\d{2,4}|MAR-\s{0,3}\d{2,4}|APRIL-\s{0,3}\d{2,4}|APR-\s{0,3}\d{2,4}|MAY-\s{0,3}\d{2,4}|JUNE-\s{0,3}\d{2,4}|JUN-\s{0,3}\d{2,4}|JULY-\s{0,3}\d{2,4}|JUL-\s{0,3}\d{2,4}|AUGUST-\s{0,3}\d{2,4}|AUG-\s{0,3}\d{2,4}|SEPTEMBER-\s{0,3}\d{2,4}|SEPT-\s{0,3}\d{2,4}|OCTOBER-\s{0,3}\d{2,4}|OCT-\s{0,3}\d{2,4}|NOVEMBER-\s{0,3}\d{2,4}|NOV-\s{0,3}\d{2,4}|DECEMBER-\s{0,3}\d{2,4}|DEC-\s{0,3}\d{2,4}''',text)
                    if periodofpay_list:
                        periodofpay_text = periodofpay_list[0]
                        confidence_periodofpay=60
                    else:
                        periodofpay_text = "NA"
                        confidence_periodofpay=0
            else:
                periodofpay_text='NA'
                confidence_periodofpay=0
    except Exception as e:
        periodofpay_text= traceback.format_exc()
        confidence_periodofpay='NA'
    periodofpay_data=[periodofpay_text,confidence_periodofpay]

########### Net Salary Extraction ########################################################
    try:
        netsalary_text='NA'
        if netsalary_cords:
            netsalarydf1=extract_attribute(df,netsalary_cords)
            netsalarydf1['Token'] = netsalarydf1['Token'].apply(lambda x: cleantotal(x))
            #netsalarydf1['Token'] = netsalarydf1['Token'].str.replace(',|:| ','')

            # when OCR does not return any text
            if netsalarydf1.empty:
                netsalary_text= "NA"
            else:
                # netsalarydf=netsalarydf1[~netsalarydf1.Token.contains(':|Net|NET|Payable|Amount|(A-B)|net|Base|Salary|NetSalary|salary|Take|take|Home|home|Pay|PAY|Credited|Credited:|:-')]
                netsalarydf=addrowno(netsalarydf1)
                netsalarydf['attribute_length']=netsalarydf['Token'].apply(lambda x: attribute_length(x))
                netsalarydf=netsalarydf[(netsalarydf['attribute_length']>1)]
                netsalarydf['attribute_type']=netsalarydf['Token'].apply(lambda x: attribute_type(x))
                netsalarydf = netsalarydf[(netsalarydf['attribute_type'] ==1)|(netsalarydf['attribute_type'] ==4)]
                if len(netsalarydf['Token'])>1:
                    netsalarydf['attribute_symbol'] = netsalarydf['Token'].apply(lambda x: attribute_symbol(x))
                    netsalarydf['attribute_symbol'] = netsalarydf['attribute_symbol'].astype(int)
                    netsalarydf2 = netsalarydf[(netsalarydf['attribute_symbol'] == 1) | (netsalarydf['attribute_symbol'] == 4)| (netsalarydf['attribute_symbol'] == 7)]
                    if len(netsalarydf2['Token'])>1:
                        #netsalarydf['Token'] = netsalarydf['Token'].str.replace(',','')
                        netsalarydf2['Token'] = netsalarydf2['Token'].apply(lambda x: cleantotal(x))
                        netsalarydf2['Token'] = netsalarydf2['Token'].apply(lambda x: x.replace('.','',1) if x.count('.')>1 else x)
                        org_netsalarydf = netsalarydf2.astype(float)
                        netsalarydf = org_netsalarydf[org_netsalarydf['Token']==org_netsalarydf['Token'].max()]
                        netsalarydf = netsalarydf.astype(str)
                        netsalary_list = netsalarydf['Token'].tolist()                
                        if len(netsalary_list)>1:
                            netsalary_text = netsalary_list[0]
                            confidence_netsalary=netsalary_score[0]                            
                        else:
                            netsalary_text = " ".join(netsalary_list)
                            confidence_netsalary=netsalary_score[0]
                    else:
                        if netsalarydf2.empty:
                            netsalarydf2=netsalarydf[(netsalarydf['attribute_symbol']==0)]
                            if len(netsalarydf2['Token'])>1:
                                #netsalarydf['Token'] = netsalarydf['Token'].str.replace(',','')
                                netsalarydf2['Token'] = netsalarydf2['Token'].apply(lambda x: cleantotal(x))
                                netsalarydf2['Token'] = netsalarydf2['Token'].apply(lambda x: x.replace('.','',1) if x.count('.')>1 else x)
                                org_netsalarydf = netsalarydf2.astype(float)
                                netsalarydf = org_netsalarydf[org_netsalarydf['Token']==org_netsalarydf['Token'].max()]
                                netsalarydf = netsalarydf.astype(str)
                                netsalary_list = netsalarydf['Token'].tolist()                
                                if len(netsalary_list)>1:
                                    netsalary_text = netsalary_list[0]
                                    confidence_netsalary=netsalary_score[0]                            
                                else:
                                    netsalary_text = " ".join(netsalary_list)
                                    confidence_netsalary=netsalary_score[0]
                            else:
                                netsalarydf=netsalarydf2.copy()
                                netsalary_list=netsalarydf['Token'].tolist()
                                netsalary_text = " ".join(netsalary_list)
                                confidence_netsalary=netsalary_score[0]
                        else:
                            netsalarydf=netsalarydf2.copy()
                            netsalary_list=netsalarydf['Token'].tolist()
                            netsalary_text = " ".join(netsalary_list)
                            confidence_netsalary=netsalary_score[0]                         
                else:
                    if netsalarydf.empty:
                        netsalary_text='NA'
                        confidence_netsalary=0
                    else:
                        netsalarydf=netsalarydf
                        netsalary_list=netsalarydf['Token'].tolist()
                        netsalary_text = " ".join(netsalary_list)
                        confidence_netsalary=netsalary_score[0]                
        if netsalary_text=='NA':            
            netsalarydf_org=df.copy()
            netsalarydf=netsalarydf_org.copy()
            #netsalarydf['Token'] = netsalarydf['Token'].str.replace(",|:| ","")
            netsalary_index = linewise_df[linewise_df['Token'].str.contains('net salary|base salary|netsalary|take home|credited:|net pay|nett pay|net amount|net to pay|net salary payable:', na=False, case = False, regex = True)].index.tolist()
            if netsalary_index:
                netsalary_linNo = linewise_df.iloc[netsalary_index[0]]['linNo']
                netsalarydf = linNodf[linNodf['linNo']==netsalary_linNo]
                netsalarydf['attribute_length']=netsalarydf['Token'].apply(lambda x: attribute_length(x))
                netsalarydf=netsalarydf[(netsalarydf['attribute_length']>1)]
                netsalarydf['Token'] = netsalarydf['Token'].apply(lambda x: cleantotal(x))
                netsalarydf['attribute_length']=netsalarydf['Token'].apply(lambda x: attribute_length(x))
                netsalarydf=netsalarydf[(netsalarydf['attribute_length']>2)]
                netsalarydf['Token'] = netsalarydf['Token'].apply(lambda x: x.replace('.','',1) if x.count('.')>1 else x)
                netsalarydf['attribute_type']=netsalarydf['Token'].apply(lambda x: attribute_type(x))            
                netsalarydf = netsalarydf[(netsalarydf['attribute_type'] ==1)]
                if len(netsalarydf['Token'])>1:
                    netsalarydf['attribute_symbol']=netsalarydf['Token'].apply(lambda x: attribute_symbol(x))
                    netsalarydf['attribute_symbol'] = netsalarydf['attribute_symbol'].astype(int)
                    netsalarydf2 = netsalarydf[(netsalarydf['attribute_symbol'] == 1)|(netsalarydf['attribute_symbol'] == 4)|(netsalarydf['attribute_symbol'] == 7)]                    
                    if len(netsalarydf2['Token'])>1:
                        #netsalarydf['Token'] = netsalarydf['Token'].str.replace(",|:| ","")
                        netsalarydf2['Token'] = netsalarydf2['Token'].apply(lambda x: cleantotal(x))
                        netsalarydf2['attribute_length']=netsalarydf2['Token'].apply(lambda x: attribute_length(x))
                        netsalarydf2=netsalarydf2[(netsalarydf2['attribute_length']>2)] 
                        netsalarydf2['Token'] = netsalarydf2['Token'].apply(lambda x: x.replace('.','',1) if x.count('.')>1 else x)
                        org_netsalarydf = netsalarydf2.astype(float)
                        netsalarydf = org_netsalarydf[org_netsalarydf['Token']==org_netsalarydf['Token'].max()]
                        netsalarydf = netsalarydf.astype(str)
                        netsalary_list = netsalarydf['Token'].tolist()
                        # if list contains more than one values, this happens specially when there are same repeatitive values
                        if len(netsalary_list)>1:
                            netsalary_text = netsalary_list[0]
                            confidence_netsalary=80                            
                        else:
                            netsalary_text = " ".join(netsalary_list)
                            confidence_netsalary=80
                    else:
                        if netsalarydf2.empty:
                            netsalarydf2 = netsalarydf[(netsalarydf['attribute_symbol'] == 0)]
                            if len(netsalarydf2['Token'])>1:
                                #netsalarydf['Token'] = netsalarydf['Token'].str.replace(",|:| ","")
                                netsalarydf2['Token'] = netsalarydf2['Token'].apply(lambda x: cleantotal(x))
                                netsalarydf2['attribute_length']=netsalarydf2['Token'].apply(lambda x: attribute_length(x))
                                netsalarydf2=netsalarydf2[(netsalarydf2['attribute_length']>2)]
                                netsalarydf2['Token'] = netsalarydf2['Token'].apply(lambda x: x.replace('.','',1) if x.count('.')>1 else x)
                                org_netsalarydf = netsalarydf2.astype(float)
                                netsalarydf = org_netsalarydf[org_netsalarydf['Token']==org_netsalarydf['Token'].max()]
                                netsalarydf = netsalarydf.astype(str)
                                netsalary_list = netsalarydf['Token'].tolist()
                                # if list contains more than one values, this happens specially when there are same repeatitive values
                                if len(netsalary_list)>1:
                                    netsalary_text = netsalary_list[0]
                                    confidence_netsalary=80                            
                                else:
                                    netsalary_text = " ".join(netsalary_list)
                                    confidence_netsalary=80
                            else:
                                netsalarydf=netsalarydf_org.copy()
                                prefix_netsalarydf = netsalarydf[netsalarydf['Token'].str.contains('Net',regex=True)]
                                prefix_netsalarydf_list=prefix_netsalarydf['Token'].tolist()
                                netsalary_text = " ".join(prefix_netsalarydf_list)
                                confidence_netsalary=70
                                if not prefix_netsalarydf_list:
                                    netsalary_text='NA'
                                    confidence_netsalary=0
                        else:                        
                            netsalary_list=netsalarydf['Token'].tolist()
                            netsalary_text = " ".join(netsalary_list)
                            confidence_netsalary=70                            
                else:
                    if netsalarydf.empty:
                        netsalarydf=netsalarydf_org.copy()
                        prefix_netsalarydf = netsalarydf[netsalarydf['Token'].str.contains('Net',regex=True)]
                        prefix_netsalarydf_list=prefix_netsalarydf['Token'].tolist()
                        netsalary_text = " ".join(prefix_netsalarydf_list)
                        confidence_netsalary=60
                        if not prefix_netsalarydf_list:
                            netsalary_text='NA'
                            confidence_netsalary=0
                    else:                        
                        netsalary_list=netsalarydf['Token'].tolist()
                        netsalary_text = " ".join(netsalary_list)
                        confidence_netsalary=60
            else:
                netsalary_text='NA'
                confidence_netsalary=0
    except Exception as e:
        # print(traceback.print_exc())
        netsalary_text= 'NA'
        confidence_netsalary=0
    netsalary_data=[netsalary_text,confidence_netsalary]


    # Visualization of the results of a detection.
    image = vis_util.visualize_boxes_and_labels_on_image_array(image_np, x, y, z, category_index,
                                                       instance_masks=output_dict.get('detection_masks'),
                                                       use_normalized_coordinates=True, line_thickness=2)
    # plt.figure(figsize=IMAGE_SIZE)
    # plt.imshow(image_np)
    #     count+=1
    im = Image.fromarray(image)
    # im = image_resize(im)
    im.show()
  
    return [employername_data,employeraddress_data,employeename_data,employeeid_data,employeepanno_data,employeeuanno_data,employeedoj_data,employeedesignation_data,employeebankaccountno_data,bankname_data,periodofpay_data,netsalary_data]
    # return [employername_text,employeename_text,periodofpay_text,netsalary_text]



    



