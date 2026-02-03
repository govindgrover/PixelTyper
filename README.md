# PixelTyper

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
  - Customize font size, color, and style.

- **Template System:**
  - Create reusable templates with named positions and font settings.
  - Save templates as JSON files in the `coord_templates/` directory.
  - Apply templates to images for batch text overlay.

- **Dynamic GUI:**
  - Modern and responsive GUI built with CustomTkinter.
  - Modular tab design for easy navigation.
  - Image preview widget with aspect-preserving resizing.

- **Font Management:**
  - Supports custom fonts from `fonts/` directory, config file, or system fonts.
  - Default font fallback to ensure compatibility.

- **Output Management:**
  - All processed images are saved in the `outputs/` directory.
  - File naming convention: `_editied-{original_filename}.jpg` (typo preserved for consistency).

---

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/govindgrover/PixelTyper.git
   cd PixelTyper
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   - **GUI:**
     ```bash
     python UI.py
     ```
   - **CLI Examples:** Uncomment the `test.py` file and run:
     ```bash
     python test.py
     ```

---

## Directory Structure

```
PixelTyper/
├── config.json          # Configuration file for fonts and UI theme
├── functions.py         # Core image processing library
├── test.py              # CLI usage examples
├── UI.py                # CustomTkinter GUI implementation
├── coord_templates/     # Directory for storing JSON templates
├── fonts/               # Directory for custom font files
├── outputs/             # Directory (Default) for processed images
```

---

## Usage

### GUI
1. **Simple Overlay:**
   - Select an image.
   - Enter text, position, font size, color, and style.
   - Save the edited image.

2. **Create Template:**
   - Select an image.
   - Enter a template name.
   - Click on the image to mark positions and label them.
   - Save the template as a JSON file.

3. **Apply Template:**
   - Select an image and a template.
   - Enter text for each labeled position.
   - Customize font settings if needed.
   - Save the edited image.

### CLI
- Use the `functions.py` library to script custom workflows for image text overlay and template application.
- Refer to `test.py` for example usage.

---

## Changelog

### v1.0
- Initial release of PixelTyper.
- Features:
  - Simple text overlay on images.
  - Template creation and application.
  - CustomTkinter-based GUI with three modes.
  - Support for custom fonts and dynamic font settings.
  - Output management with consistent naming convention.

---

## Contributing

Contributions are welcome! To contribute:
1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Commit your changes and push them to your branch.
4. Open a pull request with a detailed description of your changes.

---

## License

This project is licensed under the MIT License. See the LICENSE file for details.

---

## Contact

For any questions or feedback, please contact the repository owner at [govindgrover](https://github.com/govindgrover).