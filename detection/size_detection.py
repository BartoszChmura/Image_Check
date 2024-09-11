import cv2

from config.log_config import logger

def get_image_size(image_path):
    try:
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Failed to read image from {image_path}")

        height, width = image.shape[:2]

        total_pixels = width * height

        return total_pixels

    except Exception as e:
        logger.error(f"Error getting image size for {image_path}: {e}")
        return None

