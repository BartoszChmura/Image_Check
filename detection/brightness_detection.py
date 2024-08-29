import cv2
import os
import numpy as np

def calculate_brightness(image_path):
    img = cv2.imread(image_path)
    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    brightness = hsv_img[:, :, 2].mean()
    return brightness

def calculate_median_brightness(image_dir):
    brightness_values = []
    images = os.listdir(image_dir)

    for image in images:
        image_path = os.path.join(image_dir, image)
        brightness = calculate_brightness(image_path)
        brightness_values.append(brightness)

    median_brightness = np.median(brightness_values)
    return median_brightness