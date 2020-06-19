from peewee import *
import uuid

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


db.connect()
db.create_tables([UserModel])
db.close()
