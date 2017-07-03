#!/usr/bin/python3
# coding=utf-8

from data_types import *
from typing import *


def scene_from_markdown(lines: List[str]):
    """Read demo_scene from Markdown
    """
    title = None
    content = ""
    picture = None
    links = []
    content_pos = 0
    last_title_pos = 0
    for line in lines:
        content_pos += 1
        if line.startswith('#'):
            title = line.replace('#', '').strip()
            last_title_pos = content_pos
        elif len(line.strip()) == line.count('='):
            break
        elif len(line.strip()) == line.count('-'):
            break
    if (title is None) & (content_pos < len(lines)):
        title = lines[0]
    if content_pos >= len(lines):
        content_pos = last_title_pos
    for line in lines[content_pos:]:
        if line.startswith('!['):
            picture = line[line.find('](') + 2:line.rfind(')')]
        elif line.startswith('['):
            left = line[line.find('[') + 1:line.find('](')]
            path = line[line.find('](') + 2:line.rfind(')')]
            if left.startswith('(auto,'):
                time = float(left[left.find(',') + 1:left.find(')')].strip())
                link = Link(left[left.find(')') + 1:], path, ACTION_AUTO_NEXT_SCENE, time)
            else:
                link = Link(left, path)
            links.append(link)
        else:
            content += "\n" + line
    return Scene(picture, title, content.strip(), links)  # type: Scene
