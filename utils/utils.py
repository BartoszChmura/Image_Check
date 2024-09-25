import os
import shutil

import xml.etree.ElementTree as ET

import cv2

from detection.brightness_detection import calculate_median_brightness, detect_brightness
from detection.flare_detection import detect_flare
from detection.saturation_detection import calculate_median_saturation, detect_saturation
from detection.sharpness_detection import calculate_median_sharpness_laplacian, detect_sharpness
from model.model import detect_and_crop_person, load_model
from config.log_config import logger
from utils.helpers import get_image_files, resource_path


def process_folder(image_folder, crop_folder, progress_callback):
    try:
        thresholds = load_thresholds_from_xml(resource_path('./config/config.xml'))
    except Exception as e:
        raise Exception(f"Failed to load thresholds from config file: {e} - utils.py")

    try:
        median_laplacian = calculate_median_sharpness_laplacian(crop_folder)
        progress_callback(1, "median")
        median_saturation = calculate_median_saturation(image_folder)
        progress_callback(1, "median")
        median_brightness = calculate_median_brightness(image_folder)
        progress_callback(1, "median")

        if median_laplacian is None or median_saturation is None or median_brightness is None:
            raise Exception("Failed to calculate one or more medians. - utils.py")

    except Exception as e:
        raise Exception(f"Failed to calculate medians: {e} - utils.py")

    logger.info(f'Median sharpness of silhouette images in the folder: {median_laplacian}')
    logger.info(f'Median saturation of images in the folder: {median_saturation}')
    logger.info(f'Median brightness of images in the folder: {median_brightness}')

    detected_issues = {}

    image_files = get_image_files(image_folder)
    if image_files is None:
        raise Exception(f"Failed to list files in image folder: {image_folder} - utils.py")

    for image_name in image_files:
        image_path = os.path.join(image_folder, image_name)
        logger.info(f'Image processing: {image_name}')

        move_to_check_folder = False
        issues = []

        try:
            detected_flare = detect_flare(image_path, thresholds)
            if detected_flare is None:
                logger.warning("Skipping image due to flare detection error. - utils.py")
                continue
            elif detected_flare:
                move_to_check_folder = True
                issues.append('light flare')

            detected_saturation = detect_saturation(image_path, median_saturation, thresholds)
            if detected_saturation is None:
                logger.warning("Skipping image due to saturation detection error. - utils.py")
                continue
            elif detected_saturation:
                move_to_check_folder = True
                issues.append('low saturation')

            detected_brightness = detect_brightness(image_path, median_brightness, thresholds)
            if detected_brightness is None:
                logger.warning("Skipping image due to brightness detection error. - utils.py")
                continue
            elif detected_brightness:
                move_to_check_folder = True
                issues.append('low brightness')

        except Exception as e:
            raise Exception(f"Error during detections: {e} - utils.py")

        base_name, ext = os.path.splitext(image_name)
        cropped_image_name = f"{base_name}_person{ext}"
        cropped_image_path = os.path.join(crop_folder, cropped_image_name)

        if os.path.exists(cropped_image_path):
            try:
                sharpness_issue = detect_sharpness(cropped_image_path, median_laplacian, thresholds)
                if sharpness_issue is None:
                    logger.warning("Skipping image due to sharpness detection error. - utils.py")
                    continue
                elif sharpness_issue:
                    move_to_check_folder = True
                    issues.append(sharpness_issue)
            except Exception as e:
                raise Exception(f"Failed to detect sharpness: {e} - utils.py")

        else:
            logger.warning("Silhouette not found")
            move_to_check_folder = True
            issues.append('silhouette not found')

        detected_issues[image_name] = issues

        destination_folder = resource_path('./images/to_check') if move_to_check_folder else resource_path(
            './images/checked')

        destination_path = os.path.join(destination_folder, image_name)
        try:
            shutil.move(image_path, destination_path)
            logger.info(f'Image moved to folder: {destination_folder}')
        except (OSError, IOError) as e:
            raise Exception(f"Failed to move image {image_name}: {e} - utils.py")

        progress_callback(1, "process")

    return detected_issues


def crop_images(image_folder, crop_folder, progress_callback):
    model_path = resource_path('./model/nowy_m.pt')
    model = load_model(model_path)

    image_files = get_image_files(image_folder)
    if image_files is None:
        raise Exception(f"Failed to list files in image folder: {image_folder} - utils.py")

    for image_name in image_files:
        image_path = os.path.join(image_folder, image_name)
        try:
            detect_and_crop_person(image_path, model, crop_folder)
        except Exception as e:
            raise Exception(f"Failed to crop person from image {image_name}: {e} - utils.py")

        progress_callback(1, "crop")


def load_thresholds_from_xml(file_path):
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
    except (ET.ParseError, FileNotFoundError, IOError) as e:
        raise Exception(f"Error loading or parsing XML file: {e} - utils.py")

    try:
        sharpness_low_threshold = float(root.find('sharpness/low_threshold').text)
        sharpness_high_threshold = float(root.find('sharpness/high_threshold').text)
        saturation_low_threshold = float(root.find('saturation/low_threshold').text)
        brightness_low_threshold = float(root.find('brightness/low_threshold').text)
        brightness_high_threshold = float(root.find('brightness/high_threshold').text)
        flare_threshold = float(root.find('flare/threshold').text)
    except (AttributeError, ValueError) as e:
        raise Exception(f"Error reading thresholds from config file: {e} - utils.py")

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

def load_styles():
    qss_path = resource_path('./qss/styles.qss')
    try:
        if os.path.exists(qss_path):
            with open(qss_path, 'r') as file:
                return file.read()
        else:
            logger.warning(f"Stylesheet file not found at: {qss_path}")
    except Exception as e:
        logger.error(f"Failed to load stylesheet: {e}")
        raise Exception(f"Failed to load stylesheet: {e} - utils.py")
    return ""

