from detection.flare_detection import *
from detection.sharpness_detection import *
from detection.saturation_detection import *
from detection.brightness_detection import *
from view.interface import *
from model.model import *
import xml.etree.ElementTree as ET
import os

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

def crop_images(image_folder, crop_folder):
    model_path = 'model/drugi.pt'
    result = detect_and_crop_persons(image_folder, model_path, crop_folder)

def crop_image(image_path, crop_folder):
    model_path = 'model/drugi.pt'
    result = detect_and_crop_person(image_path, model_path, crop_folder)


def detect_flare(image_path, thresholds):
    if check_bright_glow(image_path, thresholds['flare']['threshold']):
        print(f'Zdjęcie ma jasną poświatę')
        return True
    else:
        print(f'Zdjęcie nie ma jasnej poświaty')
        return False


def detect_sharpness(image_path, median_laplacian, thresholds):
    sharpness_laplacian = calculate_image_sharpness_laplacian(image_path)

    if sharpness_laplacian < thresholds['sharpness']['low'] * median_laplacian:
        print(f'Ostrość: {sharpness_laplacian} - niska ostrość!')
        return 'niska ostrość'
    elif sharpness_laplacian > thresholds['sharpness']['high'] * median_laplacian:
        print(f'Ostrość: {sharpness_laplacian} - możliwe zaszumienie!')
        return 'możliwe zaszumienie'
    else:
        print(f'Ostrość: {sharpness_laplacian}')
        return None


def detect_saturation(image_path, median_saturation, thresholds):
    saturation = calculate_saturation(image_path)

    if saturation < thresholds['saturation']['low'] * median_saturation:
        print(f'Nasycenie: {saturation} - niskie nasycenie!')
        return True
    else:
        print(f'Nasycenie: {saturation}')
        return False


def detect_brightness(image_path, median_brightness, thresholds):
    brightness = calculate_brightness(image_path)

    if brightness < thresholds['brightness']['low'] * median_brightness:
        print(f'Jasność: {brightness} - niska jasność!')
        return True
    elif brightness > thresholds['brightness']['high'] * median_brightness:
        print(f'Jasność: {brightness} - możliwe przejaśnienie')
        return True
    else:
        print(f'Jasność: {brightness}')
        return False

def test_model(image_folder):
    model = load_model('model/drugi.pt')

    for image_name in os.listdir(image_folder):
        image_path = os.path.join(image_folder, image_name)
        process_image(model, image_path)


def detect_sharpness_in_folder(image_folder, median_laplacian):
    print(f'Mediana ostrości zdjęć w folderze: {median_laplacian}')

    for image_name in os.listdir(image_folder):
        image_path = os.path.join(image_folder, image_name)
        print(f'Przetwarzanie zdjęcia: {image_name}')
        detect_sharpness(image_path, median_laplacian)


def process_folder(image_folder, crop_folder):
    thresholds = load_thresholds_from_xml('./config/config.xml')

    median_laplacian = calculate_median_sharpness_laplacian(crop_folder)
    median_saturation = calculate_median_saturation(image_folder)
    median_brightness = calculate_median_brightness(image_folder)

    print(f'Mediana ostrości zdjęć sylwetek w folderze: {median_laplacian}')
    print(f'Mediana nasycenia zdjęć w folderze: {median_saturation}')
    print(f'Mediana jasności zdjęć w folderze: {median_brightness}')

    detected_issues = {}

    for image_name in os.listdir(image_folder):
        image_path = os.path.join(image_folder, image_name)
        print(f'Przetwarzanie zdjęcia: {image_name}')

        move_to_check_folder = False
        issues = []

        if detect_flare(image_path, thresholds):
            move_to_check_folder = True
            issues.append('jasna poświata')

        if detect_saturation(image_path, median_saturation, thresholds):
            move_to_check_folder = True
            issues.append('niskie nasycenie')

        if detect_brightness(image_path, median_brightness, thresholds):
            move_to_check_folder = True
            issues.append('niska jasność')

        base_name, ext = os.path.splitext(image_name)
        cropped_image_name = f"{base_name}_person{ext}"
        cropped_image_path = os.path.join(crop_folder, cropped_image_name)

        if os.path.exists(cropped_image_path):
            sharpness_issue = detect_sharpness(cropped_image_path, median_laplacian, thresholds)
            if sharpness_issue:
                move_to_check_folder = True
                issues.append(sharpness_issue)
        else:
            print("Sylwetka nie znaleziona")
            move_to_check_folder = True
            issues.append('sylwetka nie znaleziona')

        detected_issues[image_name] = issues

        if move_to_check_folder:
            destination_folder = './zdjecia/do_sprawdzenia'
            destination_path = os.path.join(destination_folder, image_name)
            shutil.move(image_path, destination_path)
            print(f'Zdjęcie przeniesione do folderu {destination_folder}')
        else:
            destination_folder = './zdjecia/sprawdzone'
            destination_path = os.path.join(destination_folder, image_name)
            shutil.move(image_path, destination_path)
            print('Zdjęcie jest dobre')

    return detected_issues



def init_interface(detected_issues):
    import sys
    app = QApplication(sys.argv)
    viewer = ImageViewer(detected_issues)
    viewer.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    crop_images('./zdjecia/nowe', './zdjecia/sylwetki')
    detected_issues = process_folder('./zdjecia/nowe', './zdjecia/sylwetki')
    init_interface(detected_issues)