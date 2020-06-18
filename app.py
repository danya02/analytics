from flask import Flask
from database import *

application = Flask(__name__)
app = application

@app.before_request
def open_db():
    db.connect()

@app.after_request
def close_db(resp):
    db.close()
    return resp

@app.route('/')
def index():
    return 'Hello World'
