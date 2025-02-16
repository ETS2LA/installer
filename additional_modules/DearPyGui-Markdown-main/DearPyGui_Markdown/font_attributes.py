import ast
import os.path

from .attribute_types import *


class Font(Attribute):
    color: list[int, int, int, int]
    size: int | None

    def __init__(self, color: str | list, size: str | float | int):
        if isinstance(size, str):
            try:
                size = ast.literal_eval(size)
            except Exception:
                traceback.print_exc()
                size = None
        self.size = size

        if not isinstance(color, list) and not isinstance(color, tuple):
            try:
                color = ast.literal_eval(color)
            except Exception:
                color = color.removeprefix('#')
                color = tuple(int(color[i:i + 2], 16) for i in [*range(0, len(color), 2)])  # HEX to RGB
        color = list(color)[:4:]
        for i in range(4 - len(color)):
            color.append(255)
        self.color = color


class Default(FontAttribute): ...


class Bold(FontAttribute): ...


class Italic(FontAttribute): ...


class BoldItalic(FontAttribute): ...


class H1(FontAttribute):
    font_multiply = 2


class H2(FontAttribute):
    font_multiply = 1.5


class H3(FontAttribute):
    font_multiply = 1.17


class H4(FontAttribute):
    font_multiply = 1


class H5(FontAttribute):
    font_multiply = 0.83


class H6(FontAttribute):
    font_multiply = 0.67


def set_font(font_size: int | float = 13, *,
             default: str | os.PathLike[str] = None,
             bold: str | os.PathLike[str] = None,
             italic: str | os.PathLike[str] = None,
             italic_bold: str | os.PathLike[str] = None) -> int:
    """
    :return: default font
    """
    fonts = {
        Default: default,
        Bold: bold,
        Italic: italic,
        BoldItalic: italic_bold,
    }
    for Font in fonts:
        font_path = fonts[Font]
        if font_path:
            Font.set_font(font_path, font_size)
        else:
            Font.set_font(Font.font_path, font_size)

    return Default.get_font()
