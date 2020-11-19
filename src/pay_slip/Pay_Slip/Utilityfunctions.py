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
    min_score_thresh = 0.55
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
    employeename_label=[1]
    netsalary_label = [12]
    periodofpay_label=[13]
    label = [8,1,13,12]
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
    
    # Localization of employee details
    employeename_cords,newemployeename_cords,employeename_score= get_cords(output_dict,image,employeename_label)

    # Localization of bank details
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
                employername_text="NA"
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

########### EmployeeName Extraction ########################################################
    try:
        employeename_text="NA"
        if employeename_cords:
            print("coords")
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
            print("1")
            employeenamedf_org=df.copy()
            employeenamedf=employeenamedf_org.copy()
            employeename_index = linewise_df[linewise_df['Token'].str.contains('emp name|employee name|empname|employeename|emp. name|emp name.:|employee name|employee name.:|emp name:|employee name:|name of the employee|name|mr|ms|mrs', na=False, case = False, regex = True)].index.tolist()
            print(employeename_index)
            if employeename_index:
                ### to add
                # for i in range(len(employername_index)-1):
                employeename_linNo = linewise_df.iloc[employeename_index[0]]['linNo']
                employeenamedf = linNodf[linNodf['linNo']==employeename_linNo]
                # print("employeenamedf",employeenamedf)
                employeenamedf.sort_values(['x0'],inplace = True)
                temp_df = employeenamedf.reset_index(drop=True)
                employeename_index = temp_df[temp_df['Token'].str.contains('emp name|employee name|empname|employeename|emp. name|emp name.:|employee name|employee name.:|emp name:|employee name:|name of the employee|name|mr|ms|mrs', na=False, case = False, regex = True)].index.tolist()
                print(employeename_index)
                temp_df.drop(temp_df.loc[0:employeename_index[0]].index, inplace=True)
                employeenamedf = temp_df.astype(str)
                # print(employeenamedf[employeenamedf['Token'].str.contains('emp name|employee name|empname|employeename|emp. name|emp name.:|employee name|employee name.:|emp name:|employee name:|name of the employee', na=False, case = False, regex = True)])
                # employeenamedf = employeenamedf[employeenamedf['Token'].str.contains('name|name.:|name:', na=False, case = False, regex = True).shift(1).fillna(False)]
                employeenamedf_list = employeenamedf['Token'].tolist()
                # print(employeenamedf_list)
                employeename_text = " ".join(employeenamedf_list)
                print(employeename_text)
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
                # print(namelist)
                ####to add
                if namelist :
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
    

########### Period of Pay Extraction ########################################################
    try:
        periodofpay_text= "NA"
        if periodofpay_cords:
            print("pop coords")
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
            print(periodofpay_index)
            if periodofpay_index:
                periodofpay_linNo = linewise_df.iloc[periodofpay_index[0]]['linNo']
                periodofpaydf = linNodf[linNodf['linNo']==periodofpay_linNo]
                periodofpaydf=ParaCode(periodofpaydf)
                print(periodofpaydf)
                text = periodofpaydf[0].tolist()
                text = " ".join(text)
                print("outside",text)
                periodofpay_list = re.findall(r'''January\s{0,3}\d{2,4}|Jan\s{0,3}\d{2,4}|February\s{0,3}\d{2,4}|Feb\s{0,3}\d{2,4}|March\s{0,3}\d{2,4}|Mar\s{0,3}\d{2,4}|April\s{0,3}\d{2,4}|Apr\s{0,3}\d{2,4}|May\s{0,3}\d{2,4}|June\s{0,3}\d{2,4}|Jun\s{0,3}\d{2,4}|July\s{0,3}\d{2,4}|Jul\s{0,3}\d{2,4}|August\s{0,3}\d{2,4}|Aug\s{0,3}\d{2,4}|September\s{0,3}\d{2,4}|Sept\s{0,3}\d{2,4}|October\s{0,3}\d{2,4}|Oct\s{0,3}\d{2,4}|November\s{0,3}\d{2,4}|Nov\s{0,3}\d{2,4}|December\s{0,3}\d{2,4}|Dec\s{0,3}\d{2,4}|January-\s{0,3}\d{2,4}|Jan-\s{0,3}\d{2,4}|February-\s{0,3}\d{2,4}|Feb-\s{0,3}\d{2,4}|March-\s{0,3}\d{2,4}|Mar-\s{0,3}\d{2,4}|April-\s{0,3}\d{2,4}|Apr-\s{0,3}\d{2,4}|May-\s{0,3}\d{2,4}|June-\s{0,3}\d{2,4}|Jun-\s{0,3}\d{2,4}|July-\s{0,3}\d{2,4}|Jul-\s{0,3}\d{2,4}|August-\s{0,3}\d{2,4}|Aug-\s{0,3}\d{2,4}|September-\s{0,3}\d{2,4}|Sept-\s{0,3}\d{2,4}|October-\s{0,3}\d{2,4}|Oct-\s{0,3}\d{2,4}|November-\s{0,3}\d{2,4}|Nov-\s{0,3}\d{2,4}|December-\s{0,3}\d{2,4}|Dec-\s{0,3}\d{2,4}|january-\s{0,3}\d{2,4}|jan-\s{0,3}\d{2,4}|february-\s{0,3}\d{2,4}|feb-\s{0,3}\d{2,4}|march-\s{0,3}\d{2,4}|mar-\s{0,3}\d{2,4}|april-\s{0,3}\d{2,4}|apr-\s{0,3}\d{2,4}|may-\s{0,3}\d{2,4}|june-\s{0,3}\d{2,4}|jun-\s{0,3}\d{2,4}|july-\s{0,3}\d{2,4}|jul-\s{0,3}\d{2,4}|august-\s{0,3}\d{2,4}|aug-\s{0,3}\d{2,4}|september-\s{0,3}\d{2,4}|sept-\s{0,3}\d{2,4}|october-\s{0,3}\d{2,4}|oct-\s{0,3}\d{2,4}|november-\s{0,3}\d{2,4}|nov-\s{0,3}\d{2,4}|december-\s{0,3}\d{2,4}|dec-\s{0,3}\d{2,4}|JANUARY\s{0,3}\d{2,4}|JAN\s{0,3}\d{2,4}|FEBRUARY\s{0,3}\d{2,4}|FEB\s{0,3}\d{2,4}|MARCH\s{0,3}\d{2,4}|MAR\s{0,3}\d{2,4}|APRIL\s{0,3}\d{2,4}|APR\s{0,3}\d{2,4}|MAY\s{0,3}\d{2,4}|JUNE\s{0,3}\d{2,4}|JUN\s{0,3}\d{2,4}|JULY\s{0,3}\d{2,4}|JUL\s{0,3}\d{2,4}|AUGUST\s{0,3}\d{2,4}|AUG\s{0,3}\d{2,4}|SEPTEMBER\s{0,3}\d{2,4}|SEPT\s{0,3}\d{2,4}|OCTOBER\s{0,3}\d{2,4}|OCT\s{0,3}\d{2,4}|NOVEMBER\s{0,3}\d{2,4}|NOV\s{0,3}\d{2,4}|DECEMBER\s{0,3}\d{2,4}|DEC\s{0,3}\d{2,4}|JANUARY-\s{0,3}\d{2,4}|JAN-\s{0,3}\d{2,4}|FEBRUARY-\s{0,3}\d{2,4}|FEB-\s{0,3}\d{2,4}|MARCH-\s{0,3}\d{2,4}|MAR-\s{0,3}\d{2,4}|APRIL-\s{0,3}\d{2,4}|APR-\s{0,3}\d{2,4}|MAY-\s{0,3}\d{2,4}|JUNE-\s{0,3}\d{2,4}|JUN-\s{0,3}\d{2,4}|JULY-\s{0,3}\d{2,4}|JUL-\s{0,3}\d{2,4}|AUGUST-\s{0,3}\d{2,4}|AUG-\s{0,3}\d{2,4}|SEPTEMBER-\s{0,3}\d{2,4}|SEPT-\s{0,3}\d{2,4}|OCTOBER-\s{0,3}\d{2,4}|OCT-\s{0,3}\d{2,4}|NOVEMBER-\s{0,3}\d{2,4}|NOV-\s{0,3}\d{2,4}|DECEMBER-\s{0,3}\d{2,4}|DEC-\s{0,3}\d{2,4}''',text)
                if periodofpay_list:
                    periodofpay_text = periodofpay_list[0]
                    confidence_periodofpay=80
                else:
                    periodofpaydf=linNodf[(linNodf['linNo']>=periodofpay_linNo)&(linNodf['linNo']<=periodofpay_linNo+2)]
                    periodofpaydf=ParaCode(periodofpaydf)
                    text = periodofpaydf[0].tolist()
                    text = " ".join(text)
                    print("texttt",text)
                    periodofpay_list = re.findall(r'''January\s{0,3}\d{2,4}|Jan\s{0,3}\d{2,4}|February\s{0,3}\d{2,4}|Feb\s{0,3}\d{2,4}|March\s{0,3}\d{2,4}|Mar\s{0,3}\d{2,4}|April\s{0,3}\d{2,4}|Apr\s{0,3}\d{2,4}|May\s{0,3}\d{2,4}|June\s{0,3}\d{2,4}|Jun\s{0,3}\d{2,4}|July\s{0,3}\d{2,4}|Jul\s{0,3}\d{2,4}|August\s{0,3}\d{2,4}|Aug\s{0,3}\d{2,4}|September\s{0,3}\d{2,4}|Sept\s{0,3}\d{2,4}|October\s{0,3}\d{2,4}|Oct\s{0,3}\d{2,4}|November\s{0,3}\d{2,4}|Nov\s{0,3}\d{2,4}|December\s{0,3}\d{2,4}|Dec\s{0,3}\d{2,4}|January-\s{0,3}\d{2,4}|Jan-\s{0,3}\d{2,4}|February-\s{0,3}\d{2,4}|Feb-\s{0,3}\d{2,4}|March-\s{0,3}\d{2,4}|Mar-\s{0,3}\d{2,4}|April-\s{0,3}\d{2,4}|Apr-\s{0,3}\d{2,4}|May-\s{0,3}\d{2,4}|June-\s{0,3}\d{2,4}|Jun-\s{0,3}\d{2,4}|July-\s{0,3}\d{2,4}|Jul-\s{0,3}\d{2,4}|August-\s{0,3}\d{2,4}|Aug-\s{0,3}\d{2,4}|September-\s{0,3}\d{2,4}|Sept-\s{0,3}\d{2,4}|October-\s{0,3}\d{2,4}|Oct-\s{0,3}\d{2,4}|November-\s{0,3}\d{2,4}|Nov-\s{0,3}\d{2,4}|December-\s{0,3}\d{2,4}|Dec-\s{0,3}\d{2,4}|january-\s{0,3}\d{2,4}|jan-\s{0,3}\d{2,4}|february-\s{0,3}\d{2,4}|feb-\s{0,3}\d{2,4}|march-\s{0,3}\d{2,4}|mar-\s{0,3}\d{2,4}|april-\s{0,3}\d{2,4}|apr-\s{0,3}\d{2,4}|may-\s{0,3}\d{2,4}|june-\s{0,3}\d{2,4}|jun-\s{0,3}\d{2,4}|july-\s{0,3}\d{2,4}|jul-\s{0,3}\d{2,4}|august-\s{0,3}\d{2,4}|aug-\s{0,3}\d{2,4}|september-\s{0,3}\d{2,4}|sept-\s{0,3}\d{2,4}|october-\s{0,3}\d{2,4}|oct-\s{0,3}\d{2,4}|november-\s{0,3}\d{2,4}|nov-\s{0,3}\d{2,4}|december-\s{0,3}\d{2,4}|dec-\s{0,3}\d{2,4}|JANUARY\s{0,3}\d{2,4}|JAN\s{0,3}\d{2,4}|FEBRUARY\s{0,3}\d{2,4}|FEB\s{0,3}\d{2,4}|MARCH\s{0,3}\d{2,4}|MAR\s{0,3}\d{2,4}|APRIL\s{0,3}\d{2,4}|APR\s{0,3}\d{2,4}|MAY\s{0,3}\d{2,4}|JUNE\s{0,3}\d{2,4}|JUN\s{0,3}\d{2,4}|JULY\s{0,3}\d{2,4}|JUL\s{0,3}\d{2,4}|AUGUST\s{0,3}\d{2,4}|AUG\s{0,3}\d{2,4}|SEPTEMBER\s{0,3}\d{2,4}|SEPT\s{0,3}\d{2,4}|OCTOBER\s{0,3}\d{2,4}|OCT\s{0,3}\d{2,4}|NOVEMBER\s{0,3}\d{2,4}|NOV\s{0,3}\d{2,4}|DECEMBER\s{0,3}\d{2,4}|DEC\s{0,3}\d{2,4}|JANUARY-\s{0,3}\d{2,4}|JAN-\s{0,3}\d{2,4}|FEBRUARY-\s{0,3}\d{2,4}|FEB-\s{0,3}\d{2,4}|MARCH-\s{0,3}\d{2,4}|MAR-\s{0,3}\d{2,4}|APRIL-\s{0,3}\d{2,4}|APR-\s{0,3}\d{2,4}|MAY-\s{0,3}\d{2,4}|JUNE-\s{0,3}\d{2,4}|JUN-\s{0,3}\d{2,4}|JULY-\s{0,3}\d{2,4}|JUL-\s{0,3}\d{2,4}|AUGUST-\s{0,3}\d{2,4}|AUG-\s{0,3}\d{2,4}|SEPTEMBER-\s{0,3}\d{2,4}|SEPT-\s{0,3}\d{2,4}|OCTOBER-\s{0,3}\d{2,4}|OCT-\s{0,3}\d{2,4}|NOVEMBER-\s{0,3}\d{2,4}|NOV-\s{0,3}\d{2,4}|DECEMBER-\s{0,3}\d{2,4}|DEC-\s{0,3}\d{2,4}''',text)
                    if periodofpay_list:
                        periodofpay_text = periodofpay_list[0]
                        confidence_periodofpay=60
                    else:
                        periodofpay_text = "NA"
                        confidence_periodofpay=0
                
                if periodofpay_text=="NA":
                    print(periodofpay_text)
                    print(text,"our function")
                    match = re.search(r'\d{2}.\d{2}.\d{2,4}', text)
                    if match:
                        periodofpay_text = match.group(0)
                        confidence_periodofpay=80
                    match = re.search(r'\d{2}.\d{2}.\d{2,4}', text)
                    if match:
                        periodofpay_text = match.group(0)
                        confidence_periodofpay=80
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
            # print("coords")
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
                # print(netsalarydf)
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
                    else: #if len(netsalarydf2['Token'])>1:
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
                            else: #if len(netsalarydf2['Token'])>1:
                                netsalarydf=netsalarydf2.copy()
                                netsalary_list=netsalarydf['Token'].tolist()
                                netsalary_text = " ".join(netsalary_list)
                                confidence_netsalary=netsalary_score[0]
                        else: #if netsalarydf2.empty:
                            netsalarydf=netsalarydf2.copy()
                            netsalary_list=netsalarydf['Token'].tolist()
                            netsalary_text = " ".join(netsalary_list)
                            confidence_netsalary=netsalary_score[0]                         
                else: #len(netsalarydf['Token'])>1:
                    if netsalarydf.empty:
                        netsalary_text='NA'
                        confidence_netsalary=0
                    else:
                        netsalarydf=netsalarydf
                        netsalary_list=netsalarydf['Token'].tolist()
                        netsalary_text = " ".join(netsalary_list)
                        confidence_netsalary=netsalary_score[0]                
        if netsalary_text=='NA':    #netsalary_cords        
            netsalarydf_org=df.copy()
            netsalarydf=netsalarydf_org.copy()
            #netsalarydf['Token'] = netsalarydf['Token'].str.replace(",|:| ","")
            netsalary_index = linewise_df[linewise_df['Token'].str.contains('net salary|base salary|netsalary|take home|credited:|net pay|nett pay|net amount|net to pay|net salary payable:', na=False, case = False, regex = True)].index.tolist()
            if netsalary_index:
                for i in range(len(netsalarydf)-1):
                    if netsalary_text=='NA':
                        # print(i)
                        netsalary_linNo = linewise_df.iloc[netsalary_index[i]]['linNo']
                        netsalarydf = linNodf[linNodf['linNo']==netsalary_linNo]
                        netsalarydf['attribute_length']=netsalarydf['Token'].apply(lambda x: attribute_length(x))
                        netsalarydf=netsalarydf[(netsalarydf['attribute_length']>1)]
                        netsalarydf['Token'] = netsalarydf['Token'].apply(lambda x: cleantotal(x))
                        netsalarydf['attribute_length']=netsalarydf['Token'].apply(lambda x: attribute_length(x))
                        netsalarydf=netsalarydf[(netsalarydf['attribute_length']>2)]
                        netsalarydf['Token'] = netsalarydf['Token'].apply(lambda x: x.replace('.','',1) if x.count('.')>1 else x)
                        netsalarydf['attribute_type']=netsalarydf['Token'].apply(lambda x: attribute_type(x))            
                        netsalarydf = netsalarydf[(netsalarydf['attribute_type'] ==1)]
                        # print("1",netsalarydf)
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
                                    netsalary_text = netsalary_list[i]
                                    confidence_netsalary=80                            
                                else:
                                    netsalary_text = " ".join(netsalary_list)
                                    confidence_netsalary=80
                            else: # if len(netsalarydf2['Token'])>1:
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
                                else:   # netsalarydf2.empty:                     
                                    netsalary_list=netsalarydf['Token'].tolist()
                                    netsalary_text = " ".join(netsalary_list)
                                    confidence_netsalary=70                            
                        else: #if len(netsalarydf['Token'])>1:
                            if netsalarydf.empty:
                                # print("2")
                                netsalarydf=netsalarydf_org.copy()
                                prefix_netsalarydf = netsalarydf[netsalarydf['Token'].str.contains('Net',regex=True)]
                                prefix_netsalarydf_list=prefix_netsalarydf['Token'].tolist()
                                netsalary_text = " ".join(prefix_netsalarydf_list)
                                confidence_netsalary=60
                                if not prefix_netsalarydf_list:
                                    netsalary_text='NA'
                                    confidence_netsalary=0
                            else: #netsalarydf.empty
                                # print("3")                 
                                netsalary_list=netsalarydf['Token'].tolist()
                                # print(netsalary_list)
                                netsalary_text = " ".join(netsalary_list)
                                # print(netsalary_text)
                                confidence_netsalary=60
            else: #netsalary_index
                netsalary_text='NA'
                confidence_netsalary=0
    except Exception as e:
        # print(traceback.print_exc())
        netsalary_text= 'NA'
        confidence_netsalary=0
    # print(netsalary_text,confidence_netsalary)
    netsalary_data=[netsalary_text,confidence_netsalary]


########### Gross Salary Extraction ########################################################
    try:
        print("Gross Salary Calculation")
        grosssalary_text='NA'
        grosssalarydf_org=df.copy()
        grosssalarydf=grosssalarydf_org.copy()
        grosssalary_index = linewise_df[linewise_df['Token'].str.contains('gross pay|gross entitlement|total earnings|total|gross earnings|gross earning', na=False, case = False, regex = True)].index.tolist()
        if grosssalary_index:
            for i in range(len(grosssalarydf)-1):
                if grosssalary_text=='NA':
                    grosssalary_linNo = linewise_df.iloc[grosssalary_index[i]]['linNo']
                    grosssalarydf = linNodf[linNodf['linNo']==grosssalary_linNo]
                    grosssalarydf['attribute_length']=grosssalarydf['Token'].apply(lambda x: attribute_length(x))
                    grosssalarydf=grosssalarydf[(grosssalarydf['attribute_length']>1)]
                    grosssalarydf['Token'] = grosssalarydf['Token'].apply(lambda x: cleantotal(x))
                    grosssalarydf['attribute_length']=grosssalarydf['Token'].apply(lambda x: attribute_length(x))
                    grosssalarydf=grosssalarydf[(grosssalarydf['attribute_length']>2)]
                    grosssalarydf['Token'] = grosssalarydf['Token'].apply(lambda x: x.replace('.','',1) if x.count('.')>1 else x)
                    grosssalarydf['attribute_type']=grosssalarydf['Token'].apply(lambda x: attribute_type(x))     
                    grosssalarydf = grosssalarydf[(grosssalarydf['attribute_type'] ==1 )]
                    grosssalarydf.sort_values(['x0'],inplace = True)
                    grosssalary_list = grosssalarydf['Token'].tolist()
                    grosssalary_list.sort(key=float,reverse=True)
                    if len(grosssalary_list)>=1:
                        for i in range(len(grosssalary_list)):
                            if grosssalary_list[i] not in ['0','0.00'] and grosssalary_text=='NA':
                                grosssalary_text = grosssalary_list[i]
                                confidence_grosssalary=80                            
        else: #gross_salary index
            grosssalary_text='NA'
            confidence_grosssalary=0
    except Exception as e:
        # print(traceback.print_exc())
        grosssalary_text= 'NA'
        confidence_grosssalary=0
    # print(netsalary_text,confidence_netsalary)
    grosssalary_data=[grosssalary_text,confidence_grosssalary]




    # Visualization of the results of a detection.
    # image = vis_util.visualize_boxes_and_labels_on_image_array(image_np, x, y, z, category_index,
    #                                                    instance_masks=output_dict.get('detection_masks'),
    #                                                    use_normalized_coordinates=True, line_thickness=2)
    # # plt.figure(figsize=IMAGE_SIZE)
    # # plt.imshow(image_np)
    # #     count+=1
    # im = Image.fromarray(image)
    # # im = image_resize(im)
    # im.show()
  
    return [employername_data,employeename_data,periodofpay_data,netsalary_data,grosssalary_data]
    # return [employername_text,employeename_text,periodofpay_text,netsalary_text]




    



