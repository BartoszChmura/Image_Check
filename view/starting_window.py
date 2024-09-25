import os
import shutil
import time
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QProgressBar, QApplication, QMessageBox,
    QCheckBox
)
from PyQt5.QtCore import QThread, pyqtSignal, Qt

from utils.utils import crop_images, process_folder
from view.config_window import ConfigWindow
from view.image_viewer import ImageViewer
from config.log_config import logger
from utils.helpers import resource_path



class WorkerThread(QThread):
    progress_update = pyqtSignal(int, str)
    task_complete = pyqtSignal(dict)

    def __init__(self, source_folder, destination_folder):
        super().__init__()
        self.source_folder = source_folder
        self.destination_folder = destination_folder
        self.start_time = time.time()

    def run(self):
        new_folder = resource_path('./images/new')

        try:
            image_files = [f for f in os.listdir(self.source_folder) if
                           os.path.isfile(os.path.join(self.source_folder, f))
                           and f.lower().endswith(
                               ('png', 'jpg', 'jpeg', 'bmp'))]
        except Exception as e:
            logger.error(f"Failed to list files in source folder: {e} - starting_window.py")
            self.task_complete.emit({'error': f"Failed to list files in source folder: {e}"})
            return

        total_files = len(image_files)
        crop_steps = total_files
        median_steps = 3
        process_steps = total_files

        crop_progress_range = 33
        median_progress_range = 33
        process_progress_range = 34

        total_crop_steps = crop_steps
        total_median_steps = median_steps
        total_process_steps = process_steps

        current_crop_step = 0
        current_median_step = 0
        current_process_step = 0

        stage_start_time = time.time()

        def progress_callback(step_increment=1, stage="crop"):
            nonlocal current_crop_step, current_median_step, current_process_step, stage_start_time

            if stage == "crop":
                current_crop_step += step_increment
                progress = int((current_crop_step / total_crop_steps) * crop_progress_range)
                stage_number = 1
                if current_crop_step == total_crop_steps:
                    self.progress_update.emit(progress, "Stage 2/3 - Calculating...")
                    stage = "median"
                    stage_start_time = time.time()
            elif stage == "median":
                current_median_step += step_increment
                progress = int(crop_progress_range + (current_median_step / total_median_steps) * median_progress_range)
                stage_number = 2
                if current_median_step == total_median_steps:
                    self.progress_update.emit(progress, "Stage 3/3 - Calculating...")
                    stage = "process"
                    stage_start_time = time.time()
            elif stage == "process":
                current_process_step += step_increment
                progress = int(crop_progress_range + median_progress_range + (
                        current_process_step / total_process_steps) * process_progress_range)
                stage_number = 3

            elapsed_time = time.time() - stage_start_time
            completed_steps = (current_crop_step if stage == "crop" else
                               current_median_step if stage == "median" else
                               current_process_step)

            if completed_steps > 0:
                if stage == "median":
                    estimated_total_time = elapsed_time * total_median_steps / completed_steps
                    estimated_remaining_time = estimated_total_time - elapsed_time
                else:
                    estimated_total_time = elapsed_time * (total_crop_steps if stage == "crop" else
                                                           total_median_steps if stage == "median" else
                                                           total_process_steps) / completed_steps
                    estimated_remaining_time = estimated_total_time - elapsed_time
            else:
                estimated_remaining_time = 0

            minutes, seconds = divmod(int(estimated_remaining_time), 60)
            stage_info = f"Stage {stage_number}/3 - Estimated time remaining: {minutes}m {seconds}s"

            self.progress_update.emit(min(progress, 100), stage_info)

        try:
            for file_name in image_files:
                source_path = os.path.join(self.source_folder, file_name)
                shutil.copy(source_path, new_folder)

        except (OSError, IOError) as e:
            logger.error(f"Failed to copy files: {e} - starting_window.py")
            self.task_complete.emit({'error': f"Failed to copy files: {e}"})
            return

        try:
            crop_images(new_folder, resource_path('./images/silhouette'), progress_callback)
        except Exception as e:
            logger.error(f"Failed to crop images: {e} - starting_window.py")
            self.task_complete.emit({'error': f"Failed to crop images: {e}"})
            return

        self.progress_update.emit(33, "Stage 2/3 - Calculating...")
        stage_start_time = time.time()

        try:
            detected_issues = process_folder(new_folder, resource_path('./images/silhouette'), progress_callback)
        except Exception as e:
            logger.error(f"Failed to process folder: {e} - starting_window.py")
            self.task_complete.emit({'error': f"Failed to process folder: {e}"})
            return

        self.progress_update.emit(66, "Stage 3/3 - Calculating...")
        stage_start_time = time.time()

        self.task_complete.emit(detected_issues)


class InitialWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.source_folder = ""
        self.destination_folder = ""

        self.include_deleted_images_list = False
        self.include_logs = False

        self.setWindowTitle("Starting Window")
        self.setGeometry(200, 200, 400, 300)
        self.setStyleSheet("""
                    QMainWindow {
                        background-color: #f8f9fa;
                    }
                    QLabel {
                        font-size: 14px;
                        color: #343a40;
                    }
                    QPushButton {
                        background-color: #007bff;
                        color: #fff;
                        border: none;
                        padding: 8px;
                        font-size: 12px;
                        border-radius: 4px;
                        margin: 4px;
                    }
                    QPushButton:hover {
                        background-color: #0056b3;
                    }
                    QProgressBar {
                        border: 1px solid #ced4da;
                        border-radius: 5px;
                        text-align: center;
                        height: 20px;
                    }
                    QProgressBar::chunk {
                        background-color: #28a745;
                        border-radius: 5px;
                    }
                    QCheckBox {
                        font-size: 14px;
                        margin: 5px;
                    }
                """)
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

        self.include_deleted_checkbox = QCheckBox("Include deleted images list", self)
        self.include_deleted_checkbox.stateChanged.connect(self.toggle_include_deleted)
        self.layout.addWidget(self.include_deleted_checkbox)

        self.include_logs_checkbox = QCheckBox("Include app.logs", self)
        self.include_logs_checkbox.stateChanged.connect(self.toggle_include_logs)
        self.layout.addWidget(self.include_logs_checkbox)

        self.stage_label = QLabel("", self)
        self.layout.addWidget(self.stage_label)
        self.stage_label.setVisible(False)

        self.start_button = QPushButton("Start", self)
        self.start_button.setEnabled(False)
        self.start_button.clicked.connect(self.start_processing)
        self.layout.addWidget(self.start_button)

        self.progress_bar = QProgressBar(self)
        self.layout.addWidget(self.progress_bar)
        self.progress_bar.setVisible(False)

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
        if self.source_folder:
            self.start_button.setEnabled(True)

    def toggle_include_deleted(self, state):
        self.include_deleted_images_list = state == Qt.Checked

    # Update state when "Include app.logs" checkbox is toggled
    def toggle_include_logs(self, state):
        self.include_logs = state == Qt.Checked

    def start_processing(self):
        try:
            self.start_button.setEnabled(False)
            self.config_button.setEnabled(False)

            self.clear_directories()

            if not self.destination_folder:
                self.destination_folder = os.path.join(self.source_folder,
                                                       os.path.basename(self.source_folder) + "_out")

                if not os.path.exists(self.destination_folder):
                    os.makedirs(self.destination_folder)
                    logger.info(f"Created destination folder: {self.destination_folder}")

            self.stage_label.setVisible(True)
            self.stage_label.setText("Stage: 1/3 - Calculating...")
            self.progress_bar.setVisible(True)

            self.worker = WorkerThread(self.source_folder, self.destination_folder)
            self.worker.progress_update.connect(self.update_progress_bar)
            self.worker.task_complete.connect(self.on_task_complete)
            self.worker.start()
        except Exception as e:
            logger.error(f"Failed to start processing: {e} - starting_window.py")
            QMessageBox.critical(self, "Error", f"Failed to start processing: {e}")

    def clear_directories(self):
        directories_to_clear = [
            resource_path('./images/to_check'),
            resource_path('./images/new'),
            resource_path('./images/checked'),
            resource_path('./images/silhouette')
        ]

        for directory in directories_to_clear:
            if os.path.exists(directory):
                for filename in os.listdir(directory):
                    file_path = os.path.join(directory, filename)
                    try:
                        if os.path.isfile(file_path) or os.path.islink(file_path):
                            os.unlink(file_path)
                            logger.info(f'Deleted file: {file_path}')
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)
                    except Exception as e:
                        logger.error(f"Failed to delete {file_path}: {e} - starting_window.py")
                        QMessageBox.critical(self, "Error", f"Failed to delete {file_path}. Reason: {e}")

    def update_progress_bar(self, value, stage_info):
        self.progress_bar.setValue(value)
        self.stage_label.setText(stage_info)

    def on_task_complete(self, detected_issues):
        if 'error' in detected_issues:
            logger.error(f"Error during processing: {detected_issues['error']} - starting_window.py")
            QMessageBox.critical(self, "Error", detected_issues['error'])
            self.start_button.setEnabled(True)
            self.config_button.setEnabled(True)
            return

        self.worker.quit()
        self.worker.wait()

        self.viewer = ImageViewer(
            detected_issues,
            self.destination_folder,
            include_deleted_list=self.include_deleted_images_list,
            include_logs=self.include_logs
        )
        self.viewer.show()

        self.hide()
