import cv2

image = cv2.imread('./images/new/A.png')
gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

def draw_keypoints(image, keypoints, color=(255, 0, 255)):
    return cv2.drawKeypoints(image, keypoints, None, color=color, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

def detect_features_sift(image, gray_image):
    sift = cv2.SIFT_create()
    keypoints, descriptors = sift.detectAndCompute(gray_image, None)
    return draw_keypoints(image, keypoints)


def detect_features_fast(image, gray_image):
    fast = cv2.FastFeatureDetector_create()
    keypoints = fast.detect(gray_image, None)
    return draw_keypoints(image, keypoints)

def resize_image(image, scale_percent=50):
    width = int(image.shape[1] * scale_percent / 100)
    height = int(image.shape[0] * scale_percent / 100)
    dimensions = (width, height)
    return cv2.resize(image, dimensions, interpolation=cv2.INTER_AREA)

output_sift = resize_image(detect_features_sift(image.copy(), gray_image))

output_fast = resize_image(detect_features_fast(image.copy(), gray_image))

cv2.imshow('SIFT Feature Detection', output_sift)
cv2.imshow('FAST Feature Detection', output_fast)

cv2.waitKey(0)
cv2.destroyAllWindows()
