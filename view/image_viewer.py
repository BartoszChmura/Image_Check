import os
import shutil
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QMessageBox, QHBoxLayout, QGraphicsView,
    QGraphicsScene
)
from PyQt5.QtGui import QPixmap, QImage, QWheelEvent, QPainter
from PyQt5.QtCore import Qt
from config.log_config import logger
from utils.helpers import resource_path


class CustomGraphicsView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.setDragMode(QGraphicsView.ScrollHandDrag)

    def wheelEvent(self, event: QWheelEvent):
        event.ignore()


class ImageViewer(QMainWindow):
    def __init__(self, detected_issues, destination_folder, include_deleted_list=False, include_logs=False):
        super().__init__()

        self.folder_path = resource_path('./images/to_check')
        self.checked_folder_path = resource_path('./images/checked')
        self.detected_issues = detected_issues
        self.destination_folder = destination_folder
        self.include_deleted_list = include_deleted_list
        self.include_logs = include_logs

        self.deleted_images = []

        self.image_list = [f for f in os.listdir(self.folder_path) if f.endswith(('png', 'jpg', 'jpeg', 'bmp'))]
        self.current_index = 0

        self.user_initiated_close = False

        self.setWindowTitle("Image Viewer")

        screen_size = QApplication.primaryScreen().availableGeometry()
        self.resize(screen_size.width(), screen_size.height())

        self.showMaximized()
        self.init_ui()

        self.show_image()

        self.installEventFilter(self)

    def init_ui(self):
        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)

        self.layout = QVBoxLayout(self.main_widget)
        self.button_layout = QHBoxLayout()

        self.graphics_view = CustomGraphicsView(self)
        self.graphics_view.setFocusPolicy(Qt.NoFocus)
        self.scene = QGraphicsScene(self)
        self.graphics_view.setScene(self.scene)

        self.graphics_view.setTransformationAnchor(QGraphicsView.NoAnchor)
        self.graphics_view.setResizeAnchor(QGraphicsView.NoAnchor)

        self.graphics_view.setRenderHint(QPainter.Antialiasing)
        self.graphics_view.setRenderHint(QPainter.SmoothPixmapTransform)

        self.layout.addWidget(self.graphics_view)

        self.issues_label = QLabel(self)
        self.issues_label.setText("No issues detected")
        self.layout.addWidget(self.issues_label)

        self.prev_button = QPushButton("Previous", self)
        self.prev_button.setFocusPolicy(Qt.NoFocus)
        self.next_button = QPushButton("Next", self)
        self.next_button.setFocusPolicy(Qt.NoFocus)
        self.keep_button = QPushButton("Save", self)
        self.keep_button.setFocusPolicy(Qt.NoFocus)
        self.delete_button = QPushButton("Delete", self)
        self.delete_button.setFocusPolicy(Qt.NoFocus)

        self.button_layout.addWidget(self.prev_button)
        self.button_layout.addWidget(self.next_button)
        self.button_layout.addWidget(self.keep_button)
        self.button_layout.addWidget(self.delete_button)
        self.layout.addLayout(self.button_layout)

        self.prev_button.clicked.connect(self.prev_image)
        self.next_button.clicked.connect(self.next_image)
        self.keep_button.clicked.connect(self.keep_image)
        self.delete_button.clicked.connect(self.delete_image)

        self.main_widget.setFocusPolicy(Qt.StrongFocus)
        self.main_widget.setFocus()

    def show_image(self):
        if self.image_list:
            image_name = self.image_list[self.current_index]
            image_path = os.path.join(self.folder_path, image_name)

            if not os.path.exists(image_path):
                logger.error(f"Image file not found: {image_name}")
                QMessageBox.critical(self, "Error", f"Image file not found: {image_name}")
                return

            q_image = QImage(image_path)
            if q_image.isNull():
                logger.error(f"Failed to load image: {image_name}")
                QMessageBox.critical(self, "Error", f"Failed to load image: {image_name}")
                return

            screen_size = QApplication.primaryScreen().availableGeometry().size()
            max_width, max_height = screen_size.width(), screen_size.height()

            q_image = q_image.scaled(max_width, max_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)

            pixmap = QPixmap.fromImage(q_image)
            self.scene.clear()
            self.scene.addPixmap(pixmap)
            self.setWindowTitle(f"Image Viewer - {image_name}")

            issues = self.detected_issues.get(image_name, [])
            self.issues_label.setText("Issues:\n" + "\n".join(issues) if issues else "No issues detected")
        else:
            self.close_app()

    def keep_image(self):
        if self.image_list:
            image_path = os.path.join(self.folder_path, self.image_list[self.current_index])
            new_path = os.path.join(self.checked_folder_path, self.image_list[self.current_index])
            try:
                shutil.move(image_path, new_path)
                logger.info(f"Image: {self.image_list[self.current_index]} moved to checked folder by user")
                del self.image_list[self.current_index]
            except (OSError, IOError) as e:
                logger.error(f"Failed to save image: {e} - image_viewer.py")
                QMessageBox.critical(self, "Error", f"Failed to save image: {e}")
                return

            if not self.image_list:
                self.close_app()
            elif self.current_index >= len(self.image_list):
                self.current_index = len(self.image_list) - 1
            self.show_image()

    def delete_image(self):
        if self.image_list:
            image_path = os.path.join(self.folder_path, self.image_list[self.current_index])
            try:
                os.remove(image_path)
                logger.info(f"Image: {self.image_list[self.current_index]} deleted by user")
                self.deleted_images.append(self.image_list[self.current_index])
                del self.image_list[self.current_index]
            except (OSError, IOError) as e:
                logger.error(f"Failed to delete image: {e} - image_viewer.py")
                QMessageBox.critical(self, "Error", f"Failed to delete image: {e}")
                return

            if not self.image_list:
                self.close_app()
            elif self.current_index >= len(self.image_list):
                self.current_index = len(self.image_list) - 1
            self.show_image()

    def next_image(self):
        if self.current_index < len(self.image_list) - 1:
            self.current_index += 1
            self.show_image()
        elif self.image_list:
            self.current_index = 0
            self.show_image()

    def prev_image(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.show_image()
        elif self.image_list:
            self.current_index = len(self.image_list) - 1
            self.show_image()

    def close_app(self):
        if not self.user_initiated_close:
            self.user_initiated_close = True
            self.copy_checked_images_to_destination()

            if self.include_deleted_list:
                self.save_deleted_images_list()

            if self.include_logs:
                self.copy_log_file_to_destination()

        self.clear_directories()

        self.close()

    def closeEvent(self, event):
        if self.user_initiated_close:
            event.accept()
        else:
            reply = QMessageBox.question(self, 'Close', 'Do you want to exit?',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.user_initiated_close = False
                event.accept()
            else:
                event.ignore()

    def copy_checked_images_to_destination(self):
        if self.destination_folder and os.path.exists(self.checked_folder_path):
            try:
                for file_name in os.listdir(self.checked_folder_path):
                    source_path = os.path.join(self.checked_folder_path, file_name)
                    if os.path.isfile(source_path):
                        destination_path = os.path.join(self.destination_folder, file_name)
                        shutil.copy(source_path, destination_path)
                logger.info(f'All checked images have been copied to the destination folder: {self.destination_folder}')
            except (OSError, IOError) as e:
                logger.error(f"Failed to copy checked images: {e} - image_viewer.py")
                QMessageBox.critical(self, "Error", f"Failed to copy checked images: {e}")

    def copy_log_file_to_destination(self):
        log_file_path = resource_path('./logs/app.logs')
        if os.path.exists(log_file_path):
            try:
                log_destination_path = os.path.join(self.destination_folder, 'app.logs')
                shutil.copy(log_file_path, log_destination_path)
                logger.info(f'Log file copied to the destination folder: {log_destination_path}')
            except (OSError, IOError) as e:
                logger.error(f"Failed to copy log file: {e} - image_viewer.py")
                QMessageBox.critical(self, "Error", f"Failed to copy log file: {e}")
        else:
            logger.warning(f'Log file not found at: {log_file_path}')

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
                        logger.error(f"Failed to delete {file_path}: {e} - image_viewer.py")
                        QMessageBox.critical(self, "Error", f"Failed to delete {file_path}: {e}")

    def save_deleted_images_list(self):
        try:
            deleted_images_file = os.path.join(self.destination_folder, "deleted_images.txt")
            with open(deleted_images_file, 'w') as file:
                for image_name in self.deleted_images:
                    file.write(f"{image_name}\n")
            logger.info(f"Deleted images list saved to {deleted_images_file}")
        except Exception as e:
            logger.error(f"Failed to save deleted images list: {e} - image_viewer.py")
            QMessageBox.critical(self, "Error", f"Failed to save deleted images list: {e}")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.user_initiated_close = False
            self.close()
        elif event.key() == Qt.Key_Right:
            self.next_image()
        elif event.key() == Qt.Key_Left:
            self.prev_image()
        else:
            super().keyPressEvent(event)

    def wheelEvent(self, event: QWheelEvent):
        zoom_factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15

        old_pos = self.graphics_view.mapToScene(event.pos())

        self.graphics_view.scale(zoom_factor, zoom_factor)

        new_pos = self.graphics_view.mapToScene(event.pos())
        delta = new_pos - old_pos

        self.graphics_view.translate(delta.x(), delta.y())
        event.accept()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.graphics_view.setDragMode(QGraphicsView.ScrollHandDrag)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.graphics_view.setDragMode(QGraphicsView.NoDrag)
        super().mouseReleaseEvent(event)
