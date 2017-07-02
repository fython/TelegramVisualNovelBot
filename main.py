#!/usr/bin/python3
# coding=utf-8
import requests
import telebot
from token_config import TELEBOT_TOKEN

from data_types import Scene, Link

bot = telebot.TeleBot(TELEBOT_TOKEN)

current_scenes = {}


def main():
    me = bot.get_me()

    print('Galgame Telegram Bot is running now.')
    print('Bot Account Information: ', me)

    bot.polling()


@bot.message_handler(commands=['start'])
def start_bot(message):
    """Start bot and send introduction.
    """
    bot.send_message(chat_id=message.chat.id, text=(
        '''This is a galgame bot in Telegram. Made by @fython .
目前处于初步开发阶段，功能尚未完善。
GitHub 源码：https://github.com/fython/TelegramGalgameBot'''
    ))


@bot.message_handler(commands=['load_scene'])
def load_scene_manually(message):
    """Load demo_scene from file manually.

    It will override current demo_scene without any warning.
    """
    args = message.text.split(' ')
    if len(args) != 2:
        bot.reply_to(message, ('Invalid arguments. '
                               'Example: /load_scene ./demo_scene/1.md'))
    else:
        scene = load_scene_from_local_file(args[1])
        current_scenes[message.chat.id] = scene
        send_scene(message.chat, scene)


@bot.message_handler(commands=['load_scene_url'])
def load_scene_url_manually(message):
    """Load demo_scene from url manually.

    It will override current demo_scene without any warning.
    """
    args = message.text.split(' ')
    if len(args) != 2:
        bot.reply_to(message, ('Invalid arguments. '
                               'Example: /load_scene_url https://example.com/demo_scene/1.md'))
    else:
        scene = load_scene_from_url(args[1])
        if scene is not None:
            current_scenes[message.chat.id] = scene
            send_scene(message.chat, scene)
        else:
            bot.reply_to(message, 'Failed to get demo_scene file from url. Please check if url is valid and accessible.')


def load_scene_from_local_file(path):
    """Get demo_scene from local file.
    """
    scene_file = open(path, 'r')
    scene = Scene.from_markdown(scene_file.readlines())
    scene.path = path
    print(str(scene))
    return scene


def load_scene_from_url(url):
    """Get demo_scene from url.
    """
    r = requests.get(url)
    if r.status_code == 200:
        scene = Scene.from_markdown(r.text.splitlines())
        scene.path = url
        print(str(scene))
        return scene
    return None


def send_scene(chat, scene):
    """Send demo_scene as message
    """
    if scene.picture is not None:
        pass
    bot.send_message(chat_id=chat.id, text=scene.content,
                     parse_mode='Markdown', disable_web_page_preview=False,
                     reply_markup=scene.get_reply_buttons())


@bot.message_handler(func=lambda message: True)
def receive_message(message):
    """Receive all types of message from users
    """
    if message.chat.type != 'private':
        return
    if message.chat.id in current_scenes.keys():
        current_scene = current_scenes[message.chat.id]
        choice = current_scene.find_link(message.text)
        if choice is not None:
            path = current_scene.path[:current_scene.path.rfind('/') + 1]
            if choice.path.startswith('.'):
                path += choice.path[1:]
            elif choice.path.startswith('./'):
                path += choice.path[2:]
            else:
                path += choice.path
            if path.lower().startswith('http'):
                scene = load_scene_from_url(path)
            else:
                scene = load_scene_from_local_file(path)
            if scene is not None:
                current_scenes[message.chat.id] = scene
                send_scene(message.chat, scene)
            else:
                bot.send_message(message.chat.id, 'Failed to load next demo_scene.')


if __name__ == '__main__':
    main()
