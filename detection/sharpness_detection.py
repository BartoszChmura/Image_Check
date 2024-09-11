import cv2
import os

import numpy as np

from detection.size_detection import get_image_size
from config.log_config import logger
from utils.helpers import get_image_files, read_image


def calculate_image_sharpness_laplacian(image_path):
    image = read_image(image_path)
    if image is None:
        raise Exception(f"Failed to read image from {image_path}")

    laplacian = cv2.Laplacian(image, cv2.CV_64F)

    variance = laplacian.var()

    image_size = get_image_size(image_path)
    if image_size == 0 or image_size is None:
        logger.warning(f"Image size for {image_path} is zero, cannot compute sharpness.")
        return None

    normalized_variance = variance / (image_size) * 1000000

    return normalized_variance





def calculate_median_sharpness_laplacian(image_dir):
    sharpness_values = []

    images = get_image_files(image_dir)
    if images is None:
        return None

    for image in images:
        image_path = os.path.join(image_dir, image)
        sharpness = calculate_image_sharpness_laplacian(image_path)
        if sharpness is not None:
            sharpness_values.append(sharpness)

    if not sharpness_values:
        logger.warning(f"No valid images found in directory {image_dir} - sharpness detection")
        return None

    median_sharpness = np.median(sharpness_values)
    return median_sharpness

def detect_sharpness(image_path, median_laplacian, thresholds):
    sharpness_laplacian = calculate_image_sharpness_laplacian(image_path)

    if sharpness_laplacian is None:
        logger.warning(f"Cannot detect sharpness for {image_path} due to previous errors - sharpness detection")
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
