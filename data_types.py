#!/usr/bin/python3
# coding=utf-8

from telebot import types

from typing import *

STATUS_PLAYING = 0
STATUS_GAMEOVER = -1

ACTION_NEXT_SCENE = 1
ACTION_AUTO_NEXT_SCENE = 2


class Link:
    """Link class

    Describe a link in demo_scene

    Attributes:
        title: Link title
        path: Link path
        action: Link action type
    """
    title: str
    path: str
    action: int
    delay: float

    def __init__(self, title, path, action=ACTION_NEXT_SCENE, delay=0.0):
        self.title = title
        self.path = path
        self.action = action
        self.delay = delay

    def __str__(self):
        return f'Link (title = {self.title}, path = {self.path}, action = {self.action}, delay = {self.delay})'


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
    picture: str
    title: str
    content: str
    links: List[Link]
    status: int
    path: str

    def __init__(self, picture=None, title=None, content=None,
                 links=None, status=STATUS_PLAYING, path=None):
        if links is None:
            links = []
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
        return (f'Scene (title = {self.title}, content = {self.content}, picture = {self.picture},'
                f'links = {links_str}, status = {self.status}, path = {self.path})')

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


class Package:
    """Package class

    Game package

    Attributes:
        title: Game title
        desc: The description of game
        entry_scene: The entry of game
        path: Game path
    """
    title: str
    desc: str
    entry_scene: str
    path: str

    def __init__(self, title, desc=None, entry_scene=None, path=None):
        self.title = title
        self.desc = desc
        self.entry_scene = entry_scene
        self.path = path
