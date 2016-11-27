import os
import re
import json
from falcon import HTTPInternalServerError, HTTP_201
from .tools import TODOException

movie_name_and_year = re.compile("(.*)\((.*)\)")

class BaseMovieResource():
    def __init__(self, path):
        self.path = path

class MoviesCollection(BaseMovieResource):

    def on_get(self, req, resp):
        movie_paths = [p for p in (self.path / 'Filmid').iterdir() if p.is_dir()]
        movies = []
        for movie_path in movie_paths:
            if not (movie_path / "metadata.json").exists():
                match = movie_name_and_year.match(movie_path.name)
                if not match:
                    mobj = {
                        "title":movie_path.name,
                        "title_english":movie_path.name,
                        "title_long":movie_path.name,
                        "state":"ok"
                    }
                else:
                    movie_name, movie_year = match.groups()
                    mobj = {
                        "title":movie_name,
                        "title_english":movie_name,
                        "title_long":movie_path.name,
                        "year":movie_year,
                        "state": "ok"
                    }
                movies.append(mobj)
                continue
            with (movie_path / "metadata.json").open()  as f:
                metadata = json.loads(f.read())
                mobj = {
                    "title":metadata["title"],
                    "title_english":metadata["title"],
                    "title_long":movie_path.name,
                    "year":metadata["year"],
                    "imdb_code": metadata["imdb_id"],
                    "rating": metadata["rating"],
                    "summary": metadata["plot_outline"],
                    "synopsis": metadata["plot_outline"],
                    "mpa_rating": metadata["certification"],
                    "genres": metadata["genres"],
                    "yt_trailer_code": metadata["yt_trailer_code"],
                    "state": "ok"
                }
                try:
                    metadata["runtime"] = int(metadata["runtime"]) // 100
                except ValueError as err:
                    pass
                if metadata["plots"]:
                    mobj["description_full"] = metadata["plots"][0]
                movies.append(mobj)
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
        resp.json = [{"path": self.path, "movie":movie}]

class MovieStreamUrlResource(BaseMovieResource):
    
    def on_get(self, req, resp, movie):
        movie_name = movie
        path = self.path / "Filmid"
        movie_files = os.listdir(str(path / movie_name))
        sizes = []
        for movie_file in movie_files:
            sizes.append((os.path.getsize(str(path / movie_name / movie_file)), movie_file))
        file_name = sorted(sizes)[-1][1]
        resp.json = {
            "default": 'https://media.arti.ee/Filmid/{}/{}'.format(movie_name.replace(" ", "%20"), file_name.replace(" ", "%20"))
        }

class MagnetResource():

    def on_post(self, req, resp):
        resp.json = [req.json]
