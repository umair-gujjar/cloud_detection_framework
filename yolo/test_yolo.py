# Instead just add darknet.py to somewhere in your python path
# OK actually that might not be a great idea, idk, work in progress
# Use at your own risk. or don't, i don't care
import xml.etree.ElementTree as ET
import sys
import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
import sqlite3 as db


test_images_list_file = open(os.path.join(
    '/home/simenvg/data/tmp', "test.txt"), "r")
image_filepaths = test_images_list_file.readlines()

RED = (0, 0, 255)
GREEN = (0, 255, 0)
BLUE = (255, 0, 0)


class Box(object):
    """docstring for Box"""

    def __init__(self, cls, x_min, x_max, y_min, y_max, confidence=None):
        self.cls = cls
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max
        self.confidence = confidence


def get_GT_boxes(label_filepath):
    in_file = open(os.path.join(label_filepath), 'r')
    tree = ET.parse(in_file)
    root = tree.getroot()
    boxes = []
    for obj in root.iter('object'):
        xmlbox = obj.find('bndbox')
        boxes.append(Box(obj.find('name').text, float(xmlbox.find('xmin').text), float(
            xmlbox.find('xmax').text), float(xmlbox.find('ymin').text), float(xmlbox.find('ymax').text)))
    return boxes


def convert_yolo_format(x_center, y_center, width, height):
    x_min = float(x_center) - float(width) / 2
    x_max = float(x_center) + float(width) / 2
    y_min = float(y_center) - float(height) / 2
    y_max = float(y_center) + float(height) / 2
    return [x_min, x_max, y_min, y_max]


def get_intersected_area(box1, box2):
    dx = min(box1.x_max, box2.x_max) - max(box1.x_min, box2.x_min)
    dy = min(box1.y_max, box2.y_max) - max(box1.y_min, box2.y_min)
    if dy <= 0 or dx <= 0:
        return -1
    else:
        return dx * dy


def get_iou(box1, box2):
    area_box1 = (box1.x_max - box1.x_min) * (box1.y_max - box1.y_min)
    area_box2 = (box2.x_max - box2.x_min) * (box2.y_max - box2.y_min)
    intersected_area = get_intersected_area(box1, box2)
    # print(intersected_area)
    if intersected_area == -1:
        return -1
    else:
        return intersected_area / (area_box1 + area_box2 - intersected_area)


def valid_detection(detected_box, gt_box, iou_thresh=0.5):
    return get_iou(detected_box, gt_box) >= iou_thresh


# def get_precision_recall(detections, iou_thresh, confidence_thresh=0.0):
#     true_positives = 0
#     num_detections = 0
#     num_gt_boxes = 0
#     for key, value in detections.iteritems():
#         gt_boxes = get_GT_boxes(os.path.join(
#             '/home/simenvg/tmp/test', (key.strip()[:-4] + '.xml')))
#         num_detections += len(value)
#         for gt_box in gt_boxes:
#             for detected_box in value:
#                 if detected_box.confidence >= confidence_thresh:
#                     if valid_detection(detected_box, gt_box, iou_thresh=iou_thresh):
#                         true_positives += 1
#                         value.remove(detected_box)
#                         break
#         num_gt_boxes += len(gt_boxes)
#     precision = float(true_positives) / float(num_detections)
#     recall = float(true_positives) / float(num_gt_boxes)
#     return (precision, recall)


# iou_threshs = [x * 0.01 for x in range(0, 100)]


# precisions = []
# recalls = []
# for iou_thresh in iou_threshs:
#     (precision, recall) = get_precision_recall(YOLO_detections, iou_thresh)
#     precisions.append(precision)
#     recalls.append(recall)

# print(precisions)
# print(recalls)


# plt.plot(recalls, precisions)
# plt.grid(True)
# plt.show()


conn = db.connect('''detections.db''')
c = conn.cursor()


# get_precision_recall(YOLO_detections, 0.1)
font = cv2.FONT_HERSHEY_SIMPLEX
bottomLeftCornerOfText = (10, 500)
fontScale = 0.3
fontColor = (255, 255, 255)
lineType = 1

# print(YOLO_detections['data/obj/extra_kayak_axis0000.jpg'][0].confidence)
i = 0
for img in image_filepaths:
    gt_boxes = get_GT_boxes(os.path.join(
        '', (img.strip()[:-4] + '.xml')))
    # detections = get_yolo_detections(img, net, meta_data_net)
    c.execute('SELECT * FROM detections WHERE image_name=?', (img,))
    detections = c.fetchall()
    im_path = os.path.join('/home/simenvg/data/tmp/test', img.strip())
    image = cv2.imread(im_path)
    print(img)
    if image is None:
        print('No image')
        exit()
    for box in gt_boxes:
        cv2.rectangle(image, (int(box.x_min), int(box.y_max)),
                      (int(box.x_max), int(box.y_min)), GREEN, 2)
    for box in detections:
        if (box[5] == 'building'):
            color = BLUE
        else:
            color = RED
        cv2.rectangle(image, (int(box[1]), int(box[3])),
                      (int(box[2]), int(box[4])), color, 2)
        # cv2.putText(image, box[5],
        #             (int(box[1]), int(box[3])),
        #             font,
        #             fontScale,
        #             RED,
        #             lineType)
    # cv2.imshow('ime', image)
    cv2.imwrite(os.path.join('/home/simenvg/results', 'image_' + str(i) + '.jpg'), image)
    i += 1
    # cv2.waitKey(0)
conn.close()


# image = cv2.imread(os.path.join("/home/simenvg/environments/my_env/test2/data/obj/extra_kayak_axis0000.jpg"))
# And then down here you could detect a lot more images like:
# r = dn.detect(net, meta, "data/obj/selected_08_07_frame12055.jpg")
# print r
# r = dn.detect(net, meta, "data/giraffe.jpg")
# print r
# r = dn.detect(net, meta, "data/horses.jpg")
# print r
# r = dn.detect(net, meta, "data/person.jpg")
# print r