#!/usr/bin/env python3
from base64 import b64decode
from pprint import pprint
from urllib.parse import urlencode, quote
from requests import get
import transmissionrpc
from imdbpie import Imdb
import time
import feedparser
import PTN
import sys


extratorrents = "http://extra.to"

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



def search_extra(query_term):
    query_term = quote(query_term + " ettv")
    url = f"{extratorrents}/rss.xml?type=search&search={query_term}"
    entries = feedparser.parse(url)["entries"]
    for e in entries:
        info = {
            "infoHash": e["info_hash"],
            "raw_title": e["title"],
            "seeders": e["seeders"],
            "leechers": e["leechers"],
            "size": e["size"]
        }
        info.update(PTN.parse(e["title"]))
        yield info


magnet = hash_to_magnet("6a02592d2bbc069628cd5ed8a54f88ee06ac0ba5",
                            trackers=(
                                "http://bt1.archive.org:6969/announce",
                                "http://bt2.archive.org:6969/announce"
                            )
                        )


search = "the flash s03e02"
search = sys.argv[1]
#pprint(list(search_extra(search)))
best = sorted(search_extra(search), key=lambda e: e["seeders"])[0]
pprint(best)

magnet = hash_to_magnet(best["infoHash"],
                        name=search)

tc = transmissionrpc.Client("localhost")
t = tc.add_torrent(magnet)
hashString = t.hashString
while True:
    t = tc.get_torrent(hashString)
    print(t.name, t.status, t.metadataPercentComplete*100, t.percentDone*100)
    if t.metadataPercentComplete == 1:
        pprint(t.files())
        exit(0)
    time.sleep(1)
