import dearpygui.dearpygui as dpg

try:
    import DearPyGui_Markdown as dpg_markdown
except ModuleNotFoundError:
    import os
    import sys
    # import from parent folder
    current = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(os.path.dirname(current))
    import DearPyGui_Markdown as dpg_markdown

import font
import test_text

wrap_width = -1

dpg.create_context()
dpg.create_viewport(title='Markdown example', width=900, height=900)
dpg.setup_dearpygui()
dpg.bind_font(font.load())


def clear_input():
    dpg.configure_item('markdown_input', default_value='')


def add():
    text = dpg.get_value('markdown_input')
    dpg_markdown.add_text(text, parent='view_window', wrap=wrap_width)


def clear():
    dpg.delete_item('view_window', children_only=True)


def clear_and_add():
    clear()
    add()


def set_wrap_width(width: int | float):
    global wrap_width
    wrap_width = width

    if width < 0:
        dpg.configure_item('end_wrap_indicator', show=False)
        return

    pos = dpg.get_item_pos('start_wrap_indicator')
    pos[0] += wrap_width
    dpg.configure_item('end_wrap_indicator', pos=pos, show=True)


with dpg.theme() as child_window_theme:
    with dpg.theme_component(dpg.mvChildWindow):
        dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 0, 0, category=dpg.mvThemeCat_Core)

with dpg.window() as window:
    with dpg.table(resizable=False, header_row=False):
        dpg.add_table_column()
        dpg.add_table_column(width_stretch=False, width_fixed=True)
        with dpg.table_row():
            dpg.add_button(label='Clear input', callback=clear_input)
            with dpg.group(horizontal=True):
                dpg.add_spacer(width=3)
                dpg.add_button(label='Clear', callback=clear)
                dpg.add_button(label='Add', callback=add)
                dpg.add_button(label='C+A', callback=clear_and_add)

    with dpg.table(resizable=True, header_row=False):
        dpg.add_table_column(init_width_or_weight=0.5)
        dpg.add_table_column(init_width_or_weight=0.5)
        with dpg.table_row():
            with dpg.group():
                dpg.add_slider_int(default_value=wrap_width, min_value=-1, max_value=1_000, width=-1,
                                   callback=lambda _, width: set_wrap_width(width))
                dpg.add_input_text(width=-1, height=-2, tag='markdown_input', multiline=True, default_value=test_text.text)
            with dpg.group():
                with dpg.child_window(height=dpg_markdown.font_attributes.Default.get_now_font_size() * 2):
                    with dpg.group(horizontal=True):
                        dpg_markdown.add_text_italic('|', tag='start_wrap_indicator')
                        dpg_markdown.add_text_italic('|', tag='end_wrap_indicator', show=wrap_width > 0)
                with dpg.child_window(width=-1, height=-2, tag='view_window'):
                    dpg_markdown.add_text(test_text.text)

dpg.set_primary_window(window, True)
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
