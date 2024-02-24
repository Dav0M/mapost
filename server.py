from flask import Flask, render_template, jsonify, request, session,redirect, url_for, abort
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
    if (update_user(name,email,img) == 0):
        add_user(name, email, img)
    # print(token)
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
        abort(404)
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

@app.get("/user_home")
@require_auth
def user_home():
    return render_template("user_home.html")

@app.route("/create", methods=['GET', 'POST'])
@require_auth
def create_post():
    if request.method == 'GET':
        return render_template("create.html")
    else:
        fd = request.form
        img = request.files['image-input']
        email = session["user"]["userinfo"]["email"]
        id = get_userid(email)["id"]
        #print(img)
        add_post(fd, img, id)
        return redirect("/")

# @app.get("/search", methods=["POST"])
# def search_result():
#     return 