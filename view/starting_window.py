import os
import shutil
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QProgressBar, QApplication
)
from PyQt5.QtCore import QThread, pyqtSignal

from utils.utils import crop_images, process_folder
from view.config_window import ConfigWindow
from view.image_viewer import ImageViewer


class WorkerThread(QThread):
    progress_update = pyqtSignal(int)
    task_complete = pyqtSignal(dict)

    def __init__(self, source_folder, destination_folder):
        super().__init__()
        self.source_folder = source_folder
        self.destination_folder = destination_folder

    def run(self):
        new_folder = './zdjecia/nowe'
        os.makedirs(new_folder, exist_ok=True)

        image_files = [f for f in os.listdir(self.source_folder) if os.path.isfile(os.path.join(self.source_folder, f)) and f.lower().endswith(('png', 'jpg', 'jpeg', 'bmp'))]

        total_steps = len(image_files) * 3
        current_step = 0

        def progress_callback(step_increment=1):
            nonlocal current_step
            current_step += step_increment
            progress = int((current_step / total_steps) * 100)
            self.progress_update.emit(progress)

        for file_name in image_files:
            source_path = os.path.join(self.source_folder, file_name)
            shutil.copy(source_path, new_folder)
            progress_callback(1)

        crop_images(new_folder, './zdjecia/sylwetki', progress_callback)

        detected_issues = process_folder(new_folder, './zdjecia/sylwetki', progress_callback)

        self.task_complete.emit(detected_issues)




class InitialWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.source_folder = ""
        self.destination_folder = ""

        self.setWindowTitle("Starting Window")
        self.setGeometry(200, 200, 400, 200)
        self.init_ui()

    def init_ui(self):
        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)

        self.layout = QVBoxLayout(self.main_widget)

        self.source_label = QLabel("Source folder not selected", self)
        self.layout.addWidget(self.source_label)

        self.source_button = QPushButton("Choose source folder", self)
        self.source_button.clicked.connect(self.select_source_folder)
        self.layout.addWidget(self.source_button)

        self.destination_label = QLabel("Destination folder not selected", self)
        self.layout.addWidget(self.destination_label)

        self.destination_button = QPushButton("Choose destination folder", self)
        self.destination_button.clicked.connect(self.select_destination_folder)
        self.layout.addWidget(self.destination_button)

        self.start_button = QPushButton("Start", self)
        self.start_button.setEnabled(False)
        self.start_button.clicked.connect(self.start_processing)
        self.layout.addWidget(self.start_button)

        self.progress_bar = QProgressBar(self)
        self.layout.addWidget(self.progress_bar)

        self.config_button = QPushButton("Configuration", self)
        self.config_button.clicked.connect(self.open_config_window)
        self.layout.addWidget(self.config_button)

    def open_config_window(self):
        config_window = ConfigWindow(self)
        config_window.exec_()

    def select_source_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Choose source folder")
        if folder:
            self.source_folder = folder
            self.source_label.setText(f"Source folder: {self.source_folder}")
            self.check_folders_selected()

    def select_destination_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Choose destination folder")
        if folder:
            self.destination_folder = folder
            self.destination_label.setText(f"Destination folder: {self.destination_folder}")
            self.check_folders_selected()

    def check_folders_selected(self):
        if self.source_folder and self.destination_folder:
            self.start_button.setEnabled(True)

    def start_processing(self):
        self.start_button.setEnabled(False)

        self.worker = WorkerThread(self.source_folder, self.destination_folder)
        self.worker.progress_update.connect(self.update_progress_bar)
        self.worker.task_complete.connect(self.on_task_complete)
        self.worker.start()

    def update_progress_bar(self, value):
        self.progress_bar.setValue(value)

    def on_task_complete(self, detected_issues):
        self.viewer = ImageViewer(detected_issues, self.destination_folder)
        self.viewer.show()
        self.close()


