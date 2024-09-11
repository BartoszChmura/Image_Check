import os
import shutil

from detection.brightness_detection import calculate_median_brightness, detect_brightness
from detection.flare_detection import detect_flare
from detection.saturation_detection import calculate_median_saturation, detect_saturation
from detection.sharpness_detection import calculate_median_sharpness_laplacian, detect_sharpness
from model.model import detect_and_crop_person, load_model

import xml.etree.ElementTree as ET



def process_folder(image_folder, crop_folder, progress_callback):
    thresholds = load_thresholds_from_xml('./config/config.xml')

    # Calculating medians and initializing
    median_laplacian = calculate_median_sharpness_laplacian(crop_folder)
    median_saturation = calculate_median_saturation(image_folder)
    median_brightness = calculate_median_brightness(image_folder)

    print(f'Median sharpness of silhouette images in the folder: {median_laplacian}')
    print(f'Median saturation of images in the folder: {median_saturation}')
    print(f'Median brightness of images in the folder: {median_brightness}')

    detected_issues = {}
    image_files = os.listdir(image_folder)

    for image_name in image_files:
        image_path = os.path.join(image_folder, image_name)
        print(f'Image processing: {image_name}')

        move_to_check_folder = False
        issues = []

        if detect_flare(image_path, thresholds):
            move_to_check_folder = True
            issues.append('light flare')

        if detect_saturation(image_path, median_saturation, thresholds):
            move_to_check_folder = True
            issues.append('low saturation')

        if detect_brightness(image_path, median_brightness, thresholds):
            move_to_check_folder = True
            issues.append('low brightness')

        base_name, ext = os.path.splitext(image_name)
        cropped_image_name = f"{base_name}_person{ext}"
        cropped_image_path = os.path.join(crop_folder, cropped_image_name)

        if os.path.exists(cropped_image_path):
            sharpness_issue = detect_sharpness(cropped_image_path, median_laplacian, thresholds)
            if sharpness_issue:
                move_to_check_folder = True
                issues.append(sharpness_issue)
        else:
            print("Silhouette not found")
            move_to_check_folder = True
            issues.append('silhouette not found')

        detected_issues[image_name] = issues

        if move_to_check_folder:
            destination_folder = './images/to_check'
            destination_path = os.path.join(destination_folder, image_name)
            shutil.move(image_path, destination_path)
            print(f'Image moved to folder: {destination_folder}')
        else:
            destination_folder = './images/checked'
            destination_path = os.path.join(destination_folder, image_name)
            shutil.move(image_path, destination_path)
            print('Image is good')

        # Update progress after processing each image
        progress_callback()

    return detected_issues



def crop_images(image_folder, crop_folder, progress_callback):
    model_path = 'model/second.pt'
    model = load_model(model_path)

    if not os.path.exists(crop_folder):
        os.makedirs(crop_folder)

    image_files = os.listdir(image_folder)

    for image_name in image_files:
        image_path = os.path.join(image_folder, image_name)
        detect_and_crop_person(image_path, model, crop_folder)

        # Update progress after cropping each image
        progress_callback()


def load_thresholds_from_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    sharpness_low_threshold = float(root.find('sharpness/low_threshold').text)
    sharpness_high_threshold = float(root.find('sharpness/high_threshold').text)
    saturation_low_threshold = float(root.find('saturation/low_threshold').text)
    brightness_low_threshold = float(root.find('brightness/low_threshold').text)
    brightness_high_threshold = float(root.find('brightness/high_threshold').text)
    flare_threshold = float(root.find('flare/threshold').text)

    thresholds = {
        'sharpness': {
            'low': sharpness_low_threshold,
            'high': sharpness_high_threshold
        },
        'saturation': {
            'low': saturation_low_threshold
        },
        'brightness': {
            'low': brightness_low_threshold,
            'high': brightness_high_threshold
        },
        'flare': {
            'threshold': flare_threshold
        }
    }

    return thresholds