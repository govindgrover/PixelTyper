from datetime import date

from PIL import Image, ImageDraw, ImageFont
import cv2
import json, os

import tkinter as tk
from tkinter import simpledialog, filedialog

CONFIG: dict = json.load(open("config.json", "r"))

def create_image_with_text(text, image_path, position: tuple =(), text_color=(0, 0, 0), font_size=20) -> Image.Image:
	# Create a new image with the specified background color
	image = Image.open(image_path).convert("RGB")
	
	# Initialize ImageDraw
	draw = ImageDraw.Draw(image)
	
	# Load a font
	try:
		font = ImageFont.truetype(CONFIG["fonts"]["Ocraext"]["normal"], font_size)
	except IOError:
		font = ImageFont.load_default()

	# Validate inputs
	if not text or not isinstance(text, str):
		raise ValueError("Text must be a non-empty string")
	if not position or len(position) != 2:
		raise ValueError("Position must be a tuple of (x, y)")
	if not isinstance(font_size, int) or font_size <= 0:
		raise ValueError("Font size must be a positive integer")
	
	# Single position mode
	# Draw the text onto the image
	draw.text(position, text, fill=text_color, font=font)
	# image.show()
	basename = os.path.basename(image_path)
	name, ext = os.path.splitext(basename)
	output_path = f"./outputs/{name}_edited{ext}"
	image.save(output_path)
	print(f"Image saved to {output_path}")

	return image

def make_coordinates_template(image_path, template_name, max_width=1280, max_height=720) -> None:
	# Setup a hidden Tkinter root for the dialog boxes
	root = tk.Tk()
	root.withdraw()

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
	
	# This function will be called whenever a mouse event happens
	def click_event(event, x, y, flags, params):
		if event == cv2.EVENT_LBUTTONDOWN:
			# Convert display coordinates to original image coordinates
			original_x = int(x / scale)
			original_y = int(y / scale)
			
			# Instead of input(), we use a GUI dialog
			label = simpledialog.askstring("Input", f"Name this point (original: {original_x}, {original_y}):", parent=root)
			if label is None or label.strip() == "":
				print("No label provided, point ignored.")
				return
			
			# Ask for font size
			font_size_str = simpledialog.askstring("Font Size", f"Font size for '{label}' (default: 20):", parent=root)
			font_size = int(font_size_str) if font_size_str and font_size_str.strip() else 20
			
			# Ask for font color
			font_color = simpledialog.askstring("Font Color", f"Font color for '{label}' (default: black):", parent=root)
			font_color = font_color.strip() if font_color and font_color.strip() else "black"
			
			# Ask for font style
			font_style = simpledialog.askstring("Font Style", f"Font style for '{label}' (normal/bold/italic, default: normal):", parent=root)
			font_style = font_style.strip() if font_style and font_style.strip() else "normal"

			# Store ORIGINAL coordinates with font properties
			points[label] = {
				"x": original_x, 
				"y": original_y,
				"font_size": font_size,
				"font_color": font_color,
				"font_style": font_style
			}
			print(f"Coordinates captured: X={original_x}, Y={original_y}, Font: {font_size}px {font_color} {font_style}")

			# Visual feedback: draw a small circle where you clicked
			cv2.circle(display_img, (x, y), 5, (0, 255, 0), -1)
			cv2.putText(img, label, (x + 10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
			cv2.imshow("Template Maker", display_img)
			
			# Save original coordinates to a global or return them
			global selected_point
			selected_point = (original_x, original_y)

	print("Click on the image where you want the text. Press 'q' to confirm and exit.")
	cv2.imshow("Template Maker", display_img)
	cv2.setMouseCallback("Template Maker", click_event)
	
	cv2.waitKey(0)
	cv2.destroyAllWindows()

	# Save as JSON
	with open(f"./coord_templates/{template_name}.json", "w") as f:
		json.dump(points, f, indent=4)
	print(f"Template saved as {template_name}.json")

def apply_template_to_image(image_path, template_name, text_mapping: dict, text_color=(0, 0, 0), font_size=20) -> Image.Image:
	"""
	Apply multiple texts to an image using a saved coordinate template.
	
	Args:
		image_path: Path to the image
		template_name: Name of the template (without .json extension)
		text_mapping: Dictionary mapping point names to text strings
			Example: {"name": "John Doe", "date": "2025-01-01"}
		text_color: Color of the text (RGB tuple or color name)
		font_size: Size of the font
	
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
	template_path = f"./coord_templates/{template_name}.json"
	if not os.path.exists(template_path):
		raise FileNotFoundError(f"Template not found: {template_path}")
	
	with open(template_path, "r") as f:
		coords = json.load(f)
	
	# Load image
	image = Image.open(image_path).convert("RGB")
	draw = ImageDraw.Draw(image)
	
	# Apply each text to its named coordinate
	for point_name, text in text_mapping.items():
		if point_name not in coords:
			print(f"Warning: Point '{point_name}' not found in template, skipping")
			continue
		
		point_data = coords[point_name]
		position = (point_data["x"], point_data["y"])
		
		# Use point-specific font settings if available, otherwise use defaults
		point_font_size = point_data.get("font_size", font_size)
		point_color = point_data.get("font_color", text_color)
		point_style = point_data.get("font_style", "normal")
		
		# Load font with point-specific size
		try:
			# TODO: Support font_style (bold/italic) by loading different font files
			font = ImageFont.truetype(CONFIG["fonts"]["Ocraext"]["normal"], point_font_size)
		except IOError:
			font = ImageFont.load_default()
		
		draw.text(position, text, fill=point_color, font=font)
		print(f"Applied '{text}' at {point_name} {position} with {point_font_size}px {point_color} font")
	
	# Save the image (overwrites if exists)
	basename = os.path.basename(image_path)
	name, ext = os.path.splitext(basename)
	output_path = f"./outputs/{name}_edited{ext}"
	image.save(output_path)
	print(f"Image saved to {output_path}")
	
	return image

def apply_template_interactive(image_path, template_name, text_color=(0, 0, 0), font_size=20) -> Image.Image:
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
	template_path = f"./coord_templates/{template_name}.json"
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
	return apply_template_to_image(image_path, template_name, text_mapping, text_color, font_size)

def list_templates(_print=False) -> list:
	"""
	List all available coordinate templates.
	
	Args:
		show_details: If True, prints coordinate names for each template
	
	Returns:
		list: List of template names (without .json extension)
	"""
	templates_dir = "./coord_templates"
	
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
	template_path = f"./coord_templates/{template_name}.json"
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
			print(f"Updated font settings for '{point_name}'")
		else:
			print(f"Warning: Point '{point_name}' not found in template")
	
	# Save updated template
	with open(template_path, "w") as f:
		json.dump(coords, f, indent=4)
	print(f"Template '{template_name}' updated successfully")

