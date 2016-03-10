import os
import json
from flask import Flask
from flask import render_template
from flask import request
from urllib.parse import quote_plus

movie_base = "/media/kraam/Videod/Filmid"
movie_dir = movie_base+"/Nimed"

app = Flask(__name__)

@app.route('/play/<movie_type>/<movie_name>')
@app.route('/play/<movie_type>/<movie_name>.m3u')
def gen_play_movie_url(movie_type, movie_name):
    if movie_type == "movie":
        movie_files = os.listdir(movie_dir+'/'+movie_name)
        sizes = []
        for movie_file in movie_files:
            sizes.append((os.path.getsize(movie_dir+'/'+movie_name+'/'+movie_file), movie_file))
        file_name = sorted(sizes)[-1][1]
        return 'http://karu/kraam/Filmid/Nimed/{}/{}'.format(movie_name.replace(" ", "%20"), 
                                                        file_name.replace(" ", "%20")), 200, {'Content-Type': 'audio/mpegurl; charset=utf-8'}

#@app.route('/')
@app.route('/movies/')
def show_movies():
    key = request.args.get("sort", "Viimati lisatud")
    if key.startswith("-"):
        reverse = True
        key = key[1:]
    else:
        reverse = False
    if key == "Aastad":
        reverse = not reverse
    movies = sorted(os.listdir(movie_base+"/"+key), reverse=reverse)
    movies = (os.path.realpath(movie_base+"/"+key+"/"+movie).split("/")[-1] for movie in movies)
    search = ""
    if request.args.get("search"):
        search = str(request.args.get("search").lower())
        movies = list(filter(lambda movie: search in str(movie.lower()), movies))
    sort_keys = (("Viimati lisatud", "Viimati lisatud"),
                    ("Nimed", "Nimi"),
                    ("Aastad", "Aasta"))
    view = request.args.get("view", "thumb")
    return render_template('movies.html', movies=movies,
                            selected_sort_key=key,
                            sort_keys=sort_keys,
                            view=view,
                            search=search)

@app.route('/movies/<movie_name>')
def show_movies_info(movie_name):
    try:
        metadata = json.loads(open(movie_dir+'/'+movie_name+'/metadata.json').read())
    except:
        metadata = None
    return render_template('movies_info.html', movie=movie_name, metadata=metadata)

@app.route('/series/')
def show_series():
    return render_template('series.html')

@app.route('/downloads/')
def show_downloads():
    return render_template('downloads.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
