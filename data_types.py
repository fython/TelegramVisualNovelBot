#!/usr/bin/python3
# coding=utf-8

from telebot import types

STATUS_PLAYING = 0
STATUS_GAMEOVER = -1

ACTION_NEXT_SCENE = 1
ACTION_AUTO_NEXT_SCENE = 2


class Scene:
    """Scene class

    Describe a demo_scene in game

    Attributes:
        title: Describe what the demo_scene is about. It will not be displayed while
            playing.
        content: Role dialogue text or demo_scene text.
        picture: If demo_scene has a picture, you can set it a path string.
        links: Scene links (Buttons). They point to next demo_scene as usual.
        status: The game status of current demo_scene.
    """

    def __init__(self, picture=None, title=None, content=None,
                 links=[], status=STATUS_PLAYING, path=None):
        self.picture = picture
        self.title = title
        self.content = content
        self.links = links
        self.status = status
        self.path = path

    def __str__(self):
        links_str = '['
        for link in self.links:
            links_str += str(link) + ','
        links_str = links_str[:len(links_str) - 1] + ']'
        return ('Scene (title = %s, content = %s, picture = %s, links = %s, '
                'status = %d, path = %s)') % (self.title, self.content,
                                              self.picture, links_str,
                                              self.status, self.path)

    def get_reply_buttons(self):
        """Get reply buttons (from Links)

        Get telebot.ReplyKeyboardMarkup
        """
        keyboard = types.ReplyKeyboardMarkup()
        truelen = 0
        for link in self.links:
            if link.action == ACTION_NEXT_SCENE:
                truelen += 1
                keyboard.row(types.KeyboardButton(link.title))
        if truelen <= 0:
            return types.ReplyKeyboardRemove()
        else:
            return keyboard

    def find_link(self, string):
        """Find link from links
        """
        for link in self.links:
            if link.title == string.strip():
                return link
        return None

    def get_auto_link(self):
        """Find auto next scene link
        """
        for link in self.links:
            if link.action == ACTION_AUTO_NEXT_SCENE:
                return link
        return None

    def from_markdown(lines):
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
        return Scene(picture, title, content.strip(), links)


class Link:
    """Link class

    Describe a link in demo_scene

    Attributes:
        title: Link title
        path: Link path
        action: Link action type
    """

    def __init__(self, title, path, action=ACTION_NEXT_SCENE, delay=0.0):
        self.title = title
        self.path = path
        self.action = action
        self.delay = delay

    def __str__(self):
        return 'Link (title = %s, path = %s, action = %s, delay = %d)' % (self.title, self.path,
                                                                          self.action, self.delay)
