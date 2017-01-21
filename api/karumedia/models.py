import datetime
from mongoengine import *

class Media(Document):
    title = StringField()
    slug = StringField(unique=True)
    imdb_id = StringField(unique=True)
    runtime = IntField()
    genres = ListField(StringField())
    mpa_rating = StringField()
    rating = FloatField()
    yt_trailer_code = StringField()
    date_added = DateTimeField(default=datetime.datetime.now)
    parrent = ReferenceField('self')
    season = IntField()
    episode = IntField()
    release_date = StringField()
    type = StringField()
    plot_outline = StringField()
    plots = ListField(StringField())
    year = IntField()

class MediaFile(Document):
    url = URLField()
    path = StringField()
    media = ReferenceField(Media)
    mimetype = StringField()
    resolution = StringField(choices=('480p', '720p', '1080p', 'native'), default="native")

class MediaPoster(Document):
    poster = FileField()
    media = ReferenceField(Media)

class Task(Document):
    progress = FloatField(default=0)
    state = StringField(choices=('starting', 'running', 'done'), default='starting')
    creation_time = DateTimeField(default=datetime.datetime.now)
    sub_tasks = ListField(ReferenceField('self'), default=list)

    meta = {'allow_inheritance': True}

class TaskMetainfoDl(Task):
    info_hash = StringField(required=True)
    imdb_id = StringField()

class TaskImdbDl(Task):
    imdb_id = StringField(required=True)
    media = ReferenceField(Media)

class TaskTorrentDl(Task):
    info_hash = StringField(required=True)
    imdb_id = StringField()
    media = ReferenceField(Media)

