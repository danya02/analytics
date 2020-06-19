from flask import Flask, render_template, request, Response, make_response
from database import *
import user
import functools

application = Flask(__name__)
app = application

@app.before_request
def open_db():
    db.connect()

@app.after_request
def close_db(resp):
    db.close()
    return resp

def get_user():
    return user.User(request)


def apply_cookies(resp, user):
    if len(resp)==1:
        if not isinstance(resp[0], Response):
            resp = make_response(resp[0])
    else:
        resp = make_response(*resp)
    
    to_set = set(user.cookies)
    existing = set(request.cookies)
    to_unset = existing.difference(to_set)

    for name in to_unset:
        resp.delete_cookie(name)
        
    for name in to_set:
        print(name)
        resp.set_cookie(name, str(user.cookies[name]), samesite='lax', secure=True, max_age=999999999)
    return resp

@app.route('/')
def index():
    user = get_user()
    return apply_cookies((render_template('index.html', user=user),), user)

