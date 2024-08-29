import cv2
import os
import numpy as np

from size_detection import get_image_size


def calculate_image_sharpness_laplacian(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    laplacian = cv2.Laplacian(image, cv2.CV_64F)

    variance = laplacian.var()

    image_size = get_image_size(image_path)

    normalized_variance = variance / (image_size) * 1000000

    return normalized_variance


def calculate_image_sharpness_sobel(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)

    sobel_magnitude = np.sqrt(sobel_x ** 2 + sobel_y ** 2)
    sobel_var = sobel_magnitude.var()

    image_size = get_image_size(image_path)
    normalized_sobel_var = sobel_var / image_size * 1000000

    return normalized_sobel_var


def calculate_image_sharpness_fft(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    f = np.fft.fft2(gray)
    fshift = np.fft.fftshift(f)
    magnitude_spectrum = 20 * np.log(np.abs(fshift) + 1e-7)

    mean_freq = np.mean(magnitude_spectrum)

    return mean_freq


def calculate_image_sharpness_canny(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    edges = cv2.Canny(image, 100, 200)
    edge_density = np.sum(edges) / image.size

    return edge_density * 1000


def calculate_median_sharpness_sobel(image_dir):
    sharpness_values = []
    images = os.listdir(image_dir)

    for image in images:
        image_path = os.path.join(image_dir, image)
        sharpness = calculate_image_sharpness_sobel(image_path)
        sharpness_values.append(sharpness)

    median_sharpness = np.median(sharpness_values)
    return median_sharpness


def calculate_median_sharpness_laplacian(image_dir):
    sharpness_values = []
    images = os.listdir(image_dir)

    for image in images:
        image_path = os.path.join(image_dir, image)
        sharpness = calculate_image_sharpness_laplacian(image_path)
        sharpness_values.append(sharpness)

    median_sharpness = np.median(sharpness_values)
    return median_sharpness


def calculate_median_sharpness_fft(image_dir):
    sharpness_values = []
    images = os.listdir(image_dir)

    for image in images:
        image_path = os.path.join(image_dir, image)
        sharpness = calculate_image_sharpness_fft(image_path)
        sharpness_values.append(sharpness)

    median_sharpness = np.median(sharpness_values)
    return median_sharpness


def calculate_median_sharpness_canny(image_dir):
    sharpness_values = []
    images = os.listdir(image_dir)

    for image in images:
        image_path = os.path.join(image_dir, image)
        sharpness = calculate_image_sharpness_canny(image_path)
        sharpness_values.append(sharpness)

    median_sharpness = np.median(sharpness_values)
    return median_sharpness
