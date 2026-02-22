# PIXEDIT — Image Editor 🖼️

**PIXEDIT** is a basic yet functional GUI image editor built with **Python**, **PyQt5**, and **Pillow (PIL)**. It’s designed to handle common photo editing tasks such as rotation, filters, cropping, brightness/contrast adjustments, and undo/redo support.

---

## 🚀 Features

This editor provides:

- 🗂️ Load and browse images from a folder  
- 🔄 Rotate, flip, and mirror images  
- 🎨 Apply filters: **grayscale**, **blur**, **sharpen**  
- ⚙️ Adjust **brightness** & **contrast**  
- ✂️ Crop images using a drag-select rubber-band tool  
- ↩️ Undo up to 20 steps (history)  
- 💾 Save edited images as **PNG** or **JPEG**

---

## 🧰 Requirements

| Requirement | Minimum Version |
|-------------|-----------------|
| Python      | 3.7+            |
| PyQt5       | 5.15+           |
| Pillow      | 8.0+            |

> Tested on **Windows 10/11**, **macOS 13**, and **Ubuntu 22.04**.

---

## 📦 Installation

Clone the repository:

```bash
git clone https://github.com/Nikhil00437/PIXEDIT-image-editor.git
cd PIXEDIT-image-editor
````

> (Optional) Create and activate a virtual environment:

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## ▶️ Running the Editor

```bash
python app.py
```

After launching, the editor window opens and allows you to browse, edit, and save images.

---

## 🧭 Usage Walk-through

1. **Open a Folder** – Pick a directory with `.jpg`, `.jpeg`, or `.png` files.
2. **Load an Image** – Select an image to display it.
3. **Apply Transformations** –

   * Rotate left/right
   * Mirror horizontally/vertically
4. **Filters & Adjustments** –

   * Grayscale, blur, sharpen
   * Brightness & contrast sliders
5. **Crop** – Click *Crop*, drag to select, then confirm.
6. **Undo/Redo** – Step back through edits.
7. **Save** – Export work as PNG or JPEG.

---

## 📁 Project Structure

```
PIXEDIT-image-editor/
├── app.py            # Main application entry point
├── Crop.py           # Rubber-band cropping widget
├── functions.py      # Core image logic (Pillow + history)
├── requirements.txt  # Python dependencies
├── README.md         # This documentation
```

([GitHub][1])

---

## 🚧 Future Enhancements

Potential improvements include:

* ⌨️ Keyboard shortcuts for common actions
* ⚡ Batch processing for multiple images
* 📸 New filters (e.g., edge detection, color curves)
* 📐 Advanced resizing and aspect-ratio tools

---

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch

   ```bash
   git checkout -b feature/YourFeature
   ```
3. Implement and test your changes
4. Commit and push

   ```bash
   git commit -am "Add feature"
   git push origin feature/YourFeature
   ```
5. Open a Pull Request

Please follow PEP-8 style guidelines and update this README as needed.

---

## 📜 License

This project is released under the **MIT License**. See the `LICENSE` file for details.

---

✨ *Thanks for checking out PIXEDIT — Image Editor!* 🎉
