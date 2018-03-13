from pytube import YouTube
from time import sleep
from config import BOT_SONG_FOLDER, BOT_SONG_LIST
#import subprocess
import re
import os


def compiled_image_regex(image_text):
    text = ".*?{}.*?".format(image_text)
    regex = re.compile(text)
    return regex


def util_download_song(link, name):
    yt = YouTube(link)
    yt_ext = yt.streams.filter(only_audio=True).first()
    yt_ext.download(output_path=BOT_SONG_FOLDER)

    os.replace(os.path.join(BOT_SONG_FOLDER, yt_ext.default_filename), os.path.join(BOT_SONG_FOLDER, re.sub(" ", "_", name.lower()) + "." + yt_ext.subtype))

#    command = "cp -n songs/\"{}\" songs/\"{}\"".format(yt_ext.default_filename, re.sub(" ", "_", name.lower()) + "." + yt_ext.subtype)
#    command_2 = "rm songs/\"{}\"".format(yt_ext.default_filename)

#    subprocess.call(command, shell=True)
#    sleep(1)
#    subprocess.call(command_2, shell=True)

    # TODO: verwisselen naar database
    with open(BOT_SONG_LIST, 'a') as f:
        f.write("\"{}\",\"{}\"\n".format(name, re.sub(" ", "_", name.lower()) + "." + yt_ext.subtype))

    return True
