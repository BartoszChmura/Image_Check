import cv2
import os
import numpy as np

from config.log_config import logger
from utils.helpers import get_image_files, read_image


def calculate_saturation(image_path):
    image = read_image(image_path)
    if image is None:
        raise Exception(f"Failed to read image from {image_path} - saturation detection")

    hsv_img = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    saturation = hsv_img[:, :, 1].mean()
    return saturation



def calculate_median_saturation(image_dir):
    saturation_values = []

    images = get_image_files(image_dir)
    if images is None:
        return None

    for image in images:
        image_path = os.path.join(image_dir, image)
        saturation = calculate_saturation(image_path)
        if saturation is not None:
            saturation_values.append(saturation)

    if not saturation_values:
        logger.warning(f"No valid images found in directory {image_dir} - saturation detection")
        return None

    median_saturation = np.median(saturation_values)
    return median_saturation

def detect_saturation(image_path, median_saturation, thresholds):
    saturation = calculate_saturation(image_path)

    if saturation is None:
        logger.warning(f"Skipping saturation detection for {image_path} due to error - saturation detection")
        return False

    if saturation < thresholds['saturation']['low'] * median_saturation:
        logger.warning(f'Saturation: {saturation} - low saturation!')
        return True
    else:
        logger.info(f'Saturation: {saturation}')
        return False
