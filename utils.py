#!/usr/bin/python3
# coding=utf-8
import requests

import data_parser


def load_scene_from_local_file(path):
    """Get demo_scene from local file.
    """
    try:
        scene_file = open(path, 'r')
        scene = data_parser.scene_from_markdown(scene_file.readlines())
        scene.path = path
        print(str(scene))
        return scene
    finally:
        return None


def load_scene_from_url(url):
    """Get demo_scene from url.
    """
    try:
        r = requests.get(url)
        if r.status_code == 200:
            scene = data_parser.scene_from_markdown(r.text.splitlines())
            scene.path = url
            print(str(scene))
            return scene
    finally:
        return None
