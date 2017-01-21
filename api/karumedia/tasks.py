from uwsgi_tasks import *
from .models import *
from time import sleep
from requests import get
import transmissionrpc
from pprint import pprint
from base64 import b64decode
from urllib.parse import urlencode, quote
import PTN
from imdbpie import Imdb
import os
import subprocess
import requests
import magic
import json

YTKEY = os.environ.get("YTKEY")
if not YTKEY:
    error("YTKEY not set")
    exit(1)


default_trackers = [
    'udp://glotorrents.pw:6969/announce',
    'udp://tracker.openbittorrent.com:80',
    'udp://tracker.coppersurfer.tk:6969',
    'udp://tracker.leechers-paradise.org:6969',
    'udp://p4p.arenabg.ch:1337',
    'udp://tracker.internetwarriors.net:1337',
    'udp://tracker.opentrackr.org:1337/announce'
]

r = get("https://raw.githubusercontent.com/ngosang/trackerslist/master/trackers_best.txt")

best_trackers = r.text

for tracker in best_trackers.split("\n"):
    tracker = tracker.strip()
    if tracker:
        default_trackers.append(tracker)

def hash_to_magnet(infoHash, name=None, trackers=None):
    try:
        b64decode(infoHash)
    except:
        raise Exception("Invalid infoHash")
    magnet = {
        "dn": name,
        "tr": list(default_trackers)
    }
    if not name:
        del magnet["dn"]
    if trackers:
        magnet["tr"].extend(trackers)
    return "magnet:?xt=urn:btih:{}&".format(infoHash) + urlencode(magnet, doseq=True)



tc = transmissionrpc.Client("172.20.1.2", user="admin", password="minemetsa")
imdb = Imdb()

def guess_imdb_code(title):
    info = PTN.parse(title)
    if 'year' not in info:
        print("No title year found in title")
    results = imdb.search_for_title(info["title"])
    if not results:
        return None
    if 'year' in info:
        match = [movie for movie in results if movie["year"] == str(info["year"])]
        if not match:
            pprint(results)
            return None
        else:
            match = match[0]["imdb_id"]
    else:
        match = results[0]["imdb_id"]
    return match


@task
def metainfo_dl(task_id):
    task = TaskMetainfoDl.objects.get(id=task_id)

    magnet = hash_to_magnet(task.info_hash)
    t = tc.add_torrent(magnet)
    print(task.info_hash.lower())
    print(t.hashString)

    task.state = "running"
    task.save()

    while True:
        t = tc.get_torrent(t.hashString)
        print(t.name, t.status, t.metadataPercentComplete*100, t.percentDone*100)
        if t.metadataPercentComplete == 1:
            break
        task.progress = t.metadataPercentComplete*100
        task.save()
        sleep(1)

    pprint(t.files())
    t.stop()

    if not task.imdb_id:
        imdb_id = guess_imdb_code(t.name)
    else:
        imdb_id = task.imdb_id
    print("imdb_id:", imdb_id)

    try:
        media = Media.objects.get(imdb_id=imdb_id)
        print("Found existing media object:", media)
    except DoesNotExist:
        media = Media()
        media.imdb_id = imdb_id
        media.save()
        print("Created a new media object:", media, media.imdb_id)

    imdb_dl_task = TaskImdbDl(imdb_id=imdb_id)
    imdb_dl_task.media = media
    imdb_dl_task.save()
    imdb_dl(str(imdb_dl_task.id))

    torrent_dl_task = TaskTorrentDl(info_hash=t.hashString, imdb_id=imdb_id)
    torrent_dl_task.media = media
    torrent_dl_task.save()
    torrent_dl(str(torrent_dl_task.id))

    task.state = "done"
    task.sub_tasks.append(imdb_dl_task)
    task.sub_tasks.append(torrent_dl_task)
    task.media = media
    task.save()

@task
def imdb_dl(task_id):
    task = TaskImdbDl.objects.get(id=task_id)
    task.state = "running"
    task.save()
    print("imdb_id:", task.imdb_id)
    try:
        media = Media.objects.get(imdb_id=task.imdb_id)
        print("Using existing media object:", media)
    except DoesNotExist:
        media = Media()
        print("Creating a new media object")
    media.imdb_id = task.imdb_id

    title = imdb.get_title_by_id(task.imdb_id)
    media.title = title.title
    media.year = title.year
    media.runtime = int(title.runtime)
    media.genres = title.genres
    media.mpa_rating = title.certification
    media.release_date = title.release_date
    media.type = title.type
    media.plot_outline = title.plot_outline
    media.plots = title.plots
    media.rating = title.rating
    media.save()

    task.media = media
    task.save()


    params = {"key": YTKEY,
              "part":"id", "maxResults":1,
              "q":"{} ({}) trailer".format(media.title, media.year)}
    r = requests.get("https://www.googleapis.com/youtube/v3/search", params=params)
    media.yt_trailer_code = r.json()["items"][0]["id"]["videoId"]
    media.save()

    task.state = "done"
    task.progress = 100
    task.save()


def probe(vid_file_path):
    ''' Give a json from ffprobe command line

    @vid_file_path : The absolute (full) path of the video file, string.
    '''
    if type(vid_file_path) != str:
        raise Exception('Gvie ffprobe a full file path of the video')
        return

    command = ["ffprobe",
            "-loglevel",  "quiet",
            "-print_format", "json",
             "-show_format",
             "-show_streams",
             vid_file_path
             ]

    pipe = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out, err = pipe.communicate()
    return json.loads(out)


def duration(vid_file_path):
    ''' Video's duration in seconds, return a float number
    '''
    _json = probe(vid_file_path)
    pprint(_json)

    if 'format' in _json:
        if 'duration' in _json['format']:
            return float(_json['format']['duration'])

    if 'streams' in _json:
        # commonly stream 0 is the video
        for s in _json['streams']:
            if 'duration' in s:
                return float(s['duration'])

    # if everything didn't happen,
    # we got here because no single 'return' in the above happen.
    raise Exception('I found no duration')
    #return None

@task
def torrent_dl(task_id):
    task = TaskTorrentDl.objects.get(id=task_id)
    task.state = "running"
    task.save()

    t = tc.get_torrent(task.info_hash)
    t.start()

    while True:
        t = tc.get_torrent(task.info_hash)
        print(t.name, t.status, t.metadataPercentComplete*100, t.percentDone*100)
        if t.percentDone == 1:
            break
        task.progress = t.percentDone*100
        task.save()
        sleep(1)

    if "imdb_id" in task:
        try:
            media = Media.objects.get(imdb_id=task.imdb_id)
        except DoesNotExist:
            pass
        else:
            tc.rename_torrent_path(task.info_hash, t.name, f"{media.title} ({media.year})")

    tc.move_torrent_data(task.info_hash, "/srv/media/Filmid")

    with magic.Magic(flags=magic.MAGIC_MIME_TYPE) as m:
        for file_id, file_data in t.files().items():
            file_path = "/srv/media/Filmid/"+file_data["name"]
            file_type = m.id_filename(file_path)
            video_duration = None
            if file_type.startswith("video"):
                video_duration = duration(file_path)

            print(file_path, file_type, video_duration)
            if not MediaFile.objects(path = file_path):
                media_file = MediaFile()
                media_file.media = Media.objects.get(imdb_id=task.imdb_id)
                media_file.path = file_path
                media_file.url = f"http://media.arti.ee/Filmid/{quote(file_data['name'])}"
                media_file.mimetype = file_type
                media_file.resolution = "native"
                media_file.save()

    media = task.media
    cover_path = f"/srv/media/Filmid/{media.title} ({media.year})/cover.jpg"
    if not MediaFile.objects(media=media, path=cover_path):
        subprocess.call(['wget', imdb.get_title_by_id(media.imdb_id).cover_url,
                         "-O", cover_path])
        media_poster = MediaFile()
        media_poster.path = cover_path
        movie_name_and_year = quote(f"{media.title} ({media.year})")
        media_poster.url = f"https://media.arti.ee/Filmid/{movie_name_and_year}/cover.jpg"
        media_poster.save()

    task.state = "done"
    task.progress = 100
    task.save()
