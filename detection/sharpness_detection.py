import cv2
import os

import numpy as np

from detection.size_detection import get_image_size
from config.log_config import logger


def calculate_image_sharpness_laplacian(image_path):
    try:
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            raise ValueError(f"Failed to read image from {image_path}")

        laplacian = cv2.Laplacian(image, cv2.CV_64F)

        variance = laplacian.var()

        image_size = get_image_size(image_path)
        if image_size == 0 or image_size is None:
            logger.warning(f"Image size for {image_path} is zero, cannot compute sharpness.")
            return None

        normalized_variance = variance / (image_size) * 1000000

        return normalized_variance

    except Exception as e:
        logger.error(f"Error calculating sharpness for {image_path}: {e}")
        return None



def calculate_median_sharpness_laplacian(image_dir):
    sharpness_values = []
    try:
        images = os.listdir(image_dir)
    except OSError as e:
        logger.error(f"Error reading directory {image_dir}: {e}")
        return None

    for image in images:
        image_path = os.path.join(image_dir, image)
        sharpness = calculate_image_sharpness_laplacian(image_path)
        if sharpness is not None:
            sharpness_values.append(sharpness)

    if not sharpness_values:
        logger.warning(f"No valid images found in directory {image_dir}.")
        return None

    median_sharpness = np.median(sharpness_values)
    return median_sharpness

def detect_sharpness(image_path, median_laplacian, thresholds):
    sharpness_laplacian = calculate_image_sharpness_laplacian(image_path)

    if sharpness_laplacian is None:
        logger.warning(f"Cannot detect sharpness for {image_path} due to previous errors.")
        return None

    low_threshold = thresholds['sharpness']['low']
    high_threshold = thresholds['sharpness']['high']

    if sharpness_laplacian < low_threshold * median_laplacian:
        logger.warning(f'Sharpness: {sharpness_laplacian} - low sharpness!')
        return 'low sharpness'
    elif sharpness_laplacian > high_threshold * median_laplacian:
        logger.warning(f'Sharpness: {sharpness_laplacian} - possible noise!')
        return 'noise'
    else:
        logger.info(f'Sharpness: {sharpness_laplacian}')
        return False
