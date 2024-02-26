from flask import Flask, render_template, jsonify, request, session,redirect, url_for, abort, make_response
import json, os, base64, math
from os import environ as env
from urllib.parse import quote_plus, urlencode
from authlib.integrations.flask_client import OAuth
from functools import wraps

from data import *


app = Flask(__name__)
app.secret_key = env['FLASK_SECRET']

oauth = OAuth(app)

with app.app_context():
    setup()

oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration'
)

@app.route("/login")
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )

@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    userinfo = session["user"]["userinfo"]
    name = userinfo["nickname"]
    email = userinfo["email"]
    img = userinfo["picture"]
    user_id = update_user(name, email, img)
    if (user_id is None):
        user_id = add_user(name, email, img)
    session["user_id"] = user_id
    return redirect("/")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://" + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("load_home", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('user') is None:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

@app.route("/", methods=['GET', 'POST'])
def load_home():
    page = request.args.get('page', 1, type=int)
    total = math.ceil( (get_total()['count'])/10 )
    if page < 1 or page > total:
        abort(404) #invalid page number
    if request.method == 'POST':
        session['location'] = request.form
    else:
        if request.args.get('recent') == 'true':
            session.pop('location', None)
    posts = get_posts(session.get('location', None), page)
    return render_template("home.html", posts=posts, page=page, total=total)

@app.get("/map")
def load_map():
    return render_template("map_main.html")

@app.get("/user/<int:user_id>")
def show_user_profile(user_id):
    page = request.args.get('page', 1, type=int)
    total = math.ceil( (get_total(user_id)['count'])/10 )
    if total == 0: total = 1
    if page < 1 or page > total:
        abort(404) #invalid page number
    posts = get_users_posts(user_id, page)
    user = get_users_info(user_id)
    return render_template("user_home.html", posts=posts, user=user, page=page, total=total)
    

@app.route("/create", methods=['GET', 'POST'])
@require_auth
def create_post():
    if request.method == 'GET':
        return render_template("create.html")
    else:
        fd = request.form
        img = request.files['image-input']
        user_id = session["user_id"]["id"]
        add_post(fd, img, user_id)
        return redirect("/")

@app.get("/edit/<int:user_id>")
@require_auth
def edit_post(user_id):
    if session['user_id']['id'] != user_id:
        abort(404) #not authorized
    post_id = request.args.get('post', -1, type=int)
    post = get_single_post(post_id, user_id)
    if post is None:
        abort(404) #post doesnt exist or not yours
    return render_template("edit_post.html", post=post, post_id=post_id)

@app.route("/api/post/delete", methods=['DELETE'])
@require_auth
def delete_user_post():
    post_id = request.json['id']
    if delete_post(post_id, session['user_id']['id']) == 0:
        resp = make_response("Invalid request", 400)
    else:
        resp = make_response("Row deleted", 200)
    resp.headers['Content-Type'] = "text/plain"
    return resp

@app.post("/api/post/edit")
@require_auth
def edit_user_post():
    fd = request.form
    img = request.files['image-input']
    update_post(fd, img)
    return redirect("/")


# @app.get("/search", methods=["POST"])
# def search_result():
#     return 
@app.route("/search", methods=['GET'])
def search_posts():
    search_term = request.args.get('q', '')
    posts = search_posts_in_database(search_term)
    return jsonify(posts) 
