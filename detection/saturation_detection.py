import cv2
import os
import numpy as np

from config.log_config import logger



def calculate_saturation(image_path):
    try:
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Failed to read image from {image_path}")

        hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        saturation = hsv_img[:, :, 1].mean()
        return saturation
    except Exception as e:
        logger.error(f"Error calculating saturation for {image_path}: {e}")
        return None


def calculate_median_saturation(image_dir):
    saturation_values = []
    try:
        images = os.listdir(image_dir)
    except OSError as e:
        logger.error(f"Error reading directory {image_dir}: {e}")
        return None

    for image in images:
        image_path = os.path.join(image_dir, image)
        saturation = calculate_saturation(image_path)
        if saturation is not None:
            saturation_values.append(saturation)

    if not saturation_values:
        logger.warning(f"No valid images found in directory {image_dir}.")
        return None

    median_saturation = np.median(saturation_values)
    return median_saturation

def detect_saturation(image_path, median_saturation, thresholds):
    saturation = calculate_saturation(image_path)

    if saturation is None:
        logger.warning(f"Skipping saturation detection for {image_path} due to read error.")
        return False

    if saturation < thresholds['saturation']['low'] * median_saturation:
        logger.warning(f'Saturation: {saturation} - low saturation!')
        return True
    else:
        logger.info(f'Saturation: {saturation}')
        return False
