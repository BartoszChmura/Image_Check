import cv2
import os
import numpy as np


def calculate_saturation(image_path):
    img = cv2.imread(image_path)
    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    saturation = hsv_img[:, :, 1].mean()
    return saturation


def calculate_median_saturation(image_dir):
    saturation_values = []
    images = os.listdir(image_dir)

    for image in images:
        image_path = os.path.join(image_dir, image)
        saturation = calculate_saturation(image_path)
        saturation_values.append(saturation)

    median_saturation = np.median(saturation_values)
    return median_saturation
