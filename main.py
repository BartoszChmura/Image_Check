from PyQt5.QtWidgets import QApplication

from utils.utils import crop_images, process_folder
from view.image_viewer import ImageViewer

import sys

from view.starting_window import InitialWindow
from view.image_viewer import ImageViewer


def init_interface():
    app = QApplication(sys.argv)
    window = InitialWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    init_interface()