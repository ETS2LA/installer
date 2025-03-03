import ctypes

import dearpygui.dearpygui as dpg

import DearPyGui_Markdown as dpg_markdown

font_size = 25
default_path = './example/fonts/InterTight-Regular.ttf'
bold_path = './example/fonts/InterTight-Bold.ttf'
italic_path = './example/fonts/InterTight-Italic.ttf'
italic_bold_path = './example/fonts/InterTight-BoldItalic.ttf'


def add_font(file, size: int | float, parent=0, **kwargs) -> int:
    if not isinstance(size, (int, float)):
        raise ValueError(f'font size must be an integer or float. Not {type(size)}')

    with dpg.font(file, size, parent=parent, **kwargs) as font:
        dpg.add_font_range_hint(dpg.mvFontRangeHint_Default, parent=font)
        dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic, parent=font)
    return font


def load() -> int:
    '''
    :return: default font
    '''
    ctypes.windll.shcore.SetProcessDpiAwareness(1)

    dpg_markdown.set_font_registry(dpg.add_font_registry())
    dpg_markdown.set_add_font_function(add_font)

    return dpg_markdown.set_font(
        font_size=font_size,
        default=default_path,
        bold=bold_path,
        italic=italic_path,
        italic_bold=italic_bold_path
    )
