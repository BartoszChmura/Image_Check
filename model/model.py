import os
import cv2

from config.log_config import logger
from ultralytics import YOLO

from utils.helpers import read_image, resource_path


def load_model(model_path):
    try:
        return YOLO(resource_path(model_path))
    except Exception as e:
        raise Exception(f"Failed to load model from {model_path}: {e} - model.py")


def process_image(model, image_path):
    try:
        results = model(image_path, conf=0.5)
        return results
    except Exception as e:
        raise Exception(f"Failed to process image {image_path}: {e} - model.py")


def crop_and_save_image(image, box, save_path):
    try:
        x1, y1, x2, y2 = box
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
        cropped_image = image[y1:y2, x1:x2]
        cv2.imwrite(save_path, cropped_image)
    except Exception as e:
        raise Exception(f"Failed to crop and save image to {save_path}: {e} - model.py")


def save_full_image(image, save_path):
    try:
        cv2.imwrite(save_path, image)
    except Exception as e:
        raise Exception(f"Failed to save full image to {save_path}: {e} - model.py")


def detect_and_crop_person(image_path, model, crop_folder):
    found_person = False
    image = read_image(image_path)
    if image is None:
        raise Exception(f"Failed to read image from {image_path} - model.py")

    results = process_image(model, image_path)

    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()

            base_name, ext = os.path.splitext(os.path.basename(image_path))
            save_name = f"{base_name}_person{ext}"
            save_path = os.path.join(crop_folder, save_name)

            try:
                crop_and_save_image(image, (x1, y1, x2, y2), save_path)
                found_person = True
            except Exception as e:
                logger.error(f"Error cropping and saving image: {e} - model.py")
                continue

    if not found_person:
        base_name, ext = os.path.splitext(os.path.basename(image_path))
        save_name = f"{base_name}_no_detection{ext}"
        save_path = os.path.join(crop_folder, save_name)
        save_full_image(image, save_path)

    return found_person
