import sys
import os
import shutil
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog
)
from view.image_viewer import ImageViewer
from utils.utils import crop_images, process_folder


class InitialWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.source_folder = ""
        self.destination_folder = ""

        self.setWindowTitle("Wybór folderów")
        self.setGeometry(200, 200, 400, 200)
        self.init_ui()

    def init_ui(self):
        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)

        self.layout = QVBoxLayout(self.main_widget)

        self.source_label = QLabel("Folder źródłowy: Nie wybrano", self)
        self.layout.addWidget(self.source_label)

        self.source_button = QPushButton("Wybierz folder źródłowy", self)
        self.source_button.clicked.connect(self.select_source_folder)
        self.layout.addWidget(self.source_button)

        self.destination_label = QLabel("Folder docelowy: Nie wybrano", self)
        self.layout.addWidget(self.destination_label)

        self.destination_button = QPushButton("Wybierz folder docelowy", self)
        self.destination_button.clicked.connect(self.select_destination_folder)
        self.layout.addWidget(self.destination_button)

        self.start_button = QPushButton("Start", self)
        self.start_button.setEnabled(False)
        self.start_button.clicked.connect(self.start_viewer)
        self.layout.addWidget(self.start_button)

    def select_source_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Wybierz folder źródłowy")
        if folder:
            self.source_folder = folder
            self.source_label.setText(f"Folder źródłowy: {self.source_folder}")
            self.check_folders_selected()

    def select_destination_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Wybierz folder docelowy")
        if folder:
            self.destination_folder = folder
            self.destination_label.setText(f"Folder docelowy: {self.destination_folder}")
            self.check_folders_selected()

    def check_folders_selected(self):
        if self.source_folder and self.destination_folder:
            self.start_button.setEnabled(True)

    def start_viewer(self):
        new_folder = './zdjecia/nowe'
        os.makedirs(new_folder, exist_ok=True)
        for file_name in os.listdir(self.source_folder):
            source_path = os.path.join(self.source_folder, file_name)
            if os.path.isfile(source_path) and file_name.lower().endswith(('png', 'jpg', 'jpeg', 'bmp')):
                shutil.copy(source_path, new_folder)


        crop_images(new_folder, './zdjecia/sylwetki')
        detected_issues = process_folder(new_folder, './zdjecia/sylwetki')

        self.viewer = ImageViewer(detected_issues, self.destination_folder)
        self.viewer.show()
        self.close()