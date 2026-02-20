

# 📸 PIXEDIT | A Basic Image Editor  
*A lightweight PyQt5‑based image editor with crop, transform, filters and simple undo/redo.*

---

## Table of Contents
1. [Project Overview](#project-overview)  
2. [Features](#features)  
3. [Requirements](#requirements)  
4. [Installation](#installation)  
5. [How to Run the Application](#how-to-run-the-application)  
6. [Usage Walk‑through](#usage-walk-through)  
7. [Project Structure](#project-structure)  
8. [Future Enhancements & Contributing](#future-enhancements--contributing)  
9. [License](#license)  
10. [Acknowledgements](#acknowledgements)

---  

## Project Overview
`Basic Image Editor` is a minimal yet functional GUI tool that lets you:

* Browse a folder of images and select one to edit.  
* Apply common transformations (rotate, mirror, flip).  
* Add filters (grayscale, blur, sharpen, color boost).  
* Adjust brightness & contrast with sliders.  
* Crop images with a rubber‑band selection.  
* Undo / Redo actions (up to 20 steps).  
* Save the edited image to any location of your choice.

The whole UI is styled with a dark, high‑contrast theme that is comfortable for long editing sessions.

> **Demo Screenshot**

<img width="1920" height="1080" alt="Screenshot (128)" src="https://github.com/user-attachments/assets/8749ca05-68d0-4005-a472-8fe83846bf02" />
<img width="1920" height="1080" alt="Screenshot (129)" src="https://github.com/user-attachments/assets/975d6f08-c3cb-49ab-9672-3b4a0adc73c0" />
<img width="1920" height="1080" alt="Screenshot (130)" src="https://github.com/user-attachments/assets/6025df29-a239-4fa1-9984-bc46aa91bede" />
<img width="1920" height="1080" alt="Screenshot (131)" src="https://github.com/user-attachments/assets/e7aecd19-0539-4736-b69c-e8be181355b6" />
<img width="1920" height="1080" alt="Screenshot (132)" src="https://github.com/user-attachments/assets/2a70bce9-ddb5-4049-9c16-e5eb9743b3c1" />
<img width="1920" height="1080" alt="Screenshot (133)" src="https://github.com/user-attachments/assets/890d4b90-43aa-4902-ae81-0b4201211ec7" />


---  

## Features

| Category | Feature |
|----------|----------|
| **File Handling** | Select a folder → list images → open chosen image |
| **Transformations** | Left / Right rotate, Horizontal mirror, Vertical flip |
| **Filters** | Grayscale, Color boost, Blur, Sharpen |
| **Adjustments** | Brightness slider (‑50 → +50), Contrast slider (‑50 → +50) |
| **Cropping** | Rubber‑band selection → confirm → cropped image |
| **History** | Up to 20 undo steps, full reset to original |
| **Preview Picker** | Quick preview of each operation on the original image |
| **Save** | Export edited image as PNG or JPEG |
| **UI** | Dark theme, clear button icons, labelled sections |

---  

## Requirements

| Item | Minimum Version |
|------|-----------------|
| Python | 3.7 |
| PyQt5 | 5.15 |
| Pillow (PIL) | 8.0 |
| (Optional) Virtual environment tools – `venv` or `conda` |

The code has been tested on Windows 10/11, macOS 13 and Ubuntu 22.04.

---  

# Installation

## Method 1: Running Manually

1. **Clone the repository**  

   ```bash
   git clone https://github.com/yourusername/basic-image-editor.git
   cd basic-image-editor
   ```

2. **Create a virtual environment (recommended)**  

   ```bash
   python -m venv venv
   # Activate it
   # Windows:
   venv\Scripts\activate
   # macOS / Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**  

   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

   *If you don’t have a `requirements.txt`, you can generate one from the code:*

   ```bash
   pip freeze > requirements.txt
   ```

   The minimal `requirements.txt` should contain:

   ```
   PyQt5>=5.15
   Pillow>=8.0
   ```

## Method 2: Using the exe file

Just install and run the exe file attached.

> Note:
> The Code is not Signed, so the windows defender can show warning when opened for the first time. 

---  

## How to Run the Application

1. Make sure the virtual environment is activated (see Installation step 2).  
2. Launch the editor:

   ```bash
   python main.py
   ```

   The program opens a window titled **Image Editor**.  

   > **Tip** – You can create a shortcut or a desktop entry for quicker access.

---  

## Usage Walk‑through

### 1️⃣ Open a Folder  

* Click **⊕ Select Folder**.  
* Choose a directory containing `.jpg`, `.jpeg` or `.png` files.  
* The list widget on the left populates with the found images.

### 2️⃣ Load an Image  

* Click on any file name in the list.  
* The image appears on the right canvas and the control panel becomes enabled.

### 3️⃣ Apply Transformations  

| Button | Action |
|--------|--------|
| ↺ Left Rotate | Rotate 90° clockwise |
| ↻ Right Rotate | Rotate 90° counter‑clockwise |
| ⇆ Mirror | Flip horizontally |
| ⇅ Upside Down | Flip vertically |

### 4️⃣ Apply Filters  

| Button | Action |
|--------|--------|
| ◑ B/W | Convert to grayscale |
| ◈ Color | Convert back to RGB (or boost saturation if already colour) |
| ≋ Blur | Apply Gaussian‑style blur |
| ✦ Sharpen | Apply sharpening filter |

### 5️⃣ Brightness / Contrast  

* Move the **BRIGHTNESS** slider left/right → image darkens/brightens.  
* Move the **CONTRAST** slider left/right → image contrast changes.  
* Changes are applied instantly when you release the slider.

### 6️⃣ Crop  

1. Press **✂ Crop** – the cursor turns into a rubber band.  
2. Drag to draw a selection rectangle on the canvas.  
3. Press **✔ Confirm** – the image is cropped to the selected area.  
4. Press **✂ Crop** again to start a new selection.

### 7️⃣ Undo / Reset  

* **↩ Undo** – step back through up to 20 actions.  
* **⟳ Reset** – discard all edits and reload the original image.

### 8️⃣ Save  

* Click **⬇ Save** – a standard file‑save dialog appears.  
* Choose **PNG** or **JPEG** and set a destination path.  
* The edited image is written to the file.

### 9️⃣ Preview Picker  

The **PREVIEW** combo box lets you temporarily view any operation on the original image without adding it to the history. Choose an option and the canvas updates instantly.

---  

## Project Structure

```
basic-image-editor/
│
├─ main.py                # Entry point – UI assembly & signal wiring
├─ Crop.py                # Custom QLabel with rubber‑band cropping
├─ functions.py           # ImageEditor class – all logic (PIL, history, etc.)
├─ requirements.txt       # Python dependencies (optional)
└─ screenshots/
   └─ demo.png           # Screenshot used in README
```

* **main.py** – builds the Qt layout, instantiates the editor, connects UI controls to `ImageEditor` methods.  
* **Crop.py** – overrides `QLabel` to add mouse‑tracking and `QRubberBand`‑based cropping.  
* **functions.py** – contains the `ImageEditor` class, which:  
  * loads images,  
  * maintains an undo stack (`deque`),  
  * applies transformations via Pillow,  
  * converts Pillow images to QPixmap for display.  

---  

## Future Enhancements & Contributing

* **Batch processing** – apply the same filter to all images in a folder.  
* **Advanced filters** – edge detection, vignette, colour curves.  
* **Keyboard shortcuts** – faster workflow.  
* **Theme selector** – light / high‑contrast mode.  
* **Export presets** – save common settings as presets.

### Contributing

1. Fork the repository.  
2. Create a new branch: `git checkout -b feature/your-feature`.  
3. Implement changes, add tests if applicable.  
4. Commit: `git commit -am "Add your feature"`.  
5. Push and open a Pull Request.

Please follow the existing code style (PEP‑8, 4‑space indentation) and update this README if you change functionality.

---  

## License

This project is released under the **MIT License**. See the `LICENSE` file for details.

---  

## Acknowledgements

* **PyQt5** – for the powerful GUI framework.  
* **Pillow (PIL)** – for robust image processing.  
* Icons from the **Material Design** set (used in the button labels).  

---  

Enjoy editing! 🎉  

*Made by Nikhil 🫡*
