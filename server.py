from flask import Flask, request, render_template, jsonify

app = Flask(__name__)

@app.get("/")
def load_home():
    return render_template("home.html")