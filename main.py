from detection.flare_detection import *
from detection.sharpness_detection import *
from detection.saturation_detection import *
from detection.brightness_detection import *
from detection.size_detection import *
from view.interface import *
from model.model import *
import os


def crop_images(image_folder, crop_folder):
    model_path = 'model/drugi.pt'
    result = detect_and_crop_persons(image_folder, model_path, crop_folder)

def crop_image(image_path, crop_folder):
    model_path = 'model/drugi.pt'
    result = detect_and_crop_person(image_path, model_path, crop_folder)


def detect_flare(image_path):
    if check_bright_glow(image_path):
        print(f'Zdjecie ma jasną poświatę')
        return True
    else:
        print(f'Zdjecie nie ma jasnej poświaty')
        return False


def detect_sharpness(image_path, median_laplacian):
    sharpness_laplacian = calculate_image_sharpness_laplacian(image_path)

    if sharpness_laplacian < 0.35 * median_laplacian:
        print(f'Ostrość: {sharpness_laplacian} - niska ostrość!')
        return True
    elif sharpness_laplacian > 4 * median_laplacian:
        print(f'Ostrość: {sharpness_laplacian} - możliwe zaszumienie!')
        return True
    else:
        print(f'Ostrość: {sharpness_laplacian}')
        return False


def detect_saturation(image_path, median_saturation):
    saturation = calculate_saturation(image_path)

    if saturation < 0.5 * median_saturation:
        print(f'Nasycenie: {saturation} - niskie nasycenie!')
        return True
    else:
        print(f'Nasycenie: {saturation}')
        return False


def detect_brightness(image_path, median_brightness):
    brightness = calculate_brightness(image_path)

    print(f'Jasność: {brightness}')


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
    median_laplacian = calculate_median_sharpness_laplacian(crop_folder)
    median_saturation = calculate_median_saturation(image_folder)
    median_brightness = calculate_median_brightness(image_folder)
    print(f'Mediana ostrości zdjęć sylwetek w folderze: {median_laplacian}')
    print(f'Mediana nasycenia zdjęć w folderze: {median_saturation}')
    print(f'Mediana jasności zdjęć w folderze: {median_brightness}')

    for image_name in os.listdir(image_folder):
        image_path = os.path.join(image_folder, image_name)
        print(f'Przetwarzanie zdjęcia: {image_name}')

        move_to_check_folder = False

        if detect_flare(image_path):
            move_to_check_folder = True
        if detect_saturation(image_path, median_saturation):
            move_to_check_folder = True
        if detect_brightness(image_path, median_brightness):
            move_to_check_folder = True

        base_name, ext = os.path.splitext(image_name)
        cropped_image_name = f"{base_name}_person{ext}"
        cropped_image_path = os.path.join(crop_folder, cropped_image_name)

        if os.path.exists(cropped_image_path):
            if detect_sharpness(cropped_image_path, median_laplacian):
                move_to_check_folder = True
        else:
            print("Sylwetka nie znaleziona")
            move_to_check_folder = True

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



def init_interface():
    root = tk.Tk()
    app = ImageViewer(root)
    root.mainloop()



if __name__ == "__main__":
    init_interface()

