import dearpygui.dearpygui as dpg

from . import get_text_size
from .attribute_types import CallInNextFrame
from .attribute_types import LineAttribute, AttributeConnector
from .font_attributes import Default


class Separator(LineAttribute):
    @staticmethod
    def render(parent=0, attributes_group=0):  # noqa
        height = get_text_size('|', font=Default.get_font())[1]
        with dpg.group(before=parent) as group:
            dpg.add_spacer(parent=group, height=int(height * 0.5))
            dpg.add_separator(parent=group)
            dpg.add_spacer(parent=group, height=int(height * 0.5))


class Blockquote(LineAttribute):
    width = 20
    line_width = 6

    depth: int
    color = [50, 55, 65, 255]

    drawlist_group: int

    def __init__(self, depth: int, attribute_connector: AttributeConnector):
        self.depth = depth
        self.attribute_connector = attribute_connector

    def __repr__(self):
        return f"<Blockquote.{self.depth}, id: {hex(id(self.attribute_connector))}>"

    def get_width(self) -> int | float:
        return self.width

    def render(self, text_height: int | float, parent=0, attributes_group=0):
        with dpg.group(parent=parent) as spacer_group:
            dpg.add_spacer(width=self.get_width(), parent=spacer_group)

        self.self_post_render(text_height, spacer_group, parent=parent, attributes_group=attributes_group)

    @CallInNextFrame
    def self_post_render(self, text_height: int | float, spacer_group: int, parent=0, attributes_group=0):
        group_width, group_height = dpg.get_item_rect_size(parent)

        pos = dpg.get_item_pos(spacer_group)

        x, y = pos
        y += (group_height - text_height) / 2
        if len(self.attribute_connector) != 0:
            last_attribute = self.attribute_connector[-1]
            last_drawlist_y = dpg.get_item_pos(last_attribute.drawlist_group)[1]
            last_drawlist_y += dpg.get_item_rect_size(last_attribute.drawlist_group)[1]
            extra_height = y - last_drawlist_y
            y -= extra_height
            text_height += extra_height

        with dpg.group(pos=[x, y], parent=attributes_group) as self.drawlist_group:
            with dpg.drawlist(parent=self.drawlist_group, width=self.get_width(), height=text_height) as drawlist:
                thickness = self.line_width
                x_line = (self.get_width() / 2) - 1
                y_line = text_height
                line = dpg.draw_line([x_line, 0],
                                     [x_line, y_line],
                                     parent=drawlist, color=self.color, thickness=thickness)

        self.attribute_connector.append(self)


class List(LineAttribute):
    check_box_theme: int = None
    max_index_symbols_length = 4

    depth: int
    ordered: bool
    index: int
    task: bool
    task_done: bool

    spacer_group: int = None
    task_spacer: int = None

    def __new__(cls, *args, **kwargs):
        if cls.check_box_theme is None:
            with dpg.theme() as cls.check_box_theme:
                with dpg.theme_component(dpg.mvAll, enabled_state=False, parent=cls.check_box_theme) as theme_component:
                    dpg.add_theme_color(dpg.mvThemeCol_CheckMark, (75, 255, 75, 255), category=dpg.mvThemeCat_Core, parent=theme_component)
                    dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (0, 0, 0, 0), category=dpg.mvThemeCat_Core, parent=theme_component)
                    dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 0, 0, category=dpg.mvThemeCat_Core, parent=theme_component)
                    dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 4, category=dpg.mvThemeCat_Core, parent=theme_component)
                    dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1, category=dpg.mvThemeCat_Core, parent=theme_component)
                    dpg.add_theme_color(dpg.mvThemeCol_Border, (255, 255, 255, 255), category=dpg.mvThemeCat_Core, parent=theme_component)
                    dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (0, 0, 0, 0), category=dpg.mvThemeCat_Core, parent=theme_component)
                    dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, (0, 0, 0, 0), category=dpg.mvThemeCat_Core, parent=theme_component)

        return super().__new__(cls)

    def __init__(self, depth: int, attribute_connector: AttributeConnector,
                 ordered: bool = False,
                 index: int = 1,
                 task: bool = False,
                 task_done: bool = False):
        self.depth = depth
        self.attribute_connector = attribute_connector
        self.attribute_connector.first_line_objects = None
        self.ordered = ordered
        self.index = index
        self.task = task
        self.task_done = task_done

    def __repr__(self):
        if self.ordered:
            return f"<List.{self.depth}, i: {self.index}, attr_id: {hex(id(self.attribute_connector))} id: {hex(id(self))}>"
        return f"<List.{self.depth}, attr_id: {hex(id(self.attribute_connector))} id: {hex(id(self))}>"

    def get_width(self) -> int | float:
        width = get_text_size(f"{'0' * self.max_index_symbols_length}.  ", font=Default.get_font())[0]
        width += self.get_task_width()
        return width

    def get_task_width(self) -> int | float:
        width = 0
        if not self.task:
            return width
        if self.attribute_connector.first_line_objects is not None:  # noqa
            if self in self.attribute_connector.first_line_objects:  # noqa
                width += Default.get_now_font_size() + get_text_size(" " * 2, font=Default.get_font())[0]
        else:
            width += Default.get_now_font_size() + get_text_size(" " * 2, font=Default.get_font())[0]
        return width

    def render(self, text_height: int | float, parent=0, attributes_group=0):
        with dpg.group(parent=parent, horizontal=True) as spacer_group:
            dpg.add_spacer(width=self.get_width() - self.get_task_width(), parent=spacer_group)
            if self.task:
                self.task_spacer = dpg.add_spacer(width=self.get_task_width(), parent=spacer_group)
        self.text_height = text_height
        self.spacer_group = spacer_group
        self.attribute_connector.append(self)

    @CallInNextFrame
    def post_render(self, attributes_group=0):
        if self != self.attribute_connector[0]:
            return
        self.attribute_connector.append(self)
        if self.ordered:
            self.ordered_render(attributes_group=attributes_group)
        else:
            self.unordered_render(attributes_group=attributes_group)

        if self.task:
            dpg.delete_item(self.task_spacer)
            checkbox = dpg.add_checkbox(enabled=False, default_value=self.task_done, parent=self.spacer_group)
            dpg.bind_item_theme(checkbox, self.check_box_theme)
            dpg.add_spacer(width=get_text_size(' ' * 2, font=Default.get_font())[0], parent=self.spacer_group)

    def ordered_render(self, attributes_group=0):
        text = f'{str(self.index)[-4::]}.  '
        render_text_width, render_text_height = get_text_size(text, font=Default.get_font())
        x, y = dpg.get_item_pos(self.spacer_group)
        y += (self.text_height - render_text_height) / 2
        x += (self.get_width() - self.get_task_width()) - render_text_width

        dpg_text = dpg.add_text(text, pos=(x, y), parent=attributes_group)
        dpg.bind_item_font(dpg_text, font=Default.get_font())

    def unordered_render(self, attributes_group=0):
        text = '0.  '
        render_text_width, render_text_height = get_text_size(text, font=Default.get_font())
        x, y = dpg.get_item_pos(self.spacer_group)
        y += (self.text_height - render_text_height) / 2
        x += (self.get_width() - self.get_task_width()) - render_text_width
        height = render_text_height / 2.5
        width = height
        y += (render_text_height - height) * 0.77
        thickness = height / 7
        with dpg.group(pos=(x, y), parent=attributes_group) as drawlist_group:
            drawlist = dpg.add_drawlist(width=width, height=height, parent=drawlist_group)
            # dpg.draw_quad([0, 0], [width, 0],
            #               [width, height], [0, height],
            #               color=(255, 0, 0, 255), fill=(255, 0, 0, 255),
            #               parent=drawlist)

        depth = self.depth - self.depth // 4 * 4
        match depth:
            case 1:
                dpg.draw_circle([height / 2, width / 2],
                                width / 2 - thickness / 2,
                                parent=drawlist,
                                thickness=thickness,
                                fill=(255, 255, 255, 255))
            case 2:
                dpg.draw_circle([height / 2, width / 2],
                                width / 2 - thickness / 2,
                                parent=drawlist,
                                thickness=thickness,
                                fill=(0, 0, 0, 0))
            case 3:
                dpg.draw_quad([thickness, thickness], [width - thickness, thickness],
                              [width - thickness, height - thickness], [thickness, height - thickness],
                              parent=drawlist,
                              thickness=thickness,
                              fill=(255, 255, 255, 255))
            case _:
                dpg.draw_quad([thickness, thickness], [width - thickness, thickness],
                              [width - thickness, height - thickness], [thickness, height - thickness],
                              parent=drawlist,
                              thickness=thickness,
                              fill=(0, 0, 0, 0))
