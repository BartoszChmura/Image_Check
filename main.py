from PyQt5.QtWidgets import QApplication
from view.starting_window import InitialWindow
from view.image_viewer import ImageViewer

import sys


def init_interface():
    app = QApplication(sys.argv)
    window = InitialWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    init_interface()