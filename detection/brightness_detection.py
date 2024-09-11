import cv2
import os
import numpy as np

from config.log_config import logger

def calculate_brightness(image_path):
    try:
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Failed to read image from {image_path}")

        hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        brightness = hsv_img[:, :, 2].mean()
        return brightness
    except Exception as e:
        logger.error(f"Error calculating brightness for {image_path}: {e}")
        return None

def calculate_median_brightness(image_dir):
    brightness_values = []
    try:
        images = os.listdir(image_dir)
    except OSError as e:
        logger.error(f"Error reading directory {image_dir}: {e}")
        return None

    for image in images:
        image_path = os.path.join(image_dir, image)
        brightness = calculate_brightness(image_path)
        if brightness is not None:
            brightness_values.append(brightness)

    if not brightness_values:
        logger.warning(f"No valid images found in directory {image_dir}.")
        return None

    median_brightness = np.median(brightness_values)
    return median_brightness

def detect_brightness(image_path, median_brightness, thresholds):
    brightness = calculate_brightness(image_path)

    if brightness is None:
        logger.warning(f"Skipping brightness detection for {image_path} due to read error.")
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
