import numpy as np
import os
import sys
import tensorflow as tf
import io
import re
import pandas as pd
from collections import defaultdict
from io import StringIO

from PIL import Image


from google.cloud import vision
from google.cloud.vision import types


from utils import ops as utils_ops

# This is needed to display the images.

from utils import label_map_util

from utils import visualization_utils as vis_util

# What model to download.
# Path to frozen detection graph. This is the actual model that is used for the object detection.
PATH_TO_CKPT = 'frozen_inference_graph.pb'

# List of the strings that is used to add correct label for each box.
PATH_TO_LABELS = os.path.join('trial_label_map.pbtxt')

NUM_CLASSES = 10


print('Loading model')
detection_graph = tf.Graph()
with detection_graph.as_default():
    # od_graph_def = tf.GraphDef()
    od_graph_def = tf.compat.v1.GraphDef() 
    # with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
    with tf.compat.v2.io.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')
print('Model loaded successfully.')

label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES,use_display_name=True)
category_index = label_map_util.create_category_index(categories)

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
    min_score_thresh = 0.85
    bboxes = boxes[scores > min_score_thresh]

    # get image size
    im_width, im_height = image.size
    final_box = []
    for box in bboxes:
        ymin, xmin, ymax, xmax = box
        final_box.append([xmin * im_width, xmax * im_width, ymin * im_height, ymax * im_height])

    final_box = sorted(final_box, key=lambda x: x[0])
    return final_box


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
    # print('===============text list================')
    # print(textlist)
    # print('===============text list================')
    return df, textlist


def extract_table(df, table_cords):
    df = df.sort_values(by=['x0', 'y0'])
    table_cords = table_cords[0]
    x0 = int(table_cords[0]) - 10
    x1 = int(table_cords[1]) + 10
    y0 = int(table_cords[2])
    y1 = int(table_cords[3])
    tabledf = df[(df['x0'] > x0) & (df['y0'] > y0) & (df['x2'] < x1) & (df['y2'] < y1)]
    #     print('*******************8')
    #     print(tabledf)
    return tabledf


def add_col(tabledf, column_cords):
    columnNo = 0
    tabledf = tabledf.sort_values(by=['x0', 'y0'])

    for columnNo, i in enumerate(column_cords):
        tabledf.loc[tabledf['x0'] > int(i[0]), 'columnNo'] = columnNo + 1

    return tabledf


def addrowno(dataframe):
    docDF = dataframe
    docDF = docDF.sort_values(by=['y0'])  # type: object
    docDF['ydiff'] = docDF['y0'].diff()
    meanYDiff = docDF['ydiff'].mean()

    lineStartNo = 1
    currenLIneNo = lineStartNo
    for index, row in docDF.iterrows():
        if row['ydiff'] > meanYDiff:
            currenLIneNo = currenLIneNo + 1  # type: Union[int, Any]
            docDF.loc[index, 'linNo'] = currenLIneNo
        else:
            docDF.loc[index, 'linNo'] = currenLIneNo

    return docDF


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


def table_reconstruct(tabledf):
    tabledf = tabledf.sort_values(['linNo', 'columnNo'])

    rowdf = tabledf.groupby('linNo')
    rowdf.fillna(0, inplace=True)
    lines = []
    for linNo, linNo_df in rowdf:
        column_iter = 1

        final_text = []
        #     print(linNo_df)
        coldf = linNo_df.groupby('columnNo')
        for columnNo, column_df in coldf:
            textline = []
            #             print(columnNo)

            for index, space in column_df.iterrows():
                # print(text)
                text = column_df['Token'].get(index)
                textline.append(text)
                textline = [' '.join(textline)]
            if columnNo - column_iter != 0:
                for i in range(int(columnNo - column_iter)):
                    final_text.append(' ')
                    column_iter += 1
            final_text.append(textline[0])
            #             print(final_text)
            column_iter += 1
        lines.append(final_text)
    final_table = pd.DataFrame(lines)
    return final_table





def table_detection(image_path):
    # imagename = image_path.split('/')[-1]
    # print(imagename)
    # savepath = path + imagename
    table_label = [5]
    tablehead_label = [10]
    label = [5,10]
    image = Image.open(image_path)
    # the array based representation of the image will be used later in order to prepare the
    # result image with boxes and labels on it.
    image_np = load_image_into_numpy_array(image)
    # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
    image_np_expanded = np.expand_dims(image_np, axis=0)
    # Actual detection.
    output_dict = run_inference_for_single_image(image_np, detection_graph)

    label_index = np.isin(output_dict['detection_classes'], label)
    x = output_dict['detection_boxes'][label_index]
    y = output_dict['detection_classes'][label_index]
    z = output_dict['detection_scores'][label_index]

    table_cords = get_cords(output_dict, image, table_label)
    tablehead_cords = get_cords(output_dict, image, tablehead_label)
    if table_cords and tablehead_cords:
        # df, _ = visionocr(image_path, 'apikey.json')
        # tabledf = extract_table(df, table_cords)
        # tabledf = addrowno(tabledf)
        # tabledf = add_col(tabledf, column_cords)
        # #     print(tabledf)
        # final_table = table_reconstruct(tabledf)
        table_cords=table_cords
        tablehead_cords=tablehead_cords
    else:
    
        print('Coordinates not detected')
        table_cords=''
        tablehead_cords=''

    # Visualization of the results of a detection.
    image = vis_util.visualize_boxes_and_labels_on_image_array(image_np, x, y, z, category_index,
                                                       instance_masks=output_dict.get('detection_masks'),
                                                       use_normalized_coordinates=True, line_thickness=2)
    # plt.figure(figsize=IMAGE_SIZE)
    # plt.imshow(image_np)
    #     count+=1
    im = Image.fromarray(image)
    im = image_resize(im)
    im.show()

    return table_cords,tablehead_cords

image_path = '/home/jyoti/Desktop/BankDetails/sample/satatement_images/axis-1.jpg'
table = table_detection(image_path)
print(table)
