import cv2
import os
import numpy as np

from config.log_config import logger
from utils.helpers import get_image_files, read_image, resource_path


def calculate_brightness(image_path):
    image = read_image(resource_path(image_path))
    if image is None:
        raise Exception(f"Failed to read image from {image_path} - brightness detection")

    hsv_img = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    brightness = hsv_img[:, :, 2].mean()
    return brightness

def calculate_median_brightness(image_dir):
    brightness_values = []

    images = get_image_files(image_dir)
    if images is None:
        return None

    for image in images:
        image_path = os.path.join(image_dir, image)
        brightness = calculate_brightness(image_path)
        if brightness is not None:
            brightness_values.append(brightness)

    if not brightness_values:
        logger.warning(f"No valid images found in directory {image_dir} - brightness detection")
        return None

    median_brightness = np.median(brightness_values)
    return median_brightness

def detect_brightness(image_path, median_brightness, thresholds):
    brightness = calculate_brightness(image_path)

    if brightness is None:
        logger.warning(f"Skipping brightness detection for {image_path} due to error - brightness detection")
        return None

    if brightness < thresholds['brightness']['low'] * median_brightness:
        logger.warning(f'Brightness: {brightness} - low brightness!')
        return True
    elif brightness > thresholds['brightness']['high'] * median_brightness:
        logger.warning(f'Brightness: {brightness} - possible overexposure!')
        return True
    else:
        logger.info(f'Brightness: {brightness}')
        return False
