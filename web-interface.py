import os
import re
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
        return 'https://media.arti.ee/Filmid/{}/{}'.format(movie_name.replace(" ", "%20"),
                                                        file_name.replace(" ", "%20")), 200, {'Content-Type': 'audio/mpegurl; charset=utf-8'}

@app.route('/')
@app.route('/movies/')
def show_movies():
    key = request.args.get("sort", "")
    if key.startswith("-"):
        reverse = True
        key = key[1:]
    else:
        reverse = False
    if key == "Aastad":
        reverse = not reverse
    movies = []
    if key == "Aastad":
        movies = sorted(((year, movie) for movie, year in (g.groups() for g in (re.search("(.*)\((\d{4})\)", movie_full) for movie_full in os.listdir(movie_base)) if g)), reverse=reverse)
        movies = ["{} ({})".format(movie[1].strip(), movie[0].strip()) for movie in movies]
    elif key == "Viimati lisatud":
        movies = []
        movies_to_sort = []
        for movie in os.listdir(movie_base):
            movie_files = os.listdir(movie_base+'/'+movie)
            sizes = []
            for movie_file in movie_files:
                sizes.append((os.path.getsize(movie_base+'/'+movie+'/'+movie_file), movie_file))
            file_name = sorted(sizes)[-1][1]
            stat = os.stat(movie_base+"/"+movie+"/"+file_name)
            st_atime = stat.st_atime
            st_mtime = stat.st_mtime
            st_ctime = stat.st_ctime
            #print(st_atime, "\t", st_mtime, "\t", st_ctime)
            movies_to_sort.append((int(st_atime), movie))
        movies = (movie for atime, movie in sorted(movies_to_sort, reverse=reverse))
    else:
        movies = sorted(os.listdir(movie_base), reverse=reverse)
        movies = (os.path.realpath(movie_base+"/"+movie).split("/")[-1] for movie in movies)
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
