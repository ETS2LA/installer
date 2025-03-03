"""
Source: https://github.com/LonamiWebs/Telethon/blob/v1/telethon/extensions/html.py

Simple HTML -> entity parser.
"""
import html
import struct
import traceback
from collections import deque
from dataclasses import dataclass, field
from html.parser import HTMLParser

import mistletoe

from .attribute_types import AttributeConnector


@dataclass(kw_only=True)
class MessageEntity:
    offset: int
    length: int
    _attribute_connector: AttributeConnector = None

    @property
    def attribute_connector(self) -> AttributeConnector:
        if self._attribute_connector is None:
            self._attribute_connector = AttributeConnector()
        return self._attribute_connector


@dataclass(kw_only=True)
class MessageEntityFont(MessageEntity):
    color: str | list[int, int, int, int] = field(default_factory=lambda: [255, 255, 255, 255])
    size: int | None = None


class MessageEntityBold(MessageEntity): ...


class MessageEntityItalic(MessageEntity): ...


class MessageEntityStrike(MessageEntity): ...


class MessageEntityUnderline(MessageEntity): ...


class MessageEntitySpoiler(MessageEntity): ...  # TODO


@dataclass(kw_only=True)
class MessageEntityBlockquote(MessageEntity):  # noqa
    depth: int


class MessageEntityCode(MessageEntity): ...


@dataclass(kw_only=True)
class MessageEntityPre(MessageEntity):  # noqa
    language: str


@dataclass(kw_only=True)
class MessageEntityTextUrl(MessageEntity):  # noqa
    url: str


class MessageEntityUrl(MessageEntityTextUrl): ...  # TODO


class MessageEntityEmail(MessageEntity): ...  # TODO


@dataclass(kw_only=True)
class MessageEntityList(MessageEntity):  # noqa
    depth: int
    task: bool = False
    task_done: bool = False


@dataclass(kw_only=True)
class MessageEntityUnorderedList(MessageEntityList):  ...  # noqa


@dataclass(kw_only=True)
class MessageEntityOrderedList(MessageEntityList):  # noqa
    index: int


class MessageEntitySeparator(MessageEntity): ...


class MessageEntityH1(MessageEntity): ...


class MessageEntityH2(MessageEntity): ...


class MessageEntityH3(MessageEntity): ...


class MessageEntityH4(MessageEntity): ...


class MessageEntityH5(MessageEntity): ...


class MessageEntityH6(MessageEntity): ...


def _strip_text(text, entities):
    """
    Strips whitespace from the given text modifying the provided entities.
    This assumes that there are no overlapping entities, that their length
    is greater or equal to one, and that their length is not out of bounds.
    """
    if not entities:
        return text.strip()
    while text and text[-1].isspace():
        e = entities[-1]
        if e.offset + e.length == len(text):
            if e.length == 1:
                del entities[-1]
                if not entities:
                    return text.strip()
            else:
                e.length -= 1
        text = text[:-1]

    while text and text[0].isspace():
        for i in reversed(range(len(entities))):
            e = entities[i]
            if e.offset != 0:
                e.offset -= 1
                continue

            if e.length == 1:
                del entities[0]
                if not entities:
                    return text.lstrip()
            else:
                e.length -= 1

        text = text[1:]

    return text


def _add_surrogate(text):
    return ''.join(
        ''.join(chr(y) for y in struct.unpack('<HH', x.encode('utf-16le')))
        if (0x10000 <= ord(x) <= 0x10FFFF) else x for x in text
    )


def _del_surrogate(text):
    return text.encode('utf-16', 'surrogatepass').decode('utf-16')


class _HTMLToParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = ''
        self.entities = []
        self._building_entities = {}
        self._open_tags = deque()
        self._open_tags_meta = deque()

        self.blockquote_depth = 0

        self.li_open_count = 0
        self.opened_list_depth = []
        self.ordered_list_index_by_depth = {}

    def handle_starttag(self, tag, attrs):
        self._open_tags.appendleft(tag)
        self._open_tags_meta.appendleft(None)

        attrs = dict(attrs)
        EntityType = None
        args = {}
        match tag:
            case "strong" | "b":
                EntityType = MessageEntityBold
            case "em" | "i":
                EntityType = MessageEntityItalic
            case "u":
                EntityType = MessageEntityUnderline
            case "del" | "s":
                EntityType = MessageEntityStrike
            case "spoiler":
                EntityType = MessageEntitySpoiler
            case "blockquote":
                EntityType = MessageEntityBlockquote
                self.blockquote_depth += 1
                args["depth"] = self.blockquote_depth
                tag = f'{tag}_{self.blockquote_depth}'
            case "code":
                try:
                    # If we're in the middle of a <pre> tag, this <code> tag is
                    # probably intended for syntax highlighting.
                    #
                    # Syntax highlighting is set with
                    #     <code class='language-...'>codeblock</code>
                    # inside <pre> tags
                    pre = self._building_entities['pre']
                    try:
                        pre.language = attrs['class'][len('language-'):]
                    except KeyError:
                        pass
                except KeyError:
                    EntityType = MessageEntityCode
            case "pre":
                EntityType = MessageEntityPre
                args['language'] = ''
            case "a":
                url = attrs.get("href", None)
                if not url:
                    return
                if url.startswith('mailto:'):
                    url = url.removeprefix('mailto:')
                    EntityType = MessageEntityEmail
                else:
                    if self.get_starttag_text() == url:
                        EntityType = MessageEntityUrl
                    else:
                        EntityType = MessageEntityTextUrl
                        args['url'] = url
                        url = None
                self._open_tags_meta.popleft()
                self._open_tags_meta.appendleft(url)
            case "font" | "span":
                EntityType = MessageEntityFont
                color = attrs.get("color", None)
                size = attrs.get("size", None)
                style_string = attrs.get("style", None)
                try:
                    if style_string:
                        style_dict = {}
                        for style in style_string.split(";"):
                            style = style.split(":", 1)
                            style_dict[style[0]] = style[1].strip()
                        color = style_dict.get("color", None)
                        if color:
                            color = color.removeprefix("rgb").removeprefix("a")
                except Exception:
                    traceback.print_exc()

                if color:
                    args["color"] = color
                if size:
                    args["size"] = size
            case "ol":
                self.opened_list_depth.append(MessageEntityOrderedList)
                ordered_list_index = attrs.get("start", 1)
                try:
                    ordered_list_index = int(ordered_list_index)
                except Exception:
                    ordered_list_index = 1
                    traceback.print_exc()
                finally:
                    self.ordered_list_index_by_depth[len(self.opened_list_depth)] = ordered_list_index
            case "ul":
                self.opened_list_depth.append(MessageEntityUnorderedList)
            case "li":
                self.li_open_count += 1
                tag = f"{tag}_{self.li_open_count}"
                if 'task' in attrs:
                    args['task'] = True
                elif 'task-done' in attrs:
                    args['task'] = True
                    args['task_done'] = True

                EntityType = self.opened_list_depth[-1]
                args["depth"] = len(self.opened_list_depth)
                if EntityType is MessageEntityOrderedList:
                    args["index"] = self.ordered_list_index_by_depth[len(self.opened_list_depth)]
                    self.ordered_list_index_by_depth[len(self.opened_list_depth)] += 1
            case "hr":
                EntityType = MessageEntitySeparator
            case "h1":
                EntityType = MessageEntityH1
            case "h2":
                EntityType = MessageEntityH2
            case "h3":
                EntityType = MessageEntityH3
            case "h4":
                EntityType = MessageEntityH4
            case "h5":
                EntityType = MessageEntityH5
            case "h6":
                EntityType = MessageEntityH6
        if EntityType is not None and tag not in self._building_entities:
            self._building_entities[tag] = EntityType(
                offset=len(self.text),
                # The length will be determined when closing the tag.
                length=0,
                **args)

    def handle_data(self, text):
        previous_tag = self._open_tags[0] if len(self._open_tags) > 0 else ''
        if previous_tag == 'a':
            url = self._open_tags_meta[0]
            if url:
                text = url

        text = html.unescape(text)
        for tag, entity in self._building_entities.items():
            entity.length += len(text)

        self.text += text

    def handle_endtag(self, tag):
        try:
            self._open_tags.popleft()
            self._open_tags_meta.popleft()
        except IndexError:
            pass
        match tag:
            case "blockquote":
                tag = f"{tag}_{self.blockquote_depth}"
                self.blockquote_depth -= 1
            case "ol":
                self.ordered_list_index_by_depth[len(self.opened_list_depth)] = 1
                del self.opened_list_depth[-1]
            case "ul":
                del self.opened_list_depth[-1]
            case "li":
                tag = f"{tag}_{self.li_open_count}"
                self.li_open_count += -1
        entity = self._building_entities.pop(tag, None)
        if not entity:
            return

        self.entities.append(entity)


try:
    import pygments
    from pygments import highlight
    from pygments.formatters.html import HtmlFormatter
    from pygments.lexers import get_lexer_by_name as get_lexer, guess_lexer


    class _PygmentsRenderer(mistletoe.HTMLRenderer):
        formatter = HtmlFormatter(style='monokai')
        formatter.noclasses = True

        def __init__(self, *extras):
            super().__init__(*extras)

        def render_block_code(self, token):
            code = token.children[0].content
            try:
                lexer = get_lexer(token.language) if token.language else guess_lexer(code)
            except pygments.util.ClassNotFound:  # noqa
                return f"<pre>{code}</pre>"
            return highlight(code, lexer, self.formatter)
except ModuleNotFoundError:
    class _PygmentsRenderer(mistletoe.HTMLRenderer):
        ...


def parse(html_text: str) -> [str, list[MessageEntity]]:
    """
    Parses the given HTML message and returns its stripped representation
    plus a list of the MessageEntity's that were found.

    :param html: the message with HTML to be parsed.
    :return: a tuple consisting of (clean message, [message entities]).
    """
    if not html_text:
        return html_text, []
    # html_text = html.unescape(_MarkdownIt.render(html_text))
    html_text = mistletoe.markdown(html_text, renderer=_PygmentsRenderer)

    html_text = html_text.replace('<blockquote>\n', '<blockquote>').replace('\n</blockquote>', '</blockquote>')
    html_text = html_text.replace('<li>\n', '<li>').replace('\n</li>', '</li>')
    html_text = html_text.replace('<ul>\n', '<ul>').replace('\n</ul>', '</ul>')
    html_text = html_text.replace('<ol>\n', '<ol>').replace('\n</ol>', '</ol>')
    html_text = html_text.replace('\n<ol start="', '<ol start="')

    html_text = html_text.replace('\n</pre>', '</pre>')

    html_text = html_text.replace('\n</br>', '\n')
    html_text = html_text.replace('</br>', '\n')
    # task list support
    html_text = html_text.replace("<li>[x] ", "<li>[X] ")
    html_text = html_text.replace("<li>[X] ", "<li task-done>")
    html_text = html_text.replace("<li>[ ] ", "<li task>")

    # html_text = html_text.replace("<hr /> ", "<hr />\n")

    parser = _HTMLToParser()
    parser.feed(_add_surrogate(html_text))
    text = _strip_text(parser.text, parser.entities)
    return _del_surrogate(text), parser.entities
