import os
import cv2

from config.log_config import logger
from ultralytics import YOLO

def load_model(model_path):
    try:
        return YOLO(model_path)
    except Exception as e:
        raise Exception(f"Failed to load model from {model_path}: {e}")

def process_image(model, image_path):
    try:
        results = model(image_path, conf=0.5)
        return results
    except Exception as e:
        raise Exception(f"Failed to process image {image_path}: {e}")

def crop_and_save_image(image, box, save_path):
    try:
        x1, y1, x2, y2 = box
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
        cropped_image = image[y1:y2, x1:x2]
        cv2.imwrite(save_path, cropped_image)
    except Exception as e:
        raise Exception(f"Failed to crop and save image to {save_path}: {e}")

def save_full_image(image, save_path):
    try:
        cv2.imwrite(save_path, image)
    except Exception as e:
        raise Exception(f"Failed to save full image to {save_path}: {e}")

def detect_and_crop_person(image_path, model, crop_folder):
    found_person = False
    try:
        image = cv2.imread(image_path)
        if image is None:
            logger.error(f"Failed to read image from {image_path}")
            raise ValueError(f"Failed to read image from {image_path}")

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
                    logger.error(f"Error cropping and saving image: {e}")
                    continue

        if not found_person:
            base_name, ext = os.path.splitext(os.path.basename(image_path))
            save_name = f"{base_name}_no_detection{ext}"
            save_path = os.path.join(crop_folder, save_name)
            save_full_image(image, save_path)

    except Exception as e:
        logger.error(f"Error processing {image_path}: {e}")

    return found_person


def test_model(image_folder):
    model = load_model('model/second.pt')

    for image_name in os.listdir(image_folder):
        image_path = os.path.join(image_folder, image_name)
        try:
            process_image(model, image_path)
        except Exception as e:
            logger.error(e)