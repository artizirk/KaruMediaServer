import json
from pathlib import Path

import falcon

from .tools import JsonRequest, JsonResponse, error_handler
from .controllers import *

class AboutResource():

    def on_get(self, req, resp):
        r = {"about": {
                "name": "Karu Media API",
                "version": "1",
                "docs": "TODO"
                }
            }
        r.update({"endpoints":[
                        {"url":"/",
                        "description":"About this API"}
                    ]})

        resp.body = json.dumps(r, indent=4)


app = application = falcon.API(request_type=JsonRequest, response_type=JsonResponse)
app.add_error_handler(ValueError, error_handler)
app.add_route("/", AboutResource())

path = Path("/home/arti/Videod")

app.add_route("/movies", MoviesCollection(path))
app.add_route("/movies/{movie}", MoviesResource(path))
