import customtkinter as ctk
from tkinter import filedialog, messagebox
from ctk_colorpicker_plus import AskColor
from PIL import Image, ImageTk
import os
import json
import functions as fn
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from __main__ import PixelTyperApp

CONFIG = fn.CONFIG  # Import CONFIG for font access


def _get_available_fonts():
	"""Get all available fonts from config, ./fonts/ directory, and system"""
	fonts = []  # Don't include "default" - it's a non-resizable bitmap font
	
	# Add fonts from config
	config_fonts = list(CONFIG.get("fonts", {}).keys())
	fonts.extend(config_fonts)
	
	# Scan ./fonts/ directory for any .ttf/.TTF/.otf/.OTF files
	fonts_dir = "./fonts"
	if os.path.exists(fonts_dir):
		for filename in os.listdir(fonts_dir):
			if filename.lower().endswith(('.ttf', '.otf')):
				# Remove extension and add to list if not already there
				font_name = os.path.splitext(filename)[0]
				if font_name not in fonts:
					fonts.append(font_name)
	
	# Add common system fonts (platform-specific)
	import platform
	system = platform.system()
	
	if system == "Windows":
		system_fonts_dir = "C:\\Windows\\Fonts"
		common_fonts = ["Arial", "Times New Roman", "Courier New", "Verdana", "Tahoma", "Comic Sans MS", "Georgia", "Impact", "Trebuchet MS"]
	elif system == "Darwin":  # macOS
		system_fonts_dir = "/System/Library/Fonts"
		common_fonts = ["Arial", "Helvetica", "Times New Roman", "Courier", "Verdana", "Georgia", "Monaco"]
	else:  # Linux
		system_fonts_dir = "/usr/share/fonts"
		common_fonts = ["DejaVu Sans", "Liberation Sans", "Ubuntu"]
	
	# Check which common system fonts exist
	if os.path.exists(system_fonts_dir):
		for font_name in common_fonts:
			if font_name not in fonts:
				fonts.append(f"[System] {font_name}")
	
	return fonts


def _load_config():
	config_path = os.path.join(os.path.dirname(__file__), "config.json")
	try:
		with open(config_path, "r") as f:
			return json.load(f)
	except Exception:
		return {}


def _get_theme():
	config = _load_config()
	theme = config.get("ui_theme", {})
	default_theme = {
		"appearance_mode": "dark",
		"colors": {
			"bg": "#0f1115",
			"panel": "#151922",
			"surface": "#1d2230",
			"surface_alt": "#1a1f2b",
			"accent": "#3b82f6",
			"accent_hover": "#2563eb",
			"text": "#e5e7eb",
			"text_muted": "#9ca3af",
			"border": "#2b3140",
			"success": "#22c55e",
			"warning": "#f59e0b",
			"error": "#ef4444"
		},
		"radii": {
			"panel": 12,
			"input": 8,
			"button": 10
		}
	}
	merged = default_theme
	if isinstance(theme, dict):
		merged.update({k: v for k, v in theme.items() if k in merged})
		if "colors" in theme and isinstance(theme["colors"], dict):
			merged["colors"].update(theme["colors"])
		if "radii" in theme and isinstance(theme["radii"], dict):
			merged["radii"].update(theme["radii"])
	return merged


THEME = _get_theme()
COLORS = THEME["colors"]
RADII = THEME["radii"]

# Set appearance mode
ctk.set_appearance_mode(THEME.get("appearance_mode", "dark"))


def style_button(btn, variant="primary"):
	if variant == "primary":
		btn.configure(
			fg_color=COLORS["accent"],
			hover_color=COLORS["accent_hover"],
			text_color="white",
			corner_radius=RADII["button"]
		)
	elif variant == "secondary":
		btn.configure(
			fg_color=COLORS["surface"],
			hover_color=COLORS["surface_alt"],
			text_color=COLORS["text"],
			border_width=1,
			border_color=COLORS["border"],
			corner_radius=RADII["button"]
		)
	elif variant == "ghost":
		btn.configure(
			fg_color="transparent",
			hover_color=COLORS["surface_alt"],
			text_color=COLORS["text"],
			corner_radius=RADII["button"]
		)


def style_entry(entry):
	entry.configure(
		fg_color=COLORS["surface"],
		text_color=COLORS["text"],
		placeholder_text_color=COLORS["text_muted"],
		border_color=COLORS["border"],
		corner_radius=RADII["input"]
	)


def style_label(label, muted=False):
	label.configure(text_color=COLORS["text_muted"] if muted else COLORS["text"])


class ImagePreviewWidget(ctk.CTkFrame):
	"""Modular image preview widget"""
	def __init__(self, master, parent_app: Optional['PixelTyperApp'] = None, **kwargs):
		super().__init__(master, **kwargs)
		self.parent_app = parent_app
		self.configure(fg_color=COLORS["panel"])
		
		self.current_image_path = None
		self.current_photo = None
		self.preview_label = ctk.CTkLabel(
			self,
			text="No image loaded",
			fg_color=COLORS["surface"],
			text_color=COLORS["text_muted"]
		)
		self.preview_label.pack(fill="both", expand=True, padx=10, pady=10)
	
	def load_image(self, image_path):
		"""Load and display image filling available space"""
		if not os.path.exists(image_path):
			self.preview_label.configure(text="Image not found", image=None)
			return
		
		self.current_image_path = image_path
		try:
			# Load image
			img = Image.open(image_path)
			
			# Use fixed target size for consistency (no shrinking)
			target_width = 600
			target_height = 750
			
			# Calculate scaling to fit within target while maintaining aspect ratio
			img_ratio = img.width / img.height
			target_ratio = target_width / target_height
			
			if img_ratio > target_ratio:
				# Image is wider - fit to width
				new_width = target_width
				new_height = int(target_width / img_ratio)
			else:
				# Image is taller - fit to height
				new_height = target_height
				new_width = int(target_height * img_ratio)
			
			img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
			self.current_photo = ctk.CTkImage(light_image=img_resized, dark_image=img_resized, 
											size=(new_width, new_height))
			self.preview_label.configure(image=self.current_photo, text="")
		except Exception as e:
			self.preview_label.configure(text=f"Error loading image:\n{str(e)}", image=None)
	
	def clear(self):
		"""Clear the preview"""
		self.current_image_path = None
		self.current_photo = None
		self.preview_label.configure(text="No image loaded", image=None)


class SimpleOverlayTab(ctk.CTkFrame):
	"""Tab for simple text overlay on images"""
	def __init__(self, master, parent_app: Optional['PixelTyperApp'] = None, **kwargs):
		super().__init__(master, **kwargs)
		self.parent_app = parent_app
		self.image_path = None
		self.configure(fg_color=COLORS["panel"])
		
		# Configure grid
		self.grid_columnconfigure(0, weight=1)
		
		# Image selection
		img_frame = ctk.CTkFrame(self, fg_color=COLORS["surface"], corner_radius=RADII["panel"])
		img_frame.grid(row=0, column=0, padx=20, pady=10, sticky="ew")
		
		label_img = ctk.CTkLabel(img_frame, text="Image:")
		style_label(label_img, muted=True)
		label_img.pack(side="left", padx=5)
		self.img_path_label = ctk.CTkLabel(img_frame, text="No image selected", anchor="w", text_color=COLORS["text"])
		self.img_path_label.pack(side="left", fill="x", expand=True, padx=5)
		btn_browse = ctk.CTkButton(img_frame, text="Browse", command=self.browse_image, width=100)
		style_button(btn_browse, "secondary")
		btn_browse.pack(side="right", padx=5)
		
		# Text input
		text_frame = ctk.CTkFrame(self, fg_color=COLORS["surface"], corner_radius=RADII["panel"])
		text_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
		
		label_text = ctk.CTkLabel(text_frame, text="Text:")
		style_label(label_text, muted=True)
		label_text.pack(anchor="w", padx=5, pady=5)
		self.text_entry = ctk.CTkEntry(text_frame, placeholder_text="Enter text to overlay")
		style_entry(self.text_entry)
		self.text_entry.pack(fill="x", padx=5, pady=5)
		
		# Position inputs
		pos_frame = ctk.CTkFrame(self, fg_color=COLORS["surface"], corner_radius=RADII["panel"])
		pos_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
		
		label_pos = ctk.CTkLabel(pos_frame, text="Position:")
		style_label(label_pos, muted=True)
		label_pos.pack(anchor="w", padx=5)
		coord_frame = ctk.CTkFrame(pos_frame, fg_color="transparent")
		coord_frame.pack(fill="x", padx=5, pady=5)
		
		label_x = ctk.CTkLabel(coord_frame, text="X:")
		style_label(label_x, muted=True)
		label_x.pack(side="left", padx=5)
		self.x_entry = ctk.CTkEntry(coord_frame, width=80, placeholder_text="0")
		style_entry(self.x_entry)
		self.x_entry.pack(side="left", padx=5)
		
		label_y = ctk.CTkLabel(coord_frame, text="Y:")
		style_label(label_y, muted=True)
		label_y.pack(side="left", padx=5)
		self.y_entry = ctk.CTkEntry(coord_frame, width=80, placeholder_text="0")
		style_entry(self.y_entry)
		self.y_entry.pack(side="left", padx=5)
		
		btn_select = ctk.CTkButton(coord_frame, text="Click to Select", command=self.select_coordinates)
		style_button(btn_select, "secondary")
		btn_select.pack(side="left", padx=10)
		
		# Styling options
		style_frame = ctk.CTkFrame(self, fg_color=COLORS["surface"], corner_radius=RADII["panel"])
		style_frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
		
		style_inner = ctk.CTkFrame(style_frame, fg_color="transparent")
		style_inner.pack(fill="x", padx=5, pady=5)
		
		label_fs = ctk.CTkLabel(style_inner, text="Font Size:")
		style_label(label_fs, muted=True)
		label_fs.pack(side="left", padx=5)
		self.fontsize_entry = ctk.CTkEntry(style_inner, width=60, placeholder_text="20")
		style_entry(self.fontsize_entry)
		self.fontsize_entry.insert(0, "20")
		self.fontsize_entry.pack(side="left", padx=5)
		
		label_color = ctk.CTkLabel(style_inner, text="Color:")
		style_label(label_color, muted=True)
		label_color.pack(side="left", padx=10)
		self.color_entry = ctk.CTkEntry(style_inner, width=100, placeholder_text="black")
		style_entry(self.color_entry)
		self.color_entry.insert(0, "black")
		self.color_entry.pack(side="left", padx=5)
		btn_pick = ctk.CTkButton(style_inner, text="Pick", width=50, command=self.pick_color)
		style_button(btn_pick, "secondary")
		btn_pick.pack(side="left", padx=5)
		
		# Font style dropdown
		label_font = ctk.CTkLabel(style_inner, text="Font:")
		style_label(label_font, muted=True)
		label_font.pack(side="left", padx=10)
		available_fonts = _get_available_fonts()
		self.font_style_menu = ctk.CTkOptionMenu(style_inner, values=available_fonts if available_fonts else ["Ocraext"], width=120)
		self.font_style_menu.configure(
			fg_color=COLORS["surface_alt"],
			button_color=COLORS["accent"],
			button_hover_color=COLORS["accent_hover"],
			text_color=COLORS["text"],
			dropdown_fg_color=COLORS["surface"],
			dropdown_hover_color=COLORS["surface_alt"],
			dropdown_text_color=COLORS["text"]
		)
		self.font_style_menu.set(available_fonts[0] if available_fonts else "Ocraext")
		self.font_style_menu.pack(side="left", padx=5)
		
		# Apply button
		btn_apply = ctk.CTkButton(self, text="Apply Text Overlay", command=self.apply_overlay,
					height=40, font=ctk.CTkFont(size=14, weight="bold"))
		style_button(btn_apply, "primary")
		btn_apply.grid(row=4, column=0, padx=20, pady=20, sticky="ew")
		
		# Status
		self.status_label = ctk.CTkLabel(self, text="", text_color=COLORS["text_muted"])
		self.status_label.grid(row=5, column=0, padx=20, pady=5)
	
	def browse_image(self):
		"""Browse for image file"""
		path = filedialog.askopenfilename(
			title="Select Image",
			filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif")]
		)
		if path:
			self.image_path = path
			self.img_path_label.configure(text=os.path.basename(path))
			# Don't show input image, only show output after processing
			# self.preview_widget.load_image(path)
			self.status_label.configure(text="Image loaded successfully", text_color=COLORS["success"])
	
	def select_coordinates(self):
		"""Open coordinate selection window"""
		if not self.image_path:
			messagebox.showwarning("No Image", "Please select an image first!")
			return
		
		self.status_label.configure(text="Click on image to select position, press 'q' to confirm", text_color=COLORS["accent"])
		import cv2
		
		img = cv2.imread(self.image_path)
		if img is None:
			messagebox.showerror("Error", "Failed to load image!")
			return
		
		max_width, max_height = 1280, 720
		original_height, original_width = img.shape[:2]
		
		scale_x = max_width / original_width
		scale_y = max_height / original_height
		scale = min(scale_x, scale_y, 1.0)
		
		if scale < 1.0:
			new_width = int(original_width * scale)
			new_height = int(original_height * scale)
			display_img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)
		else:
			display_img = img.copy()
			scale = 1.0
		
		selected: list = [None]
		
		def click_event(event, x, y, flags, params):
			if event == cv2.EVENT_LBUTTONDOWN:
				original_x = int(x / scale)
				original_y = int(y / scale)
				selected[0] = (original_x, original_y)
				cv2.circle(display_img, (x, y), 5, (0, 255, 0), -1)
				cv2.imshow("Select Position", display_img)
		
		cv2.imshow("Select Position", display_img)
		cv2.setMouseCallback("Select Position", click_event)
		cv2.waitKey(0)
		cv2.destroyAllWindows()
		
		if selected[0]:
			self.x_entry.delete(0, "end")
			self.x_entry.insert(0, str(selected[0][0]))
			self.y_entry.delete(0, "end")
			self.y_entry.insert(0, str(selected[0][1]))
			self.status_label.configure(text=f"Position selected: {selected[0]}", text_color=COLORS["success"])
	
	def pick_color(self):
		"""Open color picker dialog"""
		current_color = self.color_entry.get().strip() or "#000000"
		pick_color = AskColor(initial_color=current_color)  # Pass current color
		color = pick_color.get()  # Get the color hex string
		if color:
			self.color_entry.delete(0, "end")
			self.color_entry.insert(0, color)
	
	def apply_overlay(self):
		"""Apply text overlay to image"""
		if not self.image_path:
			messagebox.showwarning("No Image", "Please select an image first!")
			return
		
		text = self.text_entry.get().strip()
		if not text:
			messagebox.showwarning("No Text", "Please enter text to overlay!")
			return
		
		try:
			# Validate and parse inputs
			x_str = self.x_entry.get().strip()
			y_str = self.y_entry.get().strip()
			font_str = self.fontsize_entry.get().strip()
			
			if not x_str or not y_str:
				messagebox.showwarning("Missing Input", "Please enter X and Y coordinates!")
				return
			
			x = int(x_str)
			y = int(y_str)
			font_size = int(font_str) if font_str else 20
			
			if font_size <= 0:
				messagebox.showwarning("Invalid Input", "Font size must be positive!")
				return
			
			color = self.color_entry.get().strip() or "black"
			font_style = self.font_style_menu.get()
			
			# Ask user where to save
			basename = os.path.basename(self.image_path)
			name, ext = os.path.splitext(basename)
			default_output = f"./outputs/{name}_edited{ext}"
			
			# Ensure outputs directory exists
			os.makedirs("./outputs", exist_ok=True)
			
			# Ask user to choose save location
			output_path = filedialog.asksaveasfilename(
				title="Save Edited Image As",
				defaultextension=ext,
				initialdir="./outputs",
				initialfile=f"{name}_edited{ext}",
				filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif"), ("All files", "*.*")]
			)
			
			if not output_path:  # User cancelled
				self.status_label.configure(text="Operation cancelled", text_color=COLORS["warning"])
				return
			
			fn.create_image_with_text(
				text=text,
				image_path=self.image_path,
				position=(x, y),
				text_color=color,
				font_size=font_size,
				font_style=font_style,
				output_path=output_path
			)
			
			# Show success message with full path
			full_path = os.path.abspath(output_path)
			self.status_label.configure(text=f"✓ Image saved successfully", text_color=COLORS["success"])
			messagebox.showinfo("Success", f"Image saved to:\n{full_path}")
			
		except ValueError as e:
			messagebox.showerror("Invalid Input", f"Please enter valid numbers: {e}")
		except Exception as e:
			messagebox.showerror("Error", f"Failed to apply overlay: {e}")


class CreateTemplateTab(ctk.CTkFrame):
	"""Tab for creating coordinate templates"""
	def __init__(self, master, parent_app: Optional['PixelTyperApp'] = None, **kwargs):
		super().__init__(master, **kwargs)
		self.parent_app = parent_app
		self.image_path = None
		
		self.grid_columnconfigure(0, weight=1)
		
		# Instructions
		info_frame = ctk.CTkFrame(self, fg_color="transparent")
		info_frame.grid(row=0, column=0, padx=20, pady=10, sticky="ew")
		label_info = ctk.CTkLabel(info_frame, text="Create a reusable template by marking positions on an image",
					font=ctk.CTkFont(size=13))
		style_label(label_info, muted=True)
		label_info.pack(anchor="w")
		
		# Image selection
		img_frame = ctk.CTkFrame(self, fg_color=COLORS["surface"], corner_radius=RADII["panel"])
		img_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
		
		label_img = ctk.CTkLabel(img_frame, text="Image:")
		style_label(label_img, muted=True)
		label_img.pack(side="left", padx=5)
		self.img_path_label = ctk.CTkLabel(img_frame, text="No image selected", anchor="w", text_color=COLORS["text"])
		self.img_path_label.pack(side="left", fill="x", expand=True, padx=5)
		btn_browse = ctk.CTkButton(img_frame, text="Browse", command=self.browse_image, width=100)
		style_button(btn_browse, "secondary")
		btn_browse.pack(side="right", padx=5)
		
		# Template name
		name_frame = ctk.CTkFrame(self, fg_color=COLORS["surface"], corner_radius=RADII["panel"])
		name_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
		
		label_name = ctk.CTkLabel(name_frame, text="Template Name:")
		style_label(label_name, muted=True)
		label_name.pack(side="left", padx=5)
		self.template_name_entry = ctk.CTkEntry(name_frame, placeholder_text="e.g., certificate_template")
		style_entry(self.template_name_entry)
		self.template_name_entry.pack(side="left", fill="x", expand=True, padx=5)
		
		# Create button
		btn_create = ctk.CTkButton(self, text="Create Template (Click on Image)", command=self.create_template,
					height=40, font=ctk.CTkFont(size=14, weight="bold"))
		style_button(btn_create, "primary")
		btn_create.grid(row=3, column=0, padx=20, pady=20, sticky="ew")
		
		# Info text
		info = ctk.CTkTextbox(self, height=100, fg_color=COLORS["surface"])
		info.grid(row=4, column=0, padx=20, pady=10, sticky="ew")
		info.configure(text_color=COLORS["text"], border_width=1, border_color=COLORS["border"])
		info.insert("1.0", 
			"How to use:\n"
			"1. Select an image\n"
			"2. Enter a template name\n"
			"3. Click 'Create Template'\n"
			"4. Click on the image to mark positions\n"
			"5. Enter a label for each position\n"
			"6. Press 'q' when done\n\n"
			"Templates are saved to coord_templates/ folder")
		info.configure(state="disabled")
		
		# Status
		self.status_label = ctk.CTkLabel(self, text="", text_color=COLORS["text_muted"])
		self.status_label.grid(row=5, column=0, padx=20, pady=5)
	
	def browse_image(self):
		"""Browse for image file"""
		path = filedialog.askopenfilename(
			title="Select Image",
			filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif")]
		)
		if path:
			self.image_path = path
			self.img_path_label.configure(text=os.path.basename(path))
			self.status_label.configure(text="Image loaded", text_color=COLORS["success"])
	
	def create_template(self):
		"""Create a new coordinate template"""
		if not self.image_path:
			messagebox.showwarning("No Image", "Please select an image first!")
			return
		
		template_name = self.template_name_entry.get().strip()
		if not template_name:
			messagebox.showwarning("No Name", "Please enter a template name!")
			return
		
		try:
			self.status_label.configure(text="Click on image to mark positions...", text_color=COLORS["accent"])
			fn.make_coordinates_template(self.image_path, template_name, max_width=1280, max_height=720)
			self.status_label.configure(text=f"✓ Template '{template_name}' created!", text_color=COLORS["success"])
			messagebox.showinfo("Success", f"Template saved as {template_name}.json")
		except Exception as e:
			messagebox.showerror("Error", f"Failed to create template: {e}")
			self.status_label.configure(text="Error creating template", text_color=COLORS["error"])


class ApplyTemplateTab(ctk.CTkFrame):
	"""Tab for applying saved templates to images"""
	def __init__(self, master, parent_app: Optional['PixelTyperApp'] = None, **kwargs):
		super().__init__(master, **kwargs)
		self.parent_app = parent_app
		self.image_path = None
		self.template_data = None
		self.text_entries = {}
		self.font_size_entries = {}
		self.font_color_entries = {}
		self.font_style_entries = {}
		self.original_font_data = {}  # Track original values
		self.update_button = None  # Reference to update button
		self.configure(fg_color=COLORS["panel"])
		
		self.grid_columnconfigure(0, weight=1)
		
		# Image selection
		img_frame = ctk.CTkFrame(self, fg_color=COLORS["surface"], corner_radius=RADII["panel"])
		img_frame.grid(row=0, column=0, padx=20, pady=10, sticky="ew")
		
		label_img = ctk.CTkLabel(img_frame, text="Image:")
		style_label(label_img, muted=True)
		label_img.pack(side="left", padx=5)
		self.img_path_label = ctk.CTkLabel(img_frame, text="No image selected", anchor="w", text_color=COLORS["text"])
		self.img_path_label.pack(side="left", fill="x", expand=True, padx=5)
		btn_browse = ctk.CTkButton(img_frame, text="Browse", command=self.browse_image, width=100)
		style_button(btn_browse, "secondary")
		btn_browse.pack(side="right", padx=5)
		
		# Template selection
		template_frame = ctk.CTkFrame(self, fg_color=COLORS["surface"], corner_radius=RADII["panel"])
		template_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
		
		label_tpl = ctk.CTkLabel(template_frame, text="Template:")
		style_label(label_tpl, muted=True)
		label_tpl.pack(side="left", padx=5)
		self.template_menu = ctk.CTkOptionMenu(template_frame, values=["No templates"], command=self.on_template_selected)
		self.template_menu.configure(
			fg_color=COLORS["surface_alt"],
			button_color=COLORS["accent"],
			button_hover_color=COLORS["accent_hover"],
			text_color=COLORS["text"],
			dropdown_fg_color=COLORS["surface"],
			dropdown_hover_color=COLORS["surface_alt"],
			dropdown_text_color=COLORS["text"]
		)
		self.template_menu.pack(side="left", fill="x", expand=True, padx=5)
		btn_refresh = ctk.CTkButton(template_frame, text="Refresh", command=self.refresh_templates, width=100)
		style_button(btn_refresh, "secondary")
		btn_refresh.pack(side="right", padx=5)
		
		# Scrollable frame for text inputs
		self.text_inputs_frame = ctk.CTkScrollableFrame(self, label_text="Text Fields")
		self.text_inputs_frame.configure(
			fg_color=COLORS["surface"],
			label_text_color=COLORS["text"],
			border_color=COLORS["border"]
		)
		self.text_inputs_frame.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
		self.grid_rowconfigure(2, weight=1)
		
		# Buttons frame
		buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
		buttons_frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
		
		# Apply button
		btn_apply = ctk.CTkButton(buttons_frame, text="Apply Template to Image", command=self.apply_template,
					height=40, font=ctk.CTkFont(size=14, weight="bold"))
		style_button(btn_apply, "primary")
		btn_apply.pack(side="left", fill="x", expand=True, padx=(0, 5))
		
		# Update Template button (initially disabled)
		self.update_button = ctk.CTkButton(buttons_frame, text="Update Template", command=self.update_template,
					height=40, font=ctk.CTkFont(size=14, weight="bold"), state="disabled")
		style_button(self.update_button, "secondary")
		self.update_button.pack(side="left", fill="x", expand=True, padx=(5, 0))
		
		# Show preview checkbox
		preview_frame = ctk.CTkFrame(self, fg_color="transparent")
		preview_frame.grid(row=4, column=0, padx=20, pady=5, sticky="ew")
		self.show_preview_var = ctk.BooleanVar(value=True)
		self.show_preview_check = ctk.CTkCheckBox(
			preview_frame,
			text="Show preview popup after applying",
			variable=self.show_preview_var,
			text_color=COLORS["text"]
		)
		self.show_preview_check.pack(anchor="w")
		
		# Status
		self.status_label = ctk.CTkLabel(self, text="", text_color=COLORS["text_muted"])
		self.status_label.grid(row=5, column=0, padx=20, pady=5)
		
		# Initial load
		self.refresh_templates()
	
	def browse_image(self):
		"""Browse for image file"""
		path = filedialog.askopenfilename(
			title="Select Image",
			filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif")]
		)
		if path:
			self.image_path = path
			self.img_path_label.configure(text=os.path.basename(path))
			# Don't show input image, only show output after processing
			# self.preview_widget.load_image(path)
			self.status_label.configure(text="Image loaded", text_color=COLORS["success"])
	
	def refresh_templates(self):
		"""Refresh the list of available templates"""
		templates = fn.list_templates(_print=False)
		if templates:
			self.template_menu.configure(values=templates)
			self.template_menu.set(templates[0])
			self.on_template_selected(templates[0])
		else:
			self.template_menu.configure(values=["No templates"])
			self.template_menu.set("No templates")
			self.status_label.configure(text="No templates found", text_color=COLORS["warning"])
	
	def on_template_selected(self, template_name):
		"""Load template and create input fields"""
		if template_name == "No templates":
			return
		
		try:
			template_path = f"./coord_templates/{template_name}.json"
			with open(template_path, "r") as f:
				self.template_data = json.load(f)
			
			# Clear existing inputs
			for widget in self.text_inputs_frame.winfo_children():
				widget.destroy()
			self.text_entries.clear()
			self.font_size_entries.clear()
			self.font_color_entries.clear()
			self.font_style_entries.clear()
			self.original_font_data.clear()
			
			# Create input fields for each coordinate
			for point_name, point_data in self.template_data.items():
				frame = ctk.CTkFrame(self.text_inputs_frame, fg_color=COLORS["surface_alt"], border_width=1, border_color=COLORS["border"], corner_radius=RADII["panel"])
				frame.pack(fill="x", padx=5, pady=5)
				
				# Single line with all controls
				main_frame = ctk.CTkFrame(frame, fg_color="transparent")
				main_frame.pack(fill="x", padx=5, pady=5)
				
				# Point name and coordinates
				label_text = f"{point_name} ({point_data['x']}, {point_data['y']})"
				label_point = ctk.CTkLabel(main_frame, text=label_text, font=ctk.CTkFont(weight="bold"), width=150, anchor="w")
				style_label(label_point)
				label_point.pack(side="left", padx=(0, 10))
				
				# Text input
				label_text = ctk.CTkLabel(main_frame, text="Text:", width=40)
				style_label(label_text, muted=True)
				label_text.pack(side="left", padx=(0, 5))
				text_entry = ctk.CTkEntry(main_frame, placeholder_text="Enter text", width=150)
				style_entry(text_entry)
				text_entry.pack(side="left", padx=(0, 10))
				self.text_entries[point_name] = text_entry
				
				# Font size
				label_size = ctk.CTkLabel(main_frame, text="Size:")
				style_label(label_size, muted=True)
				label_size.pack(side="left", padx=(0, 5))
				font_size_entry = ctk.CTkEntry(main_frame, width=45)
				style_entry(font_size_entry)
				font_size_val = str(point_data.get("font_size", 20))
				font_size_entry.insert(0, font_size_val)
				font_size_entry.pack(side="left", padx=(0, 10))
				self.font_size_entries[point_name] = font_size_entry
				
				# # Font color
				# ctk.CTkLabel(main_frame, text="Color:").pack(side="left", padx=(0, 5))
				font_color_entry = ctk.CTkEntry(main_frame, width=60)
				style_entry(font_color_entry)
				font_color_val = point_data.get("font_color", "black")
				font_color_entry.insert(0, font_color_val)
				font_color_entry.pack(side="left", padx=(0, 5))
				self.font_color_entries[point_name] = font_color_entry
				
				# Color picker button
				pick_btn = ctk.CTkButton(main_frame, text="Pick", width=30,
										 command=lambda entry=font_color_entry: self.pick_color_for_entry(entry))
				style_button(pick_btn, "secondary")
				pick_btn.pack(side="left", padx=(0, 10))
				
				# Font style (dropdown)
				label_style = ctk.CTkLabel(main_frame, text="Style:")
				style_label(label_style, muted=True)
				label_style.pack(side="left", padx=(0, 5))
				
				# Get available fonts from all sources
				available_fonts = _get_available_fonts()
				font_style_val = point_data.get("font_style", "Ocraext")
				# Fallback to first available font if saved font not found
				if font_style_val not in available_fonts and available_fonts:
					font_style_val = available_fonts[0]
				elif not available_fonts:
					available_fonts = ["Ocraext"]
					font_style_val = "Ocraext"
				
				font_style_menu = ctk.CTkOptionMenu(main_frame, values=available_fonts, width=100, command=lambda _: self.check_for_changes())
				font_style_menu.configure(
					fg_color=COLORS["surface_alt"],
					button_color=COLORS["accent"],
					button_hover_color=COLORS["accent_hover"],
					text_color=COLORS["text"],
					dropdown_fg_color=COLORS["surface"],
					dropdown_hover_color=COLORS["surface_alt"],
					dropdown_text_color=COLORS["text"]
				)
				font_style_menu.set(font_style_val)
				font_style_menu.pack(side="left")
				self.font_style_entries[point_name] = font_style_menu
				
				# Store original values for change detection
				self.original_font_data[point_name] = {
					"font_size": font_size_val,
					"font_color": font_color_val,
					"font_style": font_style_val
				}
				
				# Bind change events to check for modifications
				font_size_entry.bind("<KeyRelease>", lambda e: self.check_for_changes())
				font_color_entry.bind("<KeyRelease>", lambda e: self.check_for_changes())
				# Font style dropdown already has command callback
			
			self.status_label.configure(text=f"Template '{template_name}' loaded with {len(self.template_data)} points", text_color=COLORS["success"])
			
		except Exception as e:
			messagebox.showerror("Error", f"Failed to load template: {e}")
	
	def check_for_changes(self):
		"""Check if any font fields have been modified and enable/disable update button"""
		if not self.update_button:
			return
		
		has_changes = False
		for point_name in self.original_font_data.keys():
			if point_name in self.font_size_entries:
				current_size = self.font_size_entries[point_name].get().strip()
				current_color = self.font_color_entries[point_name].get().strip()
				current_style = self.font_style_entries[point_name].get()  # OptionMenu returns string directly
				
				original = self.original_font_data[point_name]
				if (current_size != original["font_size"] or 
					current_color != original["font_color"] or 
					current_style != original["font_style"]):
					has_changes = True
					break
		
		if has_changes:
			self.update_button.configure(state="normal")
		else:
			self.update_button.configure(state="disabled")
	
	def pick_color_for_entry(self, entry):
		"""Open color picker dialog and update the given entry"""
		current_color = entry.get().strip() or "#000000"
		pick_color = AskColor(initial_color=current_color)  # Pass current color
		color = pick_color.get()  # Get the color hex string
		if color:
			entry.delete(0, "end")
			entry.insert(0, color)
			# Trigger change detection
			self.check_for_changes()
	
	def apply_template(self):
		"""Apply template with user-provided texts"""
		if not self.image_path:
			messagebox.showwarning("No Image", "Please select an image first!")
			return
		
		if not self.template_data:
			messagebox.showwarning("No Template", "Please select a template first!")
			return
		
		# Collect text inputs
		text_mapping = {}
		for point_name, entry in self.text_entries.items():
			text = entry.get().strip()
			if text:
				text_mapping[point_name] = text
		
		if not text_mapping:
			messagebox.showwarning("No Text", "Please enter at least one text field!")
			return
		
		# Collect font settings from UI (overrides template defaults)
		font_overrides = {}
		for point_name in text_mapping.keys():
			if point_name in self.font_size_entries:
				try:
					font_size = int(self.font_size_entries[point_name].get().strip())
					font_color = self.font_color_entries[point_name].get().strip()
					font_style = self.font_style_entries[point_name].get()
					
					font_overrides[point_name] = {
						"font_size": font_size,
						"font_color": font_color or "black",
						"font_style": font_style or "Ocraext"
					}
					print(f"DEBUG UI: Collected for {point_name}: size={font_size}, color={font_color}, style={font_style}")
				except ValueError:
					messagebox.showwarning("Invalid Input", f"Font size for '{point_name}' must be a number!")
					return
		
		print(f"DEBUG UI: Final font_overrides = {font_overrides}")
		
		try:
			template_name = self.template_menu.get()
			
			# Ask user where to save
			basename = os.path.basename(self.image_path)
			name, ext = os.path.splitext(basename)
			
			# Ensure outputs directory exists
			os.makedirs("./outputs", exist_ok=True)
			
			# Ask user to choose save location
			output_path = filedialog.asksaveasfilename(
				title="Save Edited Image As",
				defaultextension=ext,
				initialdir="./outputs",
				initialfile=f"{name}_edited{ext}",
				filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif"), ("All files", "*.*")]
			)
			
			if not output_path:  # User cancelled
				self.status_label.configure(text="Operation cancelled", text_color=COLORS["warning"])
				return
			
			fn.apply_template_to_image(
				image_path=self.image_path,
				template_name=template_name,
				text_mapping=text_mapping,
				text_color="black",
				font_size=20,
				font_overrides=font_overrides,
				output_path=output_path
			)
			
			# Show the output image in popup if checkbox is checked
			full_path = os.path.abspath(output_path)
			if os.path.exists(output_path):
				if self.show_preview_var.get() and self.parent_app:
					self.parent_app.show_preview_popup(output_path)
				self.status_label.configure(text="✓ Template applied successfully", text_color=COLORS["success"])
				messagebox.showinfo("Success", f"Image saved to:\n{full_path}")
			else:
				self.status_label.configure(text="✓ Template applied successfully", text_color=COLORS["success"])
				messagebox.showinfo("Success", f"Image saved to:\n{full_path}")
			
		except Exception as e:
			messagebox.showerror("Error", f"Failed to apply template: {e}")
	
	def update_template(self):
		"""Update template with modified font settings"""
		if not self.template_data:
			messagebox.showwarning("No Template", "Please select a template first!")
			return
		
		try:
			template_name = self.template_menu.get()
			font_updates = {}
			
			# Collect font settings for each point
			for point_name in self.template_data.keys():
				font_size_str = self.font_size_entries[point_name].get().strip()
				font_color = self.font_color_entries[point_name].get().strip()
				font_style = self.font_style_entries[point_name].get()  # OptionMenu returns string directly
				
				if not font_size_str:
					messagebox.showwarning("Missing Input", f"Font size for '{point_name}' cannot be empty!")
					return
				
				try:
					font_size = int(font_size_str)
					if font_size <= 0:
						messagebox.showwarning("Invalid Input", f"Font size for '{point_name}' must be positive!")
						return
				except ValueError:
					messagebox.showwarning("Invalid Input", f"Font size for '{point_name}' must be a number!")
					return
				
				font_updates[point_name] = {
					"font_size": font_size,
					"font_color": font_color or "black",
					"font_style": font_style or "normal"
				}
			
			# Update the template
			fn.update_template_fonts(template_name, font_updates)
			
			# Reload template to reflect changes
			self.on_template_selected(template_name)
			
			# Disable button again after update
			if self.update_button:
				self.update_button.configure(state="disabled")
			
			self.status_label.configure(text=f"✓ Template '{template_name}' updated!", text_color=COLORS["success"])
			messagebox.showinfo("Success", f"Template '{template_name}' updated successfully!")
			
		except Exception as e:
			messagebox.showerror("Error", f"Failed to update template: {e}")


class PixelTyperApp(ctk.CTk):
	"""Main application window"""
	def __init__(self):
		super().__init__()
		
		# Window setup
		self.title("PixelTyper - Image Text Overlay Tool")
		self.geometry("1200x700")
		self.configure(fg_color=COLORS["bg"])
		
		# Set application icon if available
		try:
			icon_path = "icon.ico"  # Place icon.ico in project root
			if os.path.exists(icon_path):
				self.iconbitmap(icon_path)
		except Exception as e:
			print(f"Could not load icon: {e}")
		
		# Configure grid
		self.grid_columnconfigure(0, weight=1)  # Full width
		self.grid_rowconfigure(0, weight=1)
		
		# Main content frame
		main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=COLORS["panel"])
		main_frame.grid(row=0, column=0, sticky="nsew")
		main_frame.grid_rowconfigure(1, weight=1)
		main_frame.grid_columnconfigure(0, weight=1)
		
		# Header
		header_frame = ctk.CTkFrame(main_frame, height=50, fg_color="transparent")
		header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
		
		label_title = ctk.CTkLabel(header_frame, text="PixelTyper",
					font=ctk.CTkFont(size=24, weight="bold"))
		style_label(label_title)
		label_title.pack(side="left", padx=10)
		
		# Tabview
		self.tabview = ctk.CTkTabview(main_frame)
		self.tabview.configure(
			fg_color=COLORS["panel"],
			segmented_button_fg_color=COLORS["surface"],
			segmented_button_selected_color=COLORS["accent"],
			segmented_button_selected_hover_color=COLORS["accent_hover"],
			segmented_button_unselected_color=COLORS["surface_alt"],
			text_color=COLORS["text"]
		)
		self.tabview.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
		
		# Create tabs
		self.tab_simple = self.tabview.add("Simple Overlay")
		self.tab_create = self.tabview.add("Create Template")
		self.tab_apply = self.tabview.add("Apply Template")
		
		# Initialize tab contents (no preview widget needed)
		self.simple_overlay_tab = SimpleOverlayTab(self.tab_simple, parent_app=self)
		self.simple_overlay_tab.pack(fill="both", expand=True)
		
		self.create_template_tab = CreateTemplateTab(self.tab_create, parent_app=self)
		self.create_template_tab.pack(fill="both", expand=True)
		
		self.apply_template_tab = ApplyTemplateTab(self.tab_apply, parent_app=self)
		self.apply_template_tab.pack(fill="both", expand=True)
	
	def show_preview_popup(self, image_path):
		"""Show image preview in a popup window"""
		if not os.path.exists(image_path):
			return
		
		# Create popup window
		popup = ctk.CTkToplevel(self)
		popup.title("Image Preview")
		popup.geometry("800x900")
		popup.configure(fg_color=COLORS["bg"])
		
		# Make it stay on top
		popup.attributes("-topmost", True)
		
		try:
			# Load image
			img = Image.open(image_path)
			
			# Scale to fit popup (max 750x800)
			max_width, max_height = 750, 800
			img_ratio = img.width / img.height
			target_ratio = max_width / max_height
			
			if img_ratio > target_ratio:
				new_width = max_width
				new_height = int(max_width / img_ratio)
			else:
				new_height = max_height
				new_width = int(max_height * img_ratio)
			
			img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
			
			# Display image
			photo = ctk.CTkImage(light_image=img_resized, dark_image=img_resized, 
								   size=(new_width, new_height))
			label = ctk.CTkLabel(popup, image=photo, text="")
			label.pack(padx=20, pady=20)
			
			# Close button
			close_btn = ctk.CTkButton(popup, text="Close", command=popup.destroy, width=100)
			style_button(close_btn, "secondary")
			close_btn.pack(pady=10)
			
		except Exception as e:
			popup.destroy()
			messagebox.showerror("Preview Error", f"Failed to load image: {e}")


def main():
	app = PixelTyperApp()
	app.mainloop()


if __name__ == "__main__":
	main()

