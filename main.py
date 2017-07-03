#!/usr/bin/python3
# coding=utf-8
import requests
import telebot
import time
import base64
from token_config import TELEBOT_TOKEN

from data_types import Scene, Link

SAVE_HEADER = 'GALBOT::P::'

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


@bot.message_handler(commands=['demo'])
def load_demo(message):
    bot.reply_to(message, 'Now loading demo scene from https://1cup.rabi.coffee/demo_scene ...')
    message.text = '/load_scene_url https://1cup.rabi.coffee/demo_scene/1.md'
    load_scene_url_manually(message)


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
            bot.reply_to(message, 'Failed to get demo_scene file from url.'
                                  'Please check if url is valid and accessible.')


@bot.message_handler(commands=['save'])
def save_progress(message):
    """Save current progress

     In fact, progress is saved by current scene url/path.
    """
    if message.chat.id in current_scenes.keys():
        code = SAVE_HEADER + base64.b64encode(current_scenes[message.chat.id].path.encode(encoding='utf-8')).decode()
        bot.send_message(chat_id=message.chat.id, text=('Your progress is saved to this code. If your want to '
                                                        'load, you can paste it to here '
                                                        f' send to me.\n```\n{code}\n```'),
                         parse_mode='Markdown')
    else:
        bot.reply_to(message, "Sorry, you aren't playing any game currently. So we cannot save your progress.")


def load_scene_from_local_file(path):
    """Get demo_scene from local file.
    """
    try:
        scene_file = open(path, 'r')
        scene = Scene.from_markdown(scene_file.readlines())
        scene.path = path
        print(str(scene))
        return scene
    finally:
        return None


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


def start_scene(chat, next_path):
    if next_path.lower().startswith('http'):
        next_scene = load_scene_from_url(next_path)
    else:
        next_scene = load_scene_from_local_file(next_path)
    if next_scene is not None:
        current_scenes[chat.id] = next_scene
        send_scene(chat, next_scene)
    else:
        bot.send_message(chat.id, 'Failed to load progress.')


def send_scene(chat, scene):
    """Send demo_scene as message
    """
    if scene is None:
        return
    bot.send_chat_action(chat.id, 'typing')
    if scene.picture is not None:
        path = scene.path[:scene.path.rfind('/') + 1]
        if scene.picture.startswith('.'):
            path += scene.picture[1:]
        elif scene.picture.startswith('./'):
            path += scene.picture[2:]
        elif scene.picture.startswith('http'):
            path = scene.picture
        else:
            path += scene.picture
        if path.startswith('http'):
            bot.send_photo(chat_id=chat.id, photo=path, caption=scene.content,
                           reply_markup=scene.get_reply_buttons())
        else:
            pic_file = open(path, 'rb')
            bot.send_photo(chat_id=chat.id, photo=pic_file, caption=scene.content,
                           reply_markup=scene.get_reply_buttons())
    else:
        time.sleep(1)
        bot.send_message(chat_id=chat.id, text=scene.content,
                         parse_mode='Markdown', disable_web_page_preview=False,
                         reply_markup=scene.get_reply_buttons())
    auto_next = scene.get_auto_link()
    if auto_next is not None:
        time.sleep(auto_next.delay)
        next_path = scene.path[:scene.path.rfind('/') + 1]
        if auto_next.path.startswith('.'):
            next_path += auto_next.path[1:]
        elif auto_next.path.startswith('./'):
            next_path += auto_next.path[2:]
        elif auto_next.path.startswith('http'):
            next_path = auto_next.path
        else:
            next_path += auto_next.path
        start_scene(chat, next_path)


@bot.message_handler(func=lambda message: True)
def receive_message(message):
    """Receive all types of message from users
    """
    if message.chat.type != 'private':
        return
    if message.text.startswith(SAVE_HEADER):
        code = message.text.replace(SAVE_HEADER, '').strip()
        path = base64.b64decode(code).decode()
        bot.reply_to(message, 'Found progress! Loading...')
        bot.send_chat_action(message.chat.id, 'typing')
        start_scene(message.chat, path)
    if message.chat.id in current_scenes.keys():
        current_scene = current_scenes[message.chat.id]
        choice = current_scene.find_link(message.text)
        if choice is not None:
            path = current_scene.path[:current_scene.path.rfind('/') + 1]
            if choice.path.startswith('.'):
                path += choice.path[1:]
            elif choice.path.startswith('./'):
                path += choice.path[2:]
            elif choice.path.startswith('http'):
                path = choice.path
            else:
                path += choice.path
            start_scene(message.chat, path)


if __name__ == '__main__':
    main()
