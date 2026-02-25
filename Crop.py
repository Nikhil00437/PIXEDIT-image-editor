from PyQt5.QtWidgets import QLabel, QSizePolicy
from PyQt5.QtCore import Qt, QRect, QSize, QPoint
from PyQt5.QtGui import QPainter, QPen, QColor, QCursor, QPainterPath, QFont

class CropLabel(QLabel):
    MIN_CROP = 10  # minimum crop dimension in pixels

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setObjectName("image_label")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.origin = QPoint()
        self.crop_rect = None
        self.cropping_mode = False
        self._drawing = False
        self._live_rect = QRect()   # rect being drawn live (before release)

    # public API
    def enable_crop(self, enabled: bool):
        self.cropping_mode = enabled
        self.crop_rect = None
        self._drawing = False
        self._live_rect = QRect()
        self.update()
        if enabled:
            self.setCursor(QCursor(Qt.CrossCursor))
        else:
            self.unsetCursor()

    # mouse events 
    def mousePressEvent(self, event):
        if self.cropping_mode and event.button() == Qt.LeftButton:
            self.origin = event.pos()
            self._drawing = True
            self.crop_rect = None
            self._live_rect = QRect(self.origin, QSize())
            self.update()

    def mouseMoveEvent(self, event):
        if self.cropping_mode and self._drawing:
            end = event.pos()
            # Shift → constrain to square
            if event.modifiers() & Qt.ShiftModifier:
                dx = end.x() - self.origin.x()
                dy = end.y() - self.origin.y()
                side = min(abs(dx), abs(dy))
                end = QPoint(
                    self.origin.x() + (side if dx >= 0 else -side),
                    self.origin.y() + (side if dy >= 0 else -side),
                )

            self._live_rect = QRect(self.origin, end).normalized()
            self.update()

    def mouseReleaseEvent(self, event):
        if self.cropping_mode and event.button() == Qt.LeftButton and self._drawing:
            self._drawing = False
            rect = self._live_rect
            if rect.width() < self.MIN_CROP or rect.height() < self.MIN_CROP:
                self._live_rect = QRect()
                self.crop_rect = None
            else:
                self.crop_rect = rect

            self.update()

    # painting
    def paintEvent(self, event):
        # Let QLabel draw the image first
        super().paintEvent(event)
        if not self.cropping_mode: return
        r = self._live_rect
        if r.isNull() or r.isEmpty(): return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        W, H = self.width(), self.height()
        # dim outside the crop rect
        dim = QColor(0, 0, 0, 130)
        painter.fillRect(0,          0,          W,          r.top(),           dim)
        painter.fillRect(0,          r.bottom(), W,          H - r.bottom(),    dim)
        painter.fillRect(0,          r.top(),    r.left(),   r.height(),        dim)
        painter.fillRect(r.right(),  r.top(),    W - r.right(), r.height(),     dim)
        # crop border
        painter.setPen(QPen(QColor(255, 255, 255, 220), 1.5, Qt.SolidLine))
        painter.drawRect(r)
        # rule-of-thirds grid
        if r.width() > 30 and r.height() > 30:
            painter.setPen(QPen(QColor(255, 255, 255, 60), 0.8, Qt.DashLine))
            x1 = r.left() + r.width() // 3
            x2 = r.left() + 2 * r.width() // 3
            y1 = r.top()  + r.height() // 3
            y2 = r.top()  + 2 * r.height() // 3
            painter.drawLine(x1, r.top(),    x1, r.bottom())
            painter.drawLine(x2, r.top(),    x2, r.bottom())
            painter.drawLine(r.left(),  y1,  r.right(), y1)
            painter.drawLine(r.left(),  y2,  r.right(), y2)
        # corner L-handles
        HL = 12
        painter.setPen(QPen(QColor(255, 255, 255, 255), 2.5, Qt.SolidLine))
        for cx, cy, hx, vy in [
            (r.left(),   r.top(),     1,  1),
            (r.right(),  r.top(),    -1,  1),
            (r.left(),   r.bottom(),  1, -1),
            (r.right(),  r.bottom(), -1, -1),
        ]:
            painter.drawLine(cx, cy, cx + hx * HL, cy)
            painter.drawLine(cx, cy, cx, cy + vy * HL)
        # mid-edge handles
        painter.setPen(QPen(QColor(255, 255, 255, 180), 2, Qt.SolidLine))
        half = HL // 2
        mx = r.left() + r.width() // 2
        my = r.top()  + r.height() // 2
        painter.drawLine(mx - half, r.top(),    mx + half, r.top())
        painter.drawLine(mx - half, r.bottom(), mx + half, r.bottom())
        painter.drawLine(r.left(),  my - half,  r.left(),  my + half)
        painter.drawLine(r.right(), my - half,  r.right(), my + half)
        # dimension badge
        if r.width() > 60 and r.height() > 30:
            badge_text = f"{r.width()} × {r.height()}"
            font = QFont("Courier New", 8, QFont.Bold)
            painter.setFont(font)
            fm = painter.fontMetrics()
            bw = fm.horizontalAdvance(badge_text) + 12
            bh = fm.height() + 6
            bx = r.left() + (r.width() - bw) // 2
            by = r.bottom() + 6
            if by + bh > H:
                by = r.top() - bh - 6

            path = QPainterPath()
            path.addRoundedRect(bx, by, bw, bh, 3, 3)
            painter.fillPath(path, QColor(0, 0, 0, 160))
            painter.setPen(QPen(QColor(255, 255, 255, 220)))
            painter.drawText(bx, by, bw, bh, Qt.AlignCenter, badge_text)

        painter.end()
