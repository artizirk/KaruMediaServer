#!/usr/bin/env python3

import os
import json
from imdbpie import Imdb
import requests
from pprint import pprint
import re
import logging
from logging import info, debug, warning, error
import subprocess

logging.basicConfig(level=logging.DEBUG)

movie_dir = "/home/arti/Videod/Filmid"

YTKEY = os.environ.get("YTKEY")
if not YTKEY:
    error("YTKEY not set")
    exit(1)

imdb = Imdb()


def download_movie_metadata(movie):
    movie, year = re.search("(.*)\((\d{4})\)", movie).groups()
    movie = movie.strip()
    info("Finding movie {} {}".format(movie, year))
    #print(movie, year)
    ret = imdb.search_for_title(movie)
    #print(ret)
    movie_metadata_basic = [m for m in ret if m["year"] == year][0]
    info("Found movie with imdb_id {}".format(movie_metadata_basic["imdb_id"]))
    info("Downloading metadata")
    movie_metadata_more = imdb.get_title_by_id(movie_metadata_basic["imdb_id"])
    info("Metadata downloaded")
    return movie_metadata_more

def write_metadata(movie_dir, mm):
    metadata = {"title":str(mm.title),
                "year": str(mm.year),
                "plot_outline": str(mm.plot_outline),
                "rating": str(mm.rating),
                "certification": str(mm.certification),
                "runtime": str(mm.runtime),
                "genres": mm.genres,
                "plots": mm.plots,
                "imdb_id":str(mm.imdb_id)}

    info("opening metadata.json in {} for {}".format(movie_dir, metadata["title"]))
    with open(movie_dir+"/metadata.json", "w") as f:
        info("writing metadata for {}".format(metadata["title"]))
        f.write(json.dumps(metadata, indent=4, sort_keys=True))

def download_poster(movie_dir, metadata):
    info("Downloading posters for {}".format(metadata.title))
    if not os.path.isfile(movie_dir+"/cover.jpg"):
        subprocess.call(['wget', metadata.cover_url,
                         "-O", movie_dir+"/cover.jpg"])
    else:
        info("cover.jpg already downloaded")
    #if not os.path.isfile(movie_dir+"/poster.jpg"):
    #    subprocess.call(['wget', metadata.poster_url,
    #                    "-O", movie_dir+"/poster.jpg"])
    #else:
    #    info("poster.jpg already downloaded")
    info("Poster downloading finished")

def download_trailer(movie_dir, metadata):
    info("Downloading trailer for {}".format(metadata.title))
    if os.path.isfile(movie_dir+"/trailer.mp4"):
        info("Trailer already downloaded")
        return
    trailers = []
    for key, val in metadata.trailers.items():
        r = requests.head(val)
        size = r.headers.get("Content-Length")
        trailers.append((size, key, val))
    trailer = sorted(trailers)[::-1][0]
    subprocess.call(['wget', trailer[2],
                     "-O", movie_dir+"/trailer.mp4"])

def add_yt_trailer_code(md):
    params = {"key": YTKEY,
              "part":"id", "maxResults":1,
              "q":"{} ({}) trailer".format(md.get("title"), md.get("year", ""))}
    r = requests.get("https://www.googleapis.com/youtube/v3/search", params=params)
    md["yt_trailer_code"] = r.json()["items"][0]["id"]["videoId"]
    return md

def metadata_update_needed(metadata_file):
    with open(metadata_file, "r") as f:
        md = json.loads(f.read())
        if "imdb_id" not in md:
            return True
        elif "yt_trailer_code" not in md:
            md = add_yt_trailer_code(md)
            print(md.get("title"), md.get("yt_trailer_code"))
            fd = open(metadata_file, "w")
            fd.write(json.dumps(md, indent=4, sort_keys=True))
            fd.close()
        else:
            return False



for movie in os.listdir(movie_dir):
    #print(movie)
    if os.path.isfile(movie_dir+"/"+movie+"/metadata.json") \
            and not metadata_update_needed(movie_dir+"/"+movie+"/metadata.json"):
        continue
    try:
        re.search("(.*)\((\d{4})\)", movie).groups()
    except:
        continue
    try:
        mm = download_movie_metadata(movie)
        write_metadata(movie_dir+"/"+movie, mm)
    except:
        logging.exception("Metadata download failed")
    try:
        download_poster(movie_dir+"/"+movie, mm)
    except:
        logging.exception("Poster download failed")
    #download_trailer(movie_dir+"/"+movie, mm)
