from PyQt5.QtWidgets import QFileDialog, QShortcut, QDialog, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QLabel, QKeySequenceEdit, QHeaderView, QMessageBox, QComboBox, QSlider, QSpinBox, QCheckBox, QLineEdit, QTextEdit, QColorDialog, QFontComboBox, QGroupBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QKeySequence, QImage, QColor, QPainter, QFont
import os, tempfile, json, math
from PIL import Image, ImageFilter, ImageEnhance, ImageOps, ImageChops
from collections import deque

# Use crop2 instead of Crop
import crop2

# Try to import ImageGenerator (optional AI feature)
try:
    from generate_image import ImageGenerator
except (ImportError, OSError):
    # Create a dummy if torch is not available
    class ImageGenerator:
        def __init__(self):
            pass
        def generate(self, prompt, path):
            print("AI generation requires torch. Install with: pip install torch diffusers")

# Default shortcuts
DEFAULT_SHORTCUTS = {
    "Open Folder":      "Ctrl+O",
    "Save":             "Ctrl+S",
    "Undo":             "Ctrl+Z",
    "Reset":            "Ctrl+R",
    "Left Rotate":      "Left",
    "Right Rotate":     "Right",
    "Flip Horizontal":  "H",
    "Flip Vertical":    "V",
    "Grayscale":        "G",
    "Color":            "C",
    "Blur":             "B",
    "Sharpen":          "Shift+S",
    "Brightness":       "Ctrl+B",
    "Contrast":         "Ctrl+T",
    "Sepia":            "Ctrl+E",
    "Invert":           "Ctrl+I",
    "Solarize":         "Shift+O",
    "Emboss":           "Shift+M",
    "Start Crop":       "Ctrl+X",
    "Confirm Crop":     "Return",
}

SETTINGS_FILE = "settings.json"

def load_shortcuts():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                data = json.load(f)
                saved = data.get("shortcuts", {})
                merged = DEFAULT_SHORTCUTS.copy()
                merged.update(saved)
                return merged
        except Exception: pass
    return DEFAULT_SHORTCUTS.copy()

def save_shortcuts_to_file(shortcuts):
    try:
        data = {}
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r") as f:
                data = json.load(f)
        data["shortcuts"] = shortcuts
        with open(SETTINGS_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Failed to save shortcuts: {e}")

def load_theme_from_file():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                data = json.load(f)
                return data.get("theme", None)
        except Exception: pass
    return None

def save_theme_to_file(theme_name):
    try:
        data = {}
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r") as f:
                data = json.load(f)
        data["theme"] = theme_name
        with open(SETTINGS_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Failed to save theme: {e}")

# Settings Window — frameless so it inherits the app stylesheet fully
class SettingsWindow(QDialog):
    def __init__(self, editor, themes, current_theme, apply_theme_fn, parent=None):
        super().__init__(parent)
        self.editor = editor
        self.themes = themes
        self.current_theme = current_theme
        self.apply_theme_fn = apply_theme_fn

        # Frameless + modal so it looks fully themed
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setModal(True)
        self.setMinimumSize(560, 520)
        self._drag_pos = None

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Custom title bar
        self._titlebar = self._build_titlebar()
        root.addWidget(self._titlebar)

        # Body
        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(12, 10, 12, 12)
        body_layout.setSpacing(8)

        tabs = QTabWidget()
        tabs.addTab(self._build_shortcuts_tab(), "⌨  Shortcuts")
        tabs.addTab(self._build_theme_tab(), "🎨  Theme")
        body_layout.addWidget(tabs)
        root.addWidget(body)

    def _build_titlebar(self):
        bar = QWidget()
        bar.setObjectName("titlebar")
        bar.setFixedHeight(40)

        layout = QHBoxLayout(bar)
        layout.setContentsMargins(14, 0, 0, 0)
        layout.setSpacing(0)

        title = QLabel("SETTINGS")
        title.setObjectName("app_title")
        layout.addWidget(title)
        layout.addStretch()

        btn_close = QPushButton("✕")
        btn_close.setObjectName("win_close")
        btn_close.setToolTip("Close")
        btn_close.clicked.connect(self.close)
        layout.addWidget(btn_close)
        return bar

    # Drag the frameless dialog
    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton and e.y() <= 40:
            self._drag_pos = e.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, e):
        if e.buttons() == Qt.LeftButton and self._drag_pos:
            self.move(e.globalPos() - self._drag_pos)

    def mouseReleaseEvent(self, e):
        self._drag_pos = None

    # Shortcuts tab
    def _build_shortcuts_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(8)

        info = QLabel("Click a shortcut cell and press your desired key combination.")
        info.setStyleSheet("font-size: 10px; color: #888;")
        layout.addWidget(info)

        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Action", "Shortcut"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.table.setColumnWidth(1, 200)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.verticalHeader().setVisible(False)

        self._shortcuts = self.editor.current_shortcuts.copy()
        self._seq_edits = {}

        for row, (action, key) in enumerate(DEFAULT_SHORTCUTS.items()):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(action))
            seq_edit = QKeySequenceEdit(QKeySequence(self._shortcuts.get(action, key)))
            seq_edit.setFixedHeight(28)
            self.table.setCellWidget(row, 1, seq_edit)
            self._seq_edits[action] = seq_edit

        layout.addWidget(self.table)

        btn_row = QHBoxLayout()
        save_btn = QPushButton("✔  Save Shortcuts")
        save_btn.clicked.connect(self._save_shortcuts)
        reset_btn = QPushButton("⟳  Reset to Defaults")
        reset_btn.clicked.connect(self._reset_shortcuts)
        btn_row.addWidget(reset_btn)
        btn_row.addStretch()
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)
        return w

    def _save_shortcuts(self):
        seen = {}
        for action, seq_edit in self._seq_edits.items():
            key = seq_edit.keySequence().toString()
            if not key: continue
            if key in seen:
                QMessageBox.warning(self, "Conflict",
                    f"'{key}' is assigned to both '{seen[key]}' and '{action}'.\nPlease resolve before saving.")
                return
            seen[key] = action

        new_shortcuts = {action: seq_edit.keySequence().toString()
                         for action, seq_edit in self._seq_edits.items()}
        self.editor.current_shortcuts = new_shortcuts
        self.editor.apply_shortcuts()
        save_shortcuts_to_file(new_shortcuts)
        QMessageBox.information(self, "Saved", "Shortcuts saved successfully.")

    def _reset_shortcuts(self):
        self.editor.current_shortcuts = DEFAULT_SHORTCUTS.copy()
        for action, seq_edit in self._seq_edits.items():
            seq_edit.setKeySequence(QKeySequence(DEFAULT_SHORTCUTS[action]))
        self.editor.apply_shortcuts()
        save_shortcuts_to_file(DEFAULT_SHORTCUTS.copy())

    # Theme tab
    def _build_theme_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        lbl = QLabel("Select Theme")
        lbl.setStyleSheet("font-size: 11px; font-weight: bold; letter-spacing: 2px;")
        layout.addWidget(lbl)

        self.theme_combo = QComboBox()
        self.theme_combo.setObjectName("theme_combo")
        for name in self.themes:
            self.theme_combo.addItem(name)
        self.theme_combo.setCurrentText(self.current_theme[0])
        layout.addWidget(self.theme_combo)

        apply_btn = QPushButton("Apply Theme")
        apply_btn.clicked.connect(self._apply_theme)
        layout.addWidget(apply_btn)
        layout.addStretch()
        return w

    def _apply_theme(self):
        name = self.theme_combo.currentText()
        self.current_theme[0] = name
        self.apply_theme_fn(name)
        save_theme_to_file(name)

# Image Editor
class ImageEditor:
    def __init__(self, widget, image_label, slider, slider2, preview=None,
                 left_rotate=None, right_rotate=None, flip_horizontal=None, flip_vertical=None,
                 grayscale=None, color=None, blur=None, sharpen=None, brightness=None, contrast=None,
                 sepia=None, solarize=None, invert=None, vignette=None, undo=None, reset=None,
                 crop_start=None, crop_confirm=None, save=None, main_window=None,
                 themes=None, current_theme=None, apply_theme_fn=None,
                 # New parameters
                 slider_saturation=None, slider_hue=None, slider_temperature=None,
                 zoom_slider=None, fit_button=None, info_label=None):

        self.widget          = widget
        self.image_label     = image_label
        self.slider          = slider
        self.slider2         = slider2
        self.preview         = preview
        self.left_rotate     = left_rotate
        self.right_rotate    = right_rotate
        self.flip_horizontal = flip_horizontal
        self.flip_vertical   = flip_vertical
        self.grayscale       = grayscale
        self.color           = color
        self.blur            = blur
        self.sharpen         = sharpen
        self.brightness      = brightness
        self.contrast        = contrast
        self.sepia_          = sepia
        self.solarize_       = solarize
        self.invert_         = invert
        self.vignette_       = vignette
        self.undo            = undo
        self.reset           = reset
        self.crop_start      = crop_start
        self.crop_confirm    = crop_confirm
        self.save            = save
        self.main_window     = main_window
        self.themes          = themes or {}
        self.current_theme   = current_theme or [""]
        self.apply_theme_fn  = apply_theme_fn or (lambda x: None)

        # New sliders and controls
        self.slider_saturation = slider_saturation
        self.slider_hue = slider_hue
        self.slider_temperature = slider_temperature
        self.zoom_slider = zoom_slider
        self.fit_button = fit_button
        self.info_label = info_label

        self.original        = None
        self.edited          = None
        self.image_path      = None
        self.last_color      = None
        self.history         = deque(maxlen=20)
        self.file_location   = ""
        self.active_shortcuts = []
        self.current_shortcuts = load_shortcuts()
        self.image_gen       = ImageGenerator()
        self.path            = None
        self.image           = None

    # Shortcut management
    def _action_map(self):
        return {
            "Open Folder":      self.getfiles,
            "Save":             self.save_image,
            "Undo":             self.undo_,
            "Reset":            self.reset_,
            "Left Rotate":      self.left_rotate_filter,
            "Right Rotate":     self.right_rotate_filter,
            "Flip Horizontal":  self.flip_horizontal_filter,
            "Flip Vertical":    self.flip_vertical_filter,
            "Grayscale":        self.grayscale_filter,
            "Color":            self.color_filter,
            "Blur":             self.blur_filter,
            "Sharpen":          self.sharpen_filter,
            "Brightness":       self.brightness_filter,
            "Contrast":         self.contrast_filter,
            "Sepia":            self.sepia,
            "Invert":           self.invert,
            "Solarize":         self.solarize,
            "Vignette":         self.vignette,
            "Start Crop":       self.start_crop,
            "Confirm Crop":     self.confirm_crop,
        }

    def apply_shortcuts(self):
        for s in self.active_shortcuts:
            s.setEnabled(False)
            s.deleteLater()
        self.active_shortcuts.clear()

        action_map = self._action_map()
        for action, key in self.current_shortcuts.items():
            if not key or action not in action_map: continue
            sc = QShortcut(QKeySequence(key), self.main_window)
            sc.activated.connect(action_map[action])
            self.active_shortcuts.append(sc)

    def setup_shortcuts(self):
        self.apply_shortcuts()

    def open_settings(self):
        dlg = SettingsWindow(self, self.themes, self.current_theme, self.apply_theme_fn, self.main_window)
        dlg.exec_()

    # History
    def history_append(self):
        if self._guard(): return
        self.history.append(self.edited.copy())

    # File helpers
    def filter_image(self, files, extension):
        results = []
        for file in files:
            for ext in extension:
                if file.lower().endswith(ext):
                    results.append(file)
                    break
        return results

    def getfiles(self):
        self.file_location = QFileDialog.getExistingDirectory()
        if not self.file_location: return
        extensions = [".jpg", ".jpeg", ".png"]
        filenames = self.filter_image(os.listdir(self.file_location), extensions)
        self.widget.clear()
        for filename in filenames:
            self.widget.addItem(filename)

    def load_image(self):
        if self.widget.currentItem() is None: return
        selected_image = self.widget.currentItem().text()
        self.image_path = os.path.join(self.file_location, selected_image)
        self.original   = Image.open(self.image_path).copy()
        self.edited     = self.original.copy()
        self.last_color = None
        self.slider.blockSignals(True)
        self.slider2.blockSignals(True)
        self.slider.setValue(0)
        self.slider2.setValue(0)
        self.slider.blockSignals(False)
        self.slider2.blockSignals(False)
        self._display_pil(self.edited)

# Display
    def _display_pil(self, pil_image):
        # Convert PIL to QPixmap for display
        img = pil_image.copy()
        if img.mode == 'L':
            img = img.convert('RGB')
        elif img.mode == 'P':
            img = img.convert('RGBA')
        elif img.mode not in ('RGB', 'RGBA'):
            img = img.convert('RGB')

        # Save to temp file and load as pixmap (more compatible)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            tmp_path = tmp.name
        img.convert('RGB').save(tmp_path)
        self.image_label.hide()
        pixmap = QPixmap(tmp_path)

        # Check if it's the new CropLabel (has setPixmap method from QScrollArea)
        if hasattr(self.image_label, 'setPixmap'):
            # New CropLabel with zoom support
            self.image_label.setPixmap(pixmap)
            self.image_label.fit_to_window()
        else:
            # Old CropLabel (legacy)
            w, h = self.image_label.width(), self.image_label.height()
            pixmap_scaled = pixmap.scaled(w, h, Qt.KeepAspectRatio)
            self.image_label.setPixmap(pixmap_scaled)

        self.image_label.show()
        os.unlink(tmp_path)

        # Enable buttons
        for btn in [self.preview, self.left_rotate, self.right_rotate,
                    self.flip_horizontal, self.flip_vertical, self.grayscale,
                    self.color, self.blur, self.sharpen, self.brightness,
                    self.contrast, self.sepia_, self.solarize_, self.invert_,
                    self.vignette_, self.undo, self.reset, self.crop_start, self.save,
                    self.slider_saturation, self.slider_hue, self.slider_temperature]:
            if btn is not None:
                btn.setEnabled(True)

    def save_image(self):
        if self._guard(): return
        save_path, _ = QFileDialog.getSaveFileName(
            self.main_window, "Save Image", "",
            "PNG Files (*.png);;JPEG Files (*.jpg *.jpeg)")
        if save_path:
            self.edited.save(save_path)

    def _guard(self):
        return self.edited is None

    # Undo / Reset
    def undo_(self):
        if self.history:
            self.edited = self.history.pop()
            self._display_pil(self.edited)

    def reset_(self):
        if self._guard(): return
        self.history.clear()
        self.last_color = None
        self.edited = self.original.copy()
        self._display_pil(self.edited)

    # Transform
    def left_rotate_filter(self):
        if self._guard(): return
        self.history_append()
        if self.edited.mode == "L" and self.last_color is not None:
            self.last_color = self.last_color.rotate(90, expand=True)
        self.edited = self.edited.rotate(90, expand=True)
        self._display_pil(self.edited)

    def right_rotate_filter(self):
        if self._guard(): return
        self.history_append()
        if self.edited.mode == "L" and self.last_color is not None:
            self.last_color = self.last_color.rotate(-90, expand=True)
        self.edited = self.edited.rotate(-90, expand=True)
        self._display_pil(self.edited)

    def flip_horizontal_filter(self):
        if self._guard(): return
        self.history_append()
        if self.edited.mode == "L" and self.last_color is not None:
            self.last_color = self.last_color.transpose(Image.FLIP_LEFT_RIGHT)
        self.edited = self.edited.transpose(Image.FLIP_LEFT_RIGHT)
        self._display_pil(self.edited)

    def flip_vertical_filter(self):
        if self._guard(): return
        self.history_append()
        if self.edited.mode == "L" and self.last_color is not None:
            self.last_color = self.last_color.transpose(Image.FLIP_TOP_BOTTOM)
        self.edited = self.edited.transpose(Image.FLIP_TOP_BOTTOM)
        self._display_pil(self.edited)

    # Filters
    def grayscale_filter(self):
        if self._guard(): return
        self.history_append()
        if self.edited.mode != "L":
            self.last_color = self.edited.copy()
        self.edited = self.edited.convert("L")
        self._display_pil(self.edited)

    def color_filter(self):
        if self._guard(): return
        self.history_append()
        if self.edited.mode == "L" and self.last_color is not None:
            self.edited = self.last_color.copy()
        else:
            enhancer = ImageEnhance.Color(self.edited)
            self.edited = enhancer.enhance(1.3)
        self._display_pil(self.edited)

    def blur_filter(self):
        if self._guard(): return
        self.history_append()
        if self.edited.mode == "L" and self.last_color is not None:
            self.last_color = self.last_color.filter(ImageFilter.BLUR)
        self.edited = self.edited.filter(ImageFilter.BLUR)
        self._display_pil(self.edited)

    def sharpen_filter(self):
        if self._guard(): return
        self.history_append()
        if self.edited.mode == "L" and self.last_color is not None:
            self.last_color = self.last_color.filter(ImageFilter.SHARPEN)
        self.edited = self.edited.filter(ImageFilter.SHARPEN)
        self._display_pil(self.edited)

    def brightness_filter(self):
        if self._guard(): return
        self.history_append()
        factor = 1 + (self.slider.value() / 50)
        if self.edited.mode == "L" and self.last_color is not None:
            self.last_color = ImageEnhance.Brightness(self.last_color).enhance(factor)
        self.edited = ImageEnhance.Brightness(self.edited).enhance(factor)
        self._display_pil(self.edited)

    def contrast_filter(self):
        if self._guard(): return
        self.history_append()
        factor = 1 + (self.slider2.value() / 50)
        if self.edited.mode == "L" and self.last_color is not None:
            self.last_color = ImageEnhance.Contrast(self.last_color).enhance(factor)
        self.edited = ImageEnhance.Contrast(self.edited).enhance(factor)
        self._display_pil(self.edited)

    def sepia(self):
        if self._guard(): return
        self.history_append()
        gray = ImageOps.grayscale(self.edited)
        self.edited = ImageOps.colorize(gray, "#704214", "#C0A080")
        self._display_pil(self.edited)

    def invert(self):
        if self._guard(): return
        self.history_append()
        img = self.edited.convert("RGB") if self.edited.mode not in ("RGB", "L") else self.edited
        self.edited = ImageOps.invert(img)
        self._display_pil(self.edited)

    def solarize(self):
        if self._guard(): return
        self.history_append()
        self.edited = ImageOps.solarize(self.edited, threshold=128)
        self._display_pil(self.edited)

    def vignette(self):
        if self._guard(): return
        self.history_append()
        width, height = self.edited.size
        center_x, center_y = width // 2, height // 2
        max_radius = math.sqrt(center_x**2 + center_y**2)
        mask = Image.new("L", (width, height), 0)
        pixels = mask.load()
        inv_max_radius = 1 / max_radius
        strength = 0.6
        for y in range(height):
            dy = y - center_y
            dy2 = dy * dy
            for x in range(width):
                dx = x - center_x
                distance = math.sqrt(dx * dx + dy2)
                intensity = int(255 * (1 - strength * distance * inv_max_radius))
                pixels[x, y] = max(0, min(255, intensity))
        mask = mask.filter(ImageFilter.GaussianBlur(25))
        vignette_layer = Image.new("RGB", (width, height), (0, 0, 0))
        result = Image.composite(self.edited, vignette_layer, mask)
        self._display_pil(result)

    # Crop
    def start_crop(self):
        if self._guard(): return
        self.crop_start.setEnabled(False)
        self.crop_confirm.setEnabled(True)
        self.image_label.enable_crop(True)
        self.image_label.setStatusTip("Draw a rectangle to crop, then press Confirm Crop")

    def confirm_crop(self):
        if self._guard(): return
        rect = self.image_label.crop_rect
        if rect is None: return
        label_w, label_h = self.image_label.width(), self.image_label.height()
        img_w,  img_h   = self.edited.size
        scale    = min(label_w / img_w, label_h / img_h)
        offset_x = (label_w - img_w * scale) / 2
        offset_y = (label_h - img_h * scale) / 2
        x1 = max(0,     (rect.left()   - offset_x) / scale)
        y1 = max(0,     (rect.top()    - offset_y) / scale)
        x2 = min(img_w, (rect.right()  - offset_x) / scale)
        y2 = min(img_h, (rect.bottom() - offset_y) / scale)
        if x2 <= x1 or y2 <= y1: return
        box = (int(x1), int(y1), int(x2), int(y2))
        self.history_append()
        if self.edited.mode == "L" and self.last_color is not None:
            self.last_color = self.last_color.crop(box)
        self.edited = self.edited.crop(box)
        self.image_label.enable_crop(False)
        self.crop_start.setEnabled(True)
        self.crop_confirm.setEnabled(False)
        self._display_pil(self.edited)

    # ========== ZOOM & DISPLAY ==========
    def zoom_in(self):
        """Zoom in the image."""
        if self.edited is None: return
        self.image_label.zoom_in()

    def zoom_out(self):
        """Zoom out the image."""
        if self.edited is None: return
        self.image_label.zoom_out()

    def set_zoom(self, value: int):
        """Set zoom percentage."""
        if self.edited is None: return
        factor = value / 100.0
        self.image_label.set_zoom(factor)

    def fit_to_window(self):
        """Fit image to window."""
        if self.edited is None: return
        self.image_label.fit_to_window()

    def zoom_actual(self):
        """Show actual size (100%)."""
        if self.edited is None: return
        self.image_label.zoom_actual_size()

    def toggle_fit_actual(self):
        """Toggle between fit and actual size."""
        if self.edited is None: return
        self.image_label.toggle_fit_actual()

    def get_image_info(self) -> str:
        """Get image info string and optionally update label."""
        info = self._compute_image_info()

        # Update label if available
        if self.info_label:
            self.info_label.setText(info)

        return info

    def _compute_image_info(self) -> str:
        """Compute the image info string."""
        if self.edited is None:
            return "No image loaded"

        w, h = self.edited.size
        mode = self.edited.mode
        mode_names = {"1": "1-bit", "L": "Grayscale", "RGB": "RGB", "RGBA": "RGBA", "P": "Palette", "CMYK": "CMYK"}
        mode_str = mode_names.get(mode, mode)

        # Get file size if available
        size_str = ""
        if self.image_path and os.path.exists(self.image_path):
            size_bytes = os.path.getsize(self.image_path)
            if size_bytes < 1024:
                size_str = f" · {size_bytes} B"
            elif size_bytes < 1024 * 1024:
                size_str = f" · {size_bytes // 1024} KB"
            else:
                size_str = f" · {size_bytes // (1024 * 1024)}.{size_bytes % (1024 * 1024) // 102400} MB"

        # Get current zoom level
        try:
            zoom_level = int(self.image_label.get_zoom() * 100)
        except:
            zoom_level = 100

        return f"{w}×{h} · {mode_str}{size_str} · {zoom_level}%"

    # ========== NEW FILTERS ==========
    def saturation_filter(self):
        """Apply saturation adjustment."""
        if self._guard(): return
        self.history_append()
        factor = 1 + (self.slider_saturation.value() / 100)
        if self.edited.mode == "L":
            self.edited = self.edited.convert("RGB")
        enhancer = ImageEnhance.Color(self.edited)
        self.edited = enhancer.enhance(factor)
        if self.last_color and self.last_color.mode == "L":
            self.last_color = self.last_color.convert("RGB")
            enhancer = ImageEnhance.Color(self.last_color)
            self.last_color = enhancer.enhance(factor)
        self._display_pil(self.edited)

    def hue_filter(self):
        """Apply hue rotation."""
        if self._guard(): return
        self.history_append()
        degrees = self.slider_hue.value()

        # Convert to HSV, rotate hue, convert back
        if self.edited.mode != "RGB":
            img = self.edited.convert("RGB")
        else:
            img = self.edited.copy()

        # Simple hue shift using PIL
        h, s, v = img.convert("HSV").split()
        h_adv = h.getchannel("H")
        # Shift hue by rotating the hue channel
        shift = int(degrees * 255 / 180)
        from PIL import ImageOps
        h_shifted = h_adv.offset(shift)
        result = ImageOps.merge("HSV", h_shifted, s, v).convert("RGB")
        self.edited = result

        if self.last_color and self.last_color.mode != "RGB":
            lc = self.last_color.convert("RGB")
        elif self.last_color:
            lc = self.last_color.copy()
        if lc:
            h2, s2, v2 = lc.convert("HSV").split()
            h2 = h2.getchannel("H").offset(shift)
            self.last_color = ImageOps.merge("HSV", h2, s2, v2).convert("RGB")

        self._display_pil(self.edited)

    def temperature_filter(self):
        """Apply temperature (warm/cool) adjustment."""
        if self._guard(): return
        self.history_append()
        temp = self.slider_temperature.value()

        if self.edited.mode != "RGB":
            img = self.edited.convert("RGB")
        else:
            img = self.edited.copy()

        # Adjust temperature by shifting R and B channels
        from PIL import ImageChops
        r, g, b = img.split()

        if temp > 0:  # Warmer - increase red, decrease blue
            factor = 1 + (temp / 100)
            from PIL import ImageEnhance
            r = ImageEnhance.Brightness(r).enhance(factor)
            b = ImageEnhance.Brightness(b).enhance(1 - temp / 150)
        elif temp < 0:  # Cooler - increase blue, decrease red
            factor = 1 + abs(temp) / 100
            from PIL import ImageEnhance
            b = ImageEnhance.Brightness(b).enhance(factor)
            r = ImageEnhance.Brightness(r).enhance(1 - abs(temp) / 150)

        self.edited = ImageOps.merge("RGB", (r, g, b))
        self._display_pil(self.edited)

    def auto_enhance(self):
        """Auto enhance brightness and contrast."""
        if self._guard(): return
        self.history_append()

        # Apply auto contrast
        self.edited = ImageOps.autocontrast(self.edited, cutoff=2)

        # Apply modest sharpness enhancement
        from PIL import ImageFilter
        self.edited = self.edited.filter(ImageFilter.UnsharpMask(radius=2, percent=50, threshold=3))

        self._display_pil(self.edited)

    # ========== DIALOGS ==========
    def resize_dialog(self):
        """Show resize dialog."""
        if self._guard(): return

        dialog = QDialog(self.main_window)
        dialog.setWindowTitle("Resize Image")
        dialog.setMinimumWidth(300)
        layout = QVBoxLayout()

        # Current size display
        w, h = self.edited.size
        current_label = QLabel(f"Current: {w} × {h}")
        layout.addWidget(current_label)

        # Width
        width_box = QGroupBox("Width (pixels)")
        width_layout = QHBoxLayout()
        width_spin = QSpinBox()
        width_spin.setRange(1, 10000)
        width_spin.setValue(w)
        self._resize_lock_aspect = QCheckBox("Lock aspect ratio")
        self._resize_lock_aspect.setChecked(True)
        width_layout.addWidget(width_spin)
        width_layout.addWidget(self._resize_lock_aspect)
        width_box.setLayout(width_layout)
        layout.addWidget(width_box)

        # Height (read-only initially)
        height_label = QLabel(f"Height: {h} px")
        layout.addWidget(height_label)

        # Percentage
        percent_box = QGroupBox("Percentage")
        percent_layout = QHBoxLayout()
        percent_slider = QSlider(Qt.Horizontal)
        percent_slider.setRange(10, 200)
        percent_slider.setValue(100)
        percent_label = QLabel("100%")
        percent_layout.addWidget(percent_slider)
        percent_layout.addWidget(percent_label)
        percent_box.setLayout(percent_layout)
        layout.addWidget(percent_box)

        # Buttons
        btn_layout = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(lambda: self._apply_resize(width_spin.value(), height_label, dialog))
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(apply_btn)
        layout.addLayout(btn_layout)

        dialog.setLayout(layout)

        # Update height when width changes
        def update_height(w_val):
            if self._resize_lock_aspect.isChecked():
                ratio = h / w
                h_val = int(w_val * ratio)
                height_label.setText(f"Height: {h_val} px (aspect locked)")
            percent_label.setText(f"{int(w_val / w * 100)}%")
            percent_slider.setValue(int(w_val / w * 100))

        width_spin.valueChanged.connect(lambda v: update_height(v))

        # Update from percentage slider
        def update_from_percent(p_val):
            new_w = int(w * p_val / 100)
            width_spin.blockSignals(True)
            width_spin.setValue(new_w)
            width_spin.blockSignals(False)
            if self._resize_lock_aspect.isChecked():
                ratio = h / w
                h_val = int(new_w * ratio)
                height_label.setText(f"Height: {h_val} px (aspect locked)")
            percent_label.setText(f"{p_val}%")

        percent_slider.valueChanged.connect(update_from_percent)

        dialog.exec_()

    def _apply_resize(self, new_width: int, height_label: QLabel, dialog: QDialog):
        """Apply the resize operation."""
        if self._guard(): return

        # Extract height from label text
        h_text = height_label.text()
        # Parse "Height: XXX px"
        import re
        match = re.search(r'(\d+)', h_text)
        if match:
            new_height = int(match.group(1))
        else:
            new_height = self.edited.height

        self.history_append()
        self.edited = self.edited.resize((new_width, new_height), Image.Resampling.LANCZOS)
        if self.last_color:
            self.last_color = self.last_color.resize((new_width, new_height), Image.Resampling.LANCZOS)
        self._display_pil(self.edited)
        dialog.accept()

    def rotate_free_dialog(self):
        """Show free rotation dialog."""
        if self._guard(): return

        dialog = QDialog(self.main_window)
        dialog.setWindowTitle("Rotate Image")
        dialog.setMinimumWidth(280)
        layout = QVBoxLayout()

        # Angle input
        angle_box = QGroupBox("Rotation Angle")
        angle_layout = QHBoxLayout()
        angle_spin = QSpinBox()
        angle_spin.setRange(-360, 360)
        angle_spin.setValue(0)
        angle_layout.addWidget(QLabel("Degrees:"))
        angle_layout.addWidget(angle_spin)
        angle_box.setLayout(angle_layout)
        layout.addWidget(angle_box)

        # Quick presets
        preset_box = QGroupBox("Quick Presets")
        preset_layout = QHBoxLayout()
        presets = [(-90, "-90°"), (90, "+90°"), (180, "180°"), (45, "+45°"), (-45, "-45°")]
        for val, text in presets:
            btn = QPushButton(text)
            btn.clicked.connect(lambda checked, v=val: angle_spin.setValue(v))
            preset_layout.addWidget(btn)
        preset_box.setLayout(preset_layout)
        layout.addWidget(preset_box)

        # Expand canvas option
        expand_check = QCheckBox("Expand canvas to fit")
        expand_check.setChecked(True)
        layout.addWidget(expand_check)

        # Buttons
        btn_layout = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(lambda: self._apply_rotate(angle_spin.value(), expand_check.isChecked(), dialog))
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(apply_btn)
        layout.addLayout(btn_layout)

        dialog.setLayout(layout)
        dialog.exec_()

    def crop_presets_dialog(self):
        """Show crop presets dialog."""
        if self._guard(): return

        dialog = QDialog(self.main_window)
        dialog.setWindowTitle("Crop Presets")
        dialog.setMinimumWidth(300)
        layout = QVBoxLayout()

        w, h = self.edited.size

        # Preset aspect ratios
        preset_box = QGroupBox("Aspect Ratios")
        preset_layout = QVBoxLayout()

        # Common presets: (label, width_ratio, height_ratio)
        presets = [
            ("16:9 (Widescreen)", 16, 9),
            ("4:3 (Standard)", 4, 3),
            ("3:2 (Photo)", 3, 2),
            ("1:1 (Square)", 1, 1),
            ("2:3 (Portrait)", 2, 3),
            ("9:16 (Vertical)", 9, 16),
        ]

        for label, rw, rh in presets:
            btn_row = QHBoxLayout()
            btn = QPushButton(label)
            btn.setObjectName("crop_btn")

            # Calculate crop dimensions for this aspect ratio
            if rw / rh > w / h:
                # Limited by width
                new_h = int(w * rh / rw)
                new_w = w
            else:
                # Limited by height
                new_w = int(h * rw / rh)
                new_h = h

            btn_layout.addWidget(btn)
            btn_row.addWidget(btn)
            btn_row.addWidget(QLabel(f"→ {new_w}×{new_h}"))
            btn_row.addStretch()

            # Store action
            btn.clicked.connect(lambda checked, nw=new_w, nh=new_h, d=dialog: self._apply_crop_preset(nw, nh, d))
            preset_layout.addLayout(btn_row)

        preset_box.setLayout(preset_layout)
        layout.addWidget(preset_box)

        # Custom crop
        custom_box = QGroupBox("Custom Size")
        custom_layout = QHBoxLayout()

        width_spin = QSpinBox()
        width_spin.setRange(1, w)
        width_spin.setValue(w)
        height_spin = QSpinBox()
        height_spin.setRange(1, h)
        height_spin.setValue(h)

        custom_layout.addWidget(QLabel("Width:"))
        custom_layout.addWidget(width_spin)
        custom_layout.addWidget(QLabel("Height:"))
        custom_layout.addWidget(height_spin)

        custom_box.setLayout(custom_layout)
        layout.addWidget(custom_box)

        # Buttons
        btn_layout = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)

        custom_apply = QPushButton("Apply Custom")
        custom_apply.setObjectName("crop_btn")
        custom_apply.clicked.connect(lambda: self._apply_crop_preset(width_spin.value(), height_spin.value(), dialog))

        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(custom_apply)
        layout.addLayout(btn_layout)

        dialog.setLayout(layout)
        dialog.exec_()

    def _apply_crop_preset(self, new_width: int, new_height: int, dialog: QDialog):
        """Apply a crop preset by resizing to specific dimensions."""
        if self._guard(): return

        # Get center crop
        w, h = self.edited.size
        x = (w - new_width) // 2
        y = (h - new_height) // 2

        # Ensure positive dimensions
        if new_width <= 0 or new_height <= 0:
            return
        if x < 0 or y < 0:
            QMessageBox.warning(self.main_window, "Too Large",
                f"Crop size {new_width}×{new_height} is larger than image {w}×{h}")
            return

        box = (x, y, x + new_width, y + new_height)
        self.history_append()
        self.edited = self.edited.crop(box)
        if self.last_color:
            self.last_color = self.last_color.crop(box)
        self._display_pil(self.edited)
        dialog.accept()

    def _apply_rotate(self, angle: int, expand: bool, dialog: QDialog):
        """Apply the rotation."""
        if self._guard(): return
        if angle == 0:
            dialog.accept()
            return

        self.history_append()
        self.edited = self.edited.rotate(angle, expand=expand, resample=Image.Resampling.BICUBIC)
        if self.last_color:
            self.last_color = self.last_color.rotate(angle, expand=expand, resample=Image.Resampling.BICUBIC)
        self._display_pil(self.edited)
        dialog.accept()

    def text_overlay_dialog(self):
        """Show text overlay dialog."""
        if self._guard(): return

        dialog = QDialog(self.main_window)
        dialog.setWindowTitle("Add Text")
        dialog.setMinimumWidth(350)
        layout = QVBoxLayout()

        # Text input
        text_label = QLabel("Text:")
        layout.addWidget(text_label)
        text_edit = QTextEdit()
        text_edit.setPlaceholderText("Enter text...")
        text_edit.setMaximumHeight(80)
        layout.addWidget(text_edit)

        # Font selection
        font_box = QGroupBox("Font")
        font_layout = QHBoxLayout()
        font_combo = QFontComboBox()
        font_layout.addWidget(font_combo)
        size_spin = QSpinBox()
        size_spin.setRange(8, 144)
        size_spin.setValue(32)
        font_layout.addWidget(QLabel("Size:"))
        font_layout.addWidget(size_spin)
        font_box.setLayout(font_layout)
        layout.addWidget(font_box)

        # Color
        color_layout = QHBoxLayout()
        color_btn = QPushButton("Choose Color")
        color_layout.addWidget(QLabel("Color:"))
        color_layout.addWidget(color_btn)
        color_layout.addStretch()

        color = [QColor(255, 255, 255)]  # Default white

        def pick_color():
            c = QColorDialog.getColor()
            if c.isValid():
                color[0] = c

        color_btn.clicked.connect(pick_color)
        layout.addLayout(color_layout)

        # Position
        pos_box = QGroupBox("Position")
        pos_layout = QHBoxLayout()
        pos_combo = QComboBox()
        pos_combo.addItems(["Center", "Top Left", "Top Right", "Bottom Left", "Bottom Right"])
        pos_layout.addWidget(QLabel("Position:"))
        pos_layout.addWidget(pos_combo)
        pos_box.setLayout(pos_layout)
        layout.addWidget(pos_box)

        # Buttons
        btn_layout = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        preview_btn = QPushButton("Preview")
        apply_btn = QPushButton("Apply")

        def do_preview():
            self._apply_text_overlay(text_edit.toPlainText(), font_combo.currentFont(), size_spin.value(), color[0], pos_combo.currentIndex(), dialog)

        preview_btn.clicked.connect(do_preview)
        apply_btn.clicked.connect(lambda: (do_preview(), dialog.accept()))

        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(preview_btn)
        btn_layout.addWidget(apply_btn)
        layout.addLayout(btn_layout)

        dialog.setLayout(layout)
        dialog.exec_()

    def _apply_text_overlay(self, text: str, font: QFont, size: int, color: QColor, position: int, dialog: QDialog):
        """Apply text overlay to image."""
        if self._guard() or not text:
            return

        self.history_append()

        # Create a new image with RGBA
        if self.edited.mode != "RGBA":
            self.edited = self.edited.convert("RGBA")

        # Create text layer
        txt_layer = Image.new("RGBA", self.edited.size, (0, 0, 0, 0))

        # Set up font
        from PIL import ImageFont
        try:
            pil_font = ImageFont.truetype(font.family(), size)
        except:
            pil_font = ImageFont.load_default()

        # Get text size
        from PIL import ImageDraw
        dummy_img = Image.new("RGBA", (1, 1))
        dummy_draw = ImageDraw.Draw(dummy_img)
        text_bbox = dummy_draw.textbbox((0, 0), text, font=pil_font)
        text_w = text_bbox[2] - text_bbox[0]
        text_h = text_bbox[3] - text_bbox[1]

        # Calculate position
        w, h = self.edited.size
        positions = {
            0: ((w - text_w) // 2, (h - text_h) // 2),
            1: (10, 10),
            2: (w - text_w - 10, 10),
            3: (10, h - text_h - 10),
            4: (w - text_w - 10, h - text_h - 10),
        }
        x, y = positions.get(position, ((w - text_w) // 2, (h - text_h) // 2))

        # Draw text
        draw = ImageDraw.Draw(txt_layer)
        draw.text((x, y), text, font=pil_font, fill=(color.red(), color.green(), color.blue(), 255))

        # Composite
        self.edited = Image.alpha_composite(self.edited, txt_layer).convert("RGB")
        self._display_pil(self.edited)

    # ==================== DRAWING TOOLS ====================
    def start_drawing_tool(self, tool: str):
        """Start drawing mode with specified tool."""
        if self._guard(): return
        self.image_label.enable_drawing(True, tool)

    def stop_drawing_tool(self):
        """Stop drawing mode."""
        if self._guard(): return
        self.image_label.enable_drawing(False)

    def set_brush_size(self, size: int):
        """Set brush size for drawing."""
        if self._guard(): return
        self.image_label.set_brush_size(size)

    def set_brush_color(self, color: QColor):
        """Set brush color for drawing."""
        if self._guard(): return
        self.image_label.set_brush_color(color)

    def apply_drawing(self):
        """Apply the current drawing to the image."""
        if self._guard(): return

        from PIL import ImageDraw, ImageFont

        drawings = self.image_label.get_drawing_path()
        if not drawings:
            return

        self.history_append()

        # Create RGBA image
        if self.edited.mode != "RGBA":
            self.edited = self.edited.convert("RGBA")

        # Get scale factor
        label_w = self.image_label.width()
        label_h = self.image_label.height()
        img_w, img_h = self.edited.size
        scale = min(label_w / img_w, label_h / img_h) if img_w > 0 else 1.0
        offset_x = (label_w - img_w * scale) / 2
        offset_y = (label_h - img_h * scale) / 2

        draw = ImageDraw.Draw(self.edited)

        for item in drawings:
            if item[0] == "stroke":
                points = item[1]
                if len(points) < 2:
                    continue

                # Convert points from label coords to image coords
                conv_points = []
                for pt in points:
                    x = int((pt.x() - offset_x) / scale)
                    y = int((pt.y() - offset_y) / scale)
                    conv_points.append((x, y))

                # Draw path
                color = self.image_label._brush_color
                width = max(1, int(self.image_label._brush_size * scale))
                for i in range(len(conv_points) - 1):
                    draw.line([conv_points[i], conv_points[i + 1]], fill=(color.red(), color.green(), color.blue(), 255), width=width)

            elif item[0] in ("line", "arrow"):
                tool, start, end = item
                # Convert coordinates
                x1 = int((start.x() - offset_x) / scale)
                y1 = int((start.y() - offset_y) / scale)
                x2 = int((end.x() - offset_x) / scale)
                y2 = int((end.y() - offset_y) / scale)

                color = self.image_label._brush_color
                width = max(1, int(self.image_label._brush_size * scale))
                draw.line([(x1, y1), (x2, y2)], fill=(color.red(), color.green(), color.blue(), 255), width=width)

                if tool == "arrow":
                    # Simple arrowhead
                    angle = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
                    if angle > 0:
                        ax = int(x2 - 15 * (x2 - x1) / angle)
                        ay = int(y2 - 15 * (y2 - y1) / angle)
                        draw.line([(x2, y2), (ax, ay)], fill=(color.red(), color.green(), color.blue(), 255), width=width)

            elif item[0] == "rectangle":
                tool, start, end = item
                x1 = int((start.x() - offset_x) / scale)
                y1 = int((start.y() - offset_y) / scale)
                x2 = int((end.x() - offset_x) / scale)
                y2 = int((end.y() - offset_y) / scale)
                color = self.image_label._brush_color
                draw.rectangle([x1, y1, x2, y2], outline=(color.red(), color.green(), color.blue(), 255), width=max(1, int(self.image_label._brush_size * scale)))

            elif item[0] == "circle":
                tool, start, end = item
                x1 = int((start.x() - offset_x) / scale)
                y1 = int((start.y() - offset_y) / scale)
                x2 = int((end.x() - offset_x) / scale)
                y2 = int((end.y() - offset_y) / scale)
                color = self.image_label._brush_color
                draw.ellipse([x1, y1, x2, y2], outline=(color.red(), color.green(), color.blue(), 255), width=max(1, int(self.image_label._brush_size * scale)))

        # Convert back and display
        self.edited = self.edited.convert("RGB")
        self.image_label.clear_drawings()
        self._display_pil(self.edited)

    # ==================== STICKERS ====================
    def add_sticker(self, sticker_type: str):
        """Add a sticker to the image."""
        if self._guard(): return

        self.history_append()

        # Create sticker as RGBA overlay
        if self.edited.mode != "RGBA":
            self.edited = self.edited.convert("RGBA")

        w, h = self.edited.size

        # Default sticker sizes
        sticker_w = min(w, h) // 5

        if sticker_type == "star":
            from PIL import ImageDraw
            sticker = Image.new("RGBA", (sticker_w, sticker_w), (0, 0, 0, 0))
            draw = ImageDraw.Draw(sticker)

            # Draw 5-pointed star
            cx, cy = sticker_w // 2, sticker_w // 2
            r = sticker_w // 2 - 5
            points = []
            for i in range(10):
                angle = i * 36 - 90
                import math
                rad = math.radians(angle)
                if i % 2 == 0:
                    px = cx + int(r * math.cos(rad))
                    py = cy + int(r * math.sin(rad))
                else:
                    px = cx + int(r * 0.4 * math.cos(rad))
                    py = cy + int(r * 0.4 * math.sin(rad))
                points.append((px, py))

            color = self.image_label._brush_color
            r, g, b = color.red(), color.green(), color.blue()
            draw.polygon(points, fill=(r, g, b, 255))

        elif sticker_type == "heart":
            from PIL import ImageDraw
            sticker = Image.new("RGBA", (sticker_w, sticker_w), (0, 0, 0, 0))
            draw = ImageDraw.Draw(sticker)

            # Simple heart shape
            color = self.image_label._brush_color
            r, g, b = color.red(), color.green(), color.blue()

            # Draw two circles and a triangle
            w2 = sticker_w // 2
            draw.ellipse([2, w2 // 3, w2 - 2, w2 + w2 // 2], fill=(r, g, b, 255))
            draw.ellipse([w2, w2 // 3, sticker_w - 2, w2 + w2 // 2], fill=(r, g, b, 255))
            draw.polygon([(5, w2 - 5), (sticker_w - 5, w2 - 5), (sticker_w // 2, sticker_w - 10)], fill=(r, g, b, 255))

        elif sticker_type == "arrow_up":
            from PIL import ImageDraw
            sticker = Image.new("RGBA", (sticker_w // 2, sticker_w), (0, 0, 0, 0))
            draw = ImageDraw.Draw(sticker)

            color = self.image_label._brush_color
            r, g, b = color.red(), color.green(), color.blue()

            # Up arrow
            w2 = sticker_w // 4
            draw.polygon([(w2, 10), (w2 * 2, sticker_w // 2), (w2 * 3, 10)], fill=(r, g, b, 255))
            draw.rectangle([(w2, sticker_w // 2), (w2 * 3, sticker_w - 10)], fill=(r, g, b, 255))

        else:
            return

        # Position sticker in center
        pos_x = (w - sticker_w) // 2
        pos_y = (h - sticker_w) // 2

        # Composite
        if sticker_type == "arrow_up":
            sticker = sticker.resize((w // 2, h), Image.Resampling.LANCZOS)
            pos_x = w // 4

        self.edited.paste(sticker, (pos_x, pos_y), sticker)
        self.edited = self.edited.convert("RGB")
        self._display_pil(self.edited)

    # Preview combo
    def display_image_choice(self):
        if self._guard(): return
        text = self.preview.currentText()
        if text == "Original":
            self._display_pil(self.original)
            return
        mapping = {
            "B/W":           lambda: self.original.convert("L"),
            "Color":         lambda: self.original.convert("RGB"),
            "Blur":          lambda: self.original.filter(ImageFilter.BLUR),
            "Sharpen":       lambda: self.original.filter(ImageFilter.SHARPEN),
            "Sepia":         lambda: ImageOps.colorize(ImageOps.grayscale(self.original), "#704214", "#C0A080"),
            "Solarize":      lambda: ImageOps.solarize(self.original, threshold=128),
            "Invert Colors": lambda: ImageOps.invert(self.original),
        }
        if text in mapping:
            self._display_pil(mapping[text]())

    def generate_img(self, prompt: str = None):
        if not prompt: return
        self.path = f"{prompt}.png"
        self.image_gen.generate(prompt, self.path)
        self.original = Image.open(self.path).copy()
        self.edited = self.original.copy()
        self._display_pil(self.edited)
