
# PIXEDIT — Image Editor 🖼️

A basic yet functional GUI image editor built with **Python**, **PyQt5**, and **Pillow (PIL)**.  
Designed for simple photo editing tasks like rotation, filters, cropping, brightness/contrast, and undo/redo support.

---

## 🚀 Features

This editor lets you:

- 📂 Load images from a folder and browse them
- 🔄 Rotate, flip, and mirror images
- 🖌️ Apply filters: **grayscale**, **blur**, **sharpen**
- 🌗 Adjust **brightness** & **contrast**
- ✂️ Crop using a rubber-band selection
- ↩️ Undo up to 20 steps (history)
- 💾 Save edited images as PNG or JPEG

---

## 🧰 Requirements

| Requirement | Minimum Version |
|-------------|-----------------|
| Python      | 3.7             |
| PyQt5       | 5.15            |
| Pillow      | 8.0             |

> Tested on Windows 10/11, macOS 13, and Ubuntu 22.04. :contentReference[oaicite:1]{index=1}

---

## 📦 Installation

### Clone the repository

```bash
git clone https://github.com/Nikhil00437/PIXEDIT-image-editor.git
cd PIXEDIT-image-editor
````

### (Recommended) Create a virtual environment

```bash
python -m venv venv
# Activate the environment:
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Run the Editor

After dependencies are installed:

```bash
python app.py
```

The editor window should open, letting you browse and edit images.

---

## 🧭 Usage Walk-through

1. **Open a Folder** – Select a directory containing `.jpg`, `.jpeg`, or `.png` files.
2. **Load an Image** – Click on any filename to display it.
3. **Apply Transformations**

   * Rotate left/right
   * Mirror horizontally/vertically
4. **Filters & Adjustments**

   * Grayscale, blur, sharpen
   * Brightness & contrast sliders
5. **Crop** – Click Crop → drag to select → confirm.
6. **Undo/Redo** – Step back through changes.
7. **Save** – Export to PNG or JPEG.

---

## 🗂️ Project Structure

```
PIXEDIT-image-editor/
├── app.py            # Main application entry point
├── Crop.py           # Rubber-band cropping widget
├── functions.py      # Core image operations (Pillow + history)
├── requirements.txt  # Python dependencies
├── README.md         # This documentation
```

---

## 🔧 Future Enhancements

* 🎛️ Keyboard shortcuts for common actions
* 🗂️ Batch editing for multiple images
* 🖼️ Additional filters (e.g., edge detection, color curves)
* 🌗 Light & dark UI themes
* 📐 Advanced resizing and aspect-ratio tools

---

## 🤝 Contributing

1. Fork the repo
2. Create a branch: `git checkout -b feature/YourFeature`
3. Implement your changes
4. Commit: `git commit -am "Add feature"`
5. Push & open a Pull Request

Please follow consistent style (PEP-8) and update this README if behavior changes.

---

## 📜 License

This project is released under the **MIT License** — see the `LICENSE` file for details.

