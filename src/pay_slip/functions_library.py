import pandas as pd
import xlrd
import os
from google.cloud import vision
from google.cloud.vision import types
from scipy.ndimage import interpolation as inter
import numpy as np
import io
import cv2
from wand.image import Image, Color
import gc
import traceback
import config.config as project_configs

key = project_configs.INTAIN_BANK_STATEMENT_GOOGLE_APPLICATION_CREDENTIALS

########################################################################################################################
def skewcorrect(img_path):
    out_image_path = img_path
    img = cv2.imread(img_path,0)
    def find_score(arr, angle):
        data = inter.rotate(arr, angle, reshape=False, order=0)
        hist = np.sum(data, axis=1)
        score = np.sum((hist[1:] - hist[:-1]) ** 2)
        return hist, score

    delta = 1
    limit = 5
    angles = np.arange(-limit, limit + delta, delta)
    scores = []
    for angle in angles:
        hist, score = find_score(img, angle)
        scores.append(score)

    best_score = max(scores)
    best_angle = angles[scores.index(best_score)]
    # print('Best angle', best_angle)

    #correct skew
    num_rows, num_cols = img.shape[:2]

    rotation_matrix = cv2.getRotationMatrix2D((num_cols / 2, num_rows / 2), best_angle, 1)
    img_rotation = cv2.warpAffine(img, rotation_matrix, (num_cols, num_rows), flags=cv2.INTER_LINEAR,
                                      borderMode=cv2.BORDER_REPLICATE)
    converted_img = cv2.cvtColor(img_rotation, cv2.COLOR_GRAY2BGR)

    cv2.imwrite(out_image_path, converted_img)
########################################################################################################################
def wandPdfSplit(filename, output_path):
    try:
        all_pages = Image(filename=filename, resolution=300)

        for i, page in enumerate(all_pages.sequence):
            with Image(page) as img:
                img.format = 'jpg'
                img.background_color = Color('white')
                img.alpha_channel = 'remove'
                image_filename = os.path.splitext(os.path.basename(filename))[0]
                image_filename = '{}_{}.jpg'.format(image_filename, i)
                image_filename = os.path.join(output_path, image_filename)
                img.save(filename=image_filename)
                skewcorrect(image_filename)

        num_images = len(all_pages.sequence)
        del all_pages
        gc.collect()
        return num_images
    except:
        print(traceback.print_exc())
        return -1
########################################################################################################################
def visionocr(imagein, csvfile, outputFilePath, outputFilePath_Coords):
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = key

    client = vision.ImageAnnotatorClient()
    with io.open(imagein, 'rb') as image_file:
        content = image_file.read()
    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    image = types.Image(content=content)
    response = client.text_detection(image=image)
    texts = response.text_annotations
    document = response.full_text_annotation
    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    with open(csvfile, 'w') as file:
        for text in texts[1:]:
            vertices = (['{}\t{}'.format(vertex.x, vertex.y) for vertex in text.bounding_poly.vertices])
            file.write(str(text.description).replace('"', '') + '\t' + '\t'.join(vertices) + '\n')
    file.close()
    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    file = open(outputFilePath, "w", encoding="utf-8")
    fileWords = open(outputFilePath_Coords, "w", encoding="utf-8")
    bounds = []; words = []; paragraphs = []
    for page in document.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                strPara = ""; coordinates = ""
                for word in paragraph.words:
                    strWord = ""
                    for symbol in word.symbols:
                        strWord = strWord + symbol.text
                    x1y1 = str(word.bounding_box.vertices[0].x) + "," + str(word.bounding_box.vertices[0].y)
                    x2y2 = str(word.bounding_box.vertices[2].x) + "," + str(word.bounding_box.vertices[2].y)
                    coords = [x1y1, x2y2]
                    strCoords = "|".join(coords)
                    words.append(strWord)
                    strPara = strPara + " " + strWord
                    coordinates = coordinates + "@#@" + strCoords
                    bounds.append(word.bounding_box)
                coordinates = coordinates[3:]
                strPara = strPara[1:]
                fileWords.write(strPara + "<-->" + coordinates + "\n")
                file.write(strPara + "\n")
                paragraphs.append(strPara)
    file.close(); fileWords.close()
########################################################################################################################
def readcsv(csvfile):
    df = pd.read_csv(csvfile, names=['Token', 'x0', 'y0', 'x1', 'y1', 'x2', 'y2', 'x3', 'y3'], delimiter='\t')
    df['Token'] = df['Token'].astype(str)
    return df
###############################################################################################
def getDataFromXL(path, sheet_index, column_number): # To read data from *.xlsx file
    workbook = xlrd.open_workbook(path)
    worksheet = workbook.sheet_by_index(sheet_index)
    list_word = []
    for row in range(1, worksheet.nrows):
        row_value = worksheet.cell_value(row, column_number)
        if not str(row_value).strip() == "NA":
            list_word.append(str(row_value).strip())

    return list_word
###############################################################################################
def addheight(dataframe):
    docDF = dataframe
    for index, row in docDF.iterrows():
        height = max(row['y2'], row['y3']) - min(row['y0'], row['y1'])
        docDF.loc[index, 'ht'] = height
        maxW = max(row['x3'], row['x1'])
        docDF.loc[index, 'maxW'] = maxW
    return docDF
###############################################################################################
def addrownoNew(dataframe):
    docDF = dataframe
    docDF = docDF.sort_values(by=['y0'])
    lineStartNo = 1
    currenLIneNo = lineStartNo

    row_iterator = docDF.iterrows()
    loc , first = next(row_iterator)
    docDF.loc[loc, 'linNo'] = currenLIneNo
    y_min = min(first['y0'], first['y1'])
    ht = first['ht']

    for index, row in row_iterator:
        if y_min-5 <= row['y0'] < y_min+ht:
            docDF.loc[index, 'linNo'] = currenLIneNo
        else:
            currenLIneNo = currenLIneNo + 1
            docDF.loc[index, 'linNo'] = currenLIneNo
            y_min = min(row['y0'], row['y1'])
            ht = row['ht']
    return docDF
###############################################################################################
def ParaCode(df, paracsvfile):
    docDF = df
    docDF = addheight(dataframe=docDF)
    docDF = addrownoNew(dataframe=docDF)
    docDF.fillna(0, inplace=True)

    ####To sort data with respect to line no and x0
    docDF = docDF.sort_values(by=['linNo', 'x0'])

    ###To find out the space
    docDF['x0_shift'] = docDF.x0.shift(periods=-1)
    docDF['xdiff'] = (docDF['x0_shift'] - docDF['maxW'])
    docDF['xdiff'] = docDF.xdiff.shift(periods=1)
    docDF = docDF.assign(xdiff=lambda x: x.xdiff.where(x.xdiff.ge(0)))
    docDF.fillna(0, inplace=True)

    medianxdiff = docDF['xdiff'].median()
    medianxdiff = int(medianxdiff)

    newdf = docDF.groupby('linNo')
    newdf.fillna(0, inplace=True)

    with open(paracsvfile, 'w') as file:

        for linNo, linNo_df in newdf:
            for index, row in linNo_df.iterrows():
                space = row['xdiff']
                space = int(space)
                text = row['Token']
                newLineSpace = row['x0']
                newLineSpace = int(newLineSpace)
                if medianxdiff == 0:
                    medianxdiff = 12
                if space == 0:
                    file.write('&nbsp;' * round(newLineSpace / medianxdiff) + str(text) + '&nbsp;')
                else:
                    file.write('&nbsp;' * round(space / medianxdiff) + str(text) + '&nbsp;')
            file.write('\n')
    file.close()
    df = pd.read_csv(paracsvfile, delimiter='\t', sep=None, header=None,error_bad_lines=False)
    pd.set_option('display.max_colwidth', -1)
    return df
###############################################################################################
def cleantext(text):
    cleanedtext = []
    for text in text:
        text = text.split()
        cleaned_string = []
        for text in text:
            text = text.strip()
            cleaned_string.append(text)
        cleaned_string = ' '.join(cleaned_string)
        cleanedtext.append(cleaned_string)
    return cleanedtext
###############################################################################################
def extracttext(df):
    df = df.replace('&nbsp;', ' ', regex=True)
    df = df.astype(str)
    textlist = df[0].values
    cleanedtext = cleantext(textlist)
    text = ' '.join(cleanedtext)
    return text #cleanedtext textlist,
###############################################################################################
