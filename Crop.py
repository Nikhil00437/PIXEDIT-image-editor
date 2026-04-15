from PyQt5.QtWidgets import QLabel, QSizePolicy, QScrollArea
from PyQt5.QtCore import Qt, QRect, QSize, QPoint, QPointF
from PyQt5.QtGui import QPainter, QPen, QColor, QCursor, QPainterPath, QFont, QPixmap, QImage, QPolygon, QBrush, QPainterPath


class CropLabel(QScrollArea):
    """
    A scrollable image label with zoom and pan support.
    Features:
    - Zoom in/out (buttons or wheel)
    - Pan (mouse drag when zoomed)
    - Fit to window toggle
    - Crop overlay support
    """

    MIN_CROP = 10  # minimum crop dimension in pixels

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setObjectName("image_label")
        self.setWidgetResizable(False)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Internal image label
        self._image_label = _InternalImageLabel(self)
        self.setWidget(self._image_label)

        # Zoom settings
        self._zoom_factor = 1.0  # 1.0 = 100%
        self._min_zoom = 0.25  # 25%
        self._max_zoom = 4.0  # 400%
        self._zoom_step = 0.25  # 25% per step

        # Fit to window
        self._fit_to_window = True

        # Crop support
        self.crop_rect = None
        self.cropping_mode = False

        # Current image
        self._current_pixmap = None

        # Mouse tracking for panning
        self._panning = False
        self._last_pan_pos = QPoint()

        self.setMouseTracking(True)

    # ==================== IMAGE DISPLAY ====================
    def setPixmap(self, pixmap: QPixmap):
        """Set the image to display."""
        self._current_pixmap = pixmap
        self._image_label.setPixmap(pixmap)
        self._update_image_size()
        if self._fit_to_window:
            self.fit_to_window()

    def _update_image_size(self):
        """Update the internal label size based on zoom."""
        if self._current_pixmap and not self._fit_to_window:
            w = int(self._current_pixmap.width() * self._zoom_factor)
            h = int(self._current_pixmap.height() * self._zoom_factor)
            self._image_label.setFixedSize(w, h)
        elif self._current_pixmap:
            self._image_label.setFixedSize(self._current_pixmap.size())

    # ==================== ZOOM CONTROLS ====================
    def zoom_in(self):
        """Zoom in by one step."""
        if self._zoom_factor < self._max_zoom:
            new_zoom = min(self._zoom_factor + self._zoom_step, self._max_zoom)
            self.set_zoom(new_zoom)

    def zoom_out(self):
        """Zoom out by one step."""
        if self._zoom_factor > self._min_zoom:
            new_zoom = max(self._zoom_factor - self._zoom_step, self._min_zoom)
            self.set_zoom(new_zoom)

    def set_zoom(self, factor: float):
        """Set zoom to a specific factor."""
        self._fit_to_window = False
        self._zoom_factor = max(self._min_zoom, min(factor, self._max_zoom))
        if self._current_pixmap:
            self._update_image_size()
        return self._zoom_factor

    def get_zoom(self) -> float:
        """Get current zoom factor."""
        return self._zoom_factor

    def zoom_to_fit(self) -> float:
        """Calculate zoom to fit the viewport."""
        if not self._current_pixmap:
            return 1.0

        viewport_w = self.viewport().width()
        viewport_h = self.viewport().height()

        if viewport_w <= 0 or viewport_h <= 0:
            return 1.0

        pix_w = self._current_pixmap.width()
        pix_h = self._current_pixmap.height()

        if pix_w <= 0 or pix_h <= 0:
            return 1.0

        scale_w = viewport_w / pix_w
        scale_h = viewport_h / pix_h

        return min(scale_w, scale_h, 1.0)

    def fit_to_window(self):
        """Fit image to window."""
        if self._current_pixmap:
            self._fit_to_window = True
            target_zoom = self.zoom_to_fit()
            self.set_zoom(target_zoom)
            self._center_image()

    def zoom_actual_size(self):
        """Show actual size (100%)."""
        self._fit_to_window = False
        self.set_zoom(1.0)
        self._center_image()

    def toggle_fit_actual(self):
        """Toggle between fit and actual size."""
        if self._fit_to_window:
            self._fit_to_window = False
            self.zoom_actual_size()
        else:
            self.fit_to_window()

    def _center_image(self):
        """Center the image in the viewport."""
        if not self._current_pixmap:
            return

        self.horizontalScrollBar().setValue(
            (self.horizontalScrollBar().maximum() + self.horizontalScrollBar().minimum()) // 2
        )
        self.verticalScrollBar().setValue(
            (self.verticalScrollBar().maximum() + self.verticalScrollBar().minimum()) // 2
        )

    # ==================== MOUSE EVENTS ====================
    def wheelEvent(self, event):
        """Handle mouse wheel for zooming."""
        if event.angleDelta().y() > 0:
            self.zoom_in()
        else:
            self.zoom_out()
        event.accept()

    def mousePressEvent(self, event):
        """Handle mouse press for panning, cropping, or drawing."""
        if event.button() == Qt.LeftButton:
            pos = event.pos()
            if self.cropping_mode:
                self._image_label.start_crop(pos)
            elif self._image_label._drawing_mode:
                self._image_label.start_drawing(pos)
            else:
                # Start panning if zoomed beyond fit
                if self._zoom_factor > 1.0:
                    self._panning = True
                    self._last_pan_pos = pos
                    self.setCursor(Qt.ClosedHandCursor)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Handle mouse move for panning, cropping, or drawing."""
        pos = event.pos()
        if self.cropping_mode:
            self._image_label.update_crop(pos)
        elif self._image_label._drawing_mode:
            self._image_label.update_drawing(pos)
        elif self._panning:
            # Pan the image
            delta = pos - self._last_pan_pos
            self._last_pan_pos = pos

            h_bar = self.horizontalScrollBar()
            v_bar = self.verticalScrollBar()

            h_bar.setValue(h_bar.value() - delta.x())
            v_bar.setValue(v_bar.value() - delta.y())

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Handle mouse release."""
        if event.button() == Qt.LeftButton:
            pos = event.pos()
            if self.cropping_mode:
                self._image_label.end_crop(pos)
            elif self._image_label._drawing_mode:
                self._image_label.end_drawing(pos)
            self._panning = False
            self.setCursor(Qt.ArrowCursor)
        super().mouseReleaseEvent(event)

    # ==================== CROP METHODS ====================
    def enable_crop(self, enabled: bool):
        """Enable or disable crop mode."""
        self.cropping_mode = enabled
        self.crop_rect = None
        self._image_label.set_crop_mode(enabled)
        if enabled:
            self.setCursor(Qt.CrossCursor)
            self._image_label.set_drawing_mode(False)
        else:
            self.setCursor(Qt.ArrowCursor)

    def get_crop_rect(self):
        """Get crop rectangle in image coordinates."""
        label_rect = self._image_label.crop_rect
        if not label_rect or label_rect.isNull():
            return None

        scale = 1.0 / self._zoom_factor if self._zoom_factor > 0 else 1.0

        x1 = int(label_rect.left() * scale)
        y1 = int(label_rect.top() * scale)
        x2 = int(label_rect.right() * scale)
        y2 = int(label_rect.bottom() * scale)

        return QRect(x1, y1, x2 - x1, y2 - y1)

    # ==================== DRAWING METHODS ====================
    def enable_drawing(self, enabled: bool, tool: str = "brush"):
        """Enable or disable drawing mode."""
        self._image_label.set_drawing_mode(enabled, tool)
        if enabled:
            self.setCursor(Qt.CrossCursor)
            self._image_label.set_crop_mode(False)
        else:
            self.setCursor(Qt.ArrowCursor)

    def set_drawing_tool(self, tool: str):
        """Set the drawing tool."""
        self._image_label.set_drawing_tool(tool)

    def set_brush_size(self, size: int):
        """Set brush size."""
        self._image_label.set_brush_size(size)

    def set_brush_color(self, color: QColor):
        """Set brush color."""
        self._image_label.set_brush_color(color)

    def clear_drawings(self):
        """Clear all drawings."""
        self._image_label.clear_drawings()

    def get_drawing_path(self) -> list:
        """Get all drawings for rasterization."""
        return self._image_label.get_drawing_path()


class _InternalImageLabel(QLabel):
    """Internal label for image display with crop and drawing overlay."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setScaledContents(False)

        # Crop overlay
        self.crop_rect = None
        self._crop_origin = QPoint()
        self._crop_mode = False
        self._drawing = False
        self._live_rect = QRect()

        # Drawing mode
        self._drawing_mode = False
        self._drawing_tool = "brush"  # brush, eraser, line, arrow, rectangle, circle
        self._brush_size = 5
        self._brush_color = QColor(255, 255, 255)
        self._drawing_points = []
        self._current_shape = None  # for shapes
        self._shape_start = QPoint()

    def set_drawing_mode(self, enabled: bool, tool: str = "brush"):
        """Enable or disable drawing mode."""
        self._drawing_mode = enabled
        if not enabled:
            self._drawing_points = []
            self._current_shape = None

    def set_drawing_tool(self, tool: str):
        """Set the drawing tool."""
        self._drawing_tool = tool

    def set_brush_size(self, size: int):
        """Set brush size."""
        self._brush_size = max(1, min(50, size))

    def set_brush_color(self, color: QColor):
        """Set brush color."""
        self._brush_color = color

    def clear_drawings(self):
        """Clear all drawings."""
        self._drawing_points = []
        self._current_shape = None
        self.update()

    def set_crop_mode(self, enabled: bool):
        """Enable or disable crop mode."""
        self._crop_mode = enabled
        self.crop_rect = None
        self._drawing = False
        self._live_rect = QRect()
        self.update()

    def start_crop(self, pos: QPoint):
        """Start cropping at position."""
        if self._crop_mode:
            self._crop_origin = pos
            self._drawing = True
            self.crop_rect = None
            self._live_rect = QRect(pos.x(), pos.y(), 0, 0)
            self.update()

    def update_crop(self, pos: QPoint):
        """Update crop rectangle during drag."""
        if self._crop_mode and self._drawing:
            self._live_rect = QRect(
                self._crop_origin.x(),
                self._crop_origin.y(),
                pos.x() - self._crop_origin.x(),
                pos.y() - self._crop_origin.y()
            ).normalized()
            self.update()

    def end_crop(self, pos: QPoint):
        """End cropping."""
        if self._crop_mode and self._drawing:
            self._drawing = False
            self._live_rect = QRect(
                self._crop_origin.x(),
                self._crop_origin.y(),
                pos.x() - self._crop_origin.x(),
                pos.y() - self._crop_origin.y()
            ).normalized()
            if self._live_rect.width() >= CropLabel.MIN_CROP and self._live_rect.height() >= CropLabel.MIN_CROP:
                self.crop_rect = self._live_rect
            else:
                self.crop_rect = None
            self.update()

    # Drawing mouse handlers
    def start_drawing(self, pos: QPoint):
        """Start drawing at position."""
        if self._drawing_mode:
            if self._drawing_tool in ("line", "arrow", "rectangle", "circle"):
                self._shape_start = pos
                self._current_shape = pos
            else:
                self._drawing_points = [pos]

    def update_drawing(self, pos: QPoint):
        """Update drawing during drag."""
        if self._drawing_mode:
            if self._drawing_tool in ("line", "arrow", "rectangle", "circle"):
                self._current_shape = pos
            else:
                self._drawing_points.append(pos)
            self.update()

    def end_drawing(self, pos: QPoint):
        """End drawing."""
        if self._drawing_mode:
            if self._drawing_tool in ("line", "arrow", "rectangle", "circle"):
                self._current_shape = pos
                # Store shape as (tool, start, end)
                self._drawing_points.append((self._drawing_tool, self._shape_start, pos))
            else:
                # Store path as list of points
                self._drawing_points.append(tuple(self._drawing_points))
                self._drawing_points = []  # Reset current stroke
            self.update()

    def get_drawing_path(self) -> list:
        """Get all drawings as list for rasterization."""
        result = []
        for item in self._drawing_points:
            if isinstance(item, tuple) and len(item) == 3:
                # It's a shape
                result.append(item)
            elif isinstance(item, list):
                # It's a stroke
                result.append(("stroke", item))
        return result

    def paintEvent(self, event):
        """Paint the image, crop overlay, and drawings."""
        super().paintEvent(event)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw saved drawings
        for item in self._drawing_points:
            if isinstance(item, tuple) and len(item) == 3:
                tool, start, end = item
                self._draw_shape(painter, tool, start, end)
            elif isinstance(item, list) and len(item) > 1:
                self._draw_stroke(painter, item)
            elif isinstance(item, tuple) and item[0] == "stroke":
                self._draw_stroke(painter, item[1])

        # Draw current stroke/shape
        if self._drawing_mode:
            if self._drawing_tool in ("line", "arrow", "rectangle", "circle") and self._current_shape:
                self._draw_shape(painter, self._drawing_tool, self._shape_start, self._current_shape)
            elif len(self._drawing_points) > 0:
                self._draw_stroke(painter, self._drawing_points)

        # Draw crop overlay if active
        if self._crop_mode and not self._live_rect.isNull():
            self._draw_crop_overlay(painter, self._live_rect)

        painter.end()

    def _draw_stroke(self, painter, points: list):
        """Draw a freehand stroke."""
        if len(points) < 2:
            return

        pen = QPen(self._brush_color, self._brush_size, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(pen)

        path = QPainterPath()
        path.moveTo(points[0])
        for pt in points[1:]:
            path.lineTo(pt)
        painter.drawPath(path)

    def _draw_shape(self, painter, tool: str, start: QPoint, end: QPoint):
        """Draw a shape (line, arrow, rectangle, circle)."""
        pen = QPen(self._brush_color, self._brush_size, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(pen)

        if tool == "line":
            painter.drawLine(start, end)
        elif tool == "arrow":
            painter.drawLine(start, end)
            # Draw arrowhead
            angle = (end - start).angle()
            arrow_size = 15
            arrow_p1 = end - QPointF.fromPolar(arrow_size, angle - 30).toPoint()
            arrow_p2 = end - QPointF.fromPolar(arrow_size, angle + 30).toPoint()
            painter.drawLine(end, arrow_p1)
            painter.drawLine(end, arrow_p2)
        elif tool == "rectangle":
            painter.drawRect(QRect(start, end).normalized())
        elif tool == "circle":
            painter.drawEllipse(QRect(start, end).normalized())

    def _draw_crop_overlay(self, painter, r: QRect):
        """Draw crop overlay."""
        if r.isNull() or r.isEmpty():
            return

        W, H = self.width(), self.height()

        # Dim outside the crop rect
        dim = QColor(0, 0, 0, 130)
        painter.fillRect(0, 0, W, r.top(), dim)
        painter.fillRect(0, r.bottom(), W, H - r.bottom(), dim)
        painter.fillRect(0, r.top(), r.left(), r.height(), dim)
        painter.fillRect(r.right(), r.top(), W - r.right(), r.height(), dim)

        # Crop border
        painter.setPen(QPen(QColor(255, 255, 255, 220), 1.5, Qt.SolidLine))
        painter.drawRect(r)

        # Rule-of-thirds grid
        if r.width() > 30 and r.height() > 30:
            painter.setPen(QPen(QColor(255, 255, 255, 60), 0.8, Qt.DashLine))
            x1 = r.left() + r.width() // 3
            x2 = r.left() + 2 * r.width() // 3
            y1 = r.top() + r.height() // 3
            y2 = r.top() + 2 * r.height() // 3
            painter.drawLine(x1, r.top(), x1, r.bottom())
            painter.drawLine(x2, r.top(), r.right(), y2)
            painter.drawLine(r.left(), y1, r.right(), y1)
            painter.drawLine(r.left(), y2, r.right(), y2)

        # Corner L-handles
        HL = 12
        painter.setPen(QPen(QColor(255, 255, 255, 255), 2.5, Qt.SolidLine))
        for cx, cy, hx, vy in [
            (r.left(), r.top(), 1, 1),
            (r.right(), r.top(), -1, 1),
            (r.left(), r.bottom(), 1, -1),
            (r.right(), r.bottom(), -1, -1),
        ]:
            painter.drawLine(cx, cy, cx + hx * HL, cy)
            painter.drawLine(cx, cy, cx, cy + vy * HL)

        # Dimension badge
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
