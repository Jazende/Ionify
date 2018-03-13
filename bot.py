import os
import re
import random
import aiohttp
import discord
import threading
import asyncio
from config import *
from utils import *
from opus_loader import load_opus_library
from datetime import datetime

class Ionify(discord.Client):
    def __init__(self):
        super().__init__()
        self.queue = []
        self.populate_songlist()
        self.populate_imagelist()
        self.populate_queue()
        self.player = 0
        self.now_playing = None
        self.shuffle = False
        self.last_set_played = "a"
        self.loop = asyncio.get_event_loop()
        self.circus_is_playing = False

    def populate_queue(self):
        self.queue = []
        with open(QUEUE_SONG_LIST, 'r') as q:
            for line in q:
                subbed = re.sub("\"", "", line.strip())
                self.queue.append((subbed.split(",")[0], subbed.split(",")[1]))

    def write_queue(self):
        with open(QUEUE_SONG_LIST, 'w') as g:
            for line in self.queue:
                text = "\"{}\",\"{}\"\n".format(line[0], line[1])
                g.write(text)

    def populate_songlist_db(self):
        songs = self.db_session.query(song).all()
        self.songlist = []
        for s in songs:
            self.songlist.append((s.name, s.file_location))

    def populate_songlist(self):
        self.songlist = []
        with open(BOT_SONG_LIST, 'r') as g:
            for line in g:
                subbed = re.sub("\"", "", line.strip())
                self.songlist.append((subbed.split(",")[0], subbed.split(",")[1]))

    def populate_imagelist(self):
        self.imagelist = []
        with open(BOT_IMG_LIST, 'r') as f:
            for line in f:
                stripped = line.strip()
                one = stripped.split(" ")[0]
                self.imagelist.append((one, compiled_image_regex(one), stripped.split(" ")[1]))

    async def download_song(self, link, name):
        t = threading.Thread(target=util_download_song, args=(link, name))
        t.start()

    def start_audio_player(self, songname, init=False):
        filename = os.path.join(BOT_SONG_FOLDER, songname)
        player = self.voice.create_ffmpeg_player(filename)
        if init:
            player.start()
            player.stop()
        return player
    
    async def circus(self, init=False):
        if self.player.is_playing():
            self.player.pause()
        circus_loc = os.path.join(BOT_SONG_FOLDER, "benny_hill_theme.mp4")
        self.play_circus = self.voice.create_ffmpeg_player(circus_loc)
        self.play_circus.start()
        self.circus_is_playing = True
        while True:
            await asyncio.sleep(5)
            if self.play_circus.is_done():
                break
        #await self.await_circus_done()
        self.play_circus.stop()
        self.circus_is_playing = False
        try:
            self.player.resume()
        except:
            pass

    def play_audio(self):
        self.populate_queue()
        if len(self.queue) > 0:
            if not self.player.is_playing():
                info = self.queue.pop(0)
                self.write_queue()
                self.now_playing = info[0]
                print(datetime.utcnow(), "Printing: Starting new song: {}".format(self.now_playing))
                songname = os.path.join(BOT_SONG_FOLDER, info[1])
                self.player = self.voice.create_ffmpeg_player(songname, after=self.play_audio)
                self.player.start()
        elif self.shuffle:
            if not self.player.is_playing():
                songmatch = random.choice(self.songlist)
                self.now_playing = songmatch[0]
                self.queue.append((songmatch[0], songmatch[1]))
                self.write_queue()
                print("Shuffled: ", songmatch[0])
                self.play_audio()
        else:
            self.now_playing = None

    async def set_presence(self, pres):
        await self.change_presence(game=discord.Game(name=pres))

    async def async_download_picture(self, name, link):
        ext = re.findall(".*\w+\/.+\.([\w\d]{1,5})\??.*", link)
        if not ext:
            return False
        picture_name = os.path.join(BOT_IMG_FOLDER, name.lower()+"."+ext[0])
        async with aiohttp.ClientSession() as session:
            async with session.get(link) as resp:
                with open(picture_name, 'wb') as f:
                    f.write(await resp.read())
            await session.close()
        with open(BOT_IMG_LIST, 'a') as g:
            g.write(name+" "+ext[0]+"\n")
        self.populate_imagelist()

    async def normie_download_picture(self, name, link):
        s = requests.Session()
        headers = {"User-Agent":"Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.3", "Upgrade-Insecure-Requests": "1", "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,image/jpg,*/*;q=0.8", "accept_encoding": "gzip, deflate, br", "dnt":"1"}
        s.headers = headers
        ext = re.findall(".*\w+\/.+\.([\w\d]{1,5})\??.*", img_link)
        if not ext:
            return False
        filename = "{}.{}".format(name, ext[0])
        picture_name = os.path.join(BOT_IMG_FOLDER, filename)
        with open(picture_name, 'wb') as f:
            f.write(s.get(img_link).content)
        with open(BOT_IMG_LIST, 'a') as g:
            g.write(name+" "+ext[0]+"\n")
        self.populate_imagelist()
        return True

    async def voice_client_creation(self):
        channel = self.get_channel(VOICE_CHANNEL_ID)
        self.voice = await self.join_voice_channel(channel)
        print("Joined voice channel.")

    async def on_ready(self):
        print('Logged in as', self.user.name, self.user.id, '-------', sep='\n')
        await self.voice_client_creation()
        self.player = self.start_audio_player('mulan_man.mp4', init=True)
        self.player.stop()
        #wawait self.circus(init=True)      

    async def on_message(self, message):
        await self.wait_until_ready()

        author = str(message.author)

        if not author == BOT:
            if message.content.startswith("!song "):
                print(str(message.timestamp), author, str(message.content))
                if message.content.startswith("!song random"):
                    await self.delete_message(message)
                    self.populate_queue()
                    songmatch = random.choice(self.songlist)
                    self.queue.append((songmatch[0], songmatch[1]))
                    self.write_queue()
                    self.play_audio()
                elif message.content.startswith("!song playing"):
                    await self.delete_message(message)
                    await self.send_message(message.channel, "Now playing: {}".format(self.now_playing))
                elif message.content.startswith("!song shuffle start"):
                    await self.delete_message(message)
                    self.shuffle = True
                    self.play_audio()
                elif message.content.startswith("!song shuffle stop"):
                    self.shuffle = False
                    self.player.stop()
                    try:
                        self.play_circus.stop()
                    except:
                        pass
                    await self.delete_message(message)
                elif message.content.startswith("!song skip"):
                    await self.delete_message(message)
                    try:
                        self.player.stop()
                    except NameError:
                        await self.send_message(message.channel, "Not playing audio.")
                elif message.content.startswith("!song stop"):
                    await self.delete_message(message)
                    try:
                        self.populate_queue()
                        self.queue = []
                        self.write_queue()
                        self.shuffle = False
                        self.player.stop()
                    except NameError:
                        await self.send_message(message.channel, "Not playing audio.")
                elif message.content.startswith("!song pause"):
                    await self.delete_message(message)
                    try:
                        self.player.pause()
                    except NameError:
                        await self.send_message(message.channel, "Not playing anything.")
                elif message.content.startswith("!song resume"):
                    await self.delete_message(message)
                    try:
                        self.player.resume()
                    except NameError:
                        await self.send_message(message.channel, "Not playing audio.")
                else:
                    for songmatch in self.songlist:
                        if message.content.startswith("!song {}".format(songmatch[0])):
                            await self.delete_message(message)
                            self.queue.append((songmatch[0], songmatch[1]))
                            self.write_queue()
                            self.play_audio()

            elif message.content.startswith("!songs"):
                if message.content.startswith("!songs add"):
                    results = re.findall("!songs add \"(.*?youtu.*?)\" \"(\S[a-zA-Z0-9\s]*?\S)\"", str(message.content), flags=re.IGNORECASE)
                    if len(results) == 1:
                        print(str(message.timestamp), author, results[0][0], results[0][1])
                        await self.download_song(results[0][0].strip(), results[0][1].lower().strip())
                elif message.content.startswith("!songs queue"):
                    reply = ", ".join([x[0] for x in self.queue[:3]])
                    if len(self.queue) == 0:
                        await self.send_message(message.channel, "No queue.")
                    elif len(self.queue) <= 3:
                        await self.send_message(message.channel, reply)
                    else:
                        await self.send_message(message.channel, "Next 3 songs, out of {}: ".format(len(self.queue))+reply)
                    await self.delete_message(message)
                elif message.content.startswith("!songs list"):
                    await self.send_message(message.channel, "Go to http://ion.kridder.eu/songs")
            elif message.content.startswith("!ion"):
                if message.content.startswith("!ions"):
                    await self.send_message(message.channel, "Go to http://ion.kridder.eu/images")
                elif message.content.startswith("!ion update songs"):
                    self.populate_songlist()
                elif message.content.startswith("!ion playing ") and author == OWNER:
                    await self.set_presence(str(message.content)[12:])
                elif message.content.startswith("!ion online") and author == OWNER:
                    await self.change_presence("")
                elif message.content.startswith("!ion offline") and author == OWNER:
                    await self.change_presence(status=discord.Status("offline"))
                elif message.content.startswith("!ion "):
                    if str(message.content).lower().split(" ")[1] in [x[0] for x in self.imagelist]:
                        await client.send_message(message.channel, "Name already exists, skipped.")
                    else:
                        _, name, link = str(message.content).lower().split(" ")
                        print(str(message.author), name)
                        await self.async_download_picture(name, link)
            elif message.content.startswith("!private") and author == OWNER:
                await self.send_message(self.get_channel(OFFTOPIC_CHANNEL_ID), str(message.content)[8:])
            elif message.content.startswith("!commands"):
                commands = "!song (shuffle), !songs list, !songs add\n!ions, !ion update songs"
                await self.send_message(message.channel, commands)
            elif message.content.startswith("!INSTANT CIRCUS"):
                if not self.circus_is_playing:
                    await self.circus(message)
            elif message.content.startswith("!INSTANT STOP"):
                try:
                    self.play_circus.stop()
                except:
                    pass
            else:
                for match in self.imagelist:
                    if match[1].match(str(message.content).lower()):
                        imagename = match[0]+"."+match[2]
                        img_loc = os.path.join(BOT_IMG_FOLDER, imagename)
                        with open(img_loc, 'rb') as f:
                            await self.send_file(message.channel, f)

def main(token):
    print("Loading...")
    ionify = Ionify()    
    async def set_playing_loop():
        await ionify.wait_until_ready()
        while True:
            if not ionify.last_set_played == ionify.now_playing:
                print('Setting played: {}'.format(ionify.now_playing))
                ionify.last_set_played = ionify.now_playing
                await ionify.change_presence(game=discord.Game(name=ionify.now_playing))
            await asyncio.sleep(5)
    ionify.loop.create_task(set_playing_loop())
    ionify.run(token)


if __name__ == '__main__':
    main(TOKEN)
