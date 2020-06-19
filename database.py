from peewee import *
import uuid
import datetime

import logging
logger = logging.getLogger('peewee')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

db = SqliteDatabase('data.db')

class MyModel(Model):
    class Meta:
        database = db

class UserModel(MyModel):
    uid = UUIDField(default=uuid.uuid4, unique=True)

class Site(MyModel):
    url = CharField(unique=True)
    name = CharField()
    description = TextField()
    uid = UUIDField(default=uuid.uuid4, unique=True)

class Endpoint(MyModel):
    site = ForeignKeyField(Site)
    address = CharField(unique=True)

class Session(MyModel):
    user = ForeignKeyField(UserModel)

class Visit(MyModel):
    ip = IPField()
    session = ForeignKeyField(Session)

    endpoint = ForeignKeyField(Endpoint)
    date = DateTimeField(default=datetime.datetime.now)

db.connect()
db.create_tables([UserModel, Site, Session, Visit])
db.close()
