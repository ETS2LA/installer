from . import get_text_size
from .attribute_types import *


class Underline(Attribute):
    @staticmethod
    def render(dpg_text: int, dpg_text_group: int, font=None, parent=0, color=(255, 255, 255, 255)):
        '''
        :return: [drawlist, draw_line]
        '''
        pos = dpg.get_item_pos(dpg_text_group)
        x, y = pos
        group_width, group_height = dpg.get_item_rect_size(dpg_text_group)
        text_width, text_height = get_text_size(dpg.get_value(dpg_text), font=font)
        y = y + (group_height - text_height) / 2
        with dpg.group(pos=[x, y], parent=parent) as drawlist_group:
            with dpg.drawlist(parent=drawlist_group, width=group_width, height=text_height) as drawlist:
                thickness = text_height / 15
                line_y = text_height - thickness + thickness / 5
                line = dpg.draw_line([0, line_y], [group_width, line_y], parent=drawlist, color=color, thickness=thickness)
        return drawlist, line


class Strike(Attribute):
    @staticmethod
    def render(dpg_text: int, dpg_text_group: int, font=None, parent=0, color=(255, 255, 255)):
        '''
        :return: [drawlist, draw_line]
        '''
        pos = dpg.get_item_pos(dpg_text_group)
        x, y = pos
        group_width, group_height = dpg.get_item_rect_size(dpg_text_group)
        text_width, text_height = get_text_size(dpg.get_value(dpg_text), font=font)
        y = y + (group_height - text_height) / 2
        with dpg.group(pos=[x, y], parent=parent) as drawlist_group:
            with dpg.drawlist(parent=drawlist_group, width=group_width, height=text_height) as drawlist:
                thickness = text_height / 15
                line_y = text_height / 2 + thickness / 2 + text_height / 20
                line = dpg.draw_line([0, line_y], [group_width, line_y], parent=drawlist, color=color, thickness=thickness)
        return drawlist, line


class Code(Attribute):
    color = (55, 55, 65, 255)
    border_color = color

    @classmethod
    def render(cls, dpg_text_group: int):
        width, height = dpg.get_item_rect_size(dpg_text_group)
        pos = dpg.get_item_pos(dpg_text_group)
        child = dpg.get_item_children(dpg_text_group, 1)[0]
        group = dpg.add_group(pos=pos, before=child)
        with dpg.drawlist(parent=group, width=width, height=height) as drawlist:
            dpg.draw_quad([0, 0], [width, 0],
                          [width, height], [0, height],
                          fill=cls.color,
                          color=cls.border_color,
                          parent=drawlist)


class Pre(Attribute):
    color = (55, 55, 65, 255)
    border_color = (110, 110, 130, 200)

    def __init__(self, attribute_connector: AttributeConnector):
        self.attribute_connector = attribute_connector
        self.attribute_connector.max_width = 0
        self.attribute_connector.x0, self.attribute_connector.y0 = (None, None)
        self.attribute_connector.x1, self.attribute_connector.y1 = (None, None)
        self.attribute_connector.used_y = []

    def render(self, dpg_text_group: int):
        self.dpg_text_group = dpg_text_group
        self.width, self.height = dpg.get_item_rect_size(dpg_text_group)
        pos = dpg.get_item_pos(dpg_text_group)
        pos_end = (self.width + pos[0], pos[1] + self.height)

        a_c = self.attribute_connector
        if a_c.x0 is None:
            a_c.x0, a_c.y0 = pos
            a_c.x1, a_c.y1 = pos_end

        if a_c.x0 > pos[0]:
            a_c.x0 = pos[0]
        if a_c.y0 > pos[1]:
            a_c.y0 = pos[1]
        if a_c.x1 < pos_end[0]:
            a_c.x1 = pos_end[0]
        if a_c.y1 < pos_end[1]:
            a_c.y1 = pos_end[1]

    @CallInNextFrame
    def post_render(self, attributes_group=0):
        width, height = dpg.get_item_rect_size(self.dpg_text_group)
        pos = dpg.get_item_pos(self.dpg_text_group)
        child = dpg.get_item_children(self.dpg_text_group, 1)[0]
        group = dpg.add_group(pos=pos, before=child)
        children = dpg.get_item_children(dpg.get_item_parent(self.dpg_text_group), 1)
        a_c = self.attribute_connector
        if children[-1] == self.dpg_text_group:
            width = a_c.x1 - pos[0]
            with dpg.group(parent=attributes_group, pos=(a_c.x0, a_c.y0)) as border_group:
                border_width = a_c.x1 - a_c.x0
                border_height = a_c.y1 - a_c.y0
                with dpg.drawlist(parent=border_group, width=border_width, height=border_height) as border_drawlist:
                    dpg.draw_quad([0, 0], [border_width, 0],
                                  [border_width, border_height], [0, border_height],
                                  color=self.border_color,
                                  parent=border_drawlist)

        with dpg.drawlist(parent=group, width=width, height=height) as drawlist:
            dpg.draw_quad([0, 0], [width, 0],
                          [width, height], [0, height],
                          fill=self.color,
                          color=self.color,
                          parent=drawlist)


class Url(HoverAttribute):
    color: list[int, int, int, int] = (85, 135, 205, 255)
    line_color: list[int, int, int, int] = (255, 255, 255, 0)
    hover_color: list[int, int, int, int] = (153, 187, 255, 255)

    url: str

    dpg_text_objects: list[int]
    underline_objects: list[int]

    def __init__(self, url: str, attribute_connector: AttributeConnector | None):
        super().__init__(attribute_connector)
        self.url = url
        self.dpg_text_objects = []
        self.underline_objects = []
        self.now_hover_item = None

    def render(self, dpg_text, font=None, parent=0):
        super().render()
        self.add_item_to_handler(dpg_text)
        self.dpg_text_objects.append(dpg_text)
        dpg.configure_item(dpg_text, color=self.color)

    def hover(self):
        for item in self.dpg_text_objects:
            dpg.configure_item(item, color=self.hover_color)
        for item in self.underline_objects:
            dpg.configure_item(item, color=self.hover_color)

    def unhover(self):
        for item in self.dpg_text_objects:
            dpg.configure_item(item, color=self.color)
        for item in self.underline_objects:
            dpg.configure_item(item, color=self.line_color)

    def click(self, mouse_button):
        if mouse_button in [2, 0]:
            import webbrowser
            webbrowser.open_new_tab(self.url)
