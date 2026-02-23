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

---

## 🖼️ ScreenShots

<img width="1920" height="1080" alt="Screenshot (143)" src="https://github.com/user-attachments/assets/ccbcc8b4-4ca1-497e-a4c2-8e8c8279b7f7" />
<img width="1920" height="1080" alt="Screenshot (144)" src="https://github.com/user-attachments/assets/8f5bdc45-d15a-4049-9523-ed041c89163e" />
<img width="1920" height="1080" alt="Screenshot (145)" src="https://github.com/user-attachments/assets/1459c79f-6e47-4709-b76b-c8f7d753fd19" />
<img width="1920" height="1080" alt="Screenshot (146)" src="https://github.com/user-attachments/assets/dbf230fd-21d2-404a-807d-04533861cd02" />
<img width="1920" height="1080" alt="Screenshot (147)" src="https://github.com/user-attachments/assets/258bf360-5e2e-42c4-bdcf-0ee33f36154c" />
<img width="1920" height="1080" alt="Screenshot (148)" src="https://github.com/user-attachments/assets/d37a61a7-4565-4785-b53f-fe04f74c9b78" />
<img width="1920" height="1080" alt="Screenshot (149)" src="https://github.com/user-attachments/assets/468b5fe8-2460-4731-a2c4-43951c0ec6a9" />
<img width="1920" height="1080" alt="Screenshot (150)" src="https://github.com/user-attachments/assets/47d34aed-8b80-4b72-8f11-3e95f705ad84" />
<img width="1920" height="1080" alt="Screenshot (151)" src="https://github.com/user-attachments/assets/0bf1468e-1859-44ab-8397-69b17df75e83" />
<img width="1920" height="1080" alt="Screenshot (152)" src="https://github.com/user-attachments/assets/d09d7191-0187-4b20-bbfb-0fba13ba57f7" />
<img width="1920" height="1080" alt="Screenshot (153)" src="https://github.com/user-attachments/assets/064fcb55-251b-46e1-8581-a9b64312fa7c" />
<img width="1920" height="1080" alt="Screenshot (154)" src="https://github.com/user-attachments/assets/25b5d2f6-e3f1-4179-af88-a3e72bec249b" />
<img width="1920" height="1080" alt="Screenshot (155)" src="https://github.com/user-attachments/assets/1849bb93-ed14-4c45-bee1-752fdbb284aa" />
<img width="1920" height="1080" alt="Screenshot (156)" src="https://github.com/user-attachments/assets/35fcef4f-c372-4129-bdaa-bd1912a4f21c" />
<img width="1920" height="1080" alt="Screenshot (157)" src="https://github.com/user-attachments/assets/4940cfe8-1c73-497d-8947-3aa65970b9e4" />
<img width="1920" height="1080" alt="Screenshot (158)" src="https://github.com/user-attachments/assets/31d6d893-708a-4d4f-860e-24b9d93a95f0" />
<img width="1920" height="1080" alt="Screenshot (159)" src="https://github.com/user-attachments/assets/4b2cd175-d025-463f-8968-9a338d556e60" />
<img width="1920" height="1080" alt="Screenshot (160)" src="https://github.com/user-attachments/assets/d0e6e79e-cc16-4ad5-85e9-e36d21592e19" />
<img width="1920" height="1080" alt="Screenshot (161)" src="https://github.com/user-attachments/assets/c478a76f-1a20-4078-a2e6-d92d8b8f80e5" />
<img width="1920" height="1080" alt="Screenshot (162)" src="https://github.com/user-attachments/assets/5115d121-a200-45be-b2a7-c7320f969ec5" />
<img width="1920" height="1080" alt="Screenshot (163)" src="https://github.com/user-attachments/assets/fc25572d-42a5-418c-8b41-ee31eb4f5e30" />
<img width="1920" height="1080" alt="Screenshot (164)" src="https://github.com/user-attachments/assets/419e8e98-1bc2-4c37-b56d-192c282371b8" />
<img width="1920" height="1080" alt="Screenshot (165)" src="https://github.com/user-attachments/assets/eb84d955-2808-478b-93e3-f83a7c61edec" />

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

### Method 1:

Installing the .exe file from the releases...

>Note :
>Note that the code is not signed so the windows defender can show you a warning when you first run the .exe file

### Method 2:

Manual running:

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
