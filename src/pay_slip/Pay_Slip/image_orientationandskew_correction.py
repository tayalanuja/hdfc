from PIL import Image
from PIL import ExifTags

import pytesseract
import PIL
from pytesseract import Output
import glob
import os
import traceback
import re
import cv2
import numpy as np
from scipy.ndimage import interpolation as inter



def orientation_correction(output_folder_path, input_image_path):
    head, tail = os.path.split(input_image_path)
    out_imPath= output_folder_path +tail
    im = Image.open(input_image_path)
    try:
        if im._getexif():
            exif=dict((ExifTags.TAGS[k], v) for k, v in im._getexif().items() if k in ExifTags.TAGS)
            print(exif)
            if exif['Orientation'] == 3:
                im=im.rotate(180, expand=True)
            elif exif['Orientation'] == 6:
                im=im.rotate(270, expand=True)
            elif exif['Orientation'] == 8:
                im=im.rotate(90, expand=True)

        try:
            newdata = pytesseract.image_to_osd(im, output_type=Output.DICT)
            conf=newdata['orientation_conf']
            if conf<1:
                if newdata['orientation']==180:
                    im1=im
                else:
                    im1 = im.rotate(360-newdata['orientation'], PIL.Image.NEAREST, expand = 1)
                
            else:
                if newdata['orientation']==180:
                    im1=im
                else:
                    im1 = im.rotate(newdata['orientation'], PIL.Image.NEAREST, expand = 1)

            im1.save(out_imPath)
        
        except Exception as e:
            im.save(out_imPath)
            
    except Exception as e:
            im.save(out_imPath)

    finally:
        return out_imPath

def find_score(arr, angle):
    data = inter.rotate(arr, angle, reshape=False, order=0)
    hist = np.sum(data, axis=1)
    score = np.sum((hist[1:] - hist[:-1]) ** 2)
    return hist, score

def skewcorrect(img_path):
    print(img_path)
    out_image_path = img_path
    img = cv2.imread(img_path,0)
    print(type(img))
    
    delta = 1
    limit = 5
    angles = np.arange(-limit, limit + delta, delta)
    scores = []
    for angle in angles:
        hist, score = find_score(img, angle)
        scores.append(score)

    best_score = max(scores)
    best_angle = angles[scores.index(best_score)]
    
    num_rows, num_cols = img.shape[:2]

    rotation_matrix = cv2.getRotationMatrix2D((num_cols / 2, num_rows / 2), best_angle, 1)
    img_rotation = cv2.warpAffine(img, rotation_matrix, (num_cols, num_rows), flags=cv2.INTER_LINEAR,
                                      borderMode=cv2.BORDER_REPLICATE)
    converted_img = cv2.cvtColor(img_rotation, cv2.COLOR_GRAY2BGR)
    cv2.imwrite(out_image_path, converted_img)
    return out_image_path

