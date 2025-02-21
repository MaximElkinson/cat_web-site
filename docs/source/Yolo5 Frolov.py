import numpy as np
import cv2

net = cv2.dnn.readNet('yolov5s.onnx')

# Train/val/test sets as 1) dir: path/to/imgs, 2) file: path/to/imgs.txt, or 3) list: [path/to/imgs1, path/to/imgs2, ..]
path: C:/yolo5 # dataset root dir
train: C:/yolo5/images/train2017 # train images (relative to 'path') 128 images
val: C:/yolo5/images/train2017 # val images (relative to 'path') 128 images
test: # test images (optional)

# Classes (80 COCO classes)
names:
    0: person
    1: bicycle
    2: car
    # ...
    77: teddy bear
    78: hair drier
    79: toothbrush