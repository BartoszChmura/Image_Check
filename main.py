import multiprocessing

from PyQt5.QtWidgets import QApplication

from utils.utils import load_styles
from view.starting_window import InitialWindow

import sys


def init_interface():
    app = QApplication(sys.argv)
    style_sheet = load_styles()
    app.setStyleSheet(style_sheet)
    window = InitialWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    multiprocessing.freeze_support()

    init_interface()
