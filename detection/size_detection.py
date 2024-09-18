import cv2

from config.log_config import logger
from utils.helpers import read_image, resource_path


def get_image_size(image_path):
    image = read_image(resource_path(image_path))
    if image is None:
        raise Exception(f"Failed to read image from {image_path} - size detection")

    height, width = image.shape[:2]

    total_pixels = width * height

    return total_pixels



