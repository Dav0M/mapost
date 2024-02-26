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
    return redirect(f"/user/{session['user_id']['id']}")


# @app.get("/search", methods=["POST"])
# def search_result():
#     return 