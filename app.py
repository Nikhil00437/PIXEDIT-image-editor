from PyQt5.QtWidgets import QApplication, QLineEdit, QWidget, QHBoxLayout, QSlider, QGroupBox, QListWidget, QLabel, QVBoxLayout, QPushButton, QComboBox, QListWidgetItem
from PyQt5.QtCore import Qt
import os, sys
from crop import CropLabel
from functions import ImageEditor, load_theme_from_file
from theme import THEMES

SUPPORTED_EXTS = {".jpg", ".jpeg", ".png"}
os.environ["QT_LOGGING_RULES"] = "*.debug=false;qt.qpa.*=false"

app = QApplication(sys.argv)

# Load saved theme or fall back to default
saved_theme = load_theme_from_file()
current_theme = [saved_theme if saved_theme in THEMES else list(THEMES.keys())[0]]

def apply_theme(name):
    app.setStyleSheet(THEMES[name])

apply_theme(current_theme[0])

# Create settings button early so TitleBar can use it
settings_btn = QPushButton("⚙")
settings_btn.setObjectName("settings_btn")
settings_btn.setToolTip("Settings  (Shortcuts & Theme)")

# Custom title bar
class TitleBar(QWidget):
    def __init__(self, parent, settings_button):
        super().__init__(parent)
        self.parent = parent
        self.setObjectName("titlebar")
        self.setFixedHeight(40)
        self._drag_pos  = None
        self._maximized = False

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 0, 0, 0)
        layout.setSpacing(0)

        title    = QLabel("PIXEDIT")
        title.setObjectName("app_title")
        subtitle = QLabel("  //  IMAGE EDITOR")
        subtitle.setObjectName("app_subtitle")
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addStretch()

        # Settings button lives in the title bar, before window controls
        layout.addWidget(settings_button)

        btn_min = QPushButton("─");  btn_min.setObjectName("win_btn")
        btn_min.setToolTip("Minimize")
        btn_min.clicked.connect(parent.showMinimized)

        btn_max = QPushButton("□");  btn_max.setObjectName("win_btn")
        btn_max.setToolTip("Maximize / Restore")

        def toggle_max():
            if self._maximized:
                parent.showNormal();  btn_max.setText("□");  self._maximized = False
            else:
                parent.showMaximized(); btn_max.setText("❐"); self._maximized = True

        btn_max.clicked.connect(toggle_max)

        btn_close = QPushButton("✕"); btn_close.setObjectName("win_close")
        btn_close.setToolTip("Close")
        btn_close.clicked.connect(parent.close)

        layout.addWidget(btn_min)
        layout.addWidget(btn_max)
        layout.addWidget(btn_close)

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._drag_pos = e.globalPos() - self.parent.frameGeometry().topLeft()

    def mouseMoveEvent(self, e):
        if e.buttons() == Qt.LeftButton and self._drag_pos:
            self.parent.move(e.globalPos() - self._drag_pos)

    def mouseReleaseEvent(self, e):
        self._drag_pos = None

    def mouseDoubleClickEvent(self, e):
        if self._maximized:
            self.parent.showNormal();  self._maximized = False
        else:
            self.parent.showMaximized(); self._maximized = True

# Main window
main_window = QWidget()
main_window.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
main_window.resize(1100, 820)

title_bar = TitleBar(main_window, settings_btn)

footer = QLabel("© PIXEDIT  ·  Basic Image Editing APP  ·  Made by Nikhil 🫡")
footer.setObjectName("footer")
footer.setAlignment(Qt.AlignCenter)
footer.setFixedHeight(28)

column1 = QGroupBox(); column1.setObjectName("sidebar")
column2 = QGroupBox(); column2.setObjectName("canvas")

vboxmain  = QVBoxLayout()
vbox2main = QVBoxLayout()

folder = QPushButton("⊕  Select Folder")
folder.setObjectName("folder_btn")

widget = QListWidget()

preview = QComboBox()
preview.setEditable(True)
preview.lineEdit().setAlignment(Qt.AlignCenter)
preview.lineEdit().setReadOnly(True)
preview.addItems(["— PREVIEW —", "Original", "B/W", "Color", "Blur", "Sharpen", "Sepia", "Solarize", "Invert Colors"])

def divider(text):
    lbl = QLabel(f"  {text}")
    lbl.setObjectName("divlabel")
    return lbl

left_rotate     = QPushButton("↺  Left Rotate")
right_rotate    = QPushButton("↻  Right Rotate")
flip_horizontal = QPushButton("⇆  Mirror")
flip_vertical   = QPushButton("⇅  Upside Down")
grayscale       = QPushButton("◑  B/W")
color           = QPushButton("◈  Color")
blur            = QPushButton("≋  Blur")
sharpen         = QPushButton("✦  Sharpen")
sepia           = QPushButton("▮  Sepia")
invert          = QPushButton("₪  Invert")
solarize        = QPushButton("●  Solarize")
vignette        = QPushButton("◌◌  Vignette")

brightness = QGroupBox("BRIGHTNESS")
slider = QSlider(Qt.Horizontal)
slider.setFocusPolicy(Qt.StrongFocus)
slider.setTickPosition(QSlider.TicksBothSides)
slider.setTickInterval(10)
slider.setSingleStep(1)
slider.setRange(-50, 50)
vbox = QVBoxLayout(); vbox.addWidget(slider)
brightness.setLayout(vbox)

contrast = QGroupBox("CONTRAST")
slider2 = QSlider(Qt.Horizontal)
slider2.setFocusPolicy(Qt.StrongFocus)
slider2.setTickPosition(QSlider.TicksBothSides)
slider2.setTickInterval(10)
slider2.setSingleStep(1)
slider2.setRange(-50, 50)
vbox2 = QVBoxLayout(); vbox2.addWidget(slider2)
contrast.setLayout(vbox2)

# ========== NEW SLIDERS ==========
# Saturation
saturation = QGroupBox("SATURATION")
slider_saturation = QSlider(Qt.Horizontal)
slider_saturation.setFocusPolicy(Qt.StrongFocus)
slider_saturation.setTickPosition(QSlider.TicksBothSides)
slider_saturation.setTickInterval(25)
slider_saturation.setSingleStep(5)
slider_saturation.setRange(-100, 100)
vbox_sat = QVBoxLayout(); vbox_sat.addWidget(slider_saturation)
saturation.setLayout(vbox_sat)

# Hue
hue_adjust = QGroupBox("HUE")
slider_hue = QSlider(Qt.Horizontal)
slider_hue.setFocusPolicy(Qt.StrongFocus)
slider_hue.setTickPosition(QSlider.TicksBothSides)
slider_hue.setTickInterval(30)
slider_hue.setSingleStep(5)
slider_hue.setRange(-180, 180)
vbox_hue = QVBoxLayout(); vbox_hue.addWidget(slider_hue)
hue_adjust.setLayout(vbox_hue)

# Temperature
temperature = QGroupBox("TEMPERATURE")
slider_temperature = QSlider(Qt.Horizontal)
slider_temperature.setFocusPolicy(Qt.StrongFocus)
slider_temperature.setTickPosition(QSlider.TicksBothSides)
slider_temperature.setTickInterval(20)
slider_temperature.setSingleStep(5)
slider_temperature.setRange(-100, 100)
vbox_temp = QVBoxLayout(); vbox_temp.addWidget(slider_temperature)
temperature.setLayout(vbox_temp)

# ========== ZOOM CONTROLS ==========
zoom_controls = QGroupBox("ZOOM")
zoom_layout = QVBoxLayout()

zoom_row1 = QHBoxLayout()
zoom_out_btn = QPushButton("−")
zoom_out_btn.setFixedWidth(30)
zoom_slider = QSlider(Qt.Horizontal)
zoom_slider.setRange(25, 400)
zoom_slider.setValue(100)
zoom_in_btn = QPushButton("+")
zoom_in_btn.setFixedWidth(30)
zoom_row1.addWidget(zoom_out_btn)
zoom_row1.addWidget(zoom_slider)
zoom_row1.addWidget(zoom_in_btn)

zoom_row2 = QHBoxLayout()
fit_button = QPushButton("🔲 Fit")
fit_button.setObjectName("util_btn")
zoom_actual_btn = QPushButton("100%")
zoom_actual_btn.setObjectName("util_btn")
zoom_row2.addWidget(fit_button)
zoom_row2.addWidget(zoom_actual_btn)
zoom_row2.addStretch()

zoom_layout.addLayout(zoom_row1)
zoom_layout.addLayout(zoom_row2)
zoom_controls.setLayout(zoom_layout)

# ========== NEW BUTTONS ==========
left_rotate     = QPushButton("↺  Left Rotate")
right_rotate    = QPushButton("↻  Right Rotate")
flip_horizontal = QPushButton("⇆  Mirror")
flip_vertical   = QPushButton("⇅  Upside Down")
rotate_free    = QPushButton("◎  Rotate")
grayscale       = QPushButton("◑  B/W")
color           = QPushButton("◈  Color")
blur            = QPushButton("≋  Blur")
sharpen         = QPushButton("✦  Sharpen")
sepia           = QPushButton("▮  Sepia")
invert          = QPushButton("₪  Invert")
solarize        = QPushButton("●  Solarize")
vignette        = QPushButton("◌◌  Vignette")
auto_enhance    = QPushButton("✨  Auto")
resize_btn     = QPushButton("⤡  Resize")
resize_btn.setObjectName("util_btn")
crop_presets_btn = QPushButton("⊞  Crop Presets")
crop_presets_btn.setObjectName("crop_btn")
text_btn       = QPushButton("T  Text")

# ========== DRAWING BUTTONS ==========
brush_btn     = QPushButton("✎  Brush")
eraser_btn    = QPushButton("◻  Eraser")
line_btn      = QPushButton("╱  Line")
arrow_btn     = QPushButton("→  Arrow")
rect_btn      = QPushButton("□  Rectangle")
circle_btn    = QPushButton("○  Circle")
clear_draw   = QPushButton("⌫  Clear Drawing")
apply_draw  = QPushButton("✓  Apply Drawing")
apply_draw.setObjectName("save_btn")

# Brush size
brush_size_group = QGroupBox("BRUSH SIZE")
brush_slider = QSlider(Qt.Horizontal)
brush_slider.setRange(1, 30)
brush_slider.setValue(5)
brush_size_layout = QVBoxLayout()
brush_size_layout.addWidget(brush_slider)
brush_size_group.setLayout(brush_size_layout)

# Color picker
color_btn = QPushButton("🎨  Color")
color_btn.setObjectName("util_btn")

# ========== STICKERS ==========
sticker_star = QPushButton("★  Star")
sticker_heart = QPushButton("♥  Heart")
sticker_arrow = QPushButton("↑  Arrow")

# Add all to layout
for w in [folder, widget, divider("PREVIEW"), preview, divider("TRANSFORM"), left_rotate, right_rotate, flip_horizontal, flip_vertical, rotate_free, divider("FILTERS"), grayscale, color, blur, sharpen, auto_enhance, divider("ADJUST"), brightness, contrast, saturation, hue_adjust, temperature, divider("EFFECTS"), sepia, solarize, invert, vignette, divider("DRAWING"), brush_btn, eraser_btn, line_btn, arrow_btn, rect_btn, circle_btn, brush_size_group, color_btn, clear_draw, apply_draw, divider("STICKERS"), sticker_star, sticker_heart, sticker_arrow, divider("TOOLS"), resize_btn, crop_presets_btn, text_btn, divider("VIEW"), zoom_controls]:
    vboxmain.addWidget(w)

# Add all to layout
for w in [folder, widget, divider("PREVIEW"), preview, divider("TRANSFORM"), left_rotate, right_rotate, flip_horizontal, flip_vertical, rotate_free, divider("FILTERS"), grayscale, color, blur, sharpen, auto_enhance, divider("ADJUST"), brightness, contrast, saturation, hue_adjust, temperature, divider("EFFECTS"), sepia, solarize, invert, vignette, divider("TOOLS"), resize_btn, crop_presets_btn, text_btn, divider("VIEW"), zoom_controls]:
    vboxmain.addWidget(w)

# Canvas toolbar (settings_btn removed — now lives in title bar)
save = QPushButton("⬇  Save");         save.setObjectName("save_btn");     save.setFixedWidth(110)
undo = QPushButton("↩  Undo");         undo.setObjectName("util_btn");     undo.setFixedWidth(100)
reset_btn = QPushButton("⟳  Reset");   reset_btn.setObjectName("util_btn"); reset_btn.setFixedWidth(100)
crop_start   = QPushButton("✂  Crop");     crop_start.setObjectName("crop_btn");   crop_start.setFixedWidth(100)
crop_confirm = QPushButton("✔  Confirm"); crop_confirm.setObjectName("crop_btn"); crop_confirm.setFixedWidth(110)
prompt = QPushButton("∭")
generate_image = QPushButton("∰ Generate")
generate_image.hide()
text_box = QLineEdit()
text_box.setPlaceholderText("A Capybara? Maybe...")
text_box.setEnabled(False)

image_label = CropLabel()

# Info bar
info_bar = QLabel("No image loaded")
info_bar.setAlignment(Qt.AlignCenter)
info_bar.setStyleSheet("font-size: 11px; padding: 4px;")

hbox = QHBoxLayout()
hbox.setSpacing(6)
hbox.addWidget(undo)
hbox.addWidget(reset_btn)
hbox.addWidget(crop_start)
hbox.addWidget(crop_confirm)
hbox.addStretch()
hbox.addWidget(prompt)
hbox.addWidget(generate_image)
hbox.addWidget(text_box)
hbox.addStretch()
hbox.addWidget(save)

vbox2main.addLayout(hbox)
vbox2main.addWidget(image_label)
vbox2main.addWidget(info_bar)
vbox2main.addWidget(footer)

column1.setLayout(vboxmain)
column2.setLayout(vbox2main)

content = QWidget()
content_layout = QHBoxLayout(content)
content_layout.setSpacing(2)
content_layout.setContentsMargins(6, 4, 6, 6)

col1 = QVBoxLayout(); col1.addWidget(column1)
col3 = QVBoxLayout(); col3.addWidget(column2)

content_layout.addLayout(col1, 20)
content_layout.addLayout(QVBoxLayout(), 1)
content_layout.addLayout(col3, 78)
content_layout.addLayout(QVBoxLayout(), 1)

root_layout = QVBoxLayout(main_window)
root_layout.setContentsMargins(0, 0, 0, 0)
root_layout.setSpacing(0)
root_layout.addWidget(title_bar)
root_layout.addWidget(content)

# Wire up ImageEditor with new parameters
main = ImageEditor(widget, image_label, slider, slider2, preview, left_rotate, right_rotate, flip_horizontal, flip_vertical,
               grayscale, color, blur, sharpen, brightness, contrast, sepia, solarize, invert, vignette,
               undo, reset_btn, crop_start, crop_confirm, save, main_window,
               themes=THEMES, current_theme=current_theme, apply_theme_fn=apply_theme,
               slider_saturation=slider_saturation, slider_hue=slider_hue, slider_temperature=slider_temperature,
               zoom_slider=zoom_slider, fit_button=fit_button, info_label=info_bar)
main.setup_shortcuts()

# Disable buttons until an image is loaded
new_disabled = [preview, left_rotate, right_rotate, flip_horizontal, flip_vertical, rotate_free,
               grayscale, color, blur, sharpen, brightness, contrast, sepia, solarize, invert, vignette,
               undo, reset_btn, crop_start, crop_confirm, save, auto_enhance, resize_btn, crop_presets_btn, text_btn,
               slider_saturation, slider_hue, slider_temperature, zoom_slider, fit_button, zoom_actual_btn,
               brush_btn, eraser_btn, line_btn, arrow_btn, rect_btn, circle_btn, clear_draw, apply_draw,
               brush_slider, color_btn, sticker_star, sticker_heart, sticker_arrow]
for w in new_disabled:
    if w:
        w.setEnabled(False)

# Connections
folder.clicked.connect(main.getfiles)
settings_btn.clicked.connect(main.open_settings)

def _on_item_changed(current, previous):
    if current is None: return
    full_path = current.data(Qt.UserRole)
    if full_path and os.path.isfile(full_path):
        current.setText(full_path)
        main.load_image()
        current.setText(os.path.basename(full_path))
    else:
        main.load_image()

widget.currentItemChanged.connect(_on_item_changed)

left_rotate.clicked.connect(main.left_rotate_filter)
right_rotate.clicked.connect(main.right_rotate_filter)
flip_horizontal.clicked.connect(main.flip_horizontal_filter)
flip_vertical.clicked.connect(main.flip_vertical_filter)
grayscale.clicked.connect(main.grayscale_filter)
color.clicked.connect(main.color_filter)
blur.clicked.connect(main.blur_filter)
sharpen.clicked.connect(main.sharpen_filter)
slider.sliderReleased.connect(main.brightness_filter)
slider2.sliderReleased.connect(main.contrast_filter)
preview.currentIndexChanged.connect(main.display_image_choice)
sepia.clicked.connect(main.sepia)
solarize.clicked.connect(main.solarize)
invert.clicked.connect(main.invert)
vignette.clicked.connect(main.vignette)

undo.clicked.connect(main.undo_)
reset_btn.clicked.connect(main.reset_)
save.clicked.connect(main.save_image)
crop_start.clicked.connect(main.start_crop)
crop_confirm.clicked.connect(main.confirm_crop)

# New feature signals
rotate_free.clicked.connect(main.rotate_free_dialog)
auto_enhance.clicked.connect(main.auto_enhance)
resize_btn.clicked.connect(main.resize_dialog)
crop_presets_btn.clicked.connect(main.crop_presets_dialog)
text_btn.clicked.connect(main.text_overlay_dialog)

# Slider signals
slider_saturation.sliderReleased.connect(main.saturation_filter)
slider_hue.sliderReleased.connect(main.hue_filter)
slider_temperature.sliderReleased.connect(main.temperature_filter)

# Zoom signals
zoom_in_btn.clicked.connect(main.zoom_in)
zoom_out_btn.clicked.connect(main.zoom_out)
zoom_slider.sliderMoved.connect(lambda v: main.set_zoom(v))
fit_button.clicked.connect(main.fit_to_window)
zoom_actual_btn.clicked.connect(main.zoom_actual)

# Update info bar after image loads
widget.currentItemChanged.connect(lambda: main.get_image_info())

# Drawing signals
brush_btn.clicked.connect(lambda: main.start_drawing_tool("brush"))
eraser_btn.clicked.connect(lambda: main.start_drawing_tool("eraser"))
line_btn.clicked.connect(lambda: main.start_drawing_tool("line"))
arrow_btn.clicked.connect(lambda: main.start_drawing_tool("arrow"))
rect_btn.clicked.connect(lambda: main.start_drawing_tool("rectangle"))
circle_btn.clicked.connect(lambda: main.start_drawing_tool("circle"))
clear_draw.clicked.connect(main.image_label.clear_drawings)
apply_draw.clicked.connect(main.apply_drawing)

brush_slider.sliderReleased.connect(lambda: main.set_brush_size(brush_slider.value()))

def pick_brush_color():
    from PyQt5.QtWidgets import QColorDialog
    color = QColorDialog.getColor()
    if color.isValid():
        main.set_brush_color(color)

color_btn.clicked.connect(pick_brush_color)

# Sticker signals
sticker_star.clicked.connect(lambda: main.add_sticker("star"))
sticker_heart.clicked.connect(lambda: main.add_sticker("heart"))
sticker_arrow.clicked.connect(lambda: main.add_sticker("arrow_up"))

# Image label drawing mode - handle clicks to stop
image_label.mousePressEvent

def prompt_click():
    text_box.setEnabled(True)
    generate_image.show()
    prompt.hide()
    
prompt.clicked.connect(prompt_click)

def generate_image_click():
    main.generate_img(text_box.text())
    text_box.setEnabled(False)
    generate_image.hide()
    prompt.show()
    
generate_image.clicked.connect(generate_image_click)

# Drag & drop
def _load_images_from_paths(paths):
    image_files = []
    for path in paths:
        path = path.strip()
        if os.path.isdir(path):
            for f in sorted(os.listdir(path)):
                if os.path.splitext(f)[1].lower() in SUPPORTED_EXTS:
                    image_files.append(os.path.join(path, f))
        elif os.path.isfile(path) and os.path.splitext(path)[1].lower() in SUPPORTED_EXTS:
            image_files.append(path)
    if not image_files: return
    widget.clear()
    for filepath in image_files:
        item = QListWidgetItem(os.path.basename(filepath))
        item.setData(Qt.UserRole, filepath)
        widget.addItem(item)
    widget.setCurrentRow(0)

def _canvas_drag_enter(event):
    if event.mimeData().hasUrls():
        for url in event.mimeData().urls():
            p = url.toLocalFile()
            if os.path.isdir(p) or os.path.splitext(p)[1].lower() in SUPPORTED_EXTS:
                image_label.setStyleSheet(
                    image_label.styleSheet() +
                    " QLabel#image_label { border: 2px dashed #C8A96E; }")
                event.acceptProposedAction()
                return
    event.ignore()

def _canvas_drag_leave(event):
    apply_theme(current_theme[0])

def _canvas_drop(event):
    apply_theme(current_theme[0])
    paths = [url.toLocalFile() for url in event.mimeData().urls()]
    _load_images_from_paths(paths)
    event.acceptProposedAction()

image_label.setAcceptDrops(True)
image_label.dragEnterEvent = _canvas_drag_enter
image_label.dragLeaveEvent = _canvas_drag_leave
image_label.dropEvent      = _canvas_drop

main_window.show()
app.exec_()
