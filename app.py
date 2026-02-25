from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QSlider, QGroupBox, QListWidget, QLabel, QVBoxLayout, QPushButton, QComboBox, QListWidgetItem
from PyQt5.QtCore import Qt
import os, sys
from Crop import CropLabel
from functions import ImageEditor

SUPPORTED_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".webp"}

os.environ["QT_LOGGING_RULES"] = "*.debug=false;qt.qpa.*=false"
app = QApplication(sys.argv)

#  THEME STYLESHEETS
def dark_theme(accent, accent_hover, accent_pressed,
               bg="#0F0F0F", sidebar="#141414", canvas="#0A0A0A",
               groupbox="#1A1A1A", border="#2E2E2E", text="#E0E0E0",
               subtext="#AAAAAA", divider_color="#2A2A2A", btn_bg="#1C1C1C"):
    return f"""
    * {{ font-family: 'Courier New', monospace; color: {text}; }}
    QWidget {{ background-color: {bg}; }}
    QWidget#titlebar {{ background-color: {sidebar}; border-bottom: 1px solid {divider_color}; }}
    QLabel#app_title {{ color: {accent}; font-size: 13px; font-weight: bold; letter-spacing: 4px; background: transparent; }}
    QLabel#app_subtitle {{ color: {divider_color}; font-size: 9px; letter-spacing: 3px; background: transparent; }}
    QPushButton#win_btn {{ background-color: transparent; color: {subtext}; border: none; font-size: 14px; padding: 0px; min-width: 32px; max-width: 32px; min-height: 32px; max-height: 32px; border-radius: 0px; }}
    QPushButton#win_btn:hover {{ background-color: {groupbox}; color: {text}; }}
    QPushButton#win_close {{ background-color: transparent; color: {subtext}; border: none; font-size: 14px; padding: 0px; min-width: 32px; max-width: 32px; min-height: 32px; max-height: 32px; border-radius: 0px; }}
    QPushButton#win_close:hover {{ background-color: #C0392B; color: #FFFFFF; }}
    QGroupBox#sidebar {{ background-color: {sidebar}; border: 1px solid {divider_color}; border-radius: 0px; margin-top: 0px; padding: 10px 8px; }}
    QGroupBox#canvas {{ background-color: {canvas}; border: 1px solid {divider_color}; border-radius: 0px; }}
    QGroupBox {{ background-color: {groupbox}; border: 1px solid {border}; border-radius: 3px; font-size: 10px; font-weight: bold; letter-spacing: 2px; color: #666666; margin-top: 12px; padding-top: 8px; }}
    QGroupBox::title {{ subcontrol-origin: margin; subcontrol-position: top left; padding: 0 6px; color: #555555; letter-spacing: 2px; }}
    QListWidget {{ background-color: {bg}; border: 1px solid {divider_color}; border-radius: 2px; font-size: 11px; color: {subtext}; padding: 4px; outline: none; }}
    QListWidget::item {{ padding: 5px 8px; border-bottom: 1px solid {groupbox}; }}
    QListWidget::item:selected {{ background-color: {accent}; color: #0F0F0F; border-radius: 2px; }}
    QListWidget::item:hover:!selected {{ background-color: {groupbox}; }}
    QPushButton {{ background-color: {btn_bg}; color: {text}; border: 1px solid {border}; border-radius: 2px; padding: 7px 12px; font-size: 10px; font-weight: bold; letter-spacing: 1.5px; }}
    QPushButton:hover {{ background-color: {accent}; color: #0F0F0F; border-color: {accent}; }}
    QPushButton:pressed {{ background-color: {accent_pressed}; color: #0F0F0F; }}
    QPushButton:disabled {{ background-color: {bg}; color: #333333; border-color: {groupbox}; }}
    QPushButton#folder_btn {{ background-color: {accent}; color: #0F0F0F; border: none; letter-spacing: 2px; font-size: 11px; padding: 9px 12px; }}
    QPushButton#folder_btn:hover {{ background-color: {accent_hover}; }}
    QPushButton#folder_btn:pressed {{ background-color: {accent_pressed}; }}
    QPushButton#save_btn {{ background-color: #2A3A2A; color: #6EBF6E; border: 1px solid #3A5A3A; letter-spacing: 2px; }}
    QPushButton#save_btn:hover {{ background-color: #6EBF6E; color: #0F0F0F; border-color: #6EBF6E; }}
    QPushButton#save_btn:disabled {{ background-color: {bg}; color: #2A3A2A; border-color: {groupbox}; }}
    QPushButton#crop_btn {{ background-color: #1C2A3A; color: #6EA8D0; border: 1px solid #2A4A6A; }}
    QPushButton#crop_btn:hover {{ background-color: #6EA8D0; color: #0F0F0F; border-color: #6EA8D0; }}
    QPushButton#crop_btn:disabled {{ background-color: {bg}; color: #1C2A3A; border-color: {groupbox}; }}
    QPushButton#util_btn {{ background-color: {btn_bg}; color: #888888; border: 1px solid {divider_color}; }}
    QPushButton#util_btn:hover {{ background-color: #888888; color: #0F0F0F; }}
    QPushButton#util_btn:disabled {{ background-color: {bg}; color: #333333; border-color: {groupbox}; }}
    QComboBox {{ background-color: {btn_bg}; border: 1px solid {border}; border-radius: 2px; padding: 6px 10px; font-size: 10px; letter-spacing: 1.5px; color: {subtext}; }}
    QComboBox:hover {{ border-color: {accent}; }}
    QComboBox::drop-down {{ border: none; width: 24px; }}
    QComboBox::down-arrow {{ width: 8px; height: 8px; border-left: 1px solid #666; border-bottom: 1px solid #666; margin-top: -3px; }}
    QComboBox QAbstractItemView {{ background-color: {groupbox}; border: 1px solid {border}; selection-background-color: {accent}; selection-color: #0F0F0F; outline: none; }}
    QComboBox#theme_combo {{ background-color: {btn_bg}; color: {accent}; border: 1px solid {accent}; font-size: 9px; font-weight: bold; letter-spacing: 2px; padding: 5px 10px; min-width: 130px; }}
    QComboBox#theme_combo:hover {{ background-color: {accent}; color: #0F0F0F; }}
    QComboBox#theme_combo QAbstractItemView {{ background-color: {groupbox}; border: 1px solid {accent}; selection-background-color: {accent}; selection-color: #0F0F0F; color: {text}; }}
    QSlider::groove:horizontal {{ height: 3px; background: {divider_color}; border-radius: 2px; }}
    QSlider::handle:horizontal {{ background: {accent}; border: none; width: 14px; height: 14px; margin: -6px 0; border-radius: 7px; }}
    QSlider::handle:horizontal:hover {{ background: {accent_hover}; width: 16px; height: 16px; margin: -7px 0; border-radius: 8px; }}
    QSlider::sub-page:horizontal {{ background: {accent}; border-radius: 2px; height: 3px; }}
    QScrollBar:vertical {{ background: {bg}; width: 6px; border: none; }}
    QScrollBar::handle:vertical {{ background: {border}; border-radius: 3px; min-height: 20px; }}
    QScrollBar::handle:vertical:hover {{ background: {accent}; }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
    QLabel#footer {{ color: #333333; font-size: 10px; letter-spacing: 1px; border-top: 1px solid {groupbox}; padding-top: 4px; }}
    QLabel#divlabel {{ color: {border}; font-size: 9px; letter-spacing: 3px; padding-top: 6px; }}
    QLabel#image_label {{ background-color: {canvas}; border: 1px solid {divider_color}; }}
"""

def light_theme(accent, accent_hover, accent_pressed,
                bg="#F5F5F5", sidebar="#EBEBEB", canvas="#FAFAFA",
                groupbox="#E8E8E8", border="#CCCCCC", text="#1A1A1A",
                subtext="#555555", divider_color="#D0D0D0", btn_bg="#FFFFFF"):
    return f"""
    * {{ font-family: 'Courier New', monospace; color: {text}; }}
    QWidget {{ background-color: {bg}; }}
    QWidget#titlebar {{ background-color: {sidebar}; border-bottom: 1px solid {divider_color}; }}
    QLabel#app_title {{ color: {accent}; font-size: 13px; font-weight: bold; letter-spacing: 4px; background: transparent; }}
    QLabel#app_subtitle {{ color: {border}; font-size: 9px; letter-spacing: 3px; background: transparent; }}
    QPushButton#win_btn {{ background-color: transparent; color: {subtext}; border: none; font-size: 14px; padding: 0px; min-width: 32px; max-width: 32px; min-height: 32px; max-height: 32px; border-radius: 0px; }}
    QPushButton#win_btn:hover {{ background-color: {groupbox}; color: {text}; }}
    QPushButton#win_close {{ background-color: transparent; color: {subtext}; border: none; font-size: 14px; padding: 0px; min-width: 32px; max-width: 32px; min-height: 32px; max-height: 32px; border-radius: 0px; }}
    QPushButton#win_close:hover {{ background-color: #C0392B; color: #FFFFFF; }}
    QGroupBox#sidebar {{ background-color: {sidebar}; border: 1px solid {divider_color}; border-radius: 0px; margin-top: 0px; padding: 10px 8px; }}
    QGroupBox#canvas {{ background-color: {canvas}; border: 1px solid {divider_color}; border-radius: 0px; }}
    QGroupBox {{ background-color: {groupbox}; border: 1px solid {border}; border-radius: 3px; font-size: 10px; font-weight: bold; letter-spacing: 2px; color: #999999; margin-top: 12px; padding-top: 8px; }}
    QGroupBox::title {{ subcontrol-origin: margin; subcontrol-position: top left; padding: 0 6px; color: #AAAAAA; letter-spacing: 2px; }}
    QListWidget {{ background-color: {btn_bg}; border: 1px solid {divider_color}; border-radius: 2px; font-size: 11px; color: {subtext}; padding: 4px; outline: none; }}
    QListWidget::item {{ padding: 5px 8px; border-bottom: 1px solid {groupbox}; }}
    QListWidget::item:selected {{ background-color: {accent}; color: #FFFFFF; border-radius: 2px; }}
    QListWidget::item:hover:!selected {{ background-color: {groupbox}; }}
    QPushButton {{ background-color: {btn_bg}; color: {text}; border: 1px solid {border}; border-radius: 2px; padding: 7px 12px; font-size: 10px; font-weight: bold; letter-spacing: 1.5px; }}
    QPushButton:hover {{ background-color: {accent}; color: #FFFFFF; border-color: {accent}; }}
    QPushButton:pressed {{ background-color: {accent_pressed}; color: #FFFFFF; }}
    QPushButton:disabled {{ background-color: {groupbox}; color: {border}; border-color: {divider_color}; }}
    QPushButton#folder_btn {{ background-color: {accent}; color: #FFFFFF; border: none; letter-spacing: 2px; font-size: 11px; padding: 9px 12px; }}
    QPushButton#folder_btn:hover {{ background-color: {accent_hover}; }}
    QPushButton#folder_btn:pressed {{ background-color: {accent_pressed}; }}
    QPushButton#save_btn {{ background-color: #EAF5EA; color: #2E7D32; border: 1px solid #A5D6A7; letter-spacing: 2px; }}
    QPushButton#save_btn:hover {{ background-color: #2E7D32; color: #FFFFFF; border-color: #2E7D32; }}
    QPushButton#save_btn:disabled {{ background-color: {groupbox}; color: {border}; border-color: {divider_color}; }}
    QPushButton#crop_btn {{ background-color: #E8F4FB; color: #1565C0; border: 1px solid #90CAF9; }}
    QPushButton#crop_btn:hover {{ background-color: #1565C0; color: #FFFFFF; border-color: #1565C0; }}
    QPushButton#crop_btn:disabled {{ background-color: {groupbox}; color: {border}; border-color: {divider_color}; }}
    QPushButton#util_btn {{ background-color: {btn_bg}; color: #888888; border: 1px solid {divider_color}; }}
    QPushButton#util_btn:hover {{ background-color: #888888; color: #FFFFFF; }}
    QPushButton#util_btn:disabled {{ background-color: {groupbox}; color: {border}; border-color: {divider_color}; }}
    QComboBox {{ background-color: {btn_bg}; border: 1px solid {border}; border-radius: 2px; padding: 6px 10px; font-size: 10px; letter-spacing: 1.5px; color: {subtext}; }}
    QComboBox:hover {{ border-color: {accent}; }}
    QComboBox::drop-down {{ border: none; width: 24px; }}
    QComboBox::down-arrow {{ width: 8px; height: 8px; border-left: 1px solid #888; border-bottom: 1px solid #888; margin-top: -3px; }}
    QComboBox QAbstractItemView {{ background-color: {btn_bg}; border: 1px solid {border}; selection-background-color: {accent}; selection-color: #FFFFFF; outline: none; }}
    QComboBox#theme_combo {{ background-color: {btn_bg}; color: {accent}; border: 1px solid {accent}; font-size: 9px; font-weight: bold; letter-spacing: 2px; padding: 5px 10px; min-width: 130px; }}
    QComboBox#theme_combo:hover {{ background-color: {accent}; color: #FFFFFF; }}
    QComboBox#theme_combo QAbstractItemView {{ background-color: {btn_bg}; border: 1px solid {accent}; selection-background-color: {accent}; selection-color: #FFFFFF; color: {text}; }}
    QSlider::groove:horizontal {{ height: 3px; background: {divider_color}; border-radius: 2px; }}
    QSlider::handle:horizontal {{ background: {accent}; border: none; width: 14px; height: 14px; margin: -6px 0; border-radius: 7px; }}
    QSlider::handle:horizontal:hover {{ background: {accent_hover}; width: 16px; height: 16px; margin: -7px 0; border-radius: 8px; }}
    QSlider::sub-page:horizontal {{ background: {accent}; border-radius: 2px; height: 3px; }}
    QScrollBar:vertical {{ background: {bg}; width: 6px; border: none; }}
    QScrollBar::handle:vertical {{ background: {border}; border-radius: 3px; min-height: 20px; }}
    QScrollBar::handle:vertical:hover {{ background: {accent}; }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
    QLabel#footer {{ color: {border}; font-size: 10px; letter-spacing: 1px; border-top: 1px solid {divider_color}; padding-top: 4px; }}
    QLabel#divlabel {{ color: {border}; font-size: 9px; letter-spacing: 3px; padding-top: 6px; }}
    QLabel#image_label {{ background-color: {canvas}; border: 1px solid {divider_color}; }}
"""
# 5 Themes
THEMES = {
    "⬛  MIDNIGHT GOLD": dark_theme(
        accent="#C8A96E", accent_hover="#E0C080", accent_pressed="#A8894E"
    ),
    "🌆  CYBERPUNK": dark_theme(
        accent="#00FFF0", accent_hover="#80FFFA", accent_pressed="#00C8C0",
        bg="#0A0A12", sidebar="#0E0E1A", canvas="#060610",
        groupbox="#12121E", border="#1E1E3A", divider_color="#1A1A30",
        btn_bg="#10101C", text="#E0E8FF", subtext="#8899CC"
    ),
    "🌲  FOREST": dark_theme(
        accent="#5DBB63", accent_hover="#82D485", accent_pressed="#3A8A40",
        bg="#0C110D", sidebar="#111A12", canvas="#090D0A",
        groupbox="#161E17", border="#253026", divider_color="#1E2B1F",
        btn_bg="#141C15", text="#D4E8D0", subtext="#8AAE86"
    ),
    "🌸  PEACH BLOOM": light_theme(
        accent="#E8735A", accent_hover="#F09080", accent_pressed="#C05040",
        bg="#FDF6F0", sidebar="#F5EBE0", canvas="#FFF9F5",
        groupbox="#EDE0D4", border="#D4BDB0", divider_color="#E0CABB",
        btn_bg="#FFFFFF", text="#3A2820", subtext="#7A5A50"
    ),
    "📜  SEPIA": light_theme(
        accent="#8B4513", accent_hover="#A0522D", accent_pressed="#6B3410",
        bg="#F4ECD8", sidebar="#EDE0C4", canvas="#FAF3E0",
        groupbox="#E5D5B0", border="#C8B888", divider_color="#D4C090",
        btn_bg="#FBF5E6", text="#2C1A0E", subtext="#6B5030"
    ),
}

current_theme = [list(THEMES.keys())[0]]

def apply_theme(name):
    app.setStyleSheet(THEMES[name])

apply_theme(current_theme[0])

#  CUSTOM TITLE BAR
class TitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setObjectName("titlebar")
        self.setFixedHeight(40)
        self._drag_pos = None
        self._maximized = False

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 0, 0, 0)
        layout.setSpacing(0)

        # App icon / name
        title = QLabel("PIXEDIT")
        title.setObjectName("app_title")
        subtitle = QLabel("  //  IMAGE EDITOR")
        subtitle.setObjectName("app_subtitle")

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addStretch()

        # Window control buttons
        btn_min = QPushButton("─")
        btn_min.setObjectName("win_btn")
        btn_min.setToolTip("Minimize")
        btn_min.clicked.connect(parent.showMinimized)

        btn_max = QPushButton("□")
        btn_max.setObjectName("win_btn")
        btn_max.setToolTip("Maximize / Restore")

        def toggle_max():
            if self._maximized:
                parent.showNormal()
                btn_max.setText("□")
                self._maximized = False
            else:
                parent.showMaximized()
                btn_max.setText("❐")
                self._maximized = True

        btn_max.clicked.connect(toggle_max)

        btn_close = QPushButton("✕")
        btn_close.setObjectName("win_close")
        btn_close.setToolTip("Close")
        btn_close.clicked.connect(parent.close)

        layout.addWidget(btn_min)
        layout.addWidget(btn_max)
        layout.addWidget(btn_close)

    # drag to move
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.parent.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self._drag_pos:
            self.parent.move(event.globalPos() - self._drag_pos)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None

    def mouseDoubleClickEvent(self, event):
        # Double-click title bar to maximise/restore
        if self._maximized:
            self.parent.showNormal()
            self._maximized = False
        else:
            self.parent.showMaximized()
            self._maximized = True

#  MAIN WINDOW  (frameless)
main_window = QWidget()
main_window.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
main_window.resize(1100, 820)

# build UI 
title_bar = TitleBar(main_window)

footer = QLabel("© PIXEDIT  ·  Basic Image Editing  ·  Made by Nikhil 🫡")
footer.setObjectName("footer")
footer.setAlignment(Qt.AlignCenter)
footer.setFixedHeight(28)

column1 = QGroupBox()
column1.setObjectName("sidebar")
column2 = QGroupBox()
column2.setObjectName("canvas")

vboxmain = QVBoxLayout()
vboxmain.setSpacing(4)
vbox2main = QVBoxLayout()

folder = QPushButton("⊕  Select Folder")
folder.setObjectName("folder_btn")

widget = QListWidget()
# widget.setFixedHeight(100)

preview = QComboBox()
preview.setEditable(True)
preview.lineEdit().setAlignment(Qt.AlignCenter)
preview.lineEdit().setReadOnly(True)
preview.addItem("— PREVIEW —")
preview.addItem("Original")
preview.addItem("Left Rotate")
preview.addItem("Right Rotate")
preview.addItem("Mirror")
preview.addItem("Flip Vertical")
preview.addItem("B/W")
preview.addItem("Color")
preview.addItem("Blur")
preview.addItem("Sharpen")

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
emboss          = QPushButton("▩  Emboss")
vignette        = QPushButton("◌◌  Vignette")

brightness = QGroupBox("BRIGHTNESS")
slider = QSlider(Qt.Horizontal)
slider.setFocusPolicy(Qt.StrongFocus)
slider.setTickPosition(QSlider.TicksBothSides)
slider.setTickInterval(10)
slider.setSingleStep(1)
slider.setRange(-50, 50)
vbox = QVBoxLayout()
vbox.addWidget(slider)
brightness.setLayout(vbox)

contrast = QGroupBox("CONTRAST")
slider2 = QSlider(Qt.Horizontal)
slider2.setFocusPolicy(Qt.StrongFocus)
slider2.setTickPosition(QSlider.TicksBothSides)
slider2.setTickInterval(10)
slider2.setSingleStep(1)
slider2.setRange(-50, 50)
vbox2 = QVBoxLayout()
vbox2.addWidget(slider2)
contrast.setLayout(vbox2)

vboxmain.addWidget(folder)
vboxmain.addWidget(widget)
vboxmain.addWidget(divider("PREVIEW"))
vboxmain.addWidget(preview)
vboxmain.addWidget(divider("TRANSFORM"))
vboxmain.addWidget(left_rotate)
vboxmain.addWidget(right_rotate)
vboxmain.addWidget(flip_horizontal)
vboxmain.addWidget(flip_vertical)
vboxmain.addWidget(divider("FILTERS"))
vboxmain.addWidget(grayscale)
vboxmain.addWidget(color)
vboxmain.addWidget(blur)
vboxmain.addWidget(sharpen)
vboxmain.addWidget(divider("ADJUST"))
vboxmain.addWidget(brightness)
vboxmain.addWidget(contrast)
vboxmain.addWidget(divider("NEW FEATURES"))
vboxmain.addWidget(sepia)
vboxmain.addWidget(solarize)
vboxmain.addWidget(invert)
vboxmain.addWidget(emboss)
vboxmain.addWidget(vignette)

save = QPushButton("⬇  Save")
save.setObjectName("save_btn")
save.setFixedWidth(110)

image_label = CropLabel()

undo = QPushButton("↩  Undo")
undo.setObjectName("util_btn")
undo.setFixedWidth(100)

reset = QPushButton("⟳  Reset")
reset.setObjectName("util_btn")
reset.setFixedWidth(100)

crop_start = QPushButton("✂  Crop")
crop_start.setObjectName("crop_btn")
crop_start.setFixedWidth(100)

crop_confirm = QPushButton("✔  Confirm")
crop_confirm.setObjectName("crop_btn")
crop_confirm.setFixedWidth(110)

theme_combo = QComboBox()
theme_combo.setObjectName("theme_combo")
theme_combo.setFixedWidth(160)
theme_combo.setToolTip("Select a theme")
for name in THEMES:
    theme_combo.addItem(name)
theme_combo.setCurrentText(current_theme[0])

def on_theme_changed(idx):
    name = theme_combo.itemText(idx)
    current_theme[0] = name
    apply_theme(name)

theme_combo.currentIndexChanged.connect(on_theme_changed)

hbox = QHBoxLayout()
hbox.setSpacing(6)
hbox.addWidget(undo)
hbox.addWidget(reset)
hbox.addWidget(crop_start)
hbox.addWidget(crop_confirm)
hbox.addStretch()
hbox.addWidget(theme_combo)
hbox.addWidget(save)

vbox2main.addLayout(hbox)
vbox2main.addWidget(image_label)
vbox2main.addWidget(footer)

column1.setLayout(vboxmain)
column2.setLayout(vbox2main)

# content area layout
content = QWidget()
content_layout = QHBoxLayout(content)
content_layout.setSpacing(2)
content_layout.setContentsMargins(6, 4, 6, 6)

col1 = QVBoxLayout()
col2 = QVBoxLayout()
col3 = QVBoxLayout()
col4 = QVBoxLayout()

col1.addWidget(column1)
col3.addWidget(column2)

content_layout.addLayout(col1, 20)
content_layout.addLayout(col2, 1)
content_layout.addLayout(col3, 78)
content_layout.addLayout(col4, 1)

# root layout: title bar on top, content below
root_layout = QVBoxLayout(main_window)
root_layout.setContentsMargins(0, 0, 0, 0)
root_layout.setSpacing(0)
root_layout.addWidget(title_bar)
root_layout.addWidget(content)

# wire up ImageEditor
main = ImageEditor(widget, image_label, slider, slider2, preview, left_rotate, right_rotate, flip_horizontal, flip_vertical, grayscale, color, blur, sharpen, brightness, contrast, sepia, solarize, invert, emboss, vignette, undo, reset, crop_start, crop_confirm, save, main_window)
main.setup_shortcuts()
# Disable until image loaded
for w in [preview, left_rotate, right_rotate, flip_horizontal, flip_vertical, grayscale, color, blur, sharpen, brightness, contrast, sepia, solarize, invert, emboss, vignette, undo, reset, crop_start, crop_confirm, save]:
    w.setEnabled(False)

folder.clicked.connect(main.getfiles)

def _on_item_changed(current, previous):
    if current is None: return
    full_path = current.data(Qt.UserRole)
    if full_path and os.path.isfile(full_path):
        # Temporarily swap item text to full path so load_image can open it,
        # then restore the basename display name
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
emboss.clicked.connect(main.emboss)
vignette.clicked.connect(main.vignette)

undo.clicked.connect(main.undo_)
reset.clicked.connect(main.reset_)
save.clicked.connect(main.save_image)
crop_start.clicked.connect(main.start_crop)
crop_confirm.clicked.connect(main.confirm_crop)
#  DRAG & DROP
def _load_images_from_paths(paths):
    image_files = []
    for path in paths:
        path = path.strip()
        if os.path.isdir(path):
            # Dropped a folder — grab all supported images inside it
            for f in sorted(os.listdir(path)):
                if os.path.splitext(f)[1].lower() in SUPPORTED_EXTS:
                    image_files.append(os.path.join(path, f))
        elif os.path.isfile(path) and os.path.splitext(path)[1].lower() in SUPPORTED_EXTS:
            image_files.append(path)
    if not image_files: return
    # Populate the list widget (same pattern as ImageEditor.getfiles)
    widget.clear()
    for filepath in image_files:
        item = QListWidgetItem(os.path.basename(filepath))
        item.setData(Qt.UserRole, filepath)   # store full path in UserRole
        widget.addItem(item)
    # Select and load the first image
    widget.setCurrentRow(0)

def _enable_drop_on(w):
    w.setAcceptDrops(True)
    def drag_enter(event):
        if event.mimeData().hasUrls():
            # Accept only if at least one URL is a supported file or directory
            for url in event.mimeData().urls():
                p = url.toLocalFile()
                if os.path.isdir(p) or os.path.splitext(p)[1].lower() in SUPPORTED_EXTS:
                    event.acceptProposedAction()
                    return
        event.ignore()

    def drop(event):
        paths = [url.toLocalFile() for url in event.mimeData().urls()]
        _load_images_from_paths(paths)
        event.acceptProposedAction()

    w.dragEnterEvent = drag_enter
    w.dropEvent = drop

# Enable drop on the canvas
_enable_drop_on(image_label)

# Visual hint on the canvas while dragging over it
_orig_drag_move = image_label.dragMoveEvent if hasattr(image_label, "dragMoveEvent") else None

def _canvas_drag_enter(event):
    if event.mimeData().hasUrls():
        for url in event.mimeData().urls():
            p = url.toLocalFile()
            if os.path.isdir(p) or os.path.splitext(p)[1].lower() in SUPPORTED_EXTS:
                image_label.setStyleSheet(
                    image_label.styleSheet() +
                    " QLabel#image_label { border: 2px dashed #C8A96E; }"
                )
                event.acceptProposedAction()
                return
    event.ignore()

def _canvas_drag_leave(event):
    # Strip the dashed border hint — re-apply theme to reset
    apply_theme(current_theme[0])

def _canvas_drop(event):
    apply_theme(current_theme[0])   # reset border first
    paths = [url.toLocalFile() for url in event.mimeData().urls()]
    _load_images_from_paths(paths)
    event.acceptProposedAction()

image_label.dragEnterEvent = _canvas_drag_enter
image_label.dragLeaveEvent = _canvas_drag_leave
image_label.dropEvent       = _canvas_drop

main_window.show()
app.exec_()
