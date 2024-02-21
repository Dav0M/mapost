from flask import Flask, render_template, jsonify, request, session,redirect, url_for
import json, os
from os import environ as env
from urllib.parse import quote_plus, urlencode
from authlib.integrations.flask_client import OAuth

from data import add_post, get_posts, setup


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
    # print(token)
    return redirect("logged")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://" + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("home", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )


@app.get("/")
def load_home():
    posts = get_posts()
    return render_template("home.html", posts=posts)

@app.route("/logged")
def logged():
    return render_template("home_logged.html")

@app.get("/user_home")
def user_home():
    return render_template("user_home.html")


@app.get("/search", methods=["POST"])
def search_result():
    return 