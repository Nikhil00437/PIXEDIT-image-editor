from PyQt5.QtWidgets import QApplication, QRubberBand, QWidget, QHBoxLayout, QSlider, QFileDialog, QGroupBox, QListWidget, QLabel, QVBoxLayout, QPushButton, QComboBox
from PyQt5.QtCore import Qt, QRect, QSize, QPoint

class CropLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("border: 1px solid black;")
        self.rubber_band = QRubberBand(QRubberBand.Rectangle, self)
        self.origin = QPoint()
        self.crop_rect = None
        self.cropping_mode = False

    def enable_crop(self, enabled):
        self.cropping_mode = enabled
        self.crop_rect = None
        if not enabled:
            self.rubber_band.hide()

    def mousePressEvent(self, event):
        if self.cropping_mode and event.button() == Qt.LeftButton:
            self.origin = event.pos()
            self.rubber_band.setGeometry(QRect(self.origin, QSize()))
            self.rubber_band.show()

    def mouseMoveEvent(self, event):
        if self.cropping_mode and not self.origin.isNull():
            self.rubber_band.setGeometry(
                QRect(self.origin, event.pos()).normalized()
            )

    def mouseReleaseEvent(self, event):
        if self.cropping_mode and event.button() == Qt.LeftButton:
            self.crop_rect = QRect(self.origin, event.pos()).normalized()
            self.rubber_band.hide()