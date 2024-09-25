import xml.etree.ElementTree as ET

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QSlider, QPushButton, QHBoxLayout, QFormLayout, QMessageBox
)
from PyQt5.QtCore import Qt
from config.log_config import logger
from utils.helpers import resource_path


class ConfigWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuration")
        self.setGeometry(300, 300, 400, 200)
        self.init_ui()
        self.load_config()

    def init_ui(self):
        self.layout = QVBoxLayout(self)

        self.form_layout = QFormLayout()

        self.sharpness_low_slider, self.sharpness_low_value = self.create_slider("Sharpness Low Threshold", 1, 100, 0.3)
        self.sharpness_high_slider, self.sharpness_high_value = self.create_slider("Sharpness High Threshold", 1, 100,
                                                                                   4)
        self.saturation_low_slider, self.saturation_low_value = self.create_slider("Saturation Low Threshold", 1, 100,
                                                                                   0.5)
        self.brightness_low_slider, self.brightness_low_value = self.create_slider("Brightness Low Threshold", 1, 100,
                                                                                   0.25)
        self.brightness_high_slider, self.brightness_high_value = self.create_slider("Brightness High Threshold", 1,
                                                                                     100, 2)
        self.flare_threshold_slider, self.flare_threshold_value = self.create_slider("Flare Threshold", 1, 30, 0.01)

        self.layout.addLayout(self.form_layout)

        self.save_button = QPushButton("Save", self)
        self.save_button.clicked.connect(self.save_config)
        self.layout.addWidget(self.save_button)

        self.reset_button = QPushButton("Reset to Default", self)
        self.reset_button.clicked.connect(self.reset_to_default)
        self.layout.addWidget(self.reset_button)

    def create_slider(self, label_text, min_val, max_val, default_val):
        slider_layout = QHBoxLayout()

        min_label = QLabel(f"{min_val / 1000:.3f}", self) if "Flare Threshold" in label_text else QLabel(
            f"{min_val / 100:.2f}", self)
        max_label = QLabel(f"{max_val / 1000:.3f}", self) if "Flare Threshold" in label_text else QLabel(
            f"{max_val / 10:.1f}", self)
        current_value_label = QLabel(f"{default_val:.3f}" if "Flare Threshold" in label_text else f"{default_val:.2f}",
                                     self)

        current_value_label.setStyleSheet("color: red; font-weight: bold;")

        slider = QSlider(Qt.Horizontal, self)
        slider.setRange(min_val, max_val)
        slider.setValue(int(default_val * 1000) if "Flare Threshold" in label_text else int(default_val * 10))
        slider.valueChanged.connect(lambda: current_value_label.setText(
            f"{slider.value() / 1000:.3f}" if "Flare Threshold" in label_text else f"{slider.value() / 10:.2f}"))

        slider_layout.addWidget(min_label)
        slider_layout.addWidget(slider)
        slider_layout.addWidget(max_label)
        slider_layout.addWidget(current_value_label)

        self.form_layout.addRow(QLabel(label_text), slider_layout)

        return slider, current_value_label

    def reset_to_default(self):
        self.sharpness_low_slider.setValue(3)
        self.sharpness_high_slider.setValue(40)
        self.saturation_low_slider.setValue(5)
        self.brightness_low_slider.setValue(2)
        self.brightness_high_slider.setValue(20)
        self.flare_threshold_slider.setValue(10)

    def load_config(self):
        try:
            tree = ET.parse(resource_path('./config/config.xml'))
            root = tree.getroot()

            self.sharpness_low_slider.setValue(int(float(root.find('sharpness/low_threshold').text) * 10))
            self.sharpness_high_slider.setValue(int(float(root.find('sharpness/high_threshold').text) * 10))
            self.saturation_low_slider.setValue(int(float(root.find('saturation/low_threshold').text) * 10))
            self.brightness_low_slider.setValue(int(float(root.find('brightness/low_threshold').text) * 10))
            self.brightness_high_slider.setValue(int(float(root.find('brightness/high_threshold').text) * 10))
            self.flare_threshold_slider.setValue(int(float(root.find('flare/threshold').text) * 1000))
        except FileNotFoundError:
            logger.error("Configuration file not found. Please ensure the config.xml file exists. - config_window.py")
            QMessageBox.critical(self, "Error",
                                 "Configuration file not found. Please ensure the config.xml file exists.")
        except ET.ParseError:
            logger.error("Error parsing configuration file. Please check the XML format. - config_window.py")
            QMessageBox.critical(self, "Error", "Error parsing configuration file. Please check the XML format.")
        except Exception as e:
            logger.error(f"An unexpected error occurred while loading config: {str(e)} - config_window.py")
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {str(e)}")

    def save_config(self):
        try:
            tree = ET.parse(resource_path('./config/config.xml'))
            root = tree.getroot()

            root.find('sharpness/low_threshold').text = str(self.sharpness_low_slider.value() / 10)
            root.find('sharpness/high_threshold').text = str(self.sharpness_high_slider.value() / 10)
            root.find('saturation/low_threshold').text = str(self.saturation_low_slider.value() / 10)
            root.find('brightness/low_threshold').text = str(self.brightness_low_slider.value() / 10)
            root.find('brightness/high_threshold').text = str(self.brightness_high_slider.value() / 10)
            root.find('flare/threshold').text = str(self.flare_threshold_slider.value() / 1000)

            tree.write(resource_path('./config/config.xml'))
            QMessageBox.information(self, "Success", "Configuration saved successfully.")
            self.accept()
        except FileNotFoundError:
            logger.error("Configuration file not found. Please ensure the config.xml file exists. - config_window.py")
            QMessageBox.critical(self, "Error",
                                 "Configuration file not found. Please ensure the config.xml file exists.")
        except ET.ParseError:
            logger.error("Error parsing configuration file. Please check the XML format. - config_window.py")
            QMessageBox.critical(self, "Error", "Error parsing configuration file. Please check the XML format.")
        except Exception as e:
            logger.error(f"An unexpected error occurred while saving config: {str(e)} - config_window.py")
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {str(e)}")
