from ultralytics import YOLO
import os
import cv2

def load_model(model_path):
    return YOLO(model_path)

def process_image(model, image_path):
    results = model(image_path, conf = 0.5)
    return results


def crop_and_save(image, box, save_path):
    x1, y1, x2, y2 = box
    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
    cropped_image = image[y1:y2, x1:x2]
    cv2.imwrite(save_path, cropped_image)

def save_full_image(image, save_path):
    cv2.imwrite(save_path, image)

def detect_and_crop_shirts(image_folder, model_path, save_folder='./wycinki'):

    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    model = load_model(model_path)

    for image_name in os.listdir(image_folder):
        found_person = False
        image_path = os.path.join(image_folder, image_name)
        image = cv2.imread(image_path)

        results = process_image(model, image_path)

        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()

                base_name, ext = os.path.splitext(image_name)
                save_name = f"{base_name}_person{ext}"
                save_path = os.path.join(save_folder, save_name)

                crop_and_save(image, (x1, y1, x2, y2), save_path)

                found_person = True

        if not found_person:
            base_name, ext = os.path.splitext(image_name)
            save_name = f"{base_name}_no_detection{ext}"
            save_path = os.path.join(save_folder, save_name)

            save_full_image(image, save_path)

    return found_person
