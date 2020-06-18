from peewee import *

import logging
logger = logging.getLogger('peewee')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

db = SqliteDatabase('data.db')

class MyModel(Model):
    class Meta:
        database = db

db.connect()
db.create_tables([])
db.close()
