import os

import cv2

from config.log_config import logger


#Helper functions


def get_image_files(image_dir):
    try:
        images = os.listdir(image_dir)
        return images
    except OSError as e:
        logger.error(f"Error reading directory {image_dir}: {e} - helpers.py")
        return None

def read_image(image_path):
    try:
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Failed to read image from {image_path} - helpers.py")
        return img
    except Exception as e:
        logger.error(f"Error reading image from {image_path}: {e} - helpers.py")
        return None