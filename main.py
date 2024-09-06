from PyQt5.QtWidgets import QApplication

from utils.utils import crop_images, process_folder
from view.interface import ImageViewer


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