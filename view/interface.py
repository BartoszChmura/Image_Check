import os
import shutil
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QMessageBox, QHBoxLayout, QGraphicsView, QGraphicsScene
)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
from PIL import Image

class ImageViewer(QMainWindow):
    def __init__(self, detected_issues):
        super().__init__()

        self.folder_path = './zdjecia/do_sprawdzenia'
        self.checked_folder_path = './zdjecia/sprawdzone'
        self.detected_issues = detected_issues

        self.image_list = [f for f in os.listdir(self.folder_path) if f.endswith(('png', 'jpg', 'jpeg', 'bmp'))]
        self.current_index = 0

        self.user_initiated_close = False

        self.setWindowTitle("Przeglądarka zdjęć")
        self.setGeometry(100, 100, 1200, 800)

        self.init_ui()

        self.show_image()

    def init_ui(self):
        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)

        self.layout = QVBoxLayout(self.main_widget)
        self.button_layout = QHBoxLayout()

        self.graphics_view = QGraphicsView(self)
        self.scene = QGraphicsScene(self)
        self.graphics_view.setScene(self.scene)
        self.layout.addWidget(self.graphics_view)

        self.issues_label = QLabel(self)
        self.issues_label.setText("Brak wykrytych wad")
        self.layout.addWidget(self.issues_label)

        self.prev_button = QPushButton("Poprzednie", self)
        self.next_button = QPushButton("Następne", self)
        self.keep_button = QPushButton("Zachowaj", self)
        self.delete_button = QPushButton("Odrzuć", self)

        self.button_layout.addWidget(self.prev_button)
        self.button_layout.addWidget(self.next_button)
        self.button_layout.addWidget(self.keep_button)
        self.button_layout.addWidget(self.delete_button)
        self.layout.addLayout(self.button_layout)

        self.prev_button.clicked.connect(self.prev_image)
        self.next_button.clicked.connect(self.next_image)
        self.keep_button.clicked.connect(self.keep_image)
        self.delete_button.clicked.connect(self.delete_image)

    def show_image(self):
        if self.image_list:
            image_name = self.image_list[self.current_index]
            image_path = os.path.join(self.folder_path, image_name)
            image = Image.open(image_path)
            image.thumbnail((1200, 1200))

            image_data = image.tobytes("raw", "RGB")
            q_image = QImage(image_data, image.width, image.height, QImage.Format_RGB888)

            pixmap = QPixmap.fromImage(q_image)

            self.scene.clear()
            self.scene.addPixmap(pixmap)
            self.setWindowTitle(f"Przeglądarka zdjęć - {image_name}")

            issues = self.detected_issues.get(image_name, [])
            self.issues_label.setText("Wady:\n" + "\n".join(issues) if issues else "Brak wykrytych wad")
        else:
            self.close_app()

    def keep_image(self):
        if self.image_list:
            image_path = os.path.join(self.folder_path, self.image_list[self.current_index])
            new_path = os.path.join(self.checked_folder_path, self.image_list[self.current_index])
            shutil.move(image_path, new_path)
            del self.image_list[self.current_index]
            if not self.image_list:
                self.close_app()
            elif self.current_index >= len(self.image_list):
                self.current_index = len(self.image_list) - 1
            self.show_image()

    def delete_image(self):
        if self.image_list:
            image_path = os.path.join(self.folder_path, self.image_list[self.current_index])
            os.remove(image_path)
            del self.image_list[self.current_index]
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
        self.user_initiated_close = True
        self.close()

    def closeEvent(self, event):
        if self.user_initiated_close:
            event.accept()
        else:
            reply = QMessageBox.question(self, 'Zamknij', 'Czy na pewno chcesz zamknąć aplikację?',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                event.accept()
            else:
                event.ignore()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.user_initiated_close = False
            self.close()
