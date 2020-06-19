from flask import Flask, render_template, request, Response, make_response, jsonify, abort, url_for, redirect
from database import *
import user
import functools

application = Flask(__name__)
app = application

app.secret_key = b'super secret super spoopy'

@app.before_request
def open_db():
    db.connect()

@app.after_request
def close_db(resp):
    db.close()
    resp.headers['Access-Control-Allow-Origin'] = 'https://developer.mozilla.org'
    resp.headers['Access-Control-Allow-Credentials'] = 'true'
    return resp

def get_user():
    return user.User(request)


def apply_cookies(resp, user):
    if isinstance(resp, tuple):
        if len(resp)==1:
            if not isinstance(resp[0], Response):
                resp = make_response(resp[0])
        else:
            resp = make_response(*resp)
    elif not isinstance(resp, Response):
        resp = make_response(resp)

    to_set = set(user.cookies)
    existing = set(request.cookies)
    to_unset = existing.difference(to_set)

    for name in to_unset:
        resp.delete_cookie(name)
        
    for name in to_set:
        print(name)
        resp.set_cookie(name, str(user.cookies[name]), secure=True, max_age=999999999)
    return resp

@app.route('/')
def index():
    user = get_user()
    return apply_cookies(render_template('index.html', user=user, site_uid='845087d3-45b0-44ec-83a6-6d3930a99b04', addr='index/slash/slashy'), user)

@app.route('/consent', methods=['POST'])
def register_consent():
    cookies = dict(request.cookies)
    cookies.update({'consent': '1'})
    class Wrap:
        def __init__(self, cookies):
            self.cookies = cookies
    return apply_cookies('', Wrap(cookies))


def transparent_pixel():
    compr = ['89504e470d0a1a0a', 7, 'd49484452', 7, '1', 7, '10804', 6, 'b51c0c02', 7, 'b49444154789c63626', 8, '9', 3,
            '31911d9e4', 8, '49454e44ae426082']
    line = ''
    for i in compr:
        if isinstance(i, int):
            line += '0'*i
        else:
            line += i
    num = int(line, 16)
    data = num.to_bytes(len(line)//2, 'big')
    return data


@app.route('/site/<uuid:site_uid>/endpoint/<path:addr>')
def tracking_img(site_uid, addr):
    user = get_user()
    try:
        user.add_visit(site_uid, addr)
        resp = Response(transparent_pixel(), mimetype='image/png')
        return apply_cookies(resp, user)
    except FileNotFoundError:
        return abort(404)

@app.route('/site/<uuid:site_uid>/track', methods=['POST'])
def track_visit(site_uid):
    user = get_user()
    try:
        user.add_visit(site_uid, request.data)
        return apply_cookies(jsonify({'uid': user.user.uid, 'consent': user.has_consented}), user)
    except FileNotFoundError:
        return jsonify({'error': 'The site ID does not exist. This may be a misconfiguration of the website.'})



@app.route('/admin/sites')
def sites_config():
    return render_template('admin-sites.html', Site=Site)

@app.route('/admin/sites/new', methods=['POST'])
def add_site():
    site = Site.create(name=request.form['name'], url=request.form['url'])
    return redirect(url_for('view_site', uid=site.uid))

@app.route('/admin/sites/<uuid:uid>')
def view_site(uid):
    try:
        site = Site.get(Site.uid == uid)
    except Site.DoesNotExist:
        return abort(404)
    return render_template('admin-view-site.html', site=site)

@app.route('/admin/sites/<uuid:uid>/alter', methods=['POST'])
def alter_site(uid):
    try:
        site = Site.get(Site.uid == uid)
    except Site.DoesNotExist:
        return abort(404)
    site.name = request.form['name']
    site.url = request.form['url']
    site.save()
    return redirect(url_for('view_site', uid=uid))

@app.route('/test')
def test():
    return Response(''.join([f'alert({repr(i)});' for i in [(v, request.cookies[v]) for v in request.cookies]]), mimetype='text/javascript')
