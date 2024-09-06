import cv2


def calculate_brightness_histogram(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    histogram = cv2.calcHist([img], [0], None, [256], [0, 256])
    return histogram


def check_bright_glow(image_path, threshold):
    histogram = calculate_brightness_histogram(image_path)
    total_pixels = sum(histogram)
    low_brightness_pixels = sum(histogram[:25])
    low_brightness_ratio = low_brightness_pixels / total_pixels

    if low_brightness_ratio < threshold:
        return True
    else:
        return False

def detect_flare(image_path, thresholds):
    if check_bright_glow(image_path, thresholds['flare']['threshold']):
        print(f'Zdjęcie ma jasną poświatę')
        return True
    else:
        print(f'Zdjęcie nie ma jasnej poświaty')
        return False