#!/bin/env python


import os
import re
import fire
from pathlib import Path


command_base = "wget " +                \
    "--load-cookies ~/.urs_cookies " +  \
    "--save-cookies ~/.urs_cookies " +  \
    "--auth-no-challenge=on " +         \
    "--keep-session-cookies " +         \
    "--content-disposition "


def parse_urls(path: str) -> [(str, str)]:
    url_list = []
    with open(file, 'r') as f:
        for line in f.readlines():
            stripped_line = line.strip()
            x = re.search(r"[^./_]+\.nc4|[^./_]+\.pdf", stripped_line)
            url_list.append((x.group(), stripped_line))
    return url_list


def download_single(url: str, path: str):
    path = check_path(path)
    location = " -P " + os.path.realpath(path)
    command = command_base + url + location
    os.system(command)


def continue_single(url: str, path: str):
    location = " -P " + os.path.realpath(path)
    command = command_base + url + location + " --continue"
    os.system(command)


def download_from_file(urls: str, path: str):
    path = check_path(path)
    location = " -P " + os.path.realpath(path)
    command = command_base + "-i " + urls + location
    os.system(command)


# TODO: fix the continuation bug
# come up with some type of metadata that knows where the download stands
def continue_from_file(urls: str, path: str):
    existing = list(Path(path).glob('*.nc4'))
    print(existing)
    with open(urls, 'r') as f:
        for line in f.readlines():
            pass
    location = " -P " + os.path.realpath(path)
    command = command_base + "-i " + urls + location + " --continue"
    os.system(command)


def check_path(path: str) -> str:
    if not re.findall(r"/$", path):
        path + "/"
    if not os.path.exists(path):
        os.mkdir(path)
    return path

def download(src: str, path: str):
    if not os.path.exists(src):
        download_single(src, path)
    else:
        download_from_file(src, path)


def continue_dl(src: str, path: str):
    if not os.path.exists(src):
        continue_single(src, path)
    else:
        continue_from_file(src, path)


if __name__ == '__main__':
    fire.Fire({
        "from": download,
        #"continue": continue_dl
    })
