# Basic Image Editing 🖼️

A sleek, dark-themed desktop image editor built with **PyQt5** and **Pillow (PIL)**. Load images from a folder, apply transforms, filters, adjustments, crop, undo changes, and save your edits. Features a live preview system and intuitive sidebar controls.

![Screenshot](screenshots/screenshot1.png)
*_(Add your own screenshot here for better visuals!)_*

## ✨ Features

- **📁 Folder-based Workflow**: Select a folder to load all JPG, JPEG, and PNG images into a sidebar list.
- **🖼️ Image Loading**: Click any image in the list to load it onto the canvas.
- **🔄 Transforms**:
  - Left Rotate (↺ 90°)
  - Right Rotate (↻ -90°)
  - Mirror (⇆ Flip Horizontal)
  - Upside Down (⇅ Flip Vertical)
- **🎨 Filters**:
  - B/W (Grayscale) / Color (Toggle back or enhance saturation)
  - Blur (≋ Gaussian Blur)
  - Sharpen (✦ Unsharp Mask)
- **⚙️ Adjustments**:
  - Brightness Slider (-50 to +50)
  - Contrast Slider (-50 to +50)
- **✂️ Crop Tool**: Drag a rectangle on the canvas and confirm to crop.
- **⏪ History & Controls**:
  - Undo (up to 20 steps)
  - Reset to Original
- **👁️ Preview Dropdown**: Quick preview of Original or filter previews applied to the original image.
- **💾 Save**: Export edited image as PNG or JPEG.
- **🎨 Dark Theme**: Custom monospace styling with hover effects and smooth animations.

## 📋 Requirements

- Python 3.6+
- PyQt5 (`pip install PyQt5`)
- Pillow (`pip install Pillow`)

Install dependencies:
```bash
pip install PyQt5 Pillow
