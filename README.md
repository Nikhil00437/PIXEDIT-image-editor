# PIXEDIT — Image Editor

> A clean, themeable desktop image editor built with Python, PyQt5, and Pillow.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square&logo=python)](https://python.org)
[![PyQt5](https://img.shields.io/badge/PyQt5-GUI-green?style=flat-square)](https://pypi.org/project/PyQt5/)
[![Pillow](https://img.shields.io/badge/Pillow-PIL-orange?style=flat-square)](https://pillow.readthedocs.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE.txt)

---

## Demo

![PIXEDIT3](https://github.com/user-attachments/assets/0ee4c948-3106-4b13-a57a-084fcee28387)

---

## Features

**Image Loading**
- Browse and load images via a file picker or drag & drop onto the canvas
- Supports `.jpg`, `.jpeg`, and `.png` formats
- Sidebar file list for quick navigation between images

**Transform**
- Rotate left / right (90°)
- Flip horizontal and vertical

**Filters**
- Grayscale with round-trip back to color
- Color boost (enhanced saturation)
- Blur and Sharpen

**Adjustments**
- Brightness slider (−50 to +50)
- Contrast slider (−50 to +50)

**Effects**
- Sepia tone
- Solarize
- Invert Colors
- Vignette (radial darkening)

**Crop**
- Draw a freehand crop rectangle directly on the canvas
- Rule-of-thirds grid overlay while cropping
- Hold **Shift** to constrain to a square
- Live pixel-dimension badge
- Corner and edge handles

**Undo / Reset**
- Up to 20 levels of undo history
- One-click reset to the original image

**Preview Mode**
- Non-destructive filter preview via a dropdown — Original, B/W, Color, Blur, Sharpen, Sepia, Solarize, Invert Colors

**Image Generation**
- Generate images from text prompts using Stable Diffusion 2.1
- Auto-detects CUDA GPU — falls back to CPU if unavailable
- Saves output directly to disk with a safe, prompt-derived filename

**Save**
- Export as PNG or JPEG to any location

**Themes — 5 built-in**

| Theme | Style |
|---|---|
| ⬛ Midnight Gold | Dark with gold accents |
| 🌆 Cyberpunk | Dark neon cyan |
| 🌲 Forest | Dark green |
| 🌸 Peach Bloom | Light warm peach |
| 📜 Sepia | Light vintage brown |

Theme preference is saved and restored automatically between sessions.

**Keyboard Shortcuts**
- Fully customisable via the Settings panel (⚙ in the title bar)
- Shortcuts saved to `settings.json` and persist across sessions
- Conflict detection prevents duplicate bindings

---

## Project Structure

```
PIXEDIT-image-editor/
├── app.py              # UI layout, theming, event wiring
├── functions.py        # ImageEditor logic, SettingsWindow, filters, shortcuts
├── Crop.py             # CropLabel — custom QLabel with rubber-band crop overlay
├── generate_image.py   # Stable Diffusion 2.1 image generation — text-to-image via diffusers, auto-detects CUDA/CPU
├── requirements.txt
└── LICENSE.txt
```

---

## Getting Started

### Prerequisites

- Python 3.8+

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/Nikhil00437/PIXEDIT-image-editor.git
cd PIXEDIT-image-editor

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
python app.py
```

### Requirements

```
PyQt5
Pillow
torch
diffusers
```

> For image generation (`generate_image.py`), a CUDA-capable GPU is recommended. The module will fall back to CPU automatically but generation will be significantly slower.

---

## Default Keyboard Shortcuts

| Action | Shortcut |
|---|---|
| Open Folder | `Ctrl+O` |
| Save | `Ctrl+S` |
| Undo | `Ctrl+Z` |
| Reset | `Ctrl+R` |
| Left Rotate | `←` |
| Right Rotate | `→` |
| Flip Horizontal | `H` |
| Flip Vertical | `V` |
| Grayscale | `G` |
| Color | `C` |
| Blur | `B` |
| Sharpen | `Shift+S` |
| Brightness | `Ctrl+B` |
| Contrast | `Ctrl+T` |
| Sepia | `Ctrl+E` |
| Invert | `Ctrl+I` |
| Solarize | `Shift+O` |
| Start Crop | `Ctrl+X` |
| Confirm Crop | `Enter` |

All shortcuts can be reassigned in **Settings → Shortcuts**.

---

## Theming

Themes are defined in `app.py` as parameterised stylesheet functions (`dark_theme` / `light_theme`). To add a custom theme, add a new entry to the `THEMES` dictionary following the same pattern — it will appear automatically in **Settings → Theme**.

---

## Related Projects

- [ARIA — Local AI Desktop Assistant](https://github.com/Nikhil00437/ARIA) — 15-module PyQt5 AI assistant with LM Studio, Stable Diffusion, and voice engine
- [RAG Chatbot](https://github.com/Nikhil00437/cap) — Verified-document RAG chatbot with FastAPI
- [Qwen3-4B Excel Fine-Tune](https://huggingface.co/Nikhil1581/qwen3-4b-instruct-2507.Q4_K_M-excel-finetuning-1.2kdataset) — GGUF model on HuggingFace

---

## License

MIT — see [LICENSE.txt](LICENSE.txt)

---

Made with 🫡 by [Nikhil](https://github.com/Nikhil00437)
