# PixelTyper

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-1.0-green.svg)](https://github.com/govindgrover/PixelTyper)

## Version: v1.0

PixelTyper is an image text overlay tool that provides two interfaces for users:
1. **Graphical User Interface (GUI):** A user-friendly desktop application built with CustomTkinter, offering three modes:
   - Simple Overlay: Add text to a single image at specified coordinates.
   - Template Creation: Create reusable templates by marking positions on an image.
   - Template Application: Apply saved templates to images for batch processing.
2. **Command-Line Interface (CLI):** A core library for scripting and automation, allowing programmatic access to the image processing functionalities.

---

## Features

- **Simple Text Overlay:**
  - Add text to images at specific coordinates.
  - Customize font size, color (with color picker), and style.
  - Adjust text opacity (0-100%).
  - Interactive coordinate selection by clicking on the image.

- **Template System:**
  - Create reusable templates with named positions and font settings.
  - Save templates as JSON files in the app data directory.
  - Apply templates to images for batch text overlay.
  - Update existing templates with new font settings.
  - Per-field font customization (size, color, style, opacity).

- **Dynamic GUI:**
  - Modern and responsive GUI built with CustomTkinter.
  - Modular tab design for easy navigation.
  - Dark theme with customizable colors via config.
  - Preview popup for processed images.

- **Font Management:**
  - Supports custom fonts from app data `fonts/` directory, bundled fonts, config file, or system fonts.
  - Easy font addition via file browser.
  - System font detection (Windows, macOS, Linux).
  - Automatic font fallback to ensure compatibility.

- **Output Management:**
  - User-selectable output location with file browser.
  - Default output directory in app data (`outputs/` folder).
  - File naming convention: `{name}_edited{ext}` preserving original format.
  - Quick "Open" button to view saved files.

---

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/govindgrover/PixelTyper.git
   cd PixelTyper-py-CLI-UI
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

   **Key Dependencies:**
   - `customtkinter` - Modern GUI framework
   - `Pillow` - Image processing
   - `opencv-python` - Interactive coordinate selection
   - `ctk-colorpicker-plus` - Color picker widget

3. Run the application:
   - **GUI:**
     ```bash
     python UI.py
     ```
   - **CLI Examples:**
     ```bash
     python test.py
     ```

---

## Directory Structure

### Project Root
```
PixelTyper-py-CLI-UI/
├── UI.py                   # Main GUI application
├── functions.py            # Core image processing library (CLI)
├── test.py                 # CLI usage examples
├── config.json             # Configuration (fonts, theme, settings)
├── requirements.txt        # Python dependencies
├── LICENSE                 # MIT License
├── README.md               # This file
├── PixelTyper.spec         # PyInstaller build specification
├── build_exe.bat           # Build script for executable
├── icon.ico                # Application icon
└── fonts/                  # Bundled font files (copied to app data on first run)
```

### User Data Directory
User data (templates, outputs, and fonts) is stored per-OS:
- **Windows:** `%APPDATA%\PixelTyper`
- **macOS:** `~/Library/Application Support/PixelTyper`
- **Linux:** `~/.local/share/PixelTyper`

```
PixelTyper/
├── coord_templates/        # Saved coordinate templates (.json)
├── outputs/                # Default output directory for edited images
└── fonts/                  # User-added custom fonts
```


---

## Usage

### GUI

#### 1. Simple Overlay Tab
   - Click **Browse** to select an image
   - Enter the text you want to overlay
   - Set position:
     - Manually enter X, Y coordinates, OR
     - Click **Click to Select** to interactively choose position on image
   - Customize styling:
     - Font size (use mouse wheel to adjust)
     - Color (use **Pick** button for color picker)
     - Font style (choose from available fonts)
     - Opacity (0-100% transparency)
   - Click **Apply Text Overlay**
   - Choose save location or use default
   - Click **Open** to view the result

#### 2. Create Template Tab
   - Click **Browse** to select a reference image
   - Enter a template name (e.g., "certificate", "id_card")
   - Click **Create Template**
   - In the popup window:
     - Left-click on positions you want to save
     - Enter a label for each position (e.g., "name", "date")
     - Press Enter/Space to finish, or Esc to cancel
   - Template is saved as `{template_name}.json`

#### 3. Apply Template Tab
   - Click **Browse** to select target image
   - Select a template from the dropdown (click **Refresh** if needed)
   - Fill in text for each field
   - Optionally customize font settings per field:
     - Font size, color, style, and opacity
     - Changes enable the **Update Template** button
   - Click **Apply Template to Image**
   - Choose save location
   - Preview popup shows result (if enabled)
   - Click **Update Template** to save font changes for future use

### CLI/Programmatic Usage

Use `functions.py` to script custom workflows:

```python
import functions as fn

# Simple text overlay
fn.create_image_with_text(
    text="Hello World",
    image_path="image.png",
    position=(100, 200),
    font_size=30,
    text_color="blue",
    font_style="Arial",
    opacity=80,
    output_path="output.png"
)

# Create a template interactively
fn.make_coordinates_template(
    image_path="template_base.png",
    template_name="my_template"
)

# Apply template
text_mapping = {
    "name": "John Doe",
    "date": "2026-02-05"
}
fn.apply_template_to_image(
    image_path="target.png",
    template_name="my_template",
    text_mapping=text_mapping,
    output_path="result.png"
)
```

See [test.py](test.py) for more examples.

---

## Changelog

### v1.0 (February 2026)
- Initial release of PixelTyper
- **Core Features:**
  - Simple text overlay with customizable styling
  - Template system for batch processing
  - Interactive coordinate selection via mouse clicks
  - Modern dark-themed GUI with CustomTkinter
- **Text Customization:**
  - Font size, color, and style selection
  - Opacity control (0-100%)
  - Visual color picker integration
  - System and custom font support
- **Template Management:**
  - Create, save, and apply coordinate templates
  - Per-field font customization
  - Template update functionality
- **User Experience:**
  - Preview popup for processed images
  - User-selectable output locations
  - Quick file open integration
  - Cross-platform app data storage

---

## Contributing

Contributions are welcome! To contribute:
1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Commit your changes and push them to your branch.
4. Open a pull request with a detailed description of your changes.

---

## License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

### What this means:
- ✅ **Free to use:** Use this software for any purpose, including commercial projects
- ✅ **Free to modify:** Change and adapt the code to your needs
- ✅ **Free to distribute:** Share the original or modified versions
- ✅ **Free to sublicense:** Include in your own projects with different licenses
- ⚠️ **Attribution required:** Include the original copyright notice and license
- ⚠️ **No warranty:** Software is provided "as is" without any guarantees

---

## Contact

For any questions or feedback, please contact the repository owner at [govindgrover](https://github.com/govindgrover).
