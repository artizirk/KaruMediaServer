import re
import json
from falcon import HTTPInternalServerError, HTTP_201
from .tools import TODOException

movie_name_and_year = re.compile("(.*)\((.*)\)")

class BaseResource():
    def __init__(self, path):
        self.path = path

class MoviesCollection(BaseResource):

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
                    "runtime": int(metadata["runtime"]) // 100,
                    "imdb_code": metadata["imdb_id"],
                    "rating": metadata["rating"],
                    "summary": metadata["plot_outline"],
                    "synopsis": metadata["plot_outline"],
                    "mpa_rating": metadata["certification"],
                    "genres": metadata["genres"],
                    "state": "ok"
                }
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

class MoviesResource(BaseResource):

    def on_get(self, req, resp, movie):
        resp.json = [{"path": self.path, "movie":movie}]
