import copy
from typing import TypeVar

import dearpygui.dearpygui as dpg  # noqa

from .font_attributes import *
from .line_atributes import *
from .text_attributes import *


class AttributeController(list[Attribute]):
    dpg_group_theme: int = None
    text_color: list[int, int, int, int]
    font: None | int

    def __new__(cls, *args, **kwargs):
        if cls.dpg_group_theme is None:
            with dpg.theme() as cls.dpg_group_theme:
                with dpg.theme_component(dpg.mvAll):
                    dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 0, 0, category=dpg.mvThemeCat_Core)
        return list.__new__(cls)

    def __init__(self, attributes: list[Attribute]):
        super().__init__()
        self.clear()

        for attribute in reversed(attributes):
            if attribute in self:
                continue

            if attribute in [Bold, Italic]:
                if BoldItalic in self:
                    continue
                opposite_attribute = Italic if (attribute is Bold) else Bold
                if opposite_attribute in self:
                    self[self.index(opposite_attribute)] = BoldItalic  # noqa
                    continue
            self.append(attribute)

    def get_font(self) -> None | int:
        font_size = Default.get_now_font_size()

        used_heading_attribute = False
        for heading_attribute in [H1, H2, H3, H4, H5, H6]:
            if heading_attribute in self:
                font_size *= heading_attribute.font_multiply
                used_heading_attribute = True
                break

        if Font in self:
            _Font: Font = self[self.index(Font)]  # noqa
            font_size = _Font.size

        if Bold in self:
            self.font = Bold.get_font(font_size)
        elif Italic in self:
            self.font = Italic.get_font(font_size)
        elif BoldItalic in self:
            self.font = BoldItalic.get_font(font_size)
        else:
            if used_heading_attribute:
                self.font = Bold.get_font(font_size)
            else:
                self.font = Default.get_font(font_size)
        return self.font

    def get_color(self) -> list[int, int, int, int]:
        self.text_color = [255, 255, 255, 255]
        if Font in self:
            _Font: Font = self[self.index(Font)]  # noqa
            self.text_color = _Font.color

        if Url in self:
            _Url: Url = self[self.index(Url)]  # noqa
            self.text_color = _Url.color
        return self.text_color

    def get_height(self) -> float | int:
        return get_text_size('Tg,y', font=self.get_font())[1]

    def render(self, text: str, parent=0, attributes_group=0, max_text_height: int | float = -1):
        if Separator in self:
            return

        self.get_font()
        self.get_color()

        parent_text_group = parent
        if max_text_height > 0:
            spacer_height = max_text_height - get_text_size(text, font=self.font)[1]
            if spacer_height > 1:
                with dpg.group(parent=parent) as parent_text_group:
                    dpg.add_spacer(height=spacer_height, parent=parent_text_group)
                dpg.bind_item_theme(parent_text_group, self.dpg_group_theme)

        with dpg.group(parent=parent_text_group) as dpg_text_group:
            dpg_text = dpg.add_text(text, parent=dpg_text_group, color=self.text_color)
            dpg.bind_item_font(dpg_text, self.font)
        dpg.bind_item_theme(dpg_text_group, self.dpg_group_theme)

        self.render_attributes(dpg_text, dpg_text_group, self.font, attributes_group)

    @CallInNextFrame
    def render_attributes(self, dpg_text, dpg_text_group, font=None, attributes_group=0):
        strike_drawlist, strike_line = None, None
        if Strike in self:
            strike_drawlist, strike_line = Strike.render(dpg_text, dpg_text_group,
                                                         font=font,
                                                         parent=attributes_group,
                                                         color=self.text_color)

        underline_drawlist, underline_line = None, None
        if Underline in self:
            underline_drawlist, underline_line = Underline.render(dpg_text, dpg_text_group,
                                                                  font=font,
                                                                  parent=attributes_group,
                                                                  color=self.text_color)

        if Url in self:
            url_attribute: Url = self[self.index(Url)]  # noqa
            if strike_drawlist:  # Strike in self
                url_attribute.add_item_to_handler(strike_drawlist)
                url_attribute._objects.append(strike_line)
                dpg.configure_item(strike_line, color=url_attribute.color)

            if underline_drawlist:  # Underline in self
                url_attribute.line_color = url_attribute.color
            else:
                underline_drawlist, underline_line = Underline.render(dpg_text, dpg_text_group, font=font, parent=attributes_group)

            url_attribute.underline_objects.append(underline_line)
            dpg.configure_item(underline_line, color=url_attribute.line_color)

            url_attribute.render(dpg_text, font=font, parent=attributes_group)

        if Code in self:
            Code.render(dpg_text_group)
        if Pre in self:
            pre_attribute: Pre = self[self.index(Pre)]  # noqa
            pre_attribute.render(dpg_text_group)


SelfStrEntity = TypeVar("SelfStrEntity", bound="StrEntity")
SelfTextEntity = TypeVar("SelfTextEntity", bound="TextEntity")


class StrEntity(str):
    attributes: AttributeController

    def __init__(self, text: str = ''):
        self.attributes = AttributeController([])

        super(StrEntity, self).__init__()

    def set_attributes(self, attributes: list[Attribute] | Attribute):
        self.attributes = AttributeController(attributes)

    def __repr__(self):
        return f'<{str(self)} ({self.attributes})>'

    def __str__(self):
        return super(StrEntity, self).__str__()

    def __add__(self, __object: SelfStrEntity | SelfTextEntity) -> SelfStrEntity | SelfTextEntity:
        if isinstance(__object, StrEntity):
            if self.attributes == __object.attributes:
                str_entity = StrEntity(''.join([self, __object]))
                str_entity.attributes = self.attributes
                return str_entity
            elif isinstance(__object, StrEntity) and len(__object) == 0:
                return self
            elif len(self) == 0:
                return __object
            else:
                return TextEntity([self, __object])
        elif isinstance(__object, TextEntity) or issubclass(__object, TextEntity):
            add_object = self + __object[0]
            if isinstance(add_object, StrEntity):
                return TextEntity([add_object, *__object[1::]])
            elif isinstance(add_object, TextEntity):
                return TextEntity([self, *__object])
            elif isinstance(add_object, LineEntity):
                return LineEntity([self, *__object])
            else:
                return TextEntity([self]) + __object

    def get_width(self) -> float | int:
        font = self.attributes.get_font()
        text = str(self)
        return get_text_size(text, font=font)[0]

    def get_height(self) -> float | int:
        return self.attributes.get_height()

    def get_all_attributes(self):
        return [*self.attributes]

    def recreate_attributes(self):
        list_of_attributes = self.attributes.copy()
        del self.attributes
        self.attributes = AttributeController([])
        for i, attribute in enumerate(list_of_attributes):
            if not isinstance(attribute, type):
                attribute_connector = attribute.attribute_connector
                attribute = copy.deepcopy(attribute)
                attribute.attribute_connector = attribute_connector
            self.attributes.append(attribute)

    def items(self) -> list[SelfStrEntity]:
        items = [*self]
        for i in range(len(items)):
            items[i] = StrEntity(items[i])
            items[i].attributes = self.attributes
        return items

    def chars(self) -> list[SelfStrEntity]:
        return self.items()

    def split(self, sep: str | None = None, **kwargs) -> list[SelfStrEntity]:
        _list: list[StrEntity | str] = super(StrEntity, self).split(sep, **kwargs)
        for i in range(len(_list)):
            _list[i] = StrEntity(_list[i])
            _list[i].attributes = self.attributes
        return _list

    def render(self, parent=0, attributes_group=0, max_text_height: int | float = -1):
        self.attributes.render(text=str(self),
                               parent=parent,
                               attributes_group=attributes_group,
                               max_text_height=max_text_height)


class TextEntity(list[StrEntity | SelfTextEntity]):
    def split(self, sep: str | None = None) -> list[StrEntity | list[SelfStrEntity]]:
        _list = []
        for StrEntity in self:
            parts = StrEntity.split(sep)
            if len(parts) == 0:
                continue

            if len(_list) == 0:
                _list.extend(parts)
            else:
                _list[-1] = _list[-1] + parts[0]
                _list.extend(parts[1::])

        return _list

    def __add__(_self, __object: StrEntity | SelfTextEntity) -> SelfTextEntity:
        self = TextEntity(_self.copy())
        if isinstance(__object, StrEntity):
            add_object = self[-1] + __object
            if isinstance(add_object, StrEntity):
                self[-1] = add_object
            elif isinstance(add_object, TextEntity) or issubclass(add_object, TextEntity):
                del self[-1]
                self.extend(add_object)
            else:
                raise ValueError(f'Undefined type: {type(add_object)}')
            return self
        else:
            add_object = self[-1] + __object[0]
            if isinstance(add_object, StrEntity):
                self[-1] = add_object
                self.extend(__object[1::])
            elif isinstance(add_object, TextEntity) or issubclass(add_object, TextEntity):
                self.extend(__object)
            else:
                raise ValueError(f'Undefined type: {type(add_object)}')
            return self

    def __repr__(self):
        return f'<TE{list([*self])}>'

    def __str__(self):
        return ''.join(str(item) for item in self)

    def recreate_attributes(self):
        for item in self:
            item.recreate_attributes()

    def get_width(self) -> float | int:
        width = 0
        for item in self:
            width += item.get_width()

        return width

    def get_height(self) -> float | int:
        max_height = 0
        for item in self:
            height = item.get_height()
            if height > max_height:
                max_height = height
        return max_height

    @property
    def attributes(self) -> AttributeController:
        if len(self) == 0:
            return AttributeController([])
        return self[0].attributes

    def get_all_attributes(self) -> list[Attribute]:
        attributes = []
        for item in self:
            attributes.extend(item.get_all_attributes())
        return attributes

    def items(self) -> list[StrEntity | SelfTextEntity]:
        return [*self]

    def chars(self) -> list[StrEntity]:
        all_chars = []
        for item in self:
            all_chars.extend(item.chars())
        return all_chars

    def render(self, parent=0, attributes_group=0, max_text_height: int | float = -1):
        with dpg.group(horizontal=True, parent=parent) as group:
            for item in self:
                item.render(parent=group,
                            attributes_group=attributes_group,
                            max_text_height=max_text_height)
        dpg.bind_item_theme(group, AttributeController.dpg_group_theme)


class LineEntity(TextEntity):
    post_render_queue: list

    def __repr__(self):
        return f'<LE{list([*self])}>'

    def __str__(self):
        return '\n'.join(str(item) for item in self)

    def recreate_attributes(self):
        for item in self:
            item.recreate_attributes()

    def append(self, __object: TextEntity | StrEntity) -> None:
        __object.recreate_attributes()
        super().append(__object)
        attributes = __object.get_all_attributes()
        list_attributes: list[List] = self.get_attributes_by_type(attributes, List)  # noqa
        if len(list_attributes) > 0:
            sorted_by_attribute_connector = {}
            for attribute in list_attributes:
                attribute_connector = attribute.attribute_connector
                if attribute_connector.first_line_objects is not None:
                    continue
                if attribute_connector not in sorted_by_attribute_connector:
                    sorted_by_attribute_connector[attribute_connector] = list()
                sorted_by_attribute_connector[attribute_connector].append(attribute)

            for attribute_connector in sorted_by_attribute_connector:
                attribute_connector.first_line_objects = []
                for attribute in sorted_by_attribute_connector[attribute_connector]:
                    attribute_connector.first_line_objects.append(attribute)

    @staticmethod
    def get_attributes_by_type(attributes: list[Attribute], type: type) -> list[Attribute]:
        return list(filter(lambda item: isinstance(item, type), attributes))

    @staticmethod
    def remove_duplicates_by_depth(attributes: list[Attribute]) -> list[Attribute]:
        return list({i.depth: i for i in attributes}.values())

    @staticmethod
    def get_width(text_entity: TextEntity | StrEntity) -> float | int:  # noqa
        width = text_entity.get_width()
        attributes = text_entity.get_all_attributes()

        blockquote_attributes: list[Blockquote] = LineEntity.get_attributes_by_type(attributes, Blockquote)  # noqa
        blockquote_attributes: list[Blockquote] = LineEntity.remove_duplicates_by_depth(blockquote_attributes)  # noqa
        for attribute in blockquote_attributes:
            width += attribute.get_width()

        list_attributes: list[List] = LineEntity.get_attributes_by_type(attributes, List)  # noqa
        list_attributes: list[List] = LineEntity.remove_duplicates_by_depth(list_attributes)  # noqa
        for attribute in list_attributes:
            width += attribute.get_width()
        separator_attributes: list[Separator] = LineEntity.get_attributes_by_type(attributes, Separator)  # noqa
        if len(separator_attributes) > 0:
            width = -1

        return width

    def render(self, parent=0, attributes_group=0):  # noqa
        self.post_render_queue = list()
        for item in self:
            with dpg.group(horizontal=True, parent=parent) as group:
                self.render_attributes(item, parent=group, attributes_group=attributes_group)
                item.render(parent=group,
                            attributes_group=attributes_group,
                            max_text_height=item.get_height())

            dpg.bind_item_theme(group, AttributeController.dpg_group_theme)

        for attribute in self.post_render_queue:
            attribute.post_render(attributes_group=attributes_group)
        del self.post_render_queue

    def render_attributes(self, text_entity: TextEntity, parent=0, attributes_group=0):
        attributes = text_entity.get_all_attributes()
        text_height = text_entity.get_height()
        blockquote_attributes: list[Blockquote] = self.get_attributes_by_type(attributes, Blockquote)  # noqa
        blockquote_attributes: list[Blockquote] = self.remove_duplicates_by_depth(blockquote_attributes)  # noqa
        for attribute in blockquote_attributes:
            attribute.render(text_height, parent=parent, attributes_group=attributes_group)

        list_attributes: list[List] = self.get_attributes_by_type(attributes, List)  # noqa
        list_attributes: list[List] = self.remove_duplicates_by_depth(list_attributes)  # noqa
        for attribute in list_attributes:
            attribute.render(text_height, parent=parent, attributes_group=attributes_group)
            self.post_render_queue.append(attribute)

        pre_attributes: list[Pre] = self.get_attributes_by_type(attributes, Pre)  # noqa
        for attribute in pre_attributes:
            self.post_render_queue.append(attribute)

        if Separator in attributes:
            Separator.render(parent=parent, attributes_group=attributes_group)
