import cv2

from config.log_config import logger

def calculate_brightness_histogram(image_path):
    try:
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise ValueError(f"Failed to read image from {image_path}")

        histogram = cv2.calcHist([img], [0], None, [256], [0, 256])
        return histogram
    except Exception as e:
        logger.error(f"Error calculating brightness histogram for {image_path}: {e}")
        return None


def check_bright_glow(image_path, threshold):
    histogram = calculate_brightness_histogram(image_path)

    if histogram is None:
        logger.warning(f"Skipping brightness histogram detection for {image_path} due to read error.")
        return None

    total_pixels = sum(histogram)
    low_brightness_pixels = sum(histogram[:25])
    low_brightness_ratio = low_brightness_pixels / total_pixels

    if low_brightness_ratio < threshold:
        return True
    else:
        return False


def detect_flare(image_path, thresholds):
    bright_glow_result = check_bright_glow(image_path, thresholds['flare']['threshold'])

    if bright_glow_result is None:
        logger.warning(f"Cannot detect flare for {image_path} due to previous errors.")
        return None
    elif bright_glow_result:
        logger.warning(f'Image has light flare')
        return True
    else:
        logger.info("Image doesn't have light flare")
        return False