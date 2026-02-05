from datetime import date

from PIL import Image, ImageDraw, ImageFont, ImageColor
import cv2
import json, os
import sys, platform
import shutil

import tkinter as tk
from tkinter import simpledialog, filedialog

def get_resource_path(relative_path):
	"""Get absolute path to resource, works for dev and for PyInstaller bundle"""
	try:
		# PyInstaller creates a temp folder and stores path in _MEIPASS
		base_path = sys._MEIPASS # type: ignore
	except Exception:
		base_path = os.path.abspath(".")
	return os.path.join(base_path, relative_path)

def get_user_data_dir():
	"""Get the persistent application data directory for the OS"""
	if platform.system() == "Windows":
		base_path = os.getenv('APPDATA') or "C:\\Users\\{username}\\AppData\\Roaming".format(username=os.getlogin())
	elif platform.system() == "Darwin":
		base_path = os.path.expanduser('~/Library/Application Support')
	else:
		base_path = os.path.expanduser('~/.local/share')
	
	app_path = os.path.join(base_path, APP_NAME)
	return app_path

def get_user_data_path(*parts):
	"""Get a path inside the app's user data directory."""
	return os.path.join(get_user_data_dir(), *parts)

def ensure_user_dir(*parts):
	"""Ensure a directory exists inside the app's user data directory and return it."""
	path = get_user_data_path(*parts)
	os.makedirs(path, exist_ok=True)
	return path


def _is_dir_empty(path: str) -> bool:
	try:
		return not any(os.scandir(path))
	except FileNotFoundError:
		return True

def ensure_user_fonts_dir():
	"""
	Ensure user fonts directory exists. If it's empty and bundled fonts exist,
	copy bundled fonts into app data once.
	"""
	fonts_dir = ensure_user_dir("fonts")
	if _is_dir_empty(fonts_dir):
		bundled_fonts_dir = get_resource_path("fonts")
		if os.path.isdir(bundled_fonts_dir):
			for filename in os.listdir(bundled_fonts_dir):
				if filename.lower().endswith((".ttf", ".otf", ".ttc")):
					src = os.path.join(bundled_fonts_dir, filename)
					dst = os.path.join(fonts_dir, filename)
					if not os.path.exists(dst):
						shutil.copy2(src, dst)
	return fonts_dir


CONFIG: dict = json.load(open(get_resource_path("config.json"), "r"))
APP_NAME = CONFIG.get("app_name", "PixelTyper")
APP_VERSION = CONFIG.get("app_version", "1.0")
DEBUG = CONFIG.get("debug", "").lower() in ("1", "true", "yes", "on")

def _debug(message: str) -> None:
	if DEBUG:
		print(message)

def _clamp_opacity(value) -> int:
	try:
		value = int(value)
	except Exception:
		return 100
	return max(0, min(100, value))

def _normalize_color(color):
	if isinstance(color, tuple):
		if len(color) == 4:
			return color[:3]
		if len(color) == 3:
			return color
	if isinstance(color, str):
		try:
			return ImageColor.getrgb(color)
		except Exception:
			return (0, 0, 0)
	return (0, 0, 0)

def _draw_text(image: Image.Image, position, text, color, font, opacity=100) -> Image.Image:
	opacity = _clamp_opacity(opacity)
	rgb = _normalize_color(color)
	if opacity >= 100:
		draw = ImageDraw.Draw(image)
		draw.text(position, text, fill=rgb, font=font)
		return image
	# Draw with alpha on overlay, then composite
	base = image.convert("RGBA")
	overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
	odraw = ImageDraw.Draw(overlay)
	odraw.text(position, text, fill=(*rgb, int(255 * (opacity / 100))), font=font)
	return Image.alpha_composite(base, overlay)

def _load_font(font_name, font_size=20):
	"""Load font from config, ./fonts/ directory, or system fonts"""
	if font_name == "default" or not font_name:
		return ImageFont.load_default()
	
	import platform
	
	try:
		# 1. Check if it's in config
		if font_name in CONFIG.get("fonts", {}):
			font_variants = CONFIG["fonts"][font_name]
			font_path = next(iter(font_variants.values()))
			return ImageFont.truetype(font_path, font_size)
		
		# 2. Check user fonts directory (app data), then bundled fonts
		for ext in ['.ttf', '.TTF', '.otf', '.OTF', '.ttc', '.TTC']:
			user_fonts_dir = ensure_user_fonts_dir()
			local_path = os.path.join(user_fonts_dir, f"{font_name}{ext}")
			if os.path.exists(local_path):
				return ImageFont.truetype(local_path, font_size)
			bundled_path = get_resource_path(f"fonts/{font_name}{ext}")
			if os.path.exists(bundled_path):
				return ImageFont.truetype(bundled_path, font_size)
		
		# 3. Check if it's a system font (prefixed with [System])
		if font_name.startswith("[System] "):
			system_font_name = font_name.replace("[System] ", "")
			system = platform.system()
			
			if system == "Windows":
				# Windows fonts are in C:\Windows\Fonts
				# Try common variations
				font_variations = [
					f"C:\\Windows\\Fonts\\{system_font_name.replace(' ', '')}.ttf",
					f"C:\\Windows\\Fonts\\{system_font_name}.ttf",
					f"C:\\Windows\\Fonts\\{system_font_name.lower().replace(' ', '')}.ttf",
					f"C:\\Windows\\Fonts\\times.ttf",  # Times New Roman -> times.ttf
					f"C:\\Windows\\Fonts\\timesbd.ttf",  # Times New Roman Bold
					f"C:\\Windows\\Fonts\\arial.ttf",  # Arial
					f"C:\\Windows\\Fonts\\cour.ttf",  # Courier New
					f"C:\\Windows\\Fonts\\verdana.ttf",  # Verdana
				]
				
				# Special mappings for common fonts
				font_map = {
					"Times New Roman": ["times.ttf", "timesbd.ttf"],
					"Arial": ["arial.ttf", "arialbd.ttf"],
					"Courier New": ["cour.ttf", "courbd.ttf"],
					"Comic Sans MS": ["comic.ttf", "comicbd.ttf"],
					"Georgia": ["georgia.ttf", "georgiab.ttf"],
					"Verdana": ["verdana.ttf", "verdanab.ttf"],
					"Trebuchet MS": ["trebuc.ttf", "trebucbd.ttf"],
					"Tahoma": ["tahoma.ttf", "tahomabd.ttf"],
					"Impact": ["impact.ttf"]
				}
				
				if system_font_name in font_map:
					for font_file in font_map[system_font_name]:
						system_path = f"C:\\Windows\\Fonts\\{font_file}"
						if os.path.exists(system_path):
							_debug(f"DEBUG: Loading Windows font: {system_path}")
							return ImageFont.truetype(system_path, font_size)
				
				# Try all variations
				for path in font_variations:
					if os.path.exists(path):
						_debug(f"DEBUG: Loading Windows font: {path}")
						return ImageFont.truetype(path, font_size)
			elif system == "Darwin":  # macOS
				# Try system fonts
				for fonts_dir in ["/System/Library/Fonts", "/Library/Fonts"]:
					system_path = f"{fonts_dir}/{system_font_name}.ttf"
					if os.path.exists(system_path):
						return ImageFont.truetype(system_path, font_size)
					system_path = f"{fonts_dir}/{system_font_name}.ttc"
					if os.path.exists(system_path):
						return ImageFont.truetype(system_path, font_size)
		
		# Fallback: if no extension match, try as-is (maybe full path)
		if os.path.exists(font_name):
			return ImageFont.truetype(font_name, font_size)
		
	except Exception as e:
		print(f"Warning: Could not load font '{font_name}': {e}")
	
	# Final fallback
	return ImageFont.load_default()

def create_image_with_text(text, image_path, position: tuple =(), text_color=(0, 0, 0), font_size=20, font_style="default", output_path=None, opacity=100) -> Image.Image:
	# Create a new image with the specified background color
	image = Image.open(image_path).convert("RGB")
	
	# Load a font
	font = _load_font(font_style, font_size)

	# Validate inputs
	if not text or not isinstance(text, str):
		raise ValueError("Text must be a non-empty string")
	if not position or len(position) != 2:
		raise ValueError("Position must be a tuple of (x, y)")
	if not isinstance(font_size, int) or font_size <= 0:
		raise ValueError("Font size must be a positive integer")
	
	# Single position mode
	# Draw the text onto the image
	image = _draw_text(image, position, text, text_color, font, opacity=opacity)
	# image.show()
	
	# Use custom output path if provided, otherwise use default
	if output_path is None:
		basename = os.path.basename(image_path)
		name, ext = os.path.splitext(basename)
		outputs_dir = ensure_user_dir("outputs")
		output_path = os.path.join(outputs_dir, f"{name}_edited{ext}")
	else:
		# Ensure directory exists for custom output path
		output_dir = os.path.dirname(output_path)
		if output_dir:  # Only create if there's a directory component
			os.makedirs(output_dir, exist_ok=True)
	
	image.convert("RGB").save(output_path)
	print(f"Image saved to {output_path}")

	return image

def make_coordinates_template(image_path, template_name, max_width=1280, max_height=720) -> None:
	# Setup a hidden Tkinter root for the dialog boxes
	root = tk.Tk()
	root.withdraw()
	try:
		icon_path = get_resource_path("icon.ico")
		if os.path.exists(icon_path):
			root.iconbitmap(icon_path)
	except Exception:
		pass

	# Load the image
	img = cv2.imread(image_path)
	points: dict = {}

	if img is None:
		raise ValueError(f"Could not load image: {image_path}")

	# Validate template name
	if not template_name or not isinstance(template_name, str) or not template_name.strip():
		raise ValueError("Template name must be a non-empty string")

	# Get original dimensions
	original_height, original_width = img.shape[:2]
	
	# Calculate scaling factor to fit within max dimensions
	scale_x = max_width / original_width
	scale_y = max_height / original_height
	scale = min(scale_x, scale_y, 1.0)  # Don't upscale, only downscale
	
	# Resize if needed
	if scale < 1.0:
		new_width = int(original_width * scale)
		new_height = int(original_height * scale)
		display_img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)
		print(f"Image resized for display: {original_width}x{original_height} -> {new_width}x{new_height}")
	else:
		display_img = img.copy()
		scale = 1.0
	
	font_size = 20
	font_color = "black"
	font_style = "default"

	def _draw_instructions(target_img):
		instruction = "Left click: add point | Enter/Space: finish | Esc: cancel"
		cv2.putText(target_img, instruction, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

	# This function will be called whenever a mouse event happens
	def click_event(event, x, y, flags, params):
		if event == cv2.EVENT_LBUTTONDOWN:
			# Convert display coordinates to original image coordinates
			original_x = int(round(x / scale))
			original_y = int(round(y / scale))
			
			# Instead of input(), we use a GUI dialog
			label = simpledialog.askstring("Input", f"Name this point (original: {original_x}, {original_y}):", parent=root)
			if label is None or label.strip() == "":
				print("No label provided, point ignored.")
				return

			# # Ask for font size
			# font_size_str = simpledialog.askstring("Font Size", f"Font size for '{label}' (default: 20):", parent=root)
			# font_size = int(font_size_str) if font_size_str and font_size_str.strip() else 20
			
			# # Ask for font color
			# font_color = simpledialog.askstring("Font Color", f"Font color for '{label}' (default: black):", parent=root)
			# font_color = font_color.strip() if font_color and font_color.strip() else "black"
			
			# # Ask for font style - user can enter any font name from config, ./fonts/, or system
			# font_style = simpledialog.askstring("Font Style", f"Font for '{label}' (e.g., Arial, or filename without extension, default: default):", parent=root)
			# font_style = font_style.strip() if font_style and font_style.strip() else "default"

			# Store ORIGINAL coordinates with font properties
			points[label] = {
				"x": original_x, 
				"y": original_y,
				"font_size": font_size,
				"font_color": font_color,
				"font_style": font_style,
				"opacity": 100
			}
			print(f"Coordinates captured: X={original_x}, Y={original_y}, Font: {font_size}px {font_color} {font_style}")

			# Visual feedback: draw a small circle where you clicked
			cv2.circle(display_img, (x, y), 5, (0, 255, 0), -1)
			cv2.line(display_img, (x - 8, y), (x + 8, y), (0, 255, 0), 1)
			cv2.line(display_img, (x, y - 8), (x, y + 8), (0, 255, 0), 1)
			cv2.putText(display_img, label, (x + 10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
			_draw_instructions(display_img)
			cv2.imshow("Template Maker", display_img)
			
			# Save original coordinates to a global or return them
			global selected_point
			selected_point = (original_x, original_y)

	print("Click on the image where you want the text. Press Enter/Space to finish or Esc to cancel.")
	_draw_instructions(display_img)
	cv2.imshow("Template Maker", display_img)
	cv2.setMouseCallback("Template Maker", click_event)
	
	cancelled = False
	while True:
		key = cv2.waitKey(20) & 0xFF
		if key in (ord('q'), 13, 32):  # q, Enter, Space
			break
		if key == 27:  # Esc
			cancelled = True
			break
	cv2.destroyAllWindows()

	if cancelled:
		print("Template creation cancelled.")
		return

	# Save as JSON
	templates_dir = ensure_user_dir("coord_templates")
	template_path = os.path.join(templates_dir, f"{template_name}.json")
	with open(template_path, "w") as f:
		json.dump(points, f, indent=4)
	print(f"Template saved as {template_name}.json")

def apply_template_to_image(image_path, template_name, text_mapping: dict, text_color=(0, 0, 0), font_size=20, font_overrides=None, output_path=None, opacity=100) -> Image.Image:
	"""
	Apply multiple texts to an image using a saved coordinate template.
	
	Args:
		image_path: Path to the image
		template_name: Name of the template (without .json extension)
		text_mapping: Dictionary mapping point names to text strings
			Example: {"name": "John Doe", "date": "2025-01-01"}
		text_color: Color of the text (RGB tuple or color name)
		font_size: Size of the font
		font_overrides: Optional dict mapping point names to font settings to override template
			Example: {"name": {"font_size": 25, "font_color": "red", "font_style": "Arial"}}
	
	Returns:
		Image.Image: The edited image
	"""
	# Validate inputs
	if not template_name or not isinstance(template_name, str):
		raise ValueError("Template name must be a non-empty string")
	if not text_mapping or not isinstance(text_mapping, dict):
		raise ValueError("Text mapping must be a non-empty dictionary")
	if not isinstance(font_size, int) or font_size <= 0:
		raise ValueError("Font size must be a positive integer")
	
	# Load the template
	template_path = get_user_data_path("coord_templates", f"{template_name}.json")
	if not os.path.exists(template_path):
		raise FileNotFoundError(f"Template not found: {template_path}")
	
	with open(template_path, "r") as f:
		coords = json.load(f)
	
	# Load image
	image = Image.open(image_path).convert("RGB")
	
	# Debug: Print font overrides
	if font_overrides:
		_debug(f"DEBUG: Font overrides received: {font_overrides}")
	
	# Apply each text to its named coordinate
	for point_name, text in text_mapping.items():
		if point_name not in coords:
			print(f"Warning: Point '{point_name}' not found in template, skipping")
			continue
		
		point_data = coords[point_name]
		position = (point_data["x"], point_data["y"])
		
		# Check if there are overrides for this point
		if font_overrides and point_name in font_overrides:
			overrides = font_overrides[point_name]
			point_font_size = overrides.get("font_size", point_data.get("font_size", font_size))
			point_color = overrides.get("font_color", point_data.get("font_color", text_color))
			point_style = overrides.get("font_style", point_data.get("font_style", "default"))
			point_opacity = overrides.get("opacity", point_data.get("opacity", opacity))
			_debug(f"DEBUG: Using overrides for {point_name}: size={point_font_size}, color={point_color}, style={point_style}")
		else:
			# Use point-specific font settings if available, otherwise use defaults
			point_font_size = point_data.get("font_size", font_size)
			point_color = point_data.get("font_color", text_color)
			point_style = point_data.get("font_style", "default")
			point_opacity = point_data.get("opacity", opacity)
			_debug(f"DEBUG: Using template defaults for {point_name}: size={point_font_size}, color={point_color}, style={point_style}")
		
		# Load font with point-specific size
		font = _load_font(point_style, point_font_size)
		
		image = _draw_text(image, position, text, point_color, font, opacity=point_opacity)
		print(f"Applied '{text}' at {point_name} {position} with {point_font_size}px {point_color} font")
	
	# Use custom output path if provided, otherwise use default
	if output_path is None:
		basename = os.path.basename(image_path)
		name, ext = os.path.splitext(basename)
		outputs_dir = ensure_user_dir("outputs")
		output_path = os.path.join(outputs_dir, f"{name}_edited{ext}")
	else:
		# Ensure directory exists for custom output path
		output_dir = os.path.dirname(output_path)
		if output_dir:  # Only create if there's a directory component
			os.makedirs(output_dir, exist_ok=True)
	
	image.convert("RGB").save(output_path)
	print(f"Image saved to {output_path}")
	
	return image

def apply_template_interactive(image_path, template_name, text_color=(0, 0, 0), font_size=20, opacity=100) -> Image.Image:
	"""
	Interactive version - prompts user for text for each coordinate in template.
	
	Args:
		image_path: Path to the image
		template_name: Name of the template (without .json extension)
		text_color: Color of the text
		font_size: Size of the font
	
	Returns:
		Image.Image: The edited image
	"""
	# Load the template
	template_path = get_user_data_path("coord_templates", f"{template_name}.json")
	if not os.path.exists(template_path):
		raise FileNotFoundError(f"Template not found: {template_path}")
	
	with open(template_path, "r") as f:
		coords = json.load(f)
	
	# Setup Tkinter for dialogs
	root = tk.Tk()
	root.withdraw()
	
	# Collect text for each coordinate
	text_mapping = {}
	for point_name, point_data in coords.items():
		text = simpledialog.askstring(
			"Enter Text", 
			f"Enter text for '{point_name}' at ({point_data['x']}, {point_data['y']}):",
			parent=root
		)
		if text and text.strip():
			text_mapping[point_name] = text
	
	root.destroy()
	
	# Use the main function to apply texts
	return apply_template_to_image(image_path, template_name, text_mapping, text_color, font_size, opacity=opacity)

def list_templates(_print=False) -> list:
	"""
	List all available coordinate templates.
	
	Args:
		show_details: If True, prints coordinate names for each template
	
	Returns:
		list: List of template names (without .json extension)
	"""
	templates_dir = get_user_data_path("coord_templates")
	
	if not os.path.exists(templates_dir):
		print("No templates directory found.")
		return []
	
	templates = [f.replace(".json", "") for f in os.listdir(templates_dir) if f.endswith(".json")]
	
	if not templates:
		print("No templates found.")
		return []
	
	if _print:
		print(f"\nFound {len(templates)} template(s):")
		for template_name in templates:
			print(f"  - {template_name}")
			
	return templates

def update_template_fonts(template_name, font_updates: dict) -> None:
	"""
	Update font settings in an existing template.
	
	Args:
		template_name: Name of the template (without .json extension)
		font_updates: Dictionary mapping point names to font settings
			Example: {"name": {"font_size": 25, "font_color": "red", "font_style": "bold"}}
	"""
	template_path = get_user_data_path("coord_templates", f"{template_name}.json")
	if not os.path.exists(template_path):
		raise FileNotFoundError(f"Template not found: {template_path}")
	
	# Load existing template
	with open(template_path, "r") as f:
		coords = json.load(f)
	
	# Update font settings for specified points
	for point_name, font_settings in font_updates.items():
		if point_name in coords:
			if "font_size" in font_settings:
				coords[point_name]["font_size"] = font_settings["font_size"]
			if "font_color" in font_settings:
				coords[point_name]["font_color"] = font_settings["font_color"]
			if "font_style" in font_settings:
				coords[point_name]["font_style"] = font_settings["font_style"]
			if "opacity" in font_settings:
				coords[point_name]["opacity"] = _clamp_opacity(font_settings["opacity"])
			print(f"Updated font settings for '{point_name}'")
		else:
			print(f"Warning: Point '{point_name}' not found in template")
	
	# Save updated template
	template_dir = os.path.dirname(template_path)
	if template_dir:
		os.makedirs(template_dir, exist_ok=True)
	with open(template_path, "w") as f:
		json.dump(coords, f, indent=4)
	print(f"Template '{template_name}' updated successfully")

