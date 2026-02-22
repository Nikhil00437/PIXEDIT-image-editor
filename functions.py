from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
import os, tempfile
from PIL import Image, ImageFilter, ImageEnhance
from collections import deque

# All functions to use
class ImageEditor:
    def __init__(self, widget, image_label, slider, slider2, preview, left_rotate, right_rotate, flip_horizontal, flip_vertical, grayscale, color, blur, sharpen, brightness, contrast, undo, reset, crop_start, crop_confirm, save, main_window):
        self.widget = widget
        self.image_label = image_label
        self.slider = slider
        self.slider2 = slider2
        self.preview = preview
        self.left_rotate = left_rotate
        self.right_rotate = right_rotate
        self.flip_horizontal = flip_horizontal
        self.flip_vertical = flip_vertical
        self.grayscale = grayscale
        self.color = color
        self.blur = blur
        self.sharpen = sharpen
        self.brightness = brightness
        self.contrast = contrast
        self.undo = undo
        self.reset = reset
        self.crop_start = crop_start
        self.crop_confirm = crop_confirm
        self.save = save
        self.original = None
        self.edited = None
        self.image_path = None 
        self.last_color = None
        self.main_window = main_window
        self.history = deque(maxlen=20)
        self.file_location = "/edits" 
        self.image_label
    
    def history_append(self):
        if self._guard(): return
        self.history.append(self.edited.copy())

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
        if not self.file_location:
            return
        extensions = [".jpg", ".jpeg", ".png"]
        filenames = self.filter_image(os.listdir(self.file_location), extensions)
        self.widget.clear()
        for filename in filenames:
            self.widget.addItem(filename)

    def load_image(self):
        if self.widget.currentItem() is None:
            return
        selected_image = self.widget.currentItem().text()
        self.image_path = os.path.join(self.file_location, selected_image)
        self.original = Image.open(self.image_path).copy()
        self.edited = self.original.copy()
        # Reset sliders without triggering filter callbacks
        self.slider.blockSignals(True)
        self.slider2.blockSignals(True)
        self.slider.setValue(0)
        self.slider2.setValue(0)
        self.slider.blockSignals(False)
        self.slider2.blockSignals(False)
        self._display_pil(self.edited)
        
    def _display_pil(self, pil_image):
        suffix = ".png"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp_path = tmp.name
        pil_image.save(tmp_path)
        self.image_label.hide()
        pixmap = QPixmap(tmp_path)
        w, h = self.image_label.width(), self.image_label.height()
        pixmap_ = pixmap.scaled(w, h, Qt.KeepAspectRatio)
        self.image_label.setPixmap(pixmap_)
        self.image_label.show()
        self.preview.setEnabled(True)
        self.left_rotate.setEnabled(True)
        self.right_rotate.setEnabled(True)
        self.flip_horizontal.setEnabled(True)
        self.flip_vertical.setEnabled(True)
        self.grayscale.setEnabled(True)
        self.color.setEnabled(True)
        self.blur.setEnabled(True)
        self.sharpen.setEnabled(True)
        self.brightness.setEnabled(True)
        self.contrast.setEnabled(True)
        self.undo.setEnabled(True)
        self.reset.setEnabled(True)
        self.crop_start.setEnabled(True) 
        self.save.setEnabled(True)
        os.unlink(tmp_path)
        
    def save_image(self):
        if self._guard(): return
        save_path, _ = QFileDialog.getSaveFileName(self.main_window, "Save Image", "", "PNG Files (*.png);;JPEG Files (*.jpg *.jpeg)")
        if save_path:
            self.edited.save(save_path)

    def _guard(self):
        return self.edited is None
    
    def undo_(self):
        if self.history:
            self.edited = self.history.pop()
            self._display_pil(self.edited)
        pass
            
    def reset_(self):
        if self._guard(): return
        self.history.clear()
        self.edited = self.original.copy()
        self._display_pil(self.edited)
            
    def left_rotate_filter(self):
        if self._guard(): return
        self.history_append()
        self.edited = self.edited.rotate(90, expand=True)
        self._display_pil(self.edited)

    def right_rotate_filter(self):
        if self._guard(): return
        self.history_append()
        self.edited = self.edited.rotate(-90, expand=True)
        self._display_pil(self.edited)

    def flip_horizontal_filter(self):
        if self._guard(): return
        self.history_append()
        self.edited = self.edited.transpose(Image.FLIP_LEFT_RIGHT)
        self._display_pil(self.edited)

    def flip_vertical_filter(self):
        if self._guard(): return
        self.history_append()
        self.edited = self.edited.transpose(Image.FLIP_TOP_BOTTOM)
        self._display_pil(self.edited)

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
        # Case 1: Image is grayscale → revert to last color version
        if self.edited.mode == "L" and self.last_color is not None:
            self.edited = self.last_color.copy()
        # Case 2: Image already has color → boost saturation
        else:
            enhancer = ImageEnhance.Color(self.edited)
            self.edited = enhancer.enhance(1.3)
        self._display_pil(self.edited)
        
    def blur_filter(self):
        if self._guard(): return
        self.history_append()
        self.edited = self.edited.filter(ImageFilter.BLUR)
        self._display_pil(self.edited)

    def sharpen_filter(self):
        if self._guard(): return
        self.history_append()
        self.edited = self.edited.filter(ImageFilter.SHARPEN)
        self._display_pil(self.edited)
        
    def brightness_filter(self):
        if self._guard(): return
        self.history_append()
        enhancer = ImageEnhance.Brightness(self.edited)
        self.edited = enhancer.enhance(1 + (self.slider.value() / 50))
        self._display_pil(self.edited)

    def contrast_filter(self):
        if self._guard(): return
        self.history_append()
        enhancer = ImageEnhance.Contrast(self.edited)
        self.edited = enhancer.enhance(1 + (self.slider2.value() / 50))
        self._display_pil(self.edited)
        
    def start_crop(self):
        if self._guard(): return
        self.crop_start.setEnabled(False)
        self.crop_confirm.setEnabled(True)
        self.image_label.enable_crop(True)
        self.image_label.setStatusTip("Draw a rectangle to crop, then press Confirm Crop")

    def confirm_crop(self):
        if self._guard(): return
        rect = self.image_label.crop_rect
        if rect is None:
            return

        # The label may have padding due to aspect-ratio scaling.
        # We need to map label coordinates back to actual image coordinates.
        label_w = self.image_label.width()
        label_h = self.image_label.height()
        img_w, img_h = self.edited.size

        # Compute the scaled image size inside the label (KeepAspectRatio)
        scale = min(label_w / img_w, label_h / img_h)
        scaled_w = img_w * scale
        scaled_h = img_h * scale

        # Offset of the image inside the label (centered)
        offset_x = (label_w - scaled_w) / 2
        offset_y = (label_h - scaled_h) / 2

        # Convert label rect to image coordinates
        x1 = max(0, (rect.left() - offset_x) / scale)
        y1 = max(0, (rect.top() - offset_y) / scale)
        x2 = min(img_w, (rect.right() - offset_x) / scale)
        y2 = min(img_h, (rect.bottom() - offset_y) / scale)

        if x2 <= x1 or y2 <= y1:
            return  # Degenerate selection, ignore

        self.history_append()
        self.edited = self.edited.crop((int(x1), int(y1), int(x2), int(y2)))
        self.image_label.enable_crop(False)
        self.crop_start.setEnabled(True)
        self.crop_confirm.setEnabled(False)
        self._display_pil(self.edited)

    def display_image_choice(self):
        if self._guard(): return
        if self.preview.currentText() == "Original":
           self._display_pil(self.original)
        else:
            mapping = {
                "Left Rotate": lambda: self.original.rotate(90, expand=True),
                "Right Rotate": lambda: self.original.rotate(-90, expand=True),
                "Mirror": lambda: self.original.transpose(Image.FLIP_LEFT_RIGHT),
                "Flip Vertical": lambda: self.original.transpose(Image.FLIP_TOP_BOTTOM),
                "B/W": lambda: self.original.convert("L"),
                "Color": lambda: self.original.convert("RGB"),
                "Blur": lambda: self.original.filter(ImageFilter.BLUR),
                "Sharpen": lambda: self.original.filter(ImageFilter.SHARPEN)
            }
            if self.preview.currentText() in mapping:
                temp = mapping[self.preview.currentText()]()
                self._display_pil(temp)
