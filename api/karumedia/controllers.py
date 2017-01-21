import os
import re
import json
from . import tasks
from falcon import HTTPInternalServerError, HTTP_201
from bson.objectid import ObjectId
from .tools import TODOException
from .models import *
from pprint import pprint
from urllib.parse import quote


movie_name_and_year = re.compile("(.*)\((.*)\)")

class BaseMovieResource():
    def __init__(self, path):
        self.path = path

def build_movie_object(media):
    mobj = {
        "title":media.title,
        "title_english":media.title,
        "title_long": f"{media.title} ({media.year})",
        "year":media.year,
        "imdb_code": media.imdb_id,
        "rating": media.rating,
        "summary": media.plot_outline,
        "synopsis": media.plot_outline,
        "mpa_rating": media.mpa_rating,
        "genres": media.genres,
        "yt_trailer_code": media.yt_trailer_code,
        "state": "ok",
        "id": media.id
    }
    try:
        mobj["runtime"] = media.runtime // 100
    except:
        pass
    if media.plots:
        mobj["description_full"] = media.plots[0]

    relevant_tasks = list(Task.objects(imdb_id=media.imdb_id, state__ne="done"))
    if relevant_tasks:
        pprint(relevant_tasks)
        mobj["state"] = "tasks_running"
        mobj["relevant_tasks"] = [task.id for task in relevant_tasks]

    mobj["streams"] = {}
    stream_urls = list(MediaFile.objects(media=media))
    if stream_urls:
        mobj["streams"] = {media_file.resolution: media_file.url for media_file in stream_urls if media_file.mimetype.startswith("video")}

    mobj["small_cover_image"] = f"https://media.arti.ee/Filmid/{quote(mobj['title_long'])}/cover.jpg"
    mobj["medium_cover_image"] = mobj["small_cover_image"]
    mobj["large_cover_image"] = mobj["medium_cover_image"]

    return mobj

class MoviesCollection(BaseMovieResource):

    def on_get(self, req, resp):
        movies = []
        for media in Media.objects:
            movies.append(build_movie_object(media))
        jobj = {"data":{
                    "limit":len(movies),
                    "count":len(movies),
                    "movies":movies,
                    "page_number":1
                    },
                "status": "ok",
                "status_message": "query was successful"
                }
        resp.json = jobj

class MoviesResource(BaseMovieResource):

    def on_get(self, req, resp, movie):
        try:
            media = Media.objects.get(id=movie)
        except ValidationError:
            media = Media.objects.get(imdb_id=movie)
        resp.json = build_movie_object(media)

class MagnetResource():

    def on_post(self, req, resp):
        json = req.json
        if not 'info_hash' in json:
            raise ValueError("info_hash missing from request")
        task = TaskMetainfoDl(info_hash=json['info_hash'])
        task.imdb_code = json.get('imdb_code')
        task.save()
        tasks.metainfo_dl(str(task.id))
        resp.json = {"task_id":task.id}


class TaskCollection():

    def on_get(self, req, resp):
        tasks = list()
        for task in Task.objects:
            tasks.append(task.to_mongo())
        resp.json = tasks

class TaskResource():
    def on_get(self, req, resp, task_id):
        task = Task.objects.get(id=task_id)
        resp.json = task.to_mongo()

    def on_delete(self, req, resp, task_id):
        Task.objects(id=task_id).delete()
