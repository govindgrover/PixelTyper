# PixelTyper Project Guide

## Critical Rules
**Token Efficiency:** Be concise. Don't generate documentation files, context summaries, or description files unless explicitly requested. Ask before creating any new files.

**File Creation:** Only create files when directly requested or absolutely necessary for functionality. Never create README updates, change logs, or summary documents without asking first.

## Overview
PixelTyper is an image text overlay tool that combines PIL for text rendering and OpenCV for interactive coordinate selection. The workflow: user clicks on an image to select position → text is rendered at that position → edited image saved to `outputs/`.

## Architecture

**Two-module design:**
- [functions.py](../functions.py): Core image processing (`create_image_with_text`, `get_coordinates`)
- [test.py](../test.py): Usage example showing the typical workflow

**Data Flow:**
1. `get_coordinates()` opens CV2 window → user clicks → returns (x, y) coordinates (converted from display scale to original image scale)
2. `create_image_with_text()` uses PIL to load image → render text at position → save to `outputs/_editied-{basename}.jpg`

## Configuration

[config.json](../config.json) stores font paths in this structure:
```json
{
  "fonts": {
    "FontName": {
      "normal": "fonts/FONTFILE.TTF"
    }
  }
}
```

Currently hardcoded to `CONFIG["fonts"]["Ocraext"]["normal"]` in [functions.py](../functions.py#L17). Add new fonts by:
1. Place `.TTF` file in `fonts/`
2. Add entry to `config.json`
3. Update font loading logic if supporting multiple fonts

## Key Patterns

**Coordinate Scaling:** [get_coordinates()](../functions.py#L27) automatically downscales images >1280x720 for display, but converts click coordinates back to original image dimensions. Always use the returned coordinates directly - they're already in original scale.

**Output Naming:** All edited images save to `outputs/` with prefix `_editied-` (note: typo in "edited"). Pattern: `./outputs/_editied-{original_basename}.jpg`

**Font Loading:** Falls back to PIL default font if TTF file not found. No error raised - silently degrades to system font.

## Development Workflow

**Testing the tool:**
```bash
python test.py
```
1. Window opens with test image
2. Click desired text position
3. Press 'q' to confirm
4. Check `outputs/` for result

**Dependencies:**
- PIL/Pillow: Text rendering, image manipulation
- OpenCV (cv2): Interactive coordinate selection UI
- Standard library: json, os

**No build process** - direct Python execution. No tests beyond [test.py](../test.py) manual verification.

## Conventions

- Global variable `selected_point` stores coordinates from CV2 callback (in [get_coordinates()](../functions.py#L77))
- All image paths are relative to project root
- RGB color tuples: `(R, G, B)` or named colors like `"black"`
- Font size in points, position as `(x, y)` tuple from top-left

## Common Extensions

**Adding font variants:** Extend config structure to support bold/italic:
```python
font = ImageFont.truetype(CONFIG["fonts"]["Ocraext"]["bold"], font_size)
```

**Multi-text support:** Call `create_image_with_text()` multiple times on the same image object (pass returned image instead of path)

**Preview before save:** Uncomment `image.show()` at [functions.py:24](../functions.py#L24)
