from flask import Flask, render_template, jsonify, request, session,redirect, url_for
import json, os, base64
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
    if request.method == 'POST':
        posts = get_posts(request.form)
    else:
        posts = get_posts()
    return render_template("home.html", posts=posts, session=session)

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

@app.route("/search", methods=['GET'])
def search_posts():
    search_term = request.args.get('q', '')
    posts = search_posts_in_database(search_term)
    return jsonify(posts) 