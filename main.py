from ultralytics import YOLO
from flare_detection import *
from sharpness_detection import *
from saturation_detection import *
from brightness_detection import *
from size_detection import *
from model import *
import os


def detect_flare(image_folder):
    for image_name in os.listdir(image_folder):
        image_path = os.path.join(image_folder, image_name)
        if check_bright_glow(image_path):
            print(f'Zdjecie [{image_name}] ma jasną poświatę')
        else:
            print(f'Zdjecie [{image_name}] nie ma jasnej poświaty')


def crop_images(image_folder):
    model_path = 'drugi.pt'
    result = detect_and_crop_shirts(image_folder, model_path)


def detect_sharpness(image_folder):
    median_laplacian = calculate_median_sharpness_laplacian(image_folder)
    #median_sobel = calculate_median_sharpness_sobel(image_folder)
    #median_fft = calculate_median_sharpness_fft(image_folder)
    #median_canny = calculate_median_sharpness_canny(image_folder)
    print(f'Mediana ostrości dla całego folderu: {median_laplacian}')
    #print(f'Mediana ostrości dla całego folderu (Sobel): {median_sobel}')
    #print(f'Mediana ostrości dla całego folderu (FFT): {median_fft}')
    #print(f'Mediana ostrości dla całego folderu (Canny): {median_canny}')
    for image_name in os.listdir(image_folder):
        image_path = os.path.join(image_folder, image_name)
        sharpness_laplacian = calculate_image_sharpness_laplacian(image_path)
        #sharpness_fft = calculate_image_sharpness_fft(image_path)
        #sharpness_sobel = calculate_image_sharpness_sobel(image_path)
        #sharpness_canny = calculate_image_sharpness_canny(image_path)
        if sharpness_laplacian < 0.35 * median_laplacian:
            print(f'Ostrość dla zdjęcia (Laplacian) [{image_name}]: {sharpness_laplacian} - niska ostrość!')
        else:
            print(f'Ostrość dla zdjęcia (Laplacian) [{image_name}]: {sharpness_laplacian}')
        #print(f'Ostrość dla zdjęcia (Canny) [{image_name}]: {sharpness_canny}')
        #print(f'Ostrość dla zdjęcia (Sobel) [{image_name}]: {sharpness_sobel}')
        #print(f'Ostrość dla zdjęcia (FFT) [{image_name}]: {sharpness_fft}')

def detect_saturation(image_folder):
    median = calculate_median_saturation(image_folder)
    print(f'Mediana nasycenia dla całego folderu: {median}')
    for image_name in os.listdir(image_folder):
        image_path = os.path.join(image_folder, image_name)
        saturation = calculate_saturation(image_path)
        if saturation < 0.5 * median:
            print(f'Nasycenie dla zdjęcia [{image_name}]: {saturation} - niskie nasycenie!')
        else:
            print(f'Nasycenie dla zdjęcia [{image_name}]: {saturation}')

def detect_brightness(image_folder):
    median = calculate_median_brightness(image_folder)
    print(f'Mediana jasności dla całego folderu: {median}')
    for image_name in os.listdir(image_folder):
        image_path = os.path.join(image_folder, image_name)
        brightness = calculate_brightness(image_path)
        print(f'Jasność dla zdjęcia [{image_name}]: {brightness}')

def test_model(image_folder):
    model = load_model('drugi.pt')
    for image_name in os.listdir(image_folder):
        image_path = os.path.join(image_folder, image_name)
        process_image(model, image_path)



if __name__ == "__main__":
    detect_sharpness('wycinki')

