from ultralytics import YOLO
from flare_detection import *
from sharpness_detection import *
from saturation_detection import *
from brightness_detection import *
from size_detection import *
from model import *
import os


def crop_images(image_folder):
    model_path = 'drugi.pt'
    result = detect_and_crop_persons(image_folder, model_path)


def detect_flare(image_path):
    if check_bright_glow(image_path):
        print(f'Zdjecie ma jasną poświatę')
    else:
        print(f'Zdjecie nie ma jasnej poświaty')


def detect_sharpness(image_path, median_laplacian):
    sharpness_laplacian = calculate_image_sharpness_laplacian(image_path)
    if sharpness_laplacian < 0.35 * median_laplacian:
        print(f'Ostrość: {sharpness_laplacian} - niska ostrość!')
    else:
        print(f'Ostrość: {sharpness_laplacian}')


def detect_saturation(image_path, median_saturation):
    saturation = calculate_saturation(image_path)
    if saturation < 0.5 * median_saturation:
        print(f'Nasycenie: {saturation} - niskie nasycenie!')
    else:
        print(f'Nasycenie: {saturation}')


def detect_brightness(image_path, median_brightness):
    brightness = calculate_brightness(image_path)
    print(f'Jasność: {brightness}')


def test_model(image_folder):
    model = load_model('drugi.pt')
    for image_name in os.listdir(image_folder):
        image_path = os.path.join(image_folder, image_name)
        process_image(model, image_path)


def detect_sharpness_in_folder(image_folder, median_laplacian):
    print(f'Mediana ostrości zdjęć w folderze: {median_laplacian}')
    for image_name in os.listdir(image_folder):
        image_path = os.path.join(image_folder, image_name)
        print(f'Przetwarzanie zdjęcia: {image_name}')
        detect_sharpness(image_path, median_laplacian)


def process_folder(image_folder):
    median_laplacian = calculate_median_sharpness_laplacian(image_folder)
    median_saturation = calculate_median_saturation(image_folder)
    median_brightness = calculate_median_brightness(image_folder)
    print(f'Mediana ostrości zdjęć w folderze: {median_laplacian}')
    print(f'Mediana nasycenia zdjęć w folderze: {median_saturation}')
    print(f'Mediana jasności zdjęć w folderze: {median_brightness}')

    for image_name in os.listdir(image_folder):
        image_path = os.path.join(image_folder, image_name)
        print(f'Przetwarzanie zdjęcia: {image_name}')
        detect_flare(image_path)
        detect_sharpness(image_path, median_laplacian)
        detect_saturation(image_path, median_saturation)
        detect_brightness(image_path, median_brightness)


if __name__ == "__main__":
    median_sharpness = calculate_median_sharpness_laplacian('./wycinki')
    detect_sharpness_in_folder('./wycinki', median_sharpness)