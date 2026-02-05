import functions as fn

# Test the list_templates function
print("Available templates:")
print(fn.list_templates())

# Test the create_image_with_text function
file = './testimg.png'
print("Using test image file:", file)

output_path = fn.get_user_data_path("outputs", "testimg_edited.jpg")
fn.create_image_with_text(
    text="Hello, World!",
    image_path=file,
    position=(50, 50),  # Example position
    text_color="black",
    font_size=30,
    font_style="default",
    output_path=output_path
)
print(f"Image saved to {output_path}")

# Test the make_coordinates_template function
print("Creating a new template...")
fn.make_coordinates_template(
    image_path=file,
    template_name="test_template"
)
print("Template created successfully!")

# Test the apply_template_to_image function
print("Applying template to image...")
text_mapping = {
    "name_field": "John Doe",
    "date_field": "2026-02-03"
}
template_output_path = fn.get_user_data_path("outputs", "testimg_template_applied.jpg")
fn.apply_template_to_image(
    image_path=file,
    template_name="test_template",
    text_mapping=text_mapping,
    output_path=template_output_path
)
print(f"Template applied and image saved to {template_output_path}")
