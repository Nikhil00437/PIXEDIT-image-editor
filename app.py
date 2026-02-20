from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QSlider, QGroupBox, QListWidget, QLabel, QVBoxLayout, QPushButton, QComboBox
from PyQt5.QtCore import Qt
import os, sys
from Crop import CropLabel
from functions import ImageEditor

os.environ["QT_LOGGING_RULES"] = "*.debug=false;qt.qpa.*=false"
app = QApplication(sys.argv)
main_window = QWidget()
main_window.setWindowTitle("Image Editing App")
main_window.resize(1000, 800)
footer = QLabel("""© Just a simple app that can provide basic image editing features.
                Made by Nikhil🫡🫡        """)
footer.setAlignment(Qt.AlignCenter)
footer.setFixedHeight(30)

footer.setStyleSheet("""
    font-size: 12px;
""")

column1 = QGroupBox()
column2 = QGroupBox()

vboxmain = QVBoxLayout()
vbox2main = QVBoxLayout()

folder = QPushButton("Select Folder")
widget = QListWidget()
# ComboBox to display the images in the original size or fit to the label
preview = QComboBox()
preview.setEditable(True)
preview.lineEdit().setAlignment(Qt.AlignCenter)
preview.lineEdit().setReadOnly(True)
preview.addItem("Select")
preview.addItem("Original")
preview.addItem("Left Rotate")
preview.addItem("Right Rotate")
preview.addItem("Mirror")
preview.addItem("Flip Vertical")
preview.addItem("B/W")
preview.addItem("Color")
preview.addItem("Blur")
preview.addItem("Sharpen")
#########################
left_rotate = QPushButton("Left")
right_rotate = QPushButton("Right")
flip_horizontal = QPushButton("Mirror")
flip_vertical = QPushButton("Upside Down")
grayscale = QPushButton("B/W")
color = QPushButton("Color")
blur = QPushButton("Blur")
sharpen = QPushButton("Sharpen")
# Slider for Brightness
brightness = QGroupBox("Brightness")
slider = QSlider(Qt.Horizontal)
slider.setFocusPolicy(Qt.StrongFocus)
slider.setTickPosition(QSlider.TicksBothSides)
slider.setTickInterval(10)
slider.setSingleStep(1)
slider.setRange(-50,50)
vbox = QVBoxLayout()
vbox.addWidget(slider)
brightness.setLayout(vbox)
# Slider for Contrast
contrast = QGroupBox("Contrast")
slider2 = QSlider(Qt.Horizontal)
slider2.setFocusPolicy(Qt.StrongFocus)
slider2.setTickPosition(QSlider.TicksBothSides)
slider2.setTickInterval(10)
slider2.setSingleStep(1)
slider2.setRange(-50,50)
vbox2 = QVBoxLayout()
vbox2.addWidget(slider2)
contrast.setLayout(vbox2)

vboxmain.addWidget(folder)
vboxmain.addWidget(widget)
vboxmain.addWidget(preview)
vboxmain.addWidget(left_rotate)
vboxmain.addWidget(right_rotate)
vboxmain.addWidget(flip_horizontal)
vboxmain.addWidget(flip_vertical)
vboxmain.addWidget(grayscale)
vboxmain.addWidget(color)
vboxmain.addWidget(blur)
vboxmain.addWidget(sharpen)
vboxmain.addWidget(brightness)
vboxmain.addWidget(contrast)

save = QPushButton("Save Image")
save.setFixedWidth(100)
# Placeholder for the image display
image_label = CropLabel()

undo = QPushButton("Undo")
undo.setFixedWidth(100)
reset = QPushButton("Reset")
reset.setFixedWidth(100)
crop_start = QPushButton("Crop Start")
crop_start.setFixedWidth(100)
crop_confirm = QPushButton("Crop Confirm")
crop_confirm.setFixedWidth(100)

hbox = QHBoxLayout()
hbox.addWidget(undo)
hbox.addWidget(reset)
hbox.addWidget(crop_start)
hbox.addWidget(crop_confirm)
hbox.addWidget(save, alignment=Qt.AlignRight)
vbox2main.addLayout(hbox)
vbox2main.addWidget(image_label)
vbox2main.addWidget(footer)

column1.setLayout(vboxmain)
column2.setLayout(vbox2main)
# main Layout initialization
main_layout = QHBoxLayout()  
# Column Layouts initialization
col1 = QVBoxLayout()
col2 = QVBoxLayout()
col3 = QVBoxLayout()
col4 = QVBoxLayout()
# Adding widgets to the first column
col1.addWidget(column1)
col3.addWidget(column2)
# Adding columns to the main layout with size percentages
main_layout.addLayout(col1,20)
main_layout.addLayout(col2,1)
main_layout.addLayout(col3,78)
main_layout.addLayout(col4,1)

main_window.setLayout(main_layout)

# Connecting buttons to functions
main = ImageEditor(widget, image_label, slider, slider2, preview, left_rotate, right_rotate, flip_horizontal, flip_vertical, grayscale, color, blur, sharpen, brightness, contrast, undo, reset, crop_start, crop_confirm, save, main_window)
# Disabling the buttons till the image is loaded
preview.setEnabled(False)
left_rotate.setEnabled(False)
right_rotate.setEnabled(False)
flip_horizontal.setEnabled(False)
flip_vertical.setEnabled(False)
grayscale.setEnabled(False)
color.setEnabled(False)
blur.setEnabled(False)
sharpen.setEnabled(False)
brightness.setEnabled(False)
contrast.setEnabled(False)
undo.setEnabled(False)
reset.setEnabled(False)
crop_start.setEnabled(False)
crop_confirm.setEnabled(False)
save.setEnabled(False)
# for loading image
folder.clicked.connect(main.getfiles)
widget.currentItemChanged.connect(main.load_image)
# Selected Filter
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
# it'll show preview of an image when applied with the features and show u how it looked before u try to apply it
preview.currentIndexChanged.connect(main.display_image_choice)

undo.clicked.connect(main.undo_)
reset.clicked.connect(main.reset_)
save.clicked.connect(main.save_image)
crop_start.clicked.connect(main.start_crop)
crop_confirm.clicked.connect(main.confirm_crop)

main_window.show()
app.exec_()