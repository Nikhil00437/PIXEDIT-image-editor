from PyQt5.QtWidgets import QFileDialog, QShortcut, QDialog, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QLabel, QKeySequenceEdit, QHeaderView, QMessageBox, QComboBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QKeySequence
import os, tempfile, json, math
from PIL import Image, ImageFilter, ImageEnhance, ImageOps
from collections import deque

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
    def __init__(self, widget, image_label, slider, slider2, preview,
                 left_rotate, right_rotate, flip_horizontal, flip_vertical,
                 grayscale, color, blur, sharpen, brightness, contrast,
                 sepia, solarize, invert, vignette, undo, reset,
                 crop_start, crop_confirm, save, main_window,
                 themes=None, current_theme=None, apply_theme_fn=None):

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

        self.original        = None
        self.edited          = None
        self.image_path      = None
        self.last_color      = None
        self.history         = deque(maxlen=20)
        self.file_location   = ""
        self.active_shortcuts = []
        self.current_shortcuts = load_shortcuts()

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
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            tmp_path = tmp.name
        pil_image.save(tmp_path)
        self.image_label.hide()
        pixmap  = QPixmap(tmp_path)
        w, h    = self.image_label.width(), self.image_label.height()
        pixmap_ = pixmap.scaled(w, h, Qt.KeepAspectRatio)
        self.image_label.setPixmap(pixmap_)
        self.image_label.show()
        for btn in [self.preview, self.left_rotate, self.right_rotate,
                    self.flip_horizontal, self.flip_vertical, self.grayscale,
                    self.color, self.blur, self.sharpen, self.brightness,
                    self.contrast, self.sepia_, self.solarize_, self.invert_,
                    self.vignette_, self.undo, self.reset, self.crop_start, self.save]:
            btn.setEnabled(True)
        os.unlink(tmp_path)

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
