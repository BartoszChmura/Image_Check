import cv2


def get_image_size(image_path):
    image = cv2.imread(image_path)

    height, width = image.shape[:2]

    total_pixels = width * height

    return total_pixels