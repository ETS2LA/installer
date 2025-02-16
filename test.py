import dearpygui.dearpygui as dpg

import DearPyGui_Markdown as dpg_markdown # Import the library

# For convenience, I will create variables in which I will 
# store the font size and the path to the different font types.
# You can use not all types, if a type not created will be used, 
# the default font will be applied.
# The default font should always be
font_size = 25
default_font_path = 'launcher/Geist-Regular.ttf'
bold_font_path = 'launcher/Geist-Medium.ttf'
italic_font_path = 'launcher/Geist-Regular.ttf'
italic_bold_font_path = 'launcher/Geist-Medium.ttf'

dpg.create_context()

# Set the DPG font registry so that the library can create 
# and load different font variations (different sizes)
# This item is mandatory!
dpg_markdown.set_font_registry(dpg.add_font_registry())

# You can also put your own fonts load function, this is needed 
# to add specific characters from the font file (e.g. Cyrillic)
# An example of the use can be found in the example folder (example/font.py)
# dpg_markdown.set_add_font_function({CUSTOM_ADD_FONT_FUNCTION})
def add_font_function(file: str, size: int, parent: int) -> int:
    with dpg.font_registry():
        font_id = dpg.add_font(file, size)
        
    return font_id

dpg_markdown.set_add_font_function(add_font_function)

# Function to set fonts, the first time you call it, 
# you must specify the default font (default argument)
# Return the default DPG font
dpg_font = dpg_markdown.set_font(
    font_size=font_size,
    default=default_font_path,
    bold=bold_font_path,
    italic=italic_font_path,
    italic_bold=italic_bold_font_path
)

# Apply the created DPG font
dpg.bind_font(dpg_font)

# Create DPG viewport, could have done this after dpg.create_context()
dpg.create_viewport(title='Markdown example', width=300, height=300)

# Minimal example of working with the library
with dpg.window(label="Example", width=240, height=210):
    dpg.add_text("This is text")
    dpg_markdown.add_text("This is text\n"
                          "*This is italic text*\n"
                          "__This is bold text__\n"
                          "***This is bold italic text***\n"
                          "<u>This is underline text</u>", wrap=200)

dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()