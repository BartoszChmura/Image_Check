import os
import shutil
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QProgressBar, QApplication, QMessageBox
)
from PyQt5.QtCore import QThread, pyqtSignal

from utils.utils import crop_images, process_folder
from view.config_window import ConfigWindow
from view.image_viewer import ImageViewer
from config.log_config import logger


class WorkerThread(QThread):
    progress_update = pyqtSignal(int)
    task_complete = pyqtSignal(dict)

    def __init__(self, source_folder, destination_folder):
        super().__init__()
        self.source_folder = source_folder
        self.destination_folder = destination_folder

    def run(self):
        new_folder = './images/new'
        try:
            os.makedirs(new_folder, exist_ok=True)
        except OSError as e:
            logger.error(f"Failed to create new folder: {e} - starting_window.py")
            self.task_complete.emit({'error': f"Failed to create new folder: {e}"})
            return

        try:
            image_files = [f for f in os.listdir(self.source_folder)
                           if os.path.isfile(os.path.join(self.source_folder, f)) and f.lower().endswith(('png', 'jpg', 'jpeg', 'bmp'))]
        except Exception as e:
            logger.error(f"Failed to list files in source folder: {e} - starting_window.py")
            self.task_complete.emit({'error': f"Failed to list files in source folder: {e}"})
            return

        total_steps = len(image_files) * 3
        current_step = 0

        def progress_callback(step_increment=1):
            nonlocal current_step
            current_step += step_increment
            progress = int((current_step / total_steps) * 100)
            self.progress_update.emit(progress)

        try:
            for file_name in image_files:
                source_path = os.path.join(self.source_folder, file_name)
                shutil.copy(source_path, new_folder)
                progress_callback(1)
        except (OSError, IOError) as e:
            logger.error(f"Failed to copy files: {e} - starting_window.py")
            self.task_complete.emit({'error': f"Failed to copy files: {e}"})
            return

        try:
            crop_images(new_folder, './images/silhouette', progress_callback)
        except Exception as e:
            logger.error(f"Failed to crop images: {e} - starting_window.py")
            self.task_complete.emit({'error': f"Failed to crop images: {e}"})
            return

        try:
            detected_issues = process_folder(new_folder, './images/silhouette', progress_callback)
        except Exception as e:
            logger.error(f"Failed to process folder: {e} - starting_window.py")
            self.task_complete.emit({'error': f"Failed to process folder: {e}"})
            return

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
        try:
            config_window = ConfigWindow(self)
            config_window.exec_()
        except Exception as e:
            logger.error(f"Failed to open configuration window: {e} - starting_window.py")
            QMessageBox.critical(self, "Error", f"Failed to open configuration window: {e}")

    def select_source_folder(self):
        try:
            folder = QFileDialog.getExistingDirectory(self, "Choose source folder")
            if folder:
                self.source_folder = folder
                self.source_label.setText(f"Source folder: {self.source_folder}")
                self.check_folders_selected()
        except Exception as e:
            logger.error(f"Failed to select source folder: {e} - starting_window.py")
            QMessageBox.critical(self, "Error", f"Failed to select source folder: {e}")

    def select_destination_folder(self):
        try:
            folder = QFileDialog.getExistingDirectory(self, "Choose destination folder")
            if folder:
                self.destination_folder = folder
                self.destination_label.setText(f"Destination folder: {self.destination_folder}")
                self.check_folders_selected()
        except Exception as e:
            logger.error(f"Failed to select destination folder: {e} - starting_window.py")
            QMessageBox.critical(self, "Error", f"Failed to select destination folder: {e}")

    def check_folders_selected(self):
        if self.source_folder and self.destination_folder:
            self.start_button.setEnabled(True)

    def start_processing(self):
        try:
            self.start_button.setEnabled(False)

            self.worker = WorkerThread(self.source_folder, self.destination_folder)
            self.worker.progress_update.connect(self.update_progress_bar)
            self.worker.task_complete.connect(self.on_task_complete)
            self.worker.start()
        except Exception as e:
            logger.error(f"Failed to start processing: {e} - starting_window.py")
            QMessageBox.critical(self, "Error", f"Failed to start processing: {e}")

    def update_progress_bar(self, value):
        self.progress_bar.setValue(value)

    def on_task_complete(self, detected_issues):
        if 'error' in detected_issues:
            logger.error(f"Error during processing: {detected_issues['error']} - starting_window.py")
            QMessageBox.critical(self, "Error", detected_issues['error'])
            self.start_button.setEnabled(True)
            return

        self.viewer = ImageViewer(detected_issues, self.destination_folder)
        self.viewer.show()
        self.close()


