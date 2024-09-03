import cv2
import numpy as np

# Wczytaj obraz
image = cv2.imread('./zdjecia/nowe/SK_b827ebf4b29dc (16).png')

# Dodaj szum gaussowski
row, col, ch = image.shape
mean = 0
sigma = 25
gauss = np.random.normal(mean, sigma, (row, col, ch))
gauss = gauss.reshape(row, col, ch)
noisy_image = cv2.add(image, gauss, dtype=cv2.CV_8UC3)

# Zapisz obraz z szumem jako plik '1_szum.jpg'
cv2.imwrite('1_szum.jpg', noisy_image)

# Pokaż wynik
cv2.imshow('Obraz z Szumem', noisy_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
