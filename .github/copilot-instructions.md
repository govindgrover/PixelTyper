# PixelTyper Project Guide

## Critical Rules
**Token Efficiency:** Be concise. Don't generate documentation files, context summaries, or description files unless explicitly requested. Ask before creating any new files.

**File Creation:** Only create files when directly requested or absolutely necessary for functionality. Never create README updates, change logs, or summary documents without asking first.

## Overview
PixelTyper is an image text overlay tool with two interfaces:
1. **GUI** ([UI.py](../UI.py)): CustomTkinter-based desktop app with three modes (simple overlay, template creation, template application)
2. **CLI/Programmatic** ([functions.py](../functions.py)): Core library for scripting/automation

**Core workflow:** Select image → place text at coordinates → save to `outputs/_editied-{filename}.jpg`

## Architecture

### Three-Layer Design
- **[functions.py](../functions.py)**: Core image processing library (PIL + OpenCV)
  - `create_image_with_text()`: Single text overlay
  - `make_coordinates_template()`: Interactive template creation with CV2 window + Tkinter dialogs
  - `apply_template_to_image()`: Batch text overlay from saved template
  - `apply_template_interactive()`: Guided template application with prompts
- **[UI.py](../UI.py)**: CustomTkinter GUI with modular tab architecture
  - `SimpleOverlayTab`: One-off text placement
  - `CreateTemplateTab`: Template creation workflow
  - `ApplyTemplateTab`: Template application with dynamic form generation
  - `ImagePreviewWidget`: Reusable preview component (600x750 max, aspect-preserving)
- **[test.py](../test.py)**: CLI usage examples (currently disabled with `exit()`)

### Template System
**Templates** are JSON files in `coord_templates/` mapping named positions to coordinates:
```json
{
  "name_field": {"x": 100, "y": 200},
  "date_field": {"x": 400, "y": 500}
}
```
Created via interactive clicking (`make_coordinates_template`), applied programmatically (`apply_template_to_image`) or interactively (`apply_template_interactive`).

## Critical Implementation Details

### Coordinate Scaling Pattern
**Both UI and functions.py implement the same scaling logic:**
- Images >1280x720 are downscaled for display only
- Click coordinates are converted back to original image dimensions via `scale` factor
- Example: [UI.py:181-184](../UI.py#L181-L184) and [functions.py:53-63](../functions.py#L53-L63)
- **Always use returned/stored coordinates directly** - they're already in original scale

### Output File Naming
**Hardcoded typo preserved for consistency:** `_editied-{basename}` (not "edited")
- All functions save to `./outputs/_editied-{original_filename}.jpg`
- Pattern used in [functions.py:27](../functions.py#L27), [UI.py:232](../UI.py#L232), [UI.py:510](../UI.py#L510)

### Font Configuration
- [config.json](../config.json) stores font paths: `CONFIG["fonts"]["Ocraext"]["normal"]`
- Currently hardcoded to Ocraext font at [functions.py:18](../functions.py#L18)
- Falls back to PIL default font silently if TTF not found (no error)
- To add fonts: place `.TTF` in `fonts/`, add JSON entry, update loading logic

### CV2 + Tkinter Integration
**Unique pattern in [functions.py:33-86](../functions.py#L33-L86):**
- Hidden Tkinter root (`root.withdraw()`) provides dialog boxes
- CV2 window handles mouse clicks (`cv2.setMouseCallback`)
- Each click triggers `simpledialog.askstring()` for labeling
- Points stored in dict, saved as JSON on 'q' press
- **Critical:** Both libraries must coexist without event loop conflicts

## Development Workflow

### Running the App
```bash
python UI.py  # GUI interface (primary)
python test.py  # CLI examples (currently exits immediately)
```

### Dependencies
- **CustomTkinter**: Modern UI framework (dark/light themes)
- **PIL/Pillow**: Text rendering, image manipulation
- **OpenCV (cv2)**: Interactive coordinate selection
- **Tkinter**: Dialog boxes (built-in, used alongside CV2)

### Testing
No automated tests. Manual verification:
1. GUI: Run [UI.py](../UI.py), test each tab
2. CLI: Uncomment [test.py](../test.py#L9) and run

## UI Architecture Patterns

### Modular Tab Design
Each tab is a self-contained `CTkFrame` subclass:
- Receives `preview_widget` reference for shared image display
- Manages own state (`image_path`, `template_data`, etc.)
- Handles file dialogs, validation, error messages
- Updates shared preview after operations

### Preview Widget Contract
[`ImagePreviewWidget`](../UI.py#L12-L58):
- `load_image(path)`: Display image with aspect-preserving resize to 600x750
- `clear()`: Reset to "No image loaded" state
- Shared across all tabs - updates reflect in all views

### Dynamic Form Generation
[`ApplyTemplateTab.on_template_selected()`](../UI.py#L442-L469):
- Reads template JSON
- Destroys existing widgets
- Creates `CTkEntry` for each coordinate point
- Stores entries in `self.text_entries` dict for batch collection

## Conventions

### Code Style
- Global variable pattern: `selected_point` for CV2 callbacks ([functions.py:79](../functions.py#L79))
- Inline variable assignment in event handlers: `selected: list = [None]` ([UI.py:186](../UI.py#L186))
- RGB colors: tuples `(0, 0, 0)` or strings `"black"`
- All paths relative to project root

### Error Handling
- GUI: `messagebox.showerror()` with try/except blocks
- Functions: Silent fallbacks (font loading) or raised exceptions
- Status updates via colored `CTkLabel` (green=success, blue=info, red=error)

### File Structure Assumptions
- `fonts/` directory for TTF files
- `coord_templates/` for JSON templates
- `outputs/` for processed images (created if missing)
- `config.json` at project root

## Common Extensions

### Adding Font Support
Extend structure to support variants (bold/italic):
```python
# config.json
{"fonts": {"Ocraext": {"normal": "...", "bold": "..."}}}

# functions.py
font = ImageFont.truetype(CONFIG["fonts"]["Ocraext"]["bold"], font_size)
```

### Multi-Text Single Image
Chain calls to avoid re-saving:
```python
img = fn.create_image_with_text("Text 1", path, (10, 10))
img = fn.apply_template_to_image(img, "template", {...})  # Modify to accept Image.Image
```

### Preview Before Save
Uncomment `image.show()` at [functions.py:24](../functions.py#L24) for PIL preview window

### Custom Output Directory
Modify all three output path constructions to use configurable directory instead of `./outputs/`
