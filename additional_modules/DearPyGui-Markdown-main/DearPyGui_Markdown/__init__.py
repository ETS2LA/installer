import threading
import time
import traceback
from typing import Iterable, List, Any, Callable, Union, Tuple

import dearpygui.dearpygui as dpg


def get_text_size(text: str, *, wrap_width: float = -1.0, font: int | str = 0, **kwargs) -> list[float | int] | tuple[float | int, ...]:
    strip_text = text.strip()
    while 1:
        size: list[float, float] = dpg.get_text_size(text, wrap_width=wrap_width, font=font, **kwargs)

        if size is None:
            continue
        if size[1] == 0:
            continue
        if size[0] == 0 and len(strip_text) != 0:
            continue
        break
    return size


class CallInNextFrame:
    __started = False
    now_frame_queue = []

    def __new__(cls, func):
        def decorator(*args, **kwargs):
            cls.append(func, *args, **kwargs)

        return decorator

    @classmethod
    def append(cls, func, *args, **kwargs):
        if cls.__started is False:
            cls.__started = True
            threading.Thread(target=cls._worker, daemon=True).start()
        cls.now_frame_queue.append(
            [func, args, kwargs]
        )

    @classmethod
    def _worker(cls):
        while True:
            if len(cls.now_frame_queue) == 0:
                time.sleep(0.015)
                continue
            next_frame_queue = cls.now_frame_queue.copy()
            cls.now_frame_queue.clear()
            dpg.split_frame()
            for func, args, kwargs in next_frame_queue:
                try:
                    func(*args, **kwargs)
                except Exception:
                    traceback.print_exc()


class CallWhenDPGStarted:
    __thread = None
    STARTUP_DONE = False
    functions_queue = []

    @classmethod
    def append(cls, func, *args, **kwargs):
        if cls.__thread is None:
            cls.__thread = True
            threading.Thread(target=cls._worker, daemon=True).start()
        if not cls.STARTUP_DONE:
            cls.functions_queue.append(
                [func, args, kwargs]
            )
            return
        try:
            func(*args, **kwargs)
        except Exception:
            traceback.print_exc()

    @classmethod
    def _worker(cls):
        while dpg.get_frame_count() <= 1:
            time.sleep(0.01)
        dpg.split_frame()
        cls.STARTUP_DONE = True
        for func, args, kwargs in cls.functions_queue:
            try:
                func(*args, **kwargs)
            except Exception:
                traceback.print_exc()
        del cls.functions_queue


from . import font_attributes
from . import line_atributes
from . import parser
from . import text_attributes
from . import text_entities
from .font_attributes import set_font_registry, set_add_font_function, set_font


def is_in_container(dpg_item: int | str, containers_list: Iterable[str]) -> bool:
    parent = dpg_item
    while True:
        parent = dpg.get_item_parent(parent)
        if parent is None:
            return False
        object_type = dpg.get_item_info(parent)['type']
        print(object_type)
        if object_type in containers_list:
            return True
        if object_type == 'mvAppItemType::mvWindowAppItem':
            return False


def wrap_text_entity(text: text_entities.StrEntity | text_entities.TextEntity, width: int | float = -1) -> text_entities.LineEntity:
    def get_width(str_entity: text_entities.StrEntity | text_entities.TextEntity) -> int | float:
        return text_entities.LineEntity.get_width(str_entity)

    def to_words(str_entity: text_entities.StrEntity | text_entities.TextEntity) -> list[text_entities.StrEntity | text_entities.TextEntity]:
        words_list = []
        word = None
        chars = str_entity.chars()
        for char in chars:
            if str(char) == " ":
                if word is not None:
                    words_list.append(word)
                words_list.append(char)
                word = None
            else:
                if word is None:
                    word = char
                else:
                    word = word + char
        if word is not None:
            words_list.append(word)
        return words_list

    print_text = text_entities.LineEntity()
    paragraphs_list = text.split('\n')
    if width < 0:
        for paragraph in paragraphs_list:
            print_text.append(paragraph)
        return print_text

    for paragraph in paragraphs_list:
        sentence = text_entities.StrEntity('')
        if len(paragraph) == 0:
            print_text.append(paragraph)
            continue

        words_list = to_words(paragraph)
        for word in words_list:
            sentence_with_next_word = sentence + word
            if get_width(sentence_with_next_word) <= width:
                sentence = sentence_with_next_word
                continue
            if len(sentence) != 0:
                print_text.append(sentence)
                if get_width(word) <= width:
                    sentence = word
                    continue

            sentence = text_entities.StrEntity('')
            for i, char in enumerate(word.chars()):
                sentence_with_next_char = sentence + char
                if get_width(sentence_with_next_char) <= width:
                    sentence = sentence_with_next_char
                else:
                    if len(sentence) > 0:
                        print_text.append(sentence)
                    sentence = char
        print_text.append(sentence)

    return print_text


class _ConvertedMessageEntity:
    def __init__(self, entity: parser.MessageEntity):
        self.entity = entity
        self.offset = entity.offset
        match type(self.entity):
            case parser.MessageEntitySeparator:
                self.end = self.offset
            case _:
                self.end = self.offset + entity.length

    @property
    def object(self):
        match type(self.entity):
            case parser.MessageEntityBold:
                return font_attributes.Bold
            case parser.MessageEntityItalic:
                return font_attributes.Italic
            case parser.MessageEntityUnderline:
                return text_attributes.Underline
            case parser.MessageEntityStrike:
                return text_attributes.Strike
            case parser.MessageEntityCode:
                return text_attributes.Code
            case parser.MessageEntityPre:
                return text_attributes.Pre(attribute_connector=self.entity.attribute_connector)
            case parser.MessageEntityTextUrl:
                return text_attributes.Url(self.entity.url,
                                           attribute_connector=self.entity.attribute_connector)
            case parser.MessageEntityFont:
                return font_attributes.Font(self.entity.color,
                                            self.entity.size)
            case parser.MessageEntityBlockquote:
                return line_atributes.Blockquote(self.entity.depth,
                                                 attribute_connector=self.entity.attribute_connector)
            case parser.MessageEntityUnorderedList:
                return line_atributes.List(self.entity.depth,
                                           attribute_connector=self.entity.attribute_connector,
                                           task=self.entity.task,
                                           task_done=self.entity.task_done)
            case parser.MessageEntityOrderedList:
                return line_atributes.List(self.entity.depth,
                                           attribute_connector=self.entity.attribute_connector,
                                           ordered=True,
                                           index=self.entity.index,
                                           task=self.entity.task,
                                           task_done=self.entity.task_done)
            case parser.MessageEntitySeparator:
                return line_atributes.Separator
            case parser.MessageEntityH1:
                return font_attributes.H1
            case parser.MessageEntityH2:
                return font_attributes.H2
            case parser.MessageEntityH3:
                return font_attributes.H3
            case parser.MessageEntityH4:
                return font_attributes.H4
            case parser.MessageEntityH5:
                return font_attributes.H5
            case parser.MessageEntityH6:
                return font_attributes.H6
            case _:
                raise ValueError(f'Unidentified MessageEntity: {type(self.entity)}')

    def __repr__(self):
        return f'<{self.offset}, {self.end} {self.entity}>'

    def __eq__(self, index: int):
        if isinstance(self.entity, parser.MessageEntitySeparator):
            return self.offset == index
        return self.offset < index <= self.end


class MarkdownText:
    text_entity: text_entities.TextEntity | text_entities.StrEntity
    black_list_render_containers = ("mvAppItemType::mvTab", # Used to prevent rendering in some containers
                                    "mvAppItemType::mvTabBar",
                                    "mvAppItemType::mvTreeNode")

    def __init__(self, markdown_text: str):
        clear_text, attributes = parser.parse(markdown_text)
        for i in range(len(attributes)):
            attributes[i] = _ConvertedMessageEntity(attributes[i])

        attribute_points = []
        for entity in attributes:
            attribute_points.append(entity.offset)
            attribute_points.append(entity.end)

        attribute_points.append(len(clear_text))
        attribute_points = list(set(attribute_points))
        attribute_points.sort()

        if len(attribute_points) == 0:
            self.text_entity = text_entities.StrEntity(clear_text)
        else:
            self.text_entity = text_entities.TextEntity()

        for i, point in enumerate(attribute_points):
            str_attributes = []
            for entity in attributes:
                if point == entity:
                    str_attributes.append(entity.object)

            past_point = attribute_points[i - 1] if i != 0 else 0

            str_entity = text_entities.StrEntity(clear_text[past_point:point:])
            if line_atributes.Separator in str_attributes:
                del str_attributes[str_attributes.index(line_atributes.Separator)]
                if len(str(str_entity)) > 0:
                    str_entity = text_entities.StrEntity(str(str_entity).removesuffix('\n'))
                    str_entity.set_attributes(str_attributes)
                    self.text_entity.append(str_entity)

                if point != 0:
                    self.text_entity.append(
                        text_entities.StrEntity('\n')
                    )
                str_entity = text_entities.StrEntity(' ')
                str_entity.set_attributes([line_atributes.Separator])  # noqa
                self.text_entity.append(str_entity)
            else:
                str_entity.set_attributes(str_attributes)
                self.text_entity.append(str_entity)

    def add(self, wrap: int | float = -1, parent=0, render_on_element_visible: int | str | bool | None = True) -> int | str:
        """
        :param wrap: Number of pixels from the start of the item until wrapping starts.
        :param parent: Parent to add this item to. (runtime adding)
        :param render_on_element_visible: Controls the rendering behavior based on visibility:
            - None: Only applies when the element is within on a dpg.tab or dpg.tree_node containers.
            - True: Default behavior. Renders the element after it becomes visible.
            - False: Explicitly renders the element immediately after creation. Caution: May cause incorrect
              rendering if the element is within a dpg.tab or dpg.tree_node containers or parent container is not visible.
            - int or str: Tag of another element. The visibility handler will be attached to the specified element.
              Note: If the target element already has a visibility handler, it will be replaced.
        :return: group with rendered text
        """
        print_text: text_entities.LineEntity = wrap_text_entity(self.text_entity, width=wrap)

        with dpg.group(parent=parent, horizontal=True) as group:
            text_group = dpg.add_group(parent=group)
            attributes_group = dpg.add_group(parent=group)

        if render_on_element_visible is None:
            render_on_element_visible = is_in_container(group, self.black_list_render_containers)

        if render_on_element_visible is not False:
            with dpg.item_handler_registry() as widget_handler:
                dpg.add_item_visible_handler(callback=self._render_after_visible_callback,
                                             user_data=(widget_handler, (print_text, group, text_group, attributes_group)))

            if render_on_element_visible is True:
                dpg.bind_item_handler_registry(group, widget_handler)
            else:
                dpg.bind_item_handler_registry(render_on_element_visible, widget_handler)

            return group

        if not CallWhenDPGStarted.STARTUP_DONE:
            CallWhenDPGStarted.append(self._render, print_text, group, text_group, attributes_group)
        else:
            self._render(print_text, group, text_group, attributes_group)
        return group

    @staticmethod
    def _render(print_text: text_entities.LineEntity, group: int | str, text_group: int | str, attributes_group: int | str):
        dpg.bind_item_theme(group, text_entities.AttributeController.dpg_group_theme)
        print_text.render(parent=text_group, attributes_group=attributes_group)

    @staticmethod
    def _render_after_visible_callback(sender, app_data):
        user_data = dpg.get_item_user_data(sender)
        if user_data is None:
            return
        
        dpg.set_item_user_data(sender, None)

        widget_handler = user_data[0]
        print_text, group, text_group, attributes_group = user_data[1]

        dpg.delete_item(sender)
        dpg.delete_item(widget_handler)

        MarkdownText._render(print_text, group, text_group, attributes_group)


def add_text(markdown_text: str,
             wrap: float | int = -1,
             parent: int | str = 0,
             pos: list[int | float, int | float] | tuple[int | float, int | float] = None,
             render_on_element_visible: int | str | bool | None = True) -> int:
    """ Adds Markdown text.
    :param wrap: Number of pixels from the start of the item until wrapping starts.
    :param parent: Parent to add this item to. (runtime adding)
    :pos: Places the item relative to window coordinates, [0,0] is top left.
    :param render_on_element_visible: Controls the rendering behavior based on visibility:
        - None: Only applies when the element is within on a dpg.tab or dpg.tree_node containers.
        - True: Default behavior. Renders the element after it becomes visible.
        - False: Explicitly renders the element immediately after creation. Caution: May cause incorrect
          rendering if the element is within a dpg.tab or dpg.tree_node containers or parent container is not visible.
        - int or str: Tag of another element. The visibility handler will be attached to the specified element.
          Note: If the target element already has a visibility handler, it will be replaced.
    :return: group with rendered Markdown text
    """
    rendered_group = MarkdownText(markdown_text=markdown_text).add(wrap=wrap, parent=parent, render_on_element_visible=render_on_element_visible)
    if pos is not None:
        dpg.set_item_pos(rendered_group, pos)
    return rendered_group


def add_text_italic(default_value: str = '', *, label: str = None, user_data: Any = None, use_internal_label: bool = True, tag: Union[int, str] = 0, indent: int = -1, parent: Union[int, str] = 0, before: Union[int, str] = 0, source: Union[int, str] = 0, payload_type: str = '$$DPG_PAYLOAD', drag_callback: Callable = None, drop_callback: Callable = None, show: bool = True, pos: Union[List[int], Tuple[int, ...]] = [], filter_key: str = '', tracked: bool = False, track_offset: float = 0.5, wrap: int = -1, bullet: bool = False, color: Union[List[int], Tuple[int, ...]] = (-255, 0, 0, 255), show_label: bool = False, **kwargs) -> Union[int, str]:
    """	 Adds italic text. Text can have an optional label that will display to the right of the text.

	Args:
		default_value (str, optional):
		label (str, optional): Overrides 'name' as label.
		user_data (Any, optional): User data for callbacks
		use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
		tag (Union[int, str], optional): Unique id used to programmatically refer to the item.If label is unused this will be the label.
		indent (int, optional): Offsets the widget to the right the specified number multiplied by the indent style.
		parent (Union[int, str], optional): Parent to add this item to. (runtime adding)
		before (Union[int, str], optional): This item will be displayed before the specified item in the parent.
		source (Union[int, str], optional): Overrides 'id' as value storage key.
		payload_type (str, optional): Sender string type must be the same as the target for the target to run the payload_callback.
		drag_callback (Callable, optional): Registers a drag callback for drag and drop.
		drop_callback (Callable, optional): Registers a drop callback for drag and drop.
		show (bool, optional): Attempt to render widget.
		pos (Union[List[int], Tuple[int, ...]], optional): Places the item relative to window coordinates, [0,0] is top left.
		filter_key (str, optional): Used by filter widget.
		tracked (bool, optional): Scroll tracking
		track_offset (float, optional): 0.0f:top, 0.5f:center, 1.0f:bottom
		wrap (int, optional): Number of pixels from the start of the item until wrapping starts.
		bullet (bool, optional): Places a bullet to the left of the text.
		color (Union[List[int], Tuple[int, ...]], optional): Color of the text (rgba).
		show_label (bool, optional): Displays the label to the right of the text.
		id (Union[int, str], optional): (deprecated)
	Returns:
		Union[int, str]
	"""
    dpg_text = dpg.add_text(default_value, label=label, user_data=user_data, use_internal_label=use_internal_label, tag=tag, indent=indent, parent=parent, before=before, source=source, payload_type=payload_type, drag_callback=drag_callback, drop_callback=drop_callback, show=show, pos=pos, filter_key=filter_key, tracked=tracked, track_offset=track_offset, wrap=wrap, bullet=bullet, color=color, show_label=show_label, **kwargs)
    dpg.bind_item_font(dpg_text,
                       font=font_attributes.Italic.get_font())
    return dpg_text


def add_text_bold(default_value: str = '', *, label: str = None, user_data: Any = None, use_internal_label: bool = True, tag: Union[int, str] = 0, indent: int = -1, parent: Union[int, str] = 0, before: Union[int, str] = 0, source: Union[int, str] = 0, payload_type: str = '$$DPG_PAYLOAD', drag_callback: Callable = None, drop_callback: Callable = None, show: bool = True, pos: Union[List[int], Tuple[int, ...]] = [], filter_key: str = '', tracked: bool = False, track_offset: float = 0.5, wrap: int = -1, bullet: bool = False, color: Union[List[int], Tuple[int, ...]] = (-255, 0, 0, 255), show_label: bool = False, **kwargs) -> Union[int, str]:
    """	 Adds bold text. Text can have an optional label that will display to the right of the text.

	Args:
		default_value (str, optional):
		label (str, optional): Overrides 'name' as label.
		user_data (Any, optional): User data for callbacks
		use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
		tag (Union[int, str], optional): Unique id used to programmatically refer to the item.If label is unused this will be the label.
		indent (int, optional): Offsets the widget to the right the specified number multiplied by the indent style.
		parent (Union[int, str], optional): Parent to add this item to. (runtime adding)
		before (Union[int, str], optional): This item will be displayed before the specified item in the parent.
		source (Union[int, str], optional): Overrides 'id' as value storage key.
		payload_type (str, optional): Sender string type must be the same as the target for the target to run the payload_callback.
		drag_callback (Callable, optional): Registers a drag callback for drag and drop.
		drop_callback (Callable, optional): Registers a drop callback for drag and drop.
		show (bool, optional): Attempt to render widget.
		pos (Union[List[int], Tuple[int, ...]], optional): Places the item relative to window coordinates, [0,0] is top left.
		filter_key (str, optional): Used by filter widget.
		tracked (bool, optional): Scroll tracking
		track_offset (float, optional): 0.0f:top, 0.5f:center, 1.0f:bottom
		wrap (int, optional): Number of pixels from the start of the item until wrapping starts.
		bullet (bool, optional): Places a bullet to the left of the text.
		color (Union[List[int], Tuple[int, ...]], optional): Color of the text (rgba).
		show_label (bool, optional): Displays the label to the right of the text.
		id (Union[int, str], optional): (deprecated)
	Returns:
		Union[int, str]
	"""
    dpg_text = dpg.add_text(default_value, label=label, user_data=user_data, use_internal_label=use_internal_label, tag=tag, indent=indent, parent=parent, before=before, source=source, payload_type=payload_type, drag_callback=drag_callback, drop_callback=drop_callback, show=show, pos=pos, filter_key=filter_key, tracked=tracked, track_offset=track_offset, wrap=wrap, bullet=bullet, color=color, show_label=show_label, **kwargs)
    dpg.bind_item_font(dpg_text,
                       font=font_attributes.Bold.get_font())
    return dpg_text


def add_text_bold_italic(default_value: str = '', *, label: str = None, user_data: Any = None, use_internal_label: bool = True, tag: Union[int, str] = 0, indent: int = -1, parent: Union[int, str] = 0, before: Union[int, str] = 0, source: Union[int, str] = 0, payload_type: str = '$$DPG_PAYLOAD', drag_callback: Callable = None, drop_callback: Callable = None, show: bool = True, pos: Union[List[int], Tuple[int, ...]] = [], filter_key: str = '', tracked: bool = False, track_offset: float = 0.5, wrap: int = -1, bullet: bool = False, color: Union[List[int], Tuple[int, ...]] = (-255, 0, 0, 255), show_label: bool = False, **kwargs) -> Union[int, str]:
    """	 Adds bold italic text. Text can have an optional label that will display to the right of the text.

	Args:
		default_value (str, optional):
		label (str, optional): Overrides 'name' as label.
		user_data (Any, optional): User data for callbacks
		use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
		tag (Union[int, str], optional): Unique id used to programmatically refer to the item.If label is unused this will be the label.
		indent (int, optional): Offsets the widget to the right the specified number multiplied by the indent style.
		parent (Union[int, str], optional): Parent to add this item to. (runtime adding)
		before (Union[int, str], optional): This item will be displayed before the specified item in the parent.
		source (Union[int, str], optional): Overrides 'id' as value storage key.
		payload_type (str, optional): Sender string type must be the same as the target for the target to run the payload_callback.
		drag_callback (Callable, optional): Registers a drag callback for drag and drop.
		drop_callback (Callable, optional): Registers a drop callback for drag and drop.
		show (bool, optional): Attempt to render widget.
		pos (Union[List[int], Tuple[int, ...]], optional): Places the item relative to window coordinates, [0,0] is top left.
		filter_key (str, optional): Used by filter widget.
		tracked (bool, optional): Scroll tracking
		track_offset (float, optional): 0.0f:top, 0.5f:center, 1.0f:bottom
		wrap (int, optional): Number of pixels from the start of the item until wrapping starts.
		bullet (bool, optional): Places a bullet to the left of the text.
		color (Union[List[int], Tuple[int, ...]], optional): Color of the text (rgba).
		show_label (bool, optional): Displays the label to the right of the text.
		id (Union[int, str], optional): (deprecated)
	Returns:
		Union[int, str]
	"""
    dpg_text = dpg.add_text(default_value, label=label, user_data=user_data, use_internal_label=use_internal_label, tag=tag, indent=indent, parent=parent, before=before, source=source, payload_type=payload_type, drag_callback=drag_callback, drop_callback=drop_callback, show=show, pos=pos, filter_key=filter_key, tracked=tracked, track_offset=track_offset, wrap=wrap, bullet=bullet, color=color, show_label=show_label, **kwargs)
    dpg.bind_item_font(dpg_text,
                       font=font_attributes.BoldItalic.get_font())
    return dpg_text
