import traceback

import dearpygui.dearpygui as dpg

from . import CallInNextFrame

font_registry = 0
add_font = dpg.add_font


def set_font_registry(font_registry_tag: int | str):
    global font_registry
    font_registry = font_registry_tag


def set_add_font_function(function):
    global add_font
    add_font = function


def math_round(number: float | int) -> int:
    return int(number + (0.5 if number > 0 else -0.5))


class AttributeConnector(list):
    handler: int | None = None

    def __hash__(self):
        return id(self)


class Attribute:
    attribute_connector: AttributeConnector | None = None

    @property
    def object(self):
        return type(self)

    def __eq__(self, other):
        if type(other) is type:
            return type(self) == other
        return super().__eq__(other)


class LineAttribute(Attribute):
    def get_width(self) -> int | float:
        ...

    def render(self, text_height: int | float, parent=0, attributes_group=0):
        ...

    @CallInNextFrame
    def post_render(self, attributes_group=0):
        ...


class FontAttribute(Attribute):
    _fonts: dict = None

    font_path: str
    font = None
    now_font_size = None

    @classmethod
    def set_font(cls, path, size: float | int):
        cls.font_path = path
        cls._fonts = {}
        size = math_round(size)
        cls.font = cls.get_font(size)
        cls.now_font_size = size

    @classmethod
    def get_font(cls, size: float | int = None):
        if size is None:
            return cls.font
        size = math_round(size)
        if cls._fonts is None:
            return None
        font = cls._fonts.get(size, None)
        if font is not None:
            return font
        font = add_font(file=cls.font_path, size=size, parent=font_registry)
        cls._fonts[size] = font
        return font

    @classmethod
    def get_now_font_size(cls):
        return cls.now_font_size


class HoverAttribute(Attribute):
    _mouse_move_handler = None
    _hovered_items = {}
    _handler: int = None

    now_hover_item = None

    def __new__(cls, *args, **kwargs):
        if cls._mouse_move_handler is None:
            with dpg.handler_registry() as cls._mouse_move_handler:
                dpg.add_mouse_move_handler(callback=lambda: cls._check_hovered_items())
        return super().__new__(cls)

    def __init__(self, attribute_connector: AttributeConnector | None):
        if attribute_connector is None:
            attribute_connector = AttributeConnector()
        self.attribute_connector = attribute_connector

    @classmethod
    def _check_hovered_items(cls):
        for item in list(cls._hovered_items):
            if not dpg.is_item_hovered(item):
                callback = cls._hovered_items[item]
                try:
                    callback()
                except Exception:
                    traceback.print_exc()
                del cls._hovered_items[item]

    @classmethod
    def add_to_check_hover_items(cls, item: int | str, callback=None):
        cls._hovered_items[item] = callback

    def _create_handler(self):
        if self.attribute_connector is not None:
            if self.attribute_connector.handler is not None:
                self._handler = self.attribute_connector.handler
                return

        with dpg.item_handler_registry() as handler:
            dpg.add_item_clicked_handler(callback=lambda s, info, u: self.click(info[0]))
            dpg.add_item_hover_handler(callback=lambda s, item, u: self._hover(item))
        self._handler = handler

        if self.attribute_connector is not None:
            self.attribute_connector.handler = self._handler

    def add_item_to_handler(self, item):
        if self._handler is None:
            self._create_handler()
        dpg.bind_item_handler_registry(item, self._handler)

    def render(self, *args, **kwargs):
        self.attribute_connector.append(self)

    def hover(self):
        ...

    def _hover(self, hovere_item):
        if self.now_hover_item is not None:
            if dpg.is_item_hovered(hovere_item):
                self.now_hover_item = hovere_item
            return
        self.now_hover_item = hovere_item
        self.add_to_check_hover_items(hovere_item, self._unhover)

        if self.attribute_connector is None:
            self.hover()
        else:
            for attribute in self.attribute_connector:
                attribute.hover()

    def unhover(self):
        ...

    def _unhover(self):
        if dpg.is_item_hovered(self.now_hover_item):
            self.add_to_check_hover_items(self.now_hover_item, self._unhover)
            return
        self.now_hover_item = None

        if self.attribute_connector is None:
            self.unhover()
        else:
            for attribute in self.attribute_connector:
                attribute.unhover()

    def click(self, mouse_button):
        ...
