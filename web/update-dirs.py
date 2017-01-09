#!/usr/bin/env python3

import os
import re
import json
import logging
from pprint import pprint
from logging import info, debug, warning

logging.basicConfig(level=logging.INFO)

movie_dir = "/media/kraam/Videod/Filmid"


def get_list_of_genres():
    genres = {}
    for movie in os.listdir(movie_dir+"/Nimed"):
        try:
            metadata = json.loads(open(movie_dir+"/Nimed/"+movie+"/metadata.json").read())
            for genre in metadata["genres"]:
                try:
                    genres[genre].append(movie)
                except:
                    genres[genre] = [movie]
        except Exception as e:
            info("bad metadata {} {}".format(movie, str(e)))
    return genres


def create_genre_dirs_and_movie_symlinks(genres):
    for genre, movies in genres.items():
        try:
            os.mkdir(movie_dir+"/Zanrid/"+genre)
        except OSError as e:
            debug("{} dir exists {}".format(genre, str(e)))
        for movie in movies:
            try:
                os.symlink(movie_dir+"/Nimed/"+movie, 
                    movie_dir+"/Zanrid/"+genre+"/"+movie)
            except Exception as e:
                pass
                debug("error while symlinking {}".format(str(e)))

def sort_movies_by_year():
    for movie_full in os.listdir(movie_dir+"/Nimed"):
        try:
            movie, year = re.search("(.*)\((\d{4})\)", movie_full).groups()
        except:
            continue
        try: 
            os.symlink(movie_dir+"/Nimed/"+movie_full,
                movie_dir+"/Aastad/({}) {}".format(year.strip(), movie.strip()))
        except Exception as e:
            debug("error while symlinking {}".format(str(e)))

def sort_by_adding_time():
    for file_name in os.listdir(movie_dir+"/Viimati lisatud"):
        try:
            os.unlink(movie_dir+"/Viimati lisatud/"+file_name)
        except Exception as e:
            debug("unlink failed {}".format(str(e)))

    movies_to_sort = []
    for movie in os.listdir(movie_dir+"/Nimed"):
        movie_files = os.listdir(movie_dir+'/Nimed/'+movie)
        sizes = []
        for movie_file in movie_files:
            sizes.append((os.path.getsize(movie_dir+'/Nimed/'+movie+'/'+movie_file), movie_file))
        file_name = sorted(sizes)[-1][1]
        stat = os.stat(movie_dir+"/Nimed/"+movie+"/"+file_name)
        st_atime = stat.st_atime
        st_mtime = stat.st_mtime
        st_ctime = stat.st_ctime
        #print(st_atime, "\t", st_mtime, "\t", st_ctime)
        movies_to_sort.append((int(st_atime), movie))
    for index, (atime, movie) in enumerate(sorted(movies_to_sort)[::-1], start=1):
        try: 
            os.symlink(movie_dir+"/Nimed/"+movie,
                movie_dir+"/Viimati lisatud/{:03d} - {}".format(index, movie.strip()))
        except Exception as e:
            debug("error while symlinking {}".format(str(e)))



def main():
    info("updating genres folder")
    g = get_list_of_genres()
    info("creating folders for {} genres and creating movie symlinks".format(len(g)))
    create_genre_dirs_and_movie_symlinks(g)
    info("sorting movies by year")
    sort_movies_by_year()
    info("sort by adding time")
    sort_by_adding_time()
    info("done")



if __name__ == '__main__':
    main()
