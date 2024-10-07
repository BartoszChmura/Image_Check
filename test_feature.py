import cv2

image = cv2.imread('./images/new/B.png')
gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def draw_keypoints(image, keypoints, color=(255, 0, 255)):
    return cv2.drawKeypoints(image, keypoints, None, color=color, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)


def detect_features_sift(image, gray_image):
    sift = cv2.SIFT_create(
        nOctaveLayers=5,
        contrastThreshold=0.01,
        edgeThreshold=10,
        sigma=1.6
    )

    keypoints, descriptors = sift.detectAndCompute(gray_image, None)

    filtered_keypoints = [kp for kp in keypoints if 1 < kp.size < 50]

    print(f"Number of keypoints: {len(filtered_keypoints)}")

    return draw_keypoints(image, filtered_keypoints)


def resize_image(image, scale_percent=50):
    width = int(image.shape[1] * scale_percent / 100)
    height = int(image.shape[0] * scale_percent / 100)
    dimensions = (width, height)
    return cv2.resize(image, dimensions, interpolation=cv2.INTER_AREA)


output_sift = resize_image(detect_features_sift(image.copy(), gray_image))

cv2.imshow('SIFT Feature Detection', output_sift)
cv2.waitKey(0)
cv2.destroyAllWindows()
