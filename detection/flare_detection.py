import cv2

from config.log_config import logger
from utils.helpers import read_image, resource_path


def calculate_brightness_histogram(image_path):
    image = read_image(resource_path(image_path))
    if image is None:
        raise Exception(f"Failed to read image from {image_path} - flare detection")

    histogram = cv2.calcHist([image], [0], None, [256], [0, 256])
    return histogram


def check_bright_glow(image_path, threshold):
    histogram = calculate_brightness_histogram(image_path)

    if histogram is None:
        logger.warning(f"Skipping brightness histogram detection for {image_path} due to empty histogram error - flare detection")
        return None

    total_pixels = sum(histogram)
    low_brightness_pixels = sum(histogram[:25])
    low_brightness_ratio = low_brightness_pixels / total_pixels

    if low_brightness_ratio < threshold:
        return True
    else:
        return False


def detect_flare(image_path, thresholds):
    bright_glow_result = check_bright_glow(resource_path(image_path), thresholds['flare']['threshold'])

    if bright_glow_result is None:
        logger.warning(f"Cannot detect flare for {image_path} due to previous errors - flare detection")
        return None
    elif bright_glow_result:
        logger.warning(f'Image has light flare')
        return True
    else:
        logger.info("Image doesn't have light flare")
        return False