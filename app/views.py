import os
import re

from app import app
from .create_db import *
from flask import jsonify, request, render_template, Blueprint, redirect, url_for, send_from_directory

music = Blueprint('songs', __name__)
default = Blueprint('default', __name__)
ion = Blueprint('ion', __name__)
tests = Blueprint('tests', __name__)
images = Blueprint('images', __name__)

conn = engine.connect()

@images.route('/', subdomain="images")
def index():
    images = []
    with open(r'/home/python/ionify/images/imgs.txt', 'r') as i:
        for line in i:
            images.append(line.strip().split(" ")[0])
    images = sorted(images)
    return render_template('images_overview.html', images = images, title="Images")
#    return "<b>List Images</b><br/>" + "<br/>".join(sorted(images))

@tests.route('/songs', subdomain="tests")
def tests_songs():
    song_list = select([songs.c.name])
    result = conn.execute(song_list)
    results = []
    for x in result:
        results.append(str(x))
    return "".join(results)

@default.route('/', defaults={'page': 'index'})
@default.route('/<page>')
def index(page):
    return "haHaa" #redirect(url_for('songs.show'))

@music.route('/', defaults={'page': 'index'}, subdomain='songs', methods=['GET','POST'])
@music.route('/<page>', subdomain='songs', methods=['GET', 'POST'])
def show(page):
    if page == 'queue':
        reply = []
        with open(r'/home/python/ionify/songs/queue.txt', 'r') as q:
            for line in q:
                reply.append(re.sub("\"", "", line.split(',')[0]))
        return render_template('songs_queue.html', queue = reply, title="Queue")

    if page == 'favicon.ico':
        return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype="image/vnd.microsoft.ico")

    if page == '_json_queue_song':
        song_id = int(request.get_json())
        songs = []
        with open(r'/home/python/ionify/songs/songs.txt', 'r') as f:
            for line in f:
                songs.append(line.strip())
        with open(r'/home/python/ionify/songs/queue.txt', 'a') as a:
            a.write(songs[song_id]+"\n")

    songs = []
    with open(r'/home/python/ionify/songs/songs.txt', 'r') as f:
        for line in f:
            songs.append(re.sub('\"', '', line.split(',')[0].strip()))

    sorted_list = sorted([(songs.index(x), x) for x in songs])
    return render_template('songs_overview.html', songs=sorted_list, title="Songlist")

@ion.route('/', defaults={'page': 'index'}, subdomain='ion')
@ion.route('/<page>', subdomain='ion')
def ion_reroute(page):
    if page == 'songs':
        return redirect(url_for('songs.show'))
    elif page == 'images':
        return "Coming soon in a shitty coded website near you."
    else:
        return redirect(url_for('default.index'))
