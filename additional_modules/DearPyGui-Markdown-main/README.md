## DearPyGui-Markdown
Almost all basic Markdown implementation, as well as additional support in the form of text customization (color, size) as a custom HTML tag.



https://user-images.githubusercontent.com/46572469/205448714-32725bbb-c2ec-4022-9ea5-1ee4718017e8.mp4



## How to install
`pip install git+https://github.com/IvanNazaruk/DearPyGui-Markdown`

## How to run example
1. `git clone https://github.com/IvanNazaruk/DearPyGui-Markdown`
2. `cd DearPyGui-Markdown`
3. `pip install -r requirements.txt`
5. `python example/main.py`

## How to use
```python
import dearpygui.dearpygui as dpg

import DearPyGui_Markdown as dpg_markdown # Import the library

# For convenience, I will create variables in which I will 
# store the font size and the path to the different font types.
# You can use not all types, if a type not created will be used, 
# the default font will be applied.
# The default font should always be
font_size = 25
default_font_path = './fonts/InterTight-Regular.ttf'
bold_font_path = './fonts/InterTight-Bold.ttf'
italic_font_path = './fonts/InterTight-Italic.ttf'
italic_bold_font_path = './fonts/InterTight-BoldItalic.ttf'

dpg.create_context()

# Set the DPG font registry so that the library can create 
# and load different font variations (different sizes)
# This item is mandatory!
dpg_markdown.set_font_registry(dpg.add_font_registry())

# You can also put your own fonts load function, this is needed 
# to add specific characters from the font file (e.g. Cyrillic)
# An example of the use can be found in the example folder (example/font.py)
# dpg_markdown.set_add_font_function({CUSTOM_ADD_FONT_FUNCTION})


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
    dpg_markdown.add_text("This is text\n"
                          "*This is italic text*\n"
                          "__This is bold text__\n"
                          "***This is bold italic text***\n"
                          "<u>This is underline text</u>")

dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
```
## What supports?
- [x] Headings
- [x] Horizontal Rules
- [x] Styling text
    - [x] Bold
    - [x] Italic
    - [x] Strikethrough
    - [x] Links
    - [ ] Subscript
    - [ ] Superscript
- [x] Blockquotes
- [x] Lists:
    - [x] Ordered
    - [x] Unordered 
    - [x] Task
    - [x] Nested
- [x] Code:
   - [x] Line **\`**
   - [x] Blocks **\`\`\`**
   - [x] Syntax highlight **\`\`\`python** (need installed Pygments: `pip install pygments`)
- [ ] Images:
   - [ ] Link
   - [ ] Path
   - [ ] Emoji
- [ ] Table
## Custom HTML tag
#### \<font\>
1. RGB color: 
   - `<font color="(255, 50, 255)">Test</font>`
   - `<font color="255, 50, 255, 50">Test</font>`          
   - `<font color="[50, 50, 255, 100]">Test</font>`   
2. HEX color:
   - `<font color="#9628d1">Test</font>`  
   - `<font color="#9628d1ba">Test</font>`  
3. Size:
   - `<font size=50>Test</font>`  
   - `<font size="25">Test</font>` 
4. Color + Size:
   - `<font size=50 color="(255, 50, 255)">Test</font>`  
   - `<font size="20" color="#9628d1ba">Test</font>`  
