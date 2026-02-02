from PIL import Image, ImageDraw, ImageFont
import json
import os

CONFIG: dict = json.load(open("config.json", "r"))

def create_image_with_text(text, image_path, position, text_color=(0, 0, 0), font_size=20):
	# Create a new image with the specified background color
	image = Image.open(image_path).convert("RGB")
	
	# Initialize ImageDraw
	draw = ImageDraw.Draw(image)
	
	# Load a font
	try:
		font = ImageFont.truetype(CONFIG["fonts"]["Ocraext"]["normal"], font_size)
	except IOError:
		font = ImageFont.load_default()
	
	# Draw the text onto the image
	draw.text(position, text, fill=text_color, font=font)

	# image.show()
	image.save("./outputs/_editied-{}.jpg".format(os.path.basename(image_path)))

	return image

